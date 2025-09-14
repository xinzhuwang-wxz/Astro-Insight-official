# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .nodes import (
    identity_check_command_node,
    qa_agent_command_node,
    task_selector_command_node,
    classification_config_command_node,
    data_retrieval_command_node,
    visualization_command_node,
    multimark_command_node,
    error_recovery_command_node
)
from .types import AstroAgentState


def route_after_identity_check(state: AstroAgentState) -> str:
    """身份识别后的路由逻辑 - 简化版本，避免重复调用"""
    user_type = state.get("user_type", "amateur")
    
    # 简化路由逻辑：根据用户类型直接路由，不再检查identity_completed状态
    if user_type == "professional":
        return "task_selector"
    else:
        # amateur用户或未知类型都进入QA流程
        return "qa_agent"




def route_after_task_selection(state: AstroAgentState) -> str:
    """任务选择后的路由逻辑 - 简化版本"""
    task_type = state.get("task_type", "classification")
    
    if task_type == "classification":
        return "classification_config"
    elif task_type == "retrieval":
        return "data_retrieval"
    elif task_type == "visualization":
        return "visualization"
    elif task_type == "multimark":
        return "multimark"
    else:
        return "error_recovery"




def route_after_error_recovery(state: AstroAgentState) -> str:
    """错误恢复后的路由逻辑 - 简化版本，避免循环调用"""
    retry_count = state.get("retry_count", 0)
    error_info = state.get("error_info")
    
    # 如果重试次数已达上限或没有错误信息，直接结束
    if retry_count >= 3 or not error_info:
        return END
    
    # 简化逻辑：错误恢复后直接结束，避免重新进入其他节点造成循环
    return END




def _build_astro_graph():
    """构建天文科研Agent的状态图 - 简化版本"""
    graph = StateGraph(AstroAgentState)
    
    # 添加节点 - 简化后的核心节点
    graph.add_node("identity_check", identity_check_command_node)
    graph.add_node("qa_agent", qa_agent_command_node)
    graph.add_node("task_selector", task_selector_command_node)
    graph.add_node("classification_config", classification_config_command_node)
    graph.add_node("data_retrieval", data_retrieval_command_node)
    graph.add_node("visualization", visualization_command_node)
    graph.add_node("multimark", multimark_command_node)
    graph.add_node("error_recovery", error_recovery_command_node)
    
    # 设置入口点
    graph.set_entry_point("identity_check")
    
    # 身份识别后的路由：爱好者→QA，专业用户→任务选择
    graph.add_conditional_edges(
        "identity_check",
        route_after_identity_check,
        {
            "qa_agent": "qa_agent",
            "task_selector": "task_selector",
            "error_recovery": "error_recovery"
        }
    )
    
    # QA节点直接结束（不再询问是否进入专业模式）
    graph.add_edge("qa_agent", END)
    
    # 任务选择后的路由：分类/检索/可视化/多模态标注
    graph.add_conditional_edges(
        "task_selector",
        route_after_task_selection,
        {
            "classification_config": "classification_config",
            "data_retrieval": "data_retrieval",
            "visualization": "visualization",
            "multimark": "multimark",
            "error_recovery": "error_recovery"
        }
    )
    
    # 所有专业任务节点都直接结束
    graph.add_edge("classification_config", END)
    graph.add_edge("data_retrieval", END)
    graph.add_edge("visualization", END)
    graph.add_edge("multimark", END)
    
    # 错误恢复后直接结束
    graph.add_conditional_edges(
        "error_recovery",
        route_after_error_recovery,
        {
            END: END
        }
    )
    
    return graph


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    # use persistent memory to save conversation history
    # TODO: be compatible with SQLite / PostgreSQL
    memory = MemorySaver()

    # build state graph
    builder = _build_astro_graph()
    return builder.compile(checkpointer=memory)


def build_graph():
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_astro_graph()
    return builder.compile()


# 移除全局图实例，每次调用build_graph()都创建新的图实例
# graph = build_graph()
