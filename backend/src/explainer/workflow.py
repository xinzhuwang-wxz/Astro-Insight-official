# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, List, Optional
import traceback

from .types import ExplainerState, CoderOutput, ExplanationComplexity
from .agent import ExplainerAgent


def context_preparation_node(state: ExplainerState) -> ExplainerState:
    """上下文准备节点"""
    agent = ExplainerAgent()
    state["current_step"] = "context_preparation"
    return agent._prepare_context(state)


def image_analysis_node(state: ExplainerState) -> ExplainerState:
    """图片分析节点"""
    agent = ExplainerAgent()
    # 确保已完成上下文准备
    if "analysis_context" not in state:
        state = agent._prepare_context(state)
        if state.get("error_info"):
            return state
    state["current_step"] = "image_analysis"
    return agent._analyze_images(state)


def explanation_generation_node(state: ExplainerState) -> ExplainerState:
    """解释生成节点"""
    agent = ExplainerAgent()
    # 确保已完成前置步骤
    if "vlm_responses" not in state or not state.get("vlm_responses"):
        if "analysis_context" not in state:
            state = agent._prepare_context(state)
            if state.get("error_info"):
                return state
        state = agent._analyze_images(state)
        if state.get("error_info"):
            return state
    state["current_step"] = "explanation_generation"
    return agent._generate_explanations(state)


def result_creation_node(state: ExplainerState) -> ExplainerState:
    """结果创建节点"""
    agent = ExplainerAgent()
    # 确保已生成解释
    if "analysis_results" not in state:
        if "vlm_responses" not in state or not state.get("vlm_responses"):
            if "analysis_context" not in state:
                state = agent._prepare_context(state)
                if state.get("error_info"):
                    return state
            state = agent._analyze_images(state)
            if state.get("error_info"):
                return state
        state = agent._generate_explanations(state)
        if state.get("error_info"):
            return state
    state["current_step"] = "result_creation"
    return agent._create_final_result(state)


def dialogue_saving_node(state: ExplainerState) -> ExplainerState:
    """对话保存节点"""
    agent = ExplainerAgent()
    state["current_step"] = "dialogue_saving"
    return agent._save_dialogue(state)


def route_after_context_preparation(state: ExplainerState) -> str:
    """上下文准备后的路由"""
    if state.get("error_info"):
        return END
    return "image_analysis"


def route_after_image_analysis(state: ExplainerState) -> str:
    """图片分析后的路由"""
    if state.get("error_info"):
        return END
    return "explanation_generation"


def route_after_explanation_generation(state: ExplainerState) -> str:
    """解释生成后的路由"""
    if state.get("error_info"):
        return END
    return "result_creation"


def route_after_result_creation(state: ExplainerState) -> str:
    """结果创建后的路由"""
    if state.get("error_info"):
        return END
    return "dialogue_saving"


def route_after_dialogue_saving(state: ExplainerState) -> str:
    """对话保存后的路由"""
    return END


def create_explainer_workflow():
    """创建解释器工作流"""
    
    # 创建状态图
    workflow = StateGraph(ExplainerState)
    
    # 添加节点
    workflow.add_node("context_preparation", context_preparation_node)
    workflow.add_node("image_analysis", image_analysis_node)
    workflow.add_node("explanation_generation", explanation_generation_node)
    workflow.add_node("result_creation", result_creation_node)
    workflow.add_node("dialogue_saving", dialogue_saving_node)
    
    # 设置入口点
    workflow.set_entry_point("context_preparation")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "context_preparation",
        route_after_context_preparation,
        {
            "image_analysis": "image_analysis",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "image_analysis",
        route_after_image_analysis,
        {
            "explanation_generation": "explanation_generation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "explanation_generation",
        route_after_explanation_generation,
        {
            "result_creation": "result_creation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "result_creation",
        route_after_result_creation,
        {
            "dialogue_saving": "dialogue_saving",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "dialogue_saving",
        route_after_dialogue_saving,
        {
            END: END
        }
    )
    
    # 编译图
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


class ExplainerWorkflow:
    """解释器工作流封装类"""
    
    def __init__(self):
        self.app = create_explainer_workflow()
        self.agent = ExplainerAgent()
    
    def explain_coder_output(self, coder_output: CoderOutput, 
                           explanation_type: ExplanationComplexity = ExplanationComplexity.DETAILED,
                           focus_aspects: Optional[List[str]] = None,
                           session_id: str = None) -> Dict[str, Any]:
        """解释Coder模块的输出"""
        
        # 创建初始状态
        initial_state = self.agent.create_initial_state(
            coder_output=coder_output,
            explanation_type=explanation_type,
            focus_aspects=focus_aspects,
            session_id=session_id
        )
        
        # 运行工作流
        config = {"configurable": {"thread_id": session_id or "default"}}
        
        try:
            last_node_state: Optional[ExplainerState] = None
            
            for event in self.app.stream(initial_state, config):
                if isinstance(event, dict) and event:
                    try:
                        last_node_state = list(event.values())[-1]
                    except Exception:
                        continue
            
            if last_node_state and isinstance(last_node_state, dict):
                return self.agent.get_final_result(last_node_state)
            else:
                return {
                    "success": False,
                    "error": "工作流执行失败：未获得最终状态",
                    "error_type": "workflow_error",
                    "debug": {
                        "has_last_state": bool(last_node_state),
                        "event_type": type(last_node_state).__name__ if last_node_state is not None else None
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"工作流执行异常: {str(e)}",
                "error_type": "workflow_exception",
                "traceback": traceback.format_exc()
            }
    
    def explain_from_coder_workflow(self, coder_result: Dict[str, Any],
                                  user_input: str,
                                  explanation_type: ExplanationComplexity = ExplanationComplexity.DETAILED,
                                  focus_aspects: Optional[List[str]] = None,
                                  session_id: str = None) -> Dict[str, Any]:
        """直接从Coder工作流的结果进行解释"""
        
        # 检查Coder结果是否成功
        if not coder_result.get("success"):
            return {
                "success": False,
                "error": f"Coder执行失败，无法进行解释: {coder_result.get('error', '未知错误')}",
                "error_type": "coder_failure"
            }
        
        # 检查是否有生成的图片
        generated_files = coder_result.get("generated_files", [])
        # 无图时允许进入文本模式解释
        
        # 构建CoderOutput结构
        coder_output = CoderOutput(
            success=coder_result["success"],
            code=coder_result.get("code", ""),
            output=coder_result.get("output", ""),
            execution_time=coder_result.get("execution_time", 0),
            generated_files=generated_files,
            generated_texts=coder_result.get("generated_texts", []),
            dataset_used=coder_result.get("dataset_used", ""),
            complexity=coder_result.get("complexity", ""),
            retry_count=coder_result.get("retry_count", 0),
            user_input=user_input
        )
        
        # 调用解释工作流
        return self.explain_coder_output(
            coder_output=coder_output,
            explanation_type=explanation_type,
            focus_aspects=focus_aspects,
            session_id=session_id
        )
    
    def run_combined_workflow(self, user_input: str,
                            explanation_type: ExplanationComplexity = ExplanationComplexity.DETAILED,
                            focus_aspects: Optional[List[str]] = None,
                            session_id: str = None) -> Dict[str, Any]:
        """运行组合工作流：Coder + Explainer"""
        
        # 导入Coder工作流
        from ..coder.workflow import CodeGenerationWorkflow
        
        print("🚀 开始运行组合工作流...")
        
        # 1. 运行Coder工作流
        print("📊 第一步：运行代码生成...")
        coder_workflow = CodeGenerationWorkflow()
        coder_result = coder_workflow.run(user_input, session_id)
        
        if not coder_result["success"]:
            return {
                "success": False,
                "error": f"代码生成失败: {coder_result.get('error', '未知错误')}",
                "error_type": "coder_failure",
                "coder_result": coder_result
            }
        
        print(f"✅ 代码生成完成，生成了 {len(coder_result.get('generated_files', []))} 个文件")
        
        # 2. 运行Explainer工作流
        print("🔍 第二步：运行图片解释...")
        explainer_result = self.explain_from_coder_workflow(
            coder_result=coder_result,
            user_input=user_input,
            explanation_type=explanation_type,
            focus_aspects=focus_aspects,
            session_id=session_id
        )
        
        if explainer_result["success"]:
            print("✅ 图片解释完成")
            
            # 合并结果
            return {
                "success": True,
                "session_id": explainer_result["session_id"],
                "coder_result": coder_result,
                "explainer_result": explainer_result,
                "total_processing_time": coder_result.get("execution_time", 0) + explainer_result.get("processing_time", 0),
                "generated_files": coder_result.get("generated_files", []),
                "explanations": explainer_result.get("explanations", []),
                "summary": explainer_result.get("summary", ""),
                "insights": explainer_result.get("insights", []),
                "output_file": explainer_result.get("output_file"),
                "warnings": explainer_result.get("warnings", [])
            }
        else:
            print("❌ 图片解释失败")
            return {
                "success": False,
                "error": f"图片解释失败: {explainer_result.get('error', '未知错误')}",
                "error_type": "explainer_failure",
                "coder_result": coder_result,
                "explainer_result": explainer_result
            }
    
    def run_single_step(self, coder_output: CoderOutput, step: str = "full") -> Dict[str, Any]:
        """运行单个步骤（用于调试）"""
        initial_state = self.agent.create_initial_state(coder_output)
        
        if step == "context_preparation":
            result_state = self.agent._prepare_context(initial_state)
        elif step == "image_analysis":
            temp_state = self.agent._prepare_context(initial_state)
            result_state = self.agent._analyze_images(temp_state)
        elif step == "explanation_generation":
            temp_state = self.agent._prepare_context(initial_state)
            temp_state = self.agent._analyze_images(temp_state)
            result_state = self.agent._generate_explanations(temp_state)
        else:
            # 运行完整流程
            return self.explain_coder_output(coder_output)
        
        return {
            "step": step,
            "state": result_state,
            "success": not bool(result_state.get("error_info"))
        }
