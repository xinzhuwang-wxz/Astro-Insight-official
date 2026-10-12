# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import time
import uuid
from typing import Optional, Dict, Any, List

from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

from .types import (
    CoderAgentState, DatasetInfo, CodeGenerationRequest, 
    CodeExecutionResult, CodeComplexity, ExecutionStatus
)
from .dataset_selector import DatasetSelector
from .prompts import CodeGenerationPrompts
from .executor import CodeExecutor


class CodeGeneratorAgent:
    """代码生成Agent - 核心代理类"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.dataset_selector = DatasetSelector()
        self.code_executor = CodeExecutor()
        self.prompts = CodeGenerationPrompts()
        
        # 获取LLM实例
        self.llm = get_llm_by_type(AGENT_LLM_MAP.get("coder", "basic"))
    
    def create_initial_state(self, user_input: str, session_id: Optional[str] = None) -> CoderAgentState:
        """创建初始状态"""
        return CoderAgentState(
            session_id=session_id or str(uuid.uuid4()),
            user_input=user_input,
            available_datasets=self.dataset_selector.get_available_datasets(),
            selected_dataset=None,
            generation_request=None,
            generated_code=None,
            execution_result=None,
            current_step="dataset_selection",
            retry_count=0,
            max_retries=self.max_retries,
            error_info=None,
            error_recovery_attempts=0,
            code_history=[],
            execution_history=[],
            timestamp=time.time()
        )
    
    def process_request(self, state: CoderAgentState) -> CoderAgentState:
        """处理完整的代码生成请求"""
        try:
            # Step 1: 选择数据集
            if state["current_step"] == "dataset_selection":
                state = self._select_dataset(state)
            
            # Step 2: 分析复杂度
            if state["current_step"] == "complexity_analysis":
                state = self._analyze_complexity(state)
            
            # Step 3: 生成代码
            if state["current_step"] == "code_generation":
                state = self._generate_code(state)
            
            # Step 4: 执行代码
            if state["current_step"] == "code_execution":
                state = self._execute_code(state)
            
            # Step 5: 错误恢复（如果需要）
            if state["current_step"] == "error_recovery":
                state = self._recover_from_error(state)
            
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "processing_error",
                "message": str(e),
                "step": state["current_step"]
            }
            state["current_step"] = "error"
            return state
    
    def _select_dataset(self, state: CoderAgentState) -> CoderAgentState:
        """选择数据集"""
        try:
            available_datasets = state["available_datasets"]
            
            if not available_datasets:
                state["error_info"] = {
                    "type": "no_datasets",
                    "message": "未找到可用的数据集"
                }
                state["current_step"] = "error"
                return state
            
            # 如果只有一个数据集，直接选择
            if len(available_datasets) == 1:
                state["selected_dataset"] = available_datasets[0]
            else:
                # 使用LLM选择最合适的数据集
                datasets_summary = self.dataset_selector.get_dataset_summary()
                selection_prompt = self.prompts.get_dataset_selection_prompt(
                    datasets_summary, state["user_input"]
                )
                
                response = self.llm.invoke(selection_prompt)
                
                # 解析选择结果
                try:
                    selected_index = int(response.content.strip()) - 1
                    if 0 <= selected_index < len(available_datasets):
                        state["selected_dataset"] = available_datasets[selected_index]
                    else:
                        # 默认选择第一个
                        state["selected_dataset"] = available_datasets[0]
                except:
                    # 解析失败，默认选择第一个
                    state["selected_dataset"] = available_datasets[0]
            
            state["current_step"] = "complexity_analysis"
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "dataset_selection_error",
                "message": str(e)
            }
            state["current_step"] = "error"
            return state
    
    def _analyze_complexity(self, state: CoderAgentState) -> CoderAgentState:
        """分析请求复杂度"""
        try:
            complexity_prompt = self.prompts.get_complexity_analysis_prompt(state["user_input"])
            response = self.llm.invoke(complexity_prompt)
            
            # 解析复杂度
            complexity_str = response.content.strip().upper()
            if complexity_str in ["SIMPLE", "MODERATE", "COMPLEX"]:
                complexity = CodeComplexity(complexity_str.lower())
            else:
                # 默认为中等复杂度
                complexity = CodeComplexity.MODERATE
            
            # 创建生成请求
            state["generation_request"] = CodeGenerationRequest(
                dataset_info=state["selected_dataset"],
                user_requirement=state["user_input"],
                complexity=complexity,
                additional_context=None
            )
            
            state["current_step"] = "code_generation"
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "complexity_analysis_error",
                "message": str(e)
            }
            state["current_step"] = "error"
            return state
    
    def _generate_code(self, state: CoderAgentState) -> CoderAgentState:
        """生成代码"""
        try:
            request = state["generation_request"]
            
            # 构建代码生成prompt
            generation_prompt = self.prompts.get_code_generation_prompt(
                request["dataset_info"],
                request["user_requirement"], 
                request["complexity"]
            )
            
            # 调用LLM生成代码
            response = self.llm.invoke(generation_prompt)
            raw_generated_code = response.content.strip()
            
            print("🤖 LLM原始输出:")
            print("=" * 40)
            print(raw_generated_code)
            print("=" * 40)
            
            # 清理代码（移除markdown格式等）
            generated_code = self._clean_generated_code(raw_generated_code)
            
            print("🧹 清理后的代码:")
            print("=" * 40)
            print(generated_code)
            print("=" * 40)
            
            # 语法验证
            syntax_check = self.code_executor.validate_code_syntax(generated_code)
            if not syntax_check["valid"]:
                print(f"⚠️ 语法错误: {syntax_check['error']}")
                
                # 设置错误信息
                state["error_info"] = {
                    "type": "syntax_error",
                    "message": syntax_check["error"],
                    "code": generated_code,
                    "error_details": syntax_check.get("details", "")
                }
                
                # 如果语法有误，尝试修复
                if state["retry_count"] < state["max_retries"]:
                    state["retry_count"] += 1
                    state["current_step"] = "error_recovery"
                    print(f"🔄 开始第 {state['retry_count']} 次错误修复...")
                    return state
                else:
                    print(f"❌ 已达到最大重试次数 ({state['max_retries']})")
                    state["error_info"] = {
                        "type": "syntax_error_max_retries",
                        "message": f"语法错误，已达到最大重试次数: {syntax_check['error']}"
                    }
                    state["current_step"] = "error"
                    return state
            
            state["generated_code"] = generated_code
            state["code_history"].append({
                "code": generated_code,
                "timestamp": time.time(),
                "attempt": state["retry_count"] + 1
            })
            
            state["current_step"] = "code_execution"
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "code_generation_error",
                "message": str(e)
            }
            state["current_step"] = "error"
            return state
    
    def _execute_code(self, state: CoderAgentState) -> CoderAgentState:
        """执行代码"""
        try:
            execution_result = self.code_executor.execute_code(state["generated_code"])
            
            state["execution_result"] = execution_result
            state["execution_history"].append(execution_result)
            
            if execution_result["status"] == ExecutionStatus.SUCCESS:
                state["current_step"] = "completed"
            else:
                # 执行失败，尝试错误恢复
                if state["retry_count"] < state["max_retries"]:
                    state["retry_count"] += 1
                    state["error_info"] = {
                        "type": "execution_error",
                        "message": execution_result["error"],
                        "code": execution_result["code"]
                    }
                    state["current_step"] = "error_recovery"
                else:
                    state["error_info"] = {
                        "type": "execution_error_max_retries",
                        "message": f"代码执行失败，已达到最大重试次数: {execution_result['error']}"
                    }
                    state["current_step"] = "error"
            
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "code_execution_error",
                "message": str(e)
            }
            state["current_step"] = "error"
            return state
    
    def _recover_from_error(self, state: CoderAgentState) -> CoderAgentState:
        """从错误中恢复 - 简化版：直接重写代码"""
        try:
            error_info = state["error_info"]
            print(f"🛠️ 错误修复: {error_info['type']}")
            print(f"🔄 第 {state['retry_count']} 次尝试，直接重写代码...")
            
            if error_info["type"] in ["syntax_error", "execution_error"]:
                # 构建重写代码的prompt，包含完整上下文
                rewrite_prompt = self._build_rewrite_prompt(
                    user_request=state["user_input"],
                    failed_code=error_info["code"],
                    error_message=error_info["message"],
                    dataset_info=state["selected_dataset"],
                    attempt_count=state["retry_count"]
                )
                
                # 让LLM完全重写代码
                response = self.llm.invoke(rewrite_prompt)
                raw_rewritten_code = response.content.strip()
                
                print("🤖 LLM重写代码原始输出:")
                print("=" * 40)
                print(raw_rewritten_code)
                print("=" * 40)
                
                rewritten_code = self._clean_generated_code(raw_rewritten_code)
                
                print("🧹 清理后的重写代码:")
                print("=" * 40)
                print(rewritten_code)
                print("=" * 40)
                
                print("🔍 验证重写后的代码...")
                syntax_check = self.code_executor.validate_code_syntax(rewritten_code)
                
                if syntax_check["valid"]:
                    print("✅ 代码重写成功!")
                    state["generated_code"] = rewritten_code
                    state["code_history"].append({
                        "code": rewritten_code,
                        "timestamp": time.time(),
                        "attempt": state["retry_count"],
                        "rewrite": True
                    })
                    state["current_step"] = "code_execution"
                    state["error_recovery_attempts"] += 1
                    # 清除错误信息
                    if "error_info" in state:
                        del state["error_info"]
                else:
                    print(f"❌ 代码重写仍有错误: {syntax_check['error']}")
                    # 继续重试
                    if state["retry_count"] < state["max_retries"]:
                        state["retry_count"] += 1
                        state["error_info"] = {
                            "type": "syntax_error",
                            "message": syntax_check["error"],
                            "code": rewritten_code
                        }
                        state["current_step"] = "error_recovery"
                    else:
                        state["error_info"] = {
                            "type": "recovery_failed",
                            "message": f"代码重写失败: {syntax_check['error']}"
                        }
                        state["current_step"] = "error"
            else:
                print(f"❌ 无法处理的错误类型: {error_info['type']}")
                state["current_step"] = "error"
            
            return state
            
        except Exception as e:
            print(f"❌ 错误恢复过程异常: {str(e)}")
            state["error_info"] = {
                "type": "error_recovery_error",
                "message": str(e)
            }
            state["current_step"] = "error"
            return state
    
    def _build_rewrite_prompt(self, user_request, failed_code, error_message, dataset_info, attempt_count):
        """构建重写代码的prompt"""
        return f"""你需要完全重写代码来满足用户需求。之前的代码失败了，请分析错误并重新编写。

## 用户需求
{user_request}

## 数据集信息
- 名称: {dataset_info['name']}
- 路径: {dataset_info['path']}
- 列名: {', '.join(dataset_info['columns'][:10])}{'...' if len(dataset_info['columns']) > 10 else ''}

## 之前失败的代码
```python
{failed_code}
```

## 错误信息
{error_message}

## 重写要求
1. **完全重新编写代码** - 不要修复，要重写
2. **避免路径问题** - 使用相对路径或raw字符串: r"{dataset_info['path']}"
3. **只用英文标点** - 绝对不要用中文标点符号
4. **简化逻辑** - 保持代码简单直接
5. **添加错误处理** - 包含try-catch和文件检查

## 特别注意
- Windows路径必须用 r"path" 或 "path"（正斜杠）
- 所有标点符号必须是英文的：, . ; : ( ) [ ] {{ }}
- 不要使用 if __name__ == "__main__": 这样的模式
- 直接执行代码，不要包装在函数中

请直接输出完整的Python代码，不要任何解释："""
    
    def _clean_generated_code(self, code: str) -> str:
        """清理生成的代码 - 简化版本，只做基本清理"""
        print("🧹 开始代码清理...")
        
        # 1. 移除markdown代码块标记
        if code.startswith("```python"):
            code = code[9:]
            print("   - 移除了```python标记")
        elif code.startswith("```"):
            code = code[3:]
            print("   - 移除了```标记")
        
        if code.endswith("```"):
            code = code[:-3]
            print("   - 移除了结尾```标记")
        
        # 2. 移除首尾空白
        code = code.strip()
        
        # 替换中文标点符号为英文标点符号 - 小心处理字符串内容
        chinese_punctuations = {
            '，': ',',  # 中文逗号 -> 英文逗号
            '；': ';',  # 中文分号 -> 英文分号
            '：': ':',  # 中文冒号 -> 英文冒号
            '！': '!',  # 中文感叹号 -> 英文感叹号
            '？': '?',  # 中文问号 -> 英文问号
            '（': '(',  # 中文左括号 -> 英文左括号
            '）': ')',  # 中文右括号 -> 英文右括号
            '【': '[',  # 中文左方括号 -> 英文左方括号
            '】': ']',  # 中文右方括号 -> 英文右方括号
            '『': '{',  # 中文左大括号 -> 英文左大括号
            '』': '}',  # 中文右大括号 -> 英文右大括号
        }
    
        
        print("🧹 代码清理完成")
        return code.strip()
    
    def get_final_result(self, state: CoderAgentState) -> Dict[str, Any]:
        """获取最终结果"""
        if state["current_step"] == "completed" and state["execution_result"]:
            result = state["execution_result"]
            return {
                "success": True,
                "code": result["code"],
                "output": result["output"],
                "execution_time": result["execution_time"],
                "generated_files": result["generated_files"],
                "generated_texts": result.get("generated_texts", []),
                "dataset_used": state["selected_dataset"]["name"],
                "complexity": state["generation_request"]["complexity"].value if state["generation_request"] else "unknown",
                "retry_count": state["retry_count"]
            }
        else:
            error_info = state.get("error_info", {})
            return {
                "success": False,
                "error": error_info.get("message", "未知错误"),
                "error_type": error_info.get("type", "unknown"),
                "code": state.get("generated_code"),
                "dataset_used": state["selected_dataset"]["name"] if state["selected_dataset"] else None,
                "retry_count": state["retry_count"]
            }
