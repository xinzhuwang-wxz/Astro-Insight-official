# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Dict, Any
from .types import DatasetInfo, CodeComplexity


class CodeGenerationPrompts:
    """代码生成专用Prompt管理器"""
    
    @staticmethod
    def get_code_generation_prompt(dataset_info: DatasetInfo, user_requirement: str, complexity: CodeComplexity) -> str:
        """生成代码生成的主prompt"""
        
        base_prompt = f"""你是一个专业的天文数据分析代码生成助手。请根据以下信息生成完整、可直接运行的Python代码。

## 数据集信息
{dataset_info['description_content']}

数据集路径: {dataset_info['path']}
数据集名称: {dataset_info['name']}
列名: {', '.join(dataset_info['columns']) if dataset_info['columns'] else '请自动检测'}

## 用户需求
{user_requirement}

## 代码生成要求
"""
        
        if complexity == CodeComplexity.SIMPLE:
            requirements = """
1. 生成简单的数据操作代码（如数据展示、基本统计）
2. 代码应该简洁明了，易于理解
3. 包含必要的数据加载和基本处理
"""
        elif complexity == CodeComplexity.MODERATE:
            requirements = """
1. 生成中等复杂度的分析代码（如数据可视化、数据清洗）
2. 包含适当的数据预处理步骤
3. 生成有意义的图表或分析结果
4. 如果生成图片，请保存到'output/'目录下
"""
        else:  # COMPLEX
            requirements = """
1. 生成复杂的分析代码（如机器学习、高级统计分析）
2. 包含完整的数据预处理流程
3. 实现合适的算法和模型
4. 提供详细的结果分析和解释
5. 包含模型评估和验证
6. 如果生成图片，请保存到'output/'目录下
"""
        
        code_standards = """
## 代码标准
1. 必须是完整可运行的Python代码
2. 包含所有必要的import语句
3. 添加适当的注释和说明（英文）
4. 处理可能的异常情况
5. 确保输出结果清晰易懂
6. 如果数据集路径不存在，请尝试相对路径
7. 生成的图片保存到'output/'目录（如果不存在请创建）

## 重要：代码格式要求
- 字符串、标点符号、可视化图片中的文字必须是英文的
- 所有代码必须使用英文标点符号（英文逗号 , 英文分号 ; 英文括号等）
- 绝对不要使用中文标点符号（如中文逗号 ，）
- 变量名和函数名使用英文


## 输出格式
请直接输出可执行的Python代码，不要包含任何其他文字说明。代码应该从import开始，到最终输出结束。
确保所有代码语法完全符合Python标准，使用正确的英文标点符号。
"""
        
        return base_prompt + requirements + code_standards
    
    @staticmethod
    def get_error_recovery_prompt(original_code: str, error_message: str, dataset_info: DatasetInfo) -> str:
        """生成错误恢复的prompt"""
        return f"""之前生成的代码执行时出现了错误，请修复这个问题并重新生成代码。

## 原始代码
```python
{original_code}
```

## 错误信息
{error_message}

## 数据集信息
数据集路径: {dataset_info['path']}
列名: {', '.join(dataset_info['columns']) if dataset_info['columns'] else '请自动检测'}

## 常见错误类型及修复方法：
1. **SyntaxWarning: invalid escape sequence '\d'** 
   - 原因：Windows路径中的反斜杠被当作转义字符
   - 修复：使用raw字符串 r"C:\path\file.csv" 或正斜杠 "C:/path/file.csv"

2. **中文标点符号语法错误**
   - 原因：使用了中文逗号、括号等
   - 修复：全部替换为英文标点符号

3. **ImportError或ModuleNotFoundError**
   - 原因：缺少必要的库导入
   - 修复：添加正确的import语句

4. **FileNotFoundError**
   - 原因：文件路径不正确
   - 修复：使用相对路径或添加路径检查

## 修复要求
1. 仔细分析错误类型，针对性修复
2. 对于路径问题，优先使用 r"" raw字符串或正斜杠
3. 确保所有标点符号都是英文的
4. 保持原有功能逻辑不变
5. 添加必要的错误处理和文件存在性检查
6. 确保代码语法完全正确

## 重要：代码格式要求
- 所有代码必须使用英文标点符号（英文逗号 , 英文分号 ; 英文括号等）
- 绝对不要使用中文标点符号（如中文逗号 ，）
- Windows路径必须使用raw字符串 r"" 或正斜杠 /
- 确保所有语法符合Python标准

请直接输出修复后的完整Python代码，不要包含任何解释文字。"""
    
    @staticmethod
    def get_complexity_analysis_prompt(user_requirement: str) -> str:
        """分析用户需求复杂度的prompt"""
        return f"""请分析以下用户需求的复杂度级别：

用户需求: {user_requirement}

复杂度级别定义：
- SIMPLE: 简单数据操作（展示数据、基本统计、简单查询）
- MODERATE: 中等复杂度（数据可视化、数据清洗、聚合分析）  
- COMPLEX: 复杂分析（机器学习、高级统计、预测建模）

请只回答复杂度级别：SIMPLE、MODERATE 或 COMPLEX"""
    
    @staticmethod
    def get_dataset_selection_prompt(available_datasets: str, user_requirement: str) -> str:
        """数据集选择prompt"""
        return f"""根据用户需求选择最合适的数据集。

## 可用数据集
{available_datasets}

## 用户需求
{user_requirement}

请选择最适合的数据集，只回答数据集的索引号（从1开始）。如果用户需求中明确提到了数据集名称，请选择对应的数据集。"""
