# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, Optional

from .types import PlannerState
from .agent import PlannerAgent


def planning_node(state: PlannerState) -> PlannerState:
    """规划节点"""
    agent = PlannerAgent()
    return agent.process_user_input(state, state.get("current_user_input", ""))


def confirmation_node(state: PlannerState) -> PlannerState:
    """确认节点"""
    agent = PlannerAgent()
    if state.get("user_confirmed", False):
        state["dialogue_status"] = "completed"
    return state


def route_after_planning(state: PlannerState) -> str:
    """规划后的路由"""
    if state.get("error_info"):
        return END
    
    if state.get("user_confirmed"):
        return "completed"
    elif state.get("current_turn", 0) >= state.get("max_turns", 10):
        return "completed"
    else:
        return "planning"


def create_planner_workflow():
    """创建Planner工作流"""
    
    # 创建状态图
    workflow = StateGraph(PlannerState)
    
    # 添加节点
    workflow.add_node("planning", planning_node)
    workflow.add_node("confirmation", confirmation_node)
    
    # 设置入口点
    workflow.set_entry_point("planning")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "planning",
        route_after_planning,
        {
            "planning": "planning",
            "completed": "confirmation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "confirmation",
        lambda state: END,
        {
            END: END
        }
    )
    
    # 编译图
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


class PlannerWorkflow:
    """Planner工作流封装类"""
    
    def __init__(self):
        self.app = create_planner_workflow()
        self.agent = PlannerAgent()
    
    def run_planning_session(
        self, 
        user_request: str, 
        session_id: Optional[str] = None,
        max_turns: int = 10
    ) -> Dict[str, Any]:
        """运行规划会话"""
        
        # 开始规划会话
        initial_state = self.agent.start_planning_session(user_request, session_id)
        
        # 运行工作流
        config = {"configurable": {"thread_id": session_id or "default"}}
        
        try:
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
    
    def run_complete_pipeline(
        self, 
        user_request: str, 
        session_id: Optional[str] = None,
        explanation_type: str = "detailed"
    ) -> Dict[str, Any]:
        """运行完整的Pipeline: Planner -> Coder -> Explainer"""
        
        print("🚀 开始运行完整Pipeline...")
        
        # 1. 运行Planner
        print("📋 第一步：需求规划和任务分解...")
        planner_result = self.agent.run_complete_session(user_request, session_id)
        
        if not planner_result.success:
            return {
                "success": False,
                "error": f"需求规划失败: {planner_result.error_message}",
                "error_type": "planner_failure",
                "planner_result": planner_result
            }
        
        print(f"✅ 规划完成，生成了 {len(planner_result.task_steps)} 个任务步骤")
        
        # 2. 运行Coder
        print("💻 第二步：代码生成和执行...")
        try:
            from ..coder.workflow import CodeGenerationWorkflow
            
            coder_workflow = CodeGenerationWorkflow()
            coder_result = coder_workflow.run(
                planner_result.final_prompt, 
                session_id
            )
            
            if not coder_result["success"]:
                return {
                    "success": False,
                    "error": f"代码生成失败: {coder_result.get('error', '未知错误')}",
                    "error_type": "coder_failure",
                    "planner_result": planner_result,
                    "coder_result": coder_result
                }
            
            print(f"✅ 代码执行完成，生成了 {len(coder_result.get('generated_files', []))} 个文件")
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Coder模块调用失败: {str(e)}",
                "error_type": "coder_integration_error",
                "planner_result": planner_result
            }
        
        # 3. 运行Explainer
        print("🔍 第三步：结果解释和分析...")
        try:
            from ..explainer.workflow import ExplainerWorkflow
            
            explainer_workflow = ExplainerWorkflow()
            explainer_result = explainer_workflow.explain_from_coder_workflow(
                coder_result=coder_result,
                user_input=planner_result.final_prompt,
                session_id=session_id
            )
            
            if explainer_result["success"]:
                print("✅ 结果解释完成")
                
                # 合并结果
                return {
                    "success": True,
                    "session_id": session_id,
                    "planner_result": planner_result,
                    "coder_result": coder_result,
                    "explainer_result": explainer_result,
                    "total_processing_time": (
                        planner_result.processing_time + 
                        coder_result.get("execution_time", 0) + 
                        explainer_result.get("processing_time", 0)
                    ),
                    "generated_files": coder_result.get("generated_files", []),
                    "explanations": explainer_result.get("explanations", []),
                    "summary": explainer_result.get("summary", ""),
                    "insights": explainer_result.get("insights", []),
                    "output_file": explainer_result.get("output_file"),
                    "warnings": explainer_result.get("warnings", []),
                    "task_steps": [
                        {
                            "step_id": step.step_id,
                            "description": step.description,
                            "action_type": step.action_type,
                            "details": step.details
                        }
                        for step in planner_result.task_steps
                    ]
                }
            else:
                print("❌ 结果解释失败")
                return {
                    "success": False,
                    "error": f"结果解释失败: {explainer_result.get('error', '未知错误')}",
                    "error_type": "explainer_failure",
                    "planner_result": planner_result,
                    "coder_result": coder_result,
                    "explainer_result": explainer_result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Explainer模块调用失败: {str(e)}",
                "error_type": "explainer_integration_error",
                "planner_result": planner_result,
                "coder_result": coder_result
            }
    
    def run_interactive_session(
        self, 
        user_request: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """运行交互式会话（支持多轮对话）"""
        
        # 开始规划会话
        state = self.agent.start_planning_session(user_request, session_id)
        
        # 处理初始用户输入
        state = self.agent.process_user_input(state, user_request)
        
        # 保存会话状态
        self.agent.save_session(state)
        
        # 获取最新的assistant回复
        assistant_response = ""
        if state.dialogue_history:
            assistant_response = state.dialogue_history[-1].assistant_response
        
        return {
            "success": True,
            "session_id": state.session_id,
            "assistant_response": assistant_response,
            "current_turn": state.current_turn,
            "max_turns": state.max_turns,
            "current_status": {
                "current_turn": state.current_turn,
                "max_turns": state.max_turns,
                "dialogue_status": state.dialogue_status.value,
                "task_steps": [{"description": step.description} for step in state.task_steps] if state.task_steps else [],
                "selected_dataset": {"name": state.selected_dataset.name} if state.selected_dataset else None
            }
        }
    
    def continue_interactive_session(
        self, 
        session_id: str, 
        user_input: str
    ) -> Dict[str, Any]:
        """继续交互式会话"""
        
        # 加载会话状态
        state = self.agent.load_session(session_id)
        if not state:
            return {
                "success": False,
                "error": f"找不到会话 {session_id}",
                "error_type": "session_not_found"
            }
        
        # 处理用户输入
        state = self.agent.process_user_input(state, user_input)
        
        # 保存会话状态
        self.agent.save_session(state)
        
        # 获取最新的assistant回复
        assistant_response = ""
        if state.dialogue_history:
            assistant_response = state.dialogue_history[-1].assistant_response
        
        # 检查是否需要确认
        needs_confirmation = (
            state.task_steps and 
            state.final_prompt and 
            not state.user_confirmed
        )
        
        if needs_confirmation:
            confirmation_request = self.agent.request_confirmation(state)
            return {
                "success": True,
                "session_id": session_id,
                "state": state,
                "assistant_response": assistant_response,
                "needs_confirmation": True,
                "confirmation_request": confirmation_request,
                "current_turn": state.current_turn,
                "max_turns": state.max_turns,
                "current_status": {
                    "current_turn": state.current_turn,
                    "max_turns": state.max_turns,
                    "dialogue_status": state.dialogue_status.value,
                    "task_steps": [{"description": step.description} for step in state.task_steps] if state.task_steps else [],
                    "selected_dataset": {"name": state.selected_dataset.name} if state.selected_dataset else None
                }
            }
        
        # 检查是否完成
        if state.dialogue_status.value == "completed" and state.user_confirmed:
            result = self.agent.get_final_result(state)
            return {
                "success": True,
                "session_id": session_id,
                "completed": True,
                "assistant_response": assistant_response,
                "final_result": result
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "state": state,
            "assistant_response": assistant_response,
            "needs_confirmation": False,
            "current_turn": state.current_turn,
            "max_turns": state.max_turns,
            "current_status": {
                "current_turn": state.current_turn,
                "max_turns": state.max_turns,
                "dialogue_status": state.dialogue_status.value,
                "task_steps": [{"description": step.description} for step in state.task_steps] if state.task_steps else [],
                "selected_dataset": {"name": state.selected_dataset.name} if state.selected_dataset else None
            }
        }
    
    def handle_confirmation(
        self, 
        session_id: str, 
        user_response: str
    ) -> Dict[str, Any]:
        """处理用户确认"""
        
        # 加载会话状态
        state = self.agent.load_session(session_id)
        if not state:
            return {
                "success": False,
                "error": f"找不到会话 {session_id}",
                "error_type": "session_not_found"
            }
        
        # 处理确认
        state = self.agent.handle_confirmation(state, user_response)
        
        # 保存会话状态
        self.agent.save_session(state)
        
        # 如果确认，运行完整pipeline
        if state.user_confirmed:
            return self.run_complete_pipeline(
                state.user_initial_request,
                session_id
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "state": state,
            "message": "已记录修改请求，请继续提供新的需求"
        }
