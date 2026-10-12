# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any

from .types import CoderAgentState
from .agent import CodeGeneratorAgent


def dataset_selection_node(state: CoderAgentState) -> CoderAgentState:
    """数据集选择节点"""
    agent = CodeGeneratorAgent()
    return agent._select_dataset(state)


def complexity_analysis_node(state: CoderAgentState) -> CoderAgentState:
    """复杂度分析节点"""
    agent = CodeGeneratorAgent()
    return agent._analyze_complexity(state)


def code_generation_node(state: CoderAgentState) -> CoderAgentState:
    """代码生成节点"""
    agent = CodeGeneratorAgent()
    return agent._generate_code(state)


def code_execution_node(state: CoderAgentState) -> CoderAgentState:
    """代码执行节点"""
    agent = CodeGeneratorAgent()
    return agent._execute_code(state)


def error_recovery_node(state: CoderAgentState) -> CoderAgentState:
    """错误恢复节点"""
    agent = CodeGeneratorAgent()
    return agent._recover_from_error(state)


def route_after_dataset_selection(state: CoderAgentState) -> str:
    """数据集选择后的路由"""
    if state.get("error_info"):
        return END
    return "complexity_analysis"


def route_after_complexity_analysis(state: CoderAgentState) -> str:
    """复杂度分析后的路由"""
    if state.get("error_info"):
        return END
    return "code_generation"


def route_after_code_generation(state: CoderAgentState) -> str:
    """代码生成后的路由"""
    current_step = state.get("current_step", "")
    
    if current_step == "error_recovery":
        return "error_recovery"
    elif current_step == "code_execution":
        return "code_execution"
    elif current_step == "error":
        return END
    else:
        return "code_execution"


def route_after_code_execution(state: CoderAgentState) -> str:
    """代码执行后的路由"""
    current_step = state.get("current_step", "")
    
    if current_step == "completed":
        return END
    elif current_step == "error_recovery":
        return "error_recovery"
    else:
        return END


def route_after_error_recovery(state: CoderAgentState) -> str:
    """错误恢复后的路由"""
    current_step = state.get("current_step", "")
    
    if current_step == "code_execution":
        return "code_execution"
    elif current_step == "code_generation":
        return "code_generation"
    else:
        return END


def create_code_generation_workflow():
    """创建代码生成工作流"""
    
    # 创建状态图
    workflow = StateGraph(CoderAgentState)
    
    # 添加节点
    workflow.add_node("dataset_selection", dataset_selection_node)
    workflow.add_node("complexity_analysis", complexity_analysis_node)
    workflow.add_node("code_generation", code_generation_node)
    workflow.add_node("code_execution", code_execution_node)
    workflow.add_node("error_recovery", error_recovery_node)
    
    # 设置入口点
    workflow.set_entry_point("dataset_selection")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "dataset_selection",
        route_after_dataset_selection,
        {
            "complexity_analysis": "complexity_analysis",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "complexity_analysis", 
        route_after_complexity_analysis,
        {
            "code_generation": "code_generation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "code_generation",
        route_after_code_generation,
        {
            "code_execution": "code_execution",
            "error_recovery": "error_recovery",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "code_execution",
        route_after_code_execution,
        {
            "error_recovery": "error_recovery",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "error_recovery",
        route_after_error_recovery,
        {
            "code_execution": "code_execution",
            "code_generation": "code_generation",
            END: END
        }
    )
    
    # 编译图
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


class CodeGenerationWorkflow:
    """代码生成工作流封装类"""
    
    def __init__(self):
        self.app = create_code_generation_workflow()
        self.agent = CodeGeneratorAgent()
    
    def run(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """运行完整的代码生成工作流"""
        
        # 创建初始状态
        initial_state = self.agent.create_initial_state(user_input, session_id)
        
        # 运行工作流
        config = {"configurable": {"thread_id": session_id or "default"}}
        
        try:
            # 执行工作流
            final_state = None
            for state in self.app.stream(initial_state, config):
                final_state = state
            
            if final_state:
                # 获取最后一个节点的状态
                last_node_state = list(final_state.values())[-1]
                return self.agent.get_final_result(last_node_state)
            else:
                return {
                    "success": False,
                    "error": "工作流执行失败",
                    "error_type": "workflow_error"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"工作流执行异常: {str(e)}",
                "error_type": "workflow_exception"
            }
    
    def run_single_step(self, user_input: str, step: str = "full") -> Dict[str, Any]:
        """运行单个步骤（用于调试）"""
        initial_state = self.agent.create_initial_state(user_input)
        
        if step == "dataset_selection":
            result_state = self.agent._select_dataset(initial_state)
        elif step == "complexity_analysis":
            # 需要先选择数据集
            temp_state = self.agent._select_dataset(initial_state)
            result_state = self.agent._analyze_complexity(temp_state)
        elif step == "code_generation":
            # 运行前面的步骤
            temp_state = self.agent._select_dataset(initial_state)
            temp_state = self.agent._analyze_complexity(temp_state)
            result_state = self.agent._generate_code(temp_state)
        else:
            # 运行完整流程
            return self.run(user_input)
        
        return {
            "step": step,
            "state": result_state,
            "success": not bool(result_state.get("error_info"))
        }
