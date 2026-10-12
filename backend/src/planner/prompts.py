# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import List, Dict, Any, Optional
from .types import DatasetInfo, DialogueTurn, TaskStep


class PlannerPrompts:
    """Planner模块的Prompt管理器"""
    
    @staticmethod
    def get_initial_analysis_prompt(user_request: str, available_datasets: List[DatasetInfo]) -> str:
        """初始需求分析prompt"""
        datasets_summary = PlannerPrompts._format_datasets_summary(available_datasets)
        
        return f"""你是一个专业的天文数据分析需求规划助手。请分析用户的初始需求并准备进行多轮对话来明确具体需求。

## 用户初始需求
{user_request}

## 可用数据集
{datasets_summary}

## 分析任务
请分析用户需求并准备第一个回应。考虑以下方面：

1. **需求理解**: 用户想要做什么类型的天文数据分析？
2. **数据集匹配**: 根据用户需求，哪个数据集最适合？请从可用数据集中选择最合适的。
3. **任务复杂度**: 这需要简单、中等还是复杂的分析？
4. **澄清问题**: 需要向用户询问哪些关键信息？

## 数据集选择指导
- 如果用户提到"star"、"恒星"、"分类"、"预测"，优先考虑包含恒星数据的数据集
- 如果用户提到"galaxy"、"星系"、"SDSS"，优先考虑包含星系数据的数据集
- 如果用户需求不明确，选择数据量适中、适合探索的数据集

## 回应要求
请提供一个友好的回应，包括：
- 对用户需求的理解确认
- 明确推荐最合适的数据集（从可用数据集中选择）
- 解释为什么选择这个数据集
- 提出1-2个关键的澄清问题
- 保持专业但友好的语调

请直接提供回应内容，不要包含其他格式标记。"""

    @staticmethod
    def get_clarification_prompt(
        user_request: str, 
        dialogue_history: List[DialogueTurn], 
        selected_dataset: DatasetInfo,
        current_turn: int,
        max_turns: int
    ) -> str:
        """澄清需求prompt"""
        
        # 构建对话历史
        history_text = ""
        if dialogue_history:
            for turn in dialogue_history[-3:]:  # 只显示最近3轮
                history_text += f"用户: {turn.user_input}\n"
                history_text += f"助手: {turn.assistant_response}\n\n"
        else:
            history_text = "暂无对话历史\n\n"
        
        dataset_info = f"""
数据集: {selected_dataset.name}
描述: {selected_dataset.description}
主要列: {', '.join(selected_dataset.columns[:8])}
"""
        
        return f"""你是天文数据分析规划助手。请基于对话历史继续澄清用户需求。

## 对话历史
{history_text}

## 当前用户输入
{user_request}

## 选定数据集信息
{dataset_info}

## 对话状态
- 当前轮次: {current_turn}/{max_turns}
- 已收集信息: {PlannerPrompts._summarize_collected_info(dialogue_history)}

## 任务
请继续对话来明确需求细节。考虑：

1. **还需要澄清什么**: 数据筛选条件、可视化类型、分析目标等
2. **数据集适配**: 基于选定数据集的具体分析方案
3. **任务分解**: 开始思考如何将需求分解为具体步骤

## 回应要求
- 回应要简洁明确，避免重复之前的问题
- 如果信息足够，可以开始总结需求
- 如果接近轮次限制，主动询问是否确认需求
- 保持专业友好的语调
- 必须确认可视化需求 

请直接提供回应内容。"""

    @staticmethod
    def get_task_decomposition_prompt(
        refined_requirements: Dict[str, Any],
        selected_dataset: DatasetInfo,
        dialogue_history: List[DialogueTurn]
    ) -> str:
        """任务分解prompt"""
        
        dataset_columns = ', '.join(selected_dataset.columns)
        
        return f"""你是天文数据分析专家。请将用户需求分解为具体的可执行任务步骤。

## 用户需求总结
{PlannerPrompts._format_requirements(refined_requirements)}

## 选定数据集
- 名称: {selected_dataset.name}
- 描述: {selected_dataset.description}
- 数据列: {dataset_columns}
- 样本数据: {selected_dataset.sample_data[:2] if selected_dataset.sample_data else '无'}

## 任务分解要求
请将需求分解为详细的、可执行的步骤，每个步骤应该：

1. **具体明确**: 如"加载SDSS星系数据集"而不是"处理数据"
2. **可操作**: 每个步骤都能用Python代码实现
3. **逻辑顺序**: 按照数据处理的自然流程排序
4. **包含细节**: 指定具体的列名、参数、输出格式等

## 常见步骤类型
- **数据加载**: 读取CSV文件，检查数据格式
- **数据清洗**: 处理缺失值、异常值、数据类型转换
- **数据筛选**: 根据条件过滤数据
- **数据探索**: 基本统计、分布分析
- **数据可视化**: 散点图、直方图、热力图等
- **数据分析**: 相关性分析、聚类、分类等
- **结果导出**: 保存图片、导出结果


## 输出格式
请按以下JSON格式输出任务步骤：
```json
{{
    "task_steps": [
        {{
            "step_id": "step_1",
            "description": "加载星系数据集",
            "action_type": "load",
            "details": "使用pandas读取CSV文件，检查数据形状和列名",
            "priority": "high"
        }},
        {{
            "step_id": "step_2", 
            "description": "数据清洗和预处理",
            "action_type": "clean",
            "details": "处理缺失值，转换数据类型，移除异常值",
            "priority": "high",
            "dependencies": ["step_1"]
        }}
    ]
}}
```

请根据用户需求生成完整的任务步骤列表。"""

    @staticmethod
    def get_final_prompt_generation_prompt(
        task_steps: List[TaskStep],
        selected_dataset: DatasetInfo,
        refined_requirements: Dict[str, Any]
    ) -> str:
        """生成最终coder prompt的prompt"""
        
        steps_text = ""
        for step in task_steps:
            steps_text += f"- {step.description}: {step.details}\n"
        
        return f"""你是天文数据分析专家。请根据任务分解生成一个完整的、逻辑清晰的用户需求描述，这个描述将直接传给代码生成模块。

## 任务步骤
{steps_text}

## 数据集信息
- 名称: {selected_dataset.name}
- 路径: {selected_dataset.path}
- 描述: {selected_dataset.description}
- 主要列: {', '.join(selected_dataset.columns)}

## 需求背景
{PlannerPrompts._format_requirements(refined_requirements)}

## 生成要求
请生成一个完整的用户需求描述，要求：

1. **逻辑清晰**: 按照数据处理流程组织内容
2. **具体详细**: 包含具体的数据列名、分析目标、可视化要求
3. **技术准确**: 使用正确的天文学和数据分析术语
4. **完整连贯**: 作为一个完整的需求描述，不是步骤列表
5. **长度适中**: 200-400字左右

## 输出格式
请直接输出用户需求描述，不要包含任何格式标记或解释文字。需求描述应该从"请帮我分析..."开始，描述完整的数据分析任务。"""

    @staticmethod
    def get_confirmation_prompt(
        task_steps: List[TaskStep],
        selected_dataset: DatasetInfo,
        final_prompt: str
    ) -> str:
        """最终确认prompt"""
        
        steps_summary = ""
        for i, step in enumerate(task_steps, 1):
            steps_summary += f"{i}. {step.description}\n"
        
        return f"""请确认以下分析计划：

## 📊 选定数据集
**{selected_dataset.name}**
- {selected_dataset.description}
- 包含 {len(selected_dataset.columns)} 个数据列

## 📋 分析步骤
{steps_summary}

## 🎯 完整需求描述
{final_prompt}

## ❓ 确认问题
1. 这个分析计划是否符合您的需求？
2. 是否需要修改或补充任何步骤？
3. 确认开始执行代码生成？

请回复：
- "确认" 或 "是" - 开始执行
- "修改" 或 "否" - 需要调整
- 其他具体修改建议"""

    @staticmethod
    def _format_datasets_summary(datasets: List[DatasetInfo]) -> str:
        """格式化数据集摘要"""
        if not datasets:
            return "暂无可用数据集"
        
        summary = ""
        for i, dataset in enumerate(datasets, 1):
            summary += f"{i}. **{dataset.name}**\n"
            summary += f"   - {dataset.description}\n"
            summary += f"   - 列数: {len(dataset.columns)}\n"
            summary += f"   - 主要列: {', '.join(dataset.columns[:5])}{'...' if len(dataset.columns) > 5 else ''}\n\n"
        
        return summary
    
    @staticmethod
    def _summarize_collected_info(dialogue_history: List[DialogueTurn]) -> str:
        """总结已收集的信息"""
        if not dialogue_history:
            return "暂无"
        
        # 简单的关键词提取
        collected = []
        for turn in dialogue_history:
            if "数据" in turn.user_input:
                collected.append("数据集信息")
            if "分析" in turn.user_input:
                collected.append("分析目标")
            if "图" in turn.user_input:
                collected.append("可视化需求")
        
        return ", ".join(set(collected)) if collected else "基本信息"
    
    @staticmethod
    def _format_requirements(requirements: Dict[str, Any]) -> str:
        """格式化需求信息"""
        if not requirements:
            return "需求信息待收集"
        
        formatted = ""
        for key, value in requirements.items():
            formatted += f"- {key}: {value}\n"
        
        return formatted
