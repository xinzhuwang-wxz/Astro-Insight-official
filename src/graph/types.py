# Maxen Wong
# SPDX-License-Identifier: MIT

from typing import TypedDict, Optional, List, Dict, Any, Annotated, Literal
from langgraph.graph.message import add_messages
import time
import uuid
from enum import Enum


class AnalysisState(Enum):
    """分析状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(Enum):
    """节点类型枚举"""

    IDENTITY_CHECK = "identity_check"
    QA_RESPONSE = "qa_response"
    CODE_GENERATOR = "code_generator"
    CODE_EXECUTOR = "code_executor"
    FINAL_ANSWER = "final_answer"
    INPUT_PROCESSOR = "input_processor"
    CELESTIAL_CLASSIFIER = "celestial_classifier"
    DATA_RETRIEVAL = "data_retrieval"
    LITERATURE_REVIEW = "literature_review"
    TASK_SELECTOR = "task_selector"
    CLASSIFICATION_CONFIG = "classification_config"
    REVIEW_LOOP = "review_loop"
    ERROR_RECOVERY = "error_recovery"


class ExecutionStatus(Enum):
    """执行状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class AstroAgentState(TypedDict):
    """LangGraph状态定义 - 天文科研Agent系统"""

    # 基础会话信息 - 这些字段在状态更新中不应该被修改
    session_id: str
    user_input: str
    messages: Annotated[List[Dict[str, Any]], add_messages]

    # 用户身份和任务信息
    user_type: Optional[Literal["amateur", "professional"]]
    task_type: Optional[Literal["classification", "retrieval", "visualization", "qa"]]

    # 配置数据
    config_data: Dict[str, Any]

    # 执行状态
    current_step: Annotated[str, "当前执行步骤"]
    next_step: Optional[str]
    is_complete: Annotated[bool, "是否完成"]
    awaiting_user_choice: bool
    user_choice: Optional[str]

    # 结果数据
    qa_response: Optional[str]  # QA响应内容
    response: Optional[str]  # 对话响应字段
    final_answer: Optional[str]  # 最终回答内容
    generated_code: Optional[str]
    execution_result: Optional[Dict[str, Any]]

    # 错误处理
    error_info: Optional[Dict[str, Any]]
    retry_count: int

    # 历史记录
    execution_history: List[Dict[str, Any]]
    node_history: List[str]  # 节点历史记录
    current_node: Optional[str]  # 当前节点
    timestamp: float

    # 多轮可视化对话相关字段
    visualization_session_id: Optional[str]  # Planner会话ID
    visualization_dialogue_state: Optional[Literal["started", "clarifying", "completed", "failed"]]  # 对话状态
    current_visualization_request: Optional[str]  # 当前澄清问题
    visualization_turn_count: int  # 对话轮次计数
    visualization_max_turns: int  # 最大对话轮次
    visualization_dialogue_history: List[Dict[str, Any]]  # 可视化对话历史


def validate_state(state: AstroAgentState) -> tuple[bool, List[str]]:
    """验证状态完整性"""
    required_fields = ["session_id", "user_input", "current_step", "timestamp"]
    missing_fields = [field for field in required_fields if field not in state]
    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields


def create_initial_state(session_id: str, user_input: str) -> AstroAgentState:
    """创建初始状态"""
    return AstroAgentState(
        session_id=session_id or str(uuid.uuid4()),
        user_input=user_input,
        messages=[{"role": "user", "content": user_input}],
        user_type=None,
        task_type=None,
        config_data={"user_input": user_input},
        current_step="identity_check",
        next_step=None,
        is_complete=False,
        awaiting_user_choice=False,
        user_choice=None,
        qa_response=None,
        response=None,
        final_answer=None,
        generated_code=None,
        execution_result=None,
        error_info=None,
        retry_count=0,
        execution_history=[],
        node_history=[],
        current_node=None,
        timestamp=time.time(),
    )
