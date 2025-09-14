# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class DialogueStatus(Enum):
    """对话状态枚举"""
    INITIAL = "initial"           # 初始状态
    COLLECTING = "collecting"     # 需求收集中
    CLARIFYING = "clarifying"     # 需求澄清中
    CONFIRMING = "confirming"     # 需求确认中
    COMPLETED = "completed"       # 
    CANCELLED = "cancelled"       # 用户取消


class TaskComplexity(Enum):
    """任务复杂度枚举"""
    SIMPLE = "simple"           # 简单任务（单一操作）
    MODERATE = "moderate"       # 中等任务（多个步骤）
    COMPLEX = "complex"         # 复杂任务（需要多个模块协作）


class TaskPriority(Enum):
    """任务优先级枚举"""
    HIGH = "high"               # 高优先级
    MEDIUM = "medium"           # 中优先级
    LOW = "low"                 # 低优先级


@dataclass
class DatasetInfo:
    """数据集信息"""
    name: str
    path: str
    description: str
    columns: List[str]
    size: int
    file_type: str
    sample_data: Optional[List[Dict]] = None
    data_types: Optional[Dict[str, str]] = None


@dataclass
class TaskStep:
    """任务步骤"""
    step_id: str
    description: str
    action_type: str  # "load", "clean", "analyze", "visualize", "export"
    details: str
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_time: Optional[int] = None  # 预估时间（秒）


@dataclass
class DialogueTurn:
    """对话轮次"""
    turn_id: int
    user_input: str
    assistant_response: str
    timestamp: float
    context_used: Dict[str, Any] = field(default_factory=dict)
    clarification_questions: List[str] = field(default_factory=list)


@dataclass
class PlannerState:
    """Planner状态"""
    session_id: str
    user_initial_request: str
    dialogue_status: DialogueStatus = DialogueStatus.INITIAL
    current_turn: int = 0
    max_turns: int = 10
    
    # 对话历史
    dialogue_history: List[DialogueTurn] = field(default_factory=list)
    
    # 需求信息
    refined_requirements: Dict[str, Any] = field(default_factory=dict)
    selected_dataset: Optional[DatasetInfo] = None
    available_datasets: List[DatasetInfo] = field(default_factory=list)
    
    # 任务分解
    task_steps: List[TaskStep] = field(default_factory=list)
    task_complexity: Optional[TaskComplexity] = None
    
    # 最终输出
    final_prompt: Optional[str] = None
    user_confirmed: bool = False
    
    # 错误和状态
    error_info: Optional[Dict[str, Any]] = None
    last_activity: float = field(default_factory=time.time)


@dataclass
class PlannerResult:
    """Planner执行结果"""
    success: bool
    session_id: str
    final_prompt: Optional[str] = None
    task_steps: List[TaskStep] = field(default_factory=list)
    dialogue_history: List[DialogueTurn] = field(default_factory=list)
    selected_dataset: Optional[DatasetInfo] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    turns_used: int = 0


@dataclass
class ClarificationQuestion:
    """澄清问题"""
    question: str
    options: List[str] = field(default_factory=list)
    required: bool = True
    context: str = ""


# 类型别名
PlannerAgentState = Dict[str, Any]
DatasetSummary = Dict[str, Any]
TaskDecompositionResult = Dict[str, Any]
DialogueContext = Dict[str, Any]
