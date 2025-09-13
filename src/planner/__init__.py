# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Planner模块 - 需求对话和任务规划

主要功能：
1. 多轮对话收集和澄清用户需求
2. 任务分解和规划
3. 集成Coder和Explainer模块
4. 生成最终的代码生成指令

使用示例：
    from src.planner import PlannerWorkflow
    
    planner = PlannerWorkflow()
    
    # 运行完整pipeline
    result = planner.run_complete_pipeline("分析星系数据")
    
    # 或运行交互式会话
    session = planner.run_interactive_session("分析星系数据")
"""

from .types import (
    PlannerState, PlannerResult, DialogueStatus, TaskComplexity, TaskPriority,
    DatasetInfo, TaskStep, DialogueTurn, ClarificationQuestion
)

from .agent import PlannerAgent
from .workflow import PlannerWorkflow
from .dataset_manager import DatasetManager
from .dialogue_manager import DialogueManager
from .task_decomposer import TaskDecomposer
from .prompts import PlannerPrompts

__all__ = [
    # 类型定义
    "PlannerState",
    "PlannerResult", 
    "DialogueStatus",
    "TaskComplexity",
    "TaskPriority",
    "DatasetInfo",
    "TaskStep",
    "DialogueTurn",
    "ClarificationQuestion",
    
    # 核心类
    "PlannerAgent",
    "PlannerWorkflow",
    "DatasetManager",
    "DialogueManager",
    "TaskDecomposer",
    "PlannerPrompts"
]

# 版本信息
__version__ = "1.0.0"
__author__ = "Astro-Insight Team"
