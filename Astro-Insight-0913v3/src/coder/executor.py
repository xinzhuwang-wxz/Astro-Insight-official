# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import sys
import subprocess
import tempfile
import time
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional, Dict, Any, List
from pathlib import Path

from .types import CodeExecutionResult, ExecutionStatus


class CodeExecutor:
    """代码执行器 - 安全执行生成的Python代码"""
    
    def __init__(self, timeout: int = 60, output_dir: str = "output"):
        self.timeout = timeout
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 安全的执行环境设置
        self.allowed_imports = {
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'sklearn', 'scipy',
            'astropy', 'astroquery', 'plotly', 'warnings', 'os', 'sys',
            'pathlib', 'json', 'csv', 're', 'math', 'statistics', 'datetime',
            'collections', 'itertools', 'functools', 'operator'
        }
        
        # 禁止的操作
        self.forbidden_patterns = [
            'import subprocess', 'import os.system', '__import__',
            'exec(', 'eval(', 'input(', 'raw_input(', 'execfile(', 'compile('
        ]
    
    def execute_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> CodeExecutionResult:
        """执行代码并返回结果"""
        start_time = time.time()
        
        # 预处理代码
        processed_code = self._preprocess_code(code)
        
        # 安全检查
        safety_check = self._safety_check(processed_code)
        if not safety_check["safe"]:
            return CodeExecutionResult(
                status=ExecutionStatus.ERROR,
                code=code,
                output=None,
                error=f"安全检查失败: {safety_check['reason']}",
                execution_time=time.time() - start_time,
                generated_files=[],
                generated_texts=[]
            )
        
        # 执行前记录已有文件
        before_files = set(self._list_output_files())
        
        # 执行代码
        try:
            result = self._execute_in_sandbox(processed_code, context or {})
            execution_time = time.time() - start_time
            
            # 执行后获取新生成的文件（差集 + 时间窗口）
            generated_files = self._find_new_generated_files(before_files, start_time)
            generated_texts = self._find_new_generated_texts(before_files, start_time)
            
            return CodeExecutionResult(
                status=ExecutionStatus.SUCCESS if result["success"] else ExecutionStatus.ERROR,
                code=code,
                output=result["output"],
                error=result["error"],
                execution_time=execution_time,
                generated_files=generated_files,
                generated_texts=generated_texts
            )
            
        except Exception as e:
            return CodeExecutionResult(
                status=ExecutionStatus.ERROR,
                code=code,
                output=None,
                error=f"执行异常: {str(e)}",
                execution_time=time.time() - start_time,
                generated_files=[],
                generated_texts=[]
            )
    
    def _preprocess_code(self, code: str) -> str:
        """预处理代码"""
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            # 处理输出目录
            if 'savefig(' in line:
                # 避免破坏 f-string/变量/Path 等动态路径
                dynamic_tokens = ["f'", 'f"', '{', 'output_dir', 'Path(', 'os.path', 'pathlib']
                is_dynamic = any(tok in line for tok in dynamic_tokens)

                # 仅在参数为纯字符串字面量，且未显式指向 output 时才注入
                if not is_dynamic:
                    try:
                        before, after = line.split('savefig(', 1)
                        after_stripped = after.lstrip()
                        if after_stripped.startswith("'") or after_stripped.startswith('"'):
                            # 纯字面量路径，若未包含 output/ 则前置输出目录
                            if 'output/' not in after_stripped and str(self.output_dir) not in after_stripped:
                                line = before + f'savefig("{self.output_dir}/' + after_stripped[1:]
                    except Exception:
                        pass

            # 处理文件路径
            if 'pd.read_csv' in line or 'pd.read_' in line:
                # 确保使用正确的路径分隔符
                line = line.replace('\\', '/')
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _safety_check(self, code: str) -> Dict[str, Any]:
        """代码安全检查"""
        # 检查禁止的模式
        for pattern in self.forbidden_patterns:
            if pattern in code:
                return {"safe": False, "reason": f"禁止的操作: {pattern}"}
        
        # 检查文件操作的安全性
        file_safety = self._check_file_operations(code)
        if not file_safety["safe"]:
            return file_safety
        
        # 检查导入的模块
        import ast
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        if module_name not in self.allowed_imports:
                            return {"safe": False, "reason": f"禁止导入模块: {module_name}"}
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        if module_name not in self.allowed_imports:
                            return {"safe": False, "reason": f"禁止导入模块: {module_name}"}
        except SyntaxError as e:
            return {"safe": False, "reason": f"语法错误: {str(e)}"}
        
        return {"safe": True, "reason": ""}
    
    def _check_file_operations(self, code: str) -> Dict[str, Any]:
        """检查文件操作的安全性"""
        import ast
        import os
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # 检查open()函数调用
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                    if node.args:
                        # 获取文件路径
                        if isinstance(node.args[0], ast.Str):  # Python 3.7及以下
                            file_path = node.args[0].s
                        elif isinstance(node.args[0], ast.Constant):  # Python 3.8+
                            file_path = node.args[0].value
                        else:
                            continue
                        
                        # 检查路径是否安全
                        if not self._is_safe_file_path(file_path):
                            return {"safe": False, "reason": f"不安全的文件路径: {file_path}"}
                
                # 检查os.path操作
                elif isinstance(node, ast.Call):
                    if (isinstance(node.func, ast.Attribute) and 
                        isinstance(node.func.value, ast.Attribute) and
                        isinstance(node.func.value.value, ast.Name) and
                        node.func.value.value.id == 'os' and
                        node.func.value.attr == 'path'):
                        # 检查os.path操作是否安全
                        if not self._is_safe_os_path_operation(node):
                            return {"safe": False, "reason": "不安全的os.path操作"}
        
        except Exception as e:
            return {"safe": False, "reason": f"文件操作检查失败: {str(e)}"}
        
        return {"safe": True, "reason": ""}
    
    def _is_safe_file_path(self, file_path: str) -> bool:
        """检查文件路径是否安全"""
        import os
        
        # 允许相对路径（在当前工作目录或output目录下）
        if not os.path.isabs(file_path):
            return True
        
        # 允许绝对路径指向output目录
        try:
            abs_path = os.path.abspath(file_path)
            output_abs_path = os.path.abspath(str(self.output_dir))
            return abs_path.startswith(output_abs_path)
        except:
            return False
    
    def _is_safe_os_path_operation(self, node) -> bool:
        """检查os.path操作是否安全"""
        # 允许常用的os.path操作，但禁止访问系统敏感路径
        safe_operations = ['join', 'exists', 'isdir', 'isfile', 'basename', 'dirname', 'splitext']
        if node.func.attr in safe_operations:
            return True
        return False
    
    def _execute_in_sandbox(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """在沙箱环境中执行代码"""
        output_buffer = StringIO()
        error_buffer = StringIO()
        
        try:
            # 准备执行环境
            import builtins
            def _safe_exit(code: int = 0):
                raise SystemExit(code)

            globals_dict = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sorted': sorted,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'open': open,             # 添加 open 函数
                    '__import__': __import__,  # 允许import
                    'locals': locals,         # 添加 locals
                    'globals': globals,       # 添加 globals
                    'exit': _safe_exit,       # 安全退出
                    'quit': _safe_exit,       # 安全退出
                },
                '__name__': '__main__',       # 添加 __name__
                '__file__': '<generated_code>',  # 添加 __file__
            }
            globals_dict.update(context)
            
            # 重定向输出
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                exec(code, globals_dict)
            
            return {
                "success": True,
                "output": output_buffer.getvalue(),
                "error": None
            }

        except SystemExit as e:
            # 将用户代码中的 exit()/quit() 视为正常结束
            return {
                "success": True,
                "output": output_buffer.getvalue(),
                "error": None
            }
        except Exception as e:
            error_info = error_buffer.getvalue()
            if not error_info:
                error_info = str(e)
            
            # 添加详细的错误信息
            error_details = f"{error_info}\n\n详细错误:\n{traceback.format_exc()}"
            
            return {
                "success": False,
                "output": output_buffer.getvalue(),
                "error": error_details
            }
    
    def _list_output_files(self) -> List[str]:
        """列出输出目录下的所有文件（绝对或相对路径字符串）"""
        files = []
        if self.output_dir.exists():
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    files.append(str(file_path))
        return files
    
    def _find_new_generated_files(self, before_files: set, start_time: float) -> List[str]:
        """根据执行前后差集与修改时间，返回本次新生成的图片文件"""
        after_files = set(self._list_output_files())
        allowed_ext = {'.png', '.jpg', '.jpeg', '.svg'}
        
        # 差集新增
        diff_new = {f for f in (after_files - before_files) if Path(f).suffix.lower() in allowed_ext}
        
        # 执行开始后被修改/写入的文件（覆盖写入的场景）
        time_new = {f for f in after_files if Path(f).suffix.lower() in allowed_ext and Path(f).stat().st_mtime >= start_time}
        
        combined = sorted(diff_new.union(time_new), key=lambda p: Path(p).stat().st_mtime)
        return list(combined)

    def _find_new_generated_texts(self, before_files: set, start_time: float) -> List[str]:
        """根据执行前后差集与修改时间，返回本次新生成的文本类工件文件"""
        after_files = set(self._list_output_files())
        allowed_ext = {'.txt', '.log', '.md', '.json', '.csv'}
        diff_new = {f for f in (after_files - before_files) if Path(f).suffix.lower() in allowed_ext}
        time_new = {f for f in after_files if Path(f).suffix.lower() in allowed_ext and Path(f).stat().st_mtime >= start_time}
        combined = sorted(diff_new.union(time_new), key=lambda p: Path(p).stat().st_mtime)
        return list(combined)
    
    def _find_generated_files(self) -> List[str]:
        """查找执行过程中生成的文件（保留旧方法以兼容，但不再用于主流程）"""
        generated_files = []
        
        if self.output_dir.exists():
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    generated_files.append(str(file_path))
        
        return generated_files
    
    def clean_output_dir(self) -> None:
        """清理输出目录"""
        if self.output_dir.exists():
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"清理文件失败 {file_path}: {e}")
    
    def validate_code_syntax(self, code: str) -> Dict[str, Any]:
        """验证代码语法"""
        try:
            compile(code, '<string>', 'exec')
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"语法错误: {str(e)}"}
        except Exception as e:
            return {"valid": False, "error": f"编译错误: {str(e)}"}
