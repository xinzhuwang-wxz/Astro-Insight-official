# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Dict, Any, List, Optional


class ExplanationPrompts:
    """解释器Prompt模板管理器"""
    
    def __init__(self):
        self.base_prompts = {
            "basic": self._get_basic_explanation_prompt(),
            "detailed": self._get_detailed_explanation_prompt(),
            "professional": self._get_professional_explanation_prompt()
        }
    
    def get_explanation_prompt(self, complexity: str, context: Dict[str, Any]) -> str:
        """获取图片解释的prompt"""
        base_prompt = self.base_prompts.get(complexity, self.base_prompts["detailed"])
        
        # 添加上下文信息
        contextualized_prompt = self._add_context_to_prompt(base_prompt, context)
        
        return contextualized_prompt
    
    def _get_basic_explanation_prompt(self) -> str:
        """基础解释prompt"""
        return """请分析这张数据可视化图片，并提供简洁的解释。

请按以下格式回答：

## 图表类型
[识别图表类型，如：直方图、散点图、饼图等]

## 主要内容
[简要描述图表显示的数据内容]

## 关键发现
[列出2-3个关键观察结果]

请用中文回答，保持简洁明了。"""

    def _get_detailed_explanation_prompt(self) -> str:
        """详细解释prompt"""
        return """作为一名天文数据分析专家，请详细分析这张数据可视化图片。

请按以下结构提供详细解释：

## 图表分析
### 图表类型
[识别具体的图表类型]

### 坐标轴和标签
[分析X轴、Y轴的含义，以及图例说明]

### 数据分布特征
[描述数据的分布模式、趋势、异常值等]

## 科学解读
### 天文学意义
[从天文学角度解释这些数据的意义]

### 数据质量评估
[评估数据的完整性、可靠性]

### 关键发现
[列出3-5个重要的科学发现或观察结果]

## 结论与启示
[总结主要结论和可能的科学启示]

请使用专业但易懂的中文表达，适合研究人员阅读。"""

    def _get_professional_explanation_prompt(self) -> str:
        """专业解释prompt"""
        return """作为资深天体物理学家，请对这张数据可视化进行深入的专业分析。

## 技术分析
### 数据特征识别
- 图表类型和可视化方法
- 统计参数和数值范围
- 数据分布的统计特性（均值、方差、偏度等）
- 可能的误差和不确定性

### 天体物理解释
- 观测数据的物理意义
- 与已知天体物理现象的关联
- 可能涉及的物理过程和机制

## 科学评估
### 数据质量与局限性
- 观测偏差和选择效应
- 数据完整性评估
- 统计显著性分析

### 科学价值
- 对当前理论的支持或挑战
- 新发现的可能性
- 后续研究方向建议

## 专业结论
### 关键科学发现
[列出具有科学价值的发现]

### 理论意义
[讨论对天体物理理论的贡献]

### 研究建议
[提出进一步的研究方向]

请使用严谨的科学语言，包含适当的专业术语，适合同行评议和学术交流。"""

    def _add_context_to_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """将上下文信息添加到prompt中"""
        context_info = "\n\n## 背景信息\n"
        
        # 添加数据集信息
        if context.get("dataset_used"):
            context_info += f"**数据集**: {context['dataset_used']}\n"
        
        # 添加用户原始需求
        if context.get("user_input"):
            context_info += f"**分析目标**: {context['user_input']}\n"
        
        # 添加数据集描述
        if context.get("dataset_description"):
            context_info += f"**数据描述**: {context['dataset_description']}\n"
        
        # 添加生成代码的关键信息
        if context.get("code_summary"):
            context_info += f"**分析方法**: {context['code_summary']}\n"
        
        # 添加图片特定信息
        if context.get("image_name"):
            context_info += f"**图片文件**: {context['image_name']}\n"
        
        # 添加关注重点
        if context.get("focus_aspects"):
            aspects = ", ".join(context["focus_aspects"])
            context_info += f"**关注重点**: {aspects}\n"
        
        return base_prompt + context_info
    
    def get_summary_prompt(self, individual_explanations: List[str], context: Dict[str, Any]) -> str:
        """获取整体总结的prompt"""
        return f"""基于以下各个图表的详细分析，请提供一个整体性的总结报告：

## 个别图表分析结果：
{chr(10).join([f"### 图表 {i+1}:\n{explanation}\n" for i, explanation in enumerate(individual_explanations)])}

## 背景信息：
- **用户需求**: {context.get('user_input', 'N/A')}
- **数据集**: {context.get('dataset_used', 'N/A')}
- **分析复杂度**: {context.get('complexity', 'N/A')}

请提供以下内容：

## 整体数据概览
[综合所有图表，描述数据的整体特征和模式]

## 关键科学发现
[整合各图表的发现，提出最重要的科学结论]

## 数据间的关联性
[分析不同图表间的关系和相互验证]

## 综合评估
[对整个分析过程和结果的总体评价]

## 研究建议
[基于当前分析结果，提出后续研究方向]

请用中文回答，保持逻辑清晰和科学严谨。"""
    
    def get_insight_extraction_prompt(self, explanations: List[str]) -> str:
        """获取关键洞察提取的prompt"""
        return f"""从以下图表解释中提取最重要的科学洞察和发现：

{chr(10).join([f"图表 {i+1}: {explanation}" for i, explanation in enumerate(explanations)])}

请提取5-8个最重要的洞察，每个洞察应该：
1. 具有科学价值
2. 基于数据支持
3. 简洁明了
4. 具有实用性

格式要求：
- [洞察1]
- [洞察2]
- [洞察3]
...

请用中文回答，确保每个洞察都是有价值的科学发现。"""
