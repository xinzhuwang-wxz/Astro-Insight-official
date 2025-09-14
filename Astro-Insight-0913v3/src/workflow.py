#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天文科研Agent系统工作流模块

提供统一的工作流入口，封装图构建和执行逻辑，
支持不同用户类型和任务类型的处理流程。
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.graph.types import AstroAgentState, create_initial_state, validate_state
from src.graph.builder import build_graph
from src.config import load_yaml_config

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AstroWorkflow:
    """
    天文科研Agent工作流类

    负责管理整个系统的工作流程，包括：
    - 图的构建和初始化
    - 用户会话管理
    - 任务执行和状态跟踪
    - 错误处理和恢复
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化工作流

        Args:
            config_path: 配置文件路径，默认使用项目根目录的conf.yaml
        """
        self.config = load_yaml_config(config_path)
        self.graph = None
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._initialize_graph()

    def _initialize_graph(self):
        """
        初始化LangGraph图
        """
        try:
            logger.info("正在初始化天文科研Agent图...")
            self.graph = build_graph()
            logger.info("图初始化完成")
        except Exception as e:
            logger.error(f"图初始化失败: {str(e)}")
            raise

    def create_session(
        self,
        session_id: str,
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> AstroAgentState:
        """
        创建新的用户会话

        Args:
            session_id: 会话ID
            user_input: 用户输入
            user_context: 用户上下文信息（可选）

        Returns:
            初始化的状态对象
        """
        logger.info(f"创建新会话: {session_id}")

        # 创建初始状态
        initial_state = create_initial_state(session_id, user_input)

        # 添加用户上下文
        if user_context:
            initial_state.update(user_context)

        # 验证状态
        if not validate_state(initial_state):
            raise ValueError("初始状态验证失败")

        # 保存会话信息
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "initial_input": user_input,
            "current_state": initial_state,
        }

        return initial_state

    def execute_workflow(
        self,
        session_id: str,
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> AstroAgentState:
        """
        执行完整的工作流程

        Args:
            session_id: 会话ID
            user_input: 用户输入
            user_context: 用户上下文信息（可选）

        Returns:
            最终状态对象
        """
        start_time = time.time()
        logger.info(f"开始执行工作流 - 会话: {session_id}")

        try:
            # 创建或获取会话
            if session_id not in self.sessions:
                initial_state = self.create_session(
                    session_id, user_input, user_context
                )
            else:
                # 更新现有会话
                session = self.sessions[session_id]
                initial_state = session["current_state"].copy()
                initial_state["user_input"] = user_input
                if user_context:
                    # 只更新非session_id字段
                    for key, value in user_context.items():
                        if key != "session_id":
                            initial_state[key] = value
                session["last_updated"] = datetime.now()

            # 执行图
            logger.info(f"执行图处理 - 输入: {user_input[:50]}...")
            final_state = self.graph.invoke(initial_state)

            # 更新会话状态
            self.sessions[session_id]["current_state"] = final_state

            # 记录执行时间
            execution_time = time.time() - start_time
            logger.info(f"工作流执行完成 - 耗时: {execution_time:.2f}秒")

            # 记录执行结果
            self._log_execution_result(session_id, final_state, execution_time)

            return final_state

        except Exception as e:
            logger.error(f"工作流执行失败 - 会话: {session_id}, 错误: {str(e)}")
            # 记录错误信息到状态中
            if session_id in self.sessions:
                error_state = self.sessions[session_id]["current_state"].copy()
                error_state["error_info"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat(),
                }
                self.sessions[session_id]["current_state"] = error_state
                return error_state
            raise

    def _continue_visualization_dialogue(
        self,
        current_state: AstroAgentState,
        user_choice: str,
        session_id: str,
        start_time: float
    ) -> AstroAgentState:
        """继续可视化多轮对话"""
        
        try:
            # 导入 Planner 模块
            from src.planner import PlannerWorkflow
            
            # 获取可视化会话ID
            viz_session_id = current_state.get("visualization_session_id")
            if not viz_session_id:
                raise ValueError("可视化会话ID不存在")
            
            # 创建 Planner 实例
            planner = PlannerWorkflow()
            
            # 继续可视化对话
            result = planner.continue_interactive_session(viz_session_id, user_choice)
            
            if not result["success"]:
                # 处理失败情况
                updated_state = current_state.copy()
                updated_state["current_step"] = "visualization_failed"
                updated_state["is_complete"] = True
                updated_state["final_answer"] = f"可视化对话失败：{result.get('error')}"
                updated_state["awaiting_user_choice"] = False
                return updated_state
            
            # 更新状态
            updated_state = current_state.copy()
            updated_state["awaiting_user_choice"] = False
            
            # 更新对话历史
            if result.get("assistant_response"):
                dialogue_history = updated_state.get("visualization_dialogue_history", [])
                dialogue_history.append({
                    "turn": result.get("current_turn", 1),
                    "user_input": user_choice,
                    "assistant_response": result["assistant_response"],
                    "timestamp": time.time()
                })
                updated_state["visualization_dialogue_history"] = dialogue_history
            
            # 更新对话轮次
            if result.get("current_turn"):
                updated_state["visualization_turn_count"] = result["current_turn"]
            
            # 检查是否需要确认
            if result.get("needs_confirmation"):
                updated_state["awaiting_user_choice"] = True
                updated_state["current_visualization_request"] = result["confirmation_request"]
                updated_state["current_step"] = "visualization_clarifying"
                return updated_state
            
            # 检查是否已完成
            if result.get("completed"):
                # 执行完整 Pipeline
                from src.graph.nodes import _execute_visualization_pipeline
                return _execute_visualization_pipeline(updated_state, planner, viz_session_id, result)
            
            # 继续澄清
            updated_state["awaiting_user_choice"] = True
            updated_state["current_visualization_request"] = "请继续提供更多细节来完善您的可视化需求"
            updated_state["current_step"] = "visualization_clarifying"
            updated_state["visualization_dialogue_state"] = "clarifying"
            
            # 更新会话状态
            self.sessions[session_id]["current_state"] = updated_state
            self.sessions[session_id]["last_updated"] = datetime.now()
            
            # 记录执行时间
            execution_time = time.time() - start_time
            logger.info(f"可视化对话继续完成 - 耗时: {execution_time:.2f}秒")
            
            return updated_state
            
        except Exception as e:
            logger.error(f"可视化对话继续失败: {str(e)}")
            # 返回错误状态
            updated_state = current_state.copy()
            updated_state["current_step"] = "visualization_failed"
            updated_state["is_complete"] = True
            updated_state["final_answer"] = f"可视化对话继续失败：{str(e)}"
            updated_state["awaiting_user_choice"] = False
            return updated_state

    def handle_visualization_confirmation(
        self,
        session_id: str,
        confirmation_input: str,
    ) -> AstroAgentState:
        """处理可视化需求确认并执行完整Pipeline"""
        
        start_time = time.time()
        logger.info(f"处理可视化确认 - 会话: {session_id}, 确认: {confirmation_input}")
        
        try:
            # 获取现有会话
            if session_id not in self.sessions:
                raise ValueError(f"会话不存在: {session_id}")
                
            session = self.sessions[session_id]
            current_state = session["current_state"].copy()
            
            # 获取可视化会话ID
            viz_session_id = current_state.get("visualization_session_id")
            if not viz_session_id:
                raise ValueError("可视化会话ID不存在")
            
            # 导入 Planner 模块
            from src.planner import PlannerWorkflow
            
            # 创建 Planner 实例
            planner = PlannerWorkflow()
            
            # 处理确认
            confirmation_result = planner.handle_confirmation(viz_session_id, confirmation_input)
            
            if not confirmation_result["success"]:
                # 处理失败情况
                updated_state = current_state.copy()
                updated_state["current_step"] = "visualization_failed"
                updated_state["is_complete"] = True
                updated_state["final_answer"] = f"需求确认失败：{confirmation_result.get('error')}"
                updated_state["awaiting_user_choice"] = False
                return updated_state
            
            # 执行完整 Pipeline
            from src.graph.nodes import _execute_visualization_pipeline
            final_command = _execute_visualization_pipeline(current_state, planner, viz_session_id, confirmation_result)
            
            # 从Command对象中提取状态
            if hasattr(final_command, 'update') and final_command.update:
                final_state = final_command.update
            else:
                final_state = current_state.copy()
                final_state["current_step"] = "visualization_completed"
                final_state["is_complete"] = True
                final_state["final_answer"] = "可视化Pipeline执行完成"
            
            # 更新会话状态
            self.sessions[session_id]["current_state"] = final_state
            self.sessions[session_id]["last_updated"] = datetime.now()
            
            # 记录执行时间
            execution_time = time.time() - start_time
            logger.info(f"可视化确认处理完成 - 耗时: {execution_time:.2f}秒")
            
            return final_state
            
        except Exception as e:
            logger.error(f"可视化确认处理失败: {str(e)}")
            # 返回错误状态
            if session_id in self.sessions:
                error_state = self.sessions[session_id]["current_state"].copy()
            else:
                error_state = {}
            
            error_state["current_step"] = "visualization_failed"
            error_state["is_complete"] = True
            error_state["final_answer"] = f"可视化确认处理失败：{str(e)}"
            error_state["awaiting_user_choice"] = False
            return error_state

    def continue_workflow(
        self,
        session_id: str,
        user_choice: str,
    ) -> AstroAgentState:
        """
        继续执行工作流（用于处理用户选择）
        
        Args:
            session_id: 会话ID
            user_choice: 用户选择（"是"或"否"）
            
        Returns:
            最终状态对象
        """
        start_time = time.time()
        logger.info(f"继续执行工作流 - 会话: {session_id}, 用户选择: {user_choice}")
        
        try:
            # 获取现有会话
            if session_id not in self.sessions:
                raise ValueError(f"会话不存在: {session_id}")
                
            session = self.sessions[session_id]
            current_state = session["current_state"].copy()
            
            # 检查是否是可视化多轮对话
            if (current_state.get("task_type") == "visualization" and 
                current_state.get("visualization_session_id")):
                
                # 处理可视化多轮对话
                return self._continue_visualization_dialogue(current_state, user_choice, session_id, start_time)
            
            # 设置用户选择，但不覆盖原始user_input
            current_state["user_choice"] = user_choice
            current_state["awaiting_user_choice"] = False
            session["last_updated"] = datetime.now()
            
            # 使用LangGraph的invoke方法继续执行工作流
            logger.info(f"使用LangGraph继续执行工作流，用户选择: {user_choice}")
            
            # 使用图的invoke方法从当前状态继续执行
            final_state = self.graph.invoke(current_state)
            
            # 更新会话状态
            self.sessions[session_id]["current_state"] = final_state
            
            # 记录执行时间
            execution_time = time.time() - start_time
            logger.info(f"工作流继续执行完成 - 耗时: {execution_time:.2f}秒")
            
            # 记录执行结果
            self._log_execution_result(session_id, final_state, execution_time)
            
            return final_state
            
        except Exception as e:
            logger.error(f"工作流继续执行失败 - 会话: {session_id}, 错误: {str(e)}")
            # 记录错误信息到状态中
            if session_id in self.sessions:
                error_state = self.sessions[session_id]["current_state"].copy()
                error_state["error_info"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat(),
                }
                self.sessions[session_id]["current_state"] = error_state
                return error_state
            raise

    def _log_execution_result(
        self, session_id: str, final_state: AstroAgentState, execution_time: float
    ):
        """
        记录执行结果

        Args:
            session_id: 会话ID
            final_state: 最终状态
            execution_time: 执行时间
        """
        user_type = final_state.get("user_type", "未识别")
        task_type = final_state.get("task_type", "未分类")
        current_step = final_state.get("current_step", "未知")
        is_complete = final_state.get("is_complete", False)

        logger.info(f"执行结果 - 会话: {session_id}")
        logger.info(f"  用户类型: {user_type}")
        logger.info(f"  任务类型: {task_type}")
        logger.info(f"  当前步骤: {current_step}")
        logger.info(f"  是否完成: {is_complete}")
        logger.info(f"  执行时间: {execution_time:.2f}秒")

        # 记录执行历史
        history = final_state.get("execution_history", [])
        if history:
            logger.info(f"  执行步骤数: {len(history)}")
            for i, step in enumerate(history[-3:], 1):  # 只显示最后3步
                logger.info(
                    f"    {i}. {step.get('node', '未知')}: {step.get('action', '未知')}"
                )

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息字典，如果会话不存在则返回None
        """
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[str]:
        """
        列出所有会话ID

        Returns:
            会话ID列表
        """
        return list(self.sessions.keys())

    def clear_session(self, session_id: str) -> bool:
        """
        清除指定会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功清除
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"会话已清除: {session_id}")
            return True
        return False

    def clear_all_sessions(self):
        """
        清除所有会话
        """
        session_count = len(self.sessions)
        self.sessions.clear()
        logger.info(f"已清除所有会话，共 {session_count} 个")

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态信息

        Returns:
            系统状态字典
        """
        return {
            "graph_initialized": self.graph is not None,
            "active_sessions": len(self.sessions),
            "session_ids": list(self.sessions.keys()),
            "config_loaded": self.config is not None,
        }


# 全局工作流实例
_workflow_instance: Optional[AstroWorkflow] = None


def get_workflow(config_path: Optional[str] = None) -> AstroWorkflow:
    """
    获取全局工作流实例（单例模式）

    Args:
        config_path: 配置文件路径

    Returns:
        工作流实例
    """
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = AstroWorkflow(config_path)
    return _workflow_instance


def execute_astro_workflow(
    session_id: str,
    user_input: str,
    user_context: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None,
) -> AstroAgentState:
    """
    便捷函数：执行天文科研Agent工作流

    Args:
        session_id: 会话ID
        user_input: 用户输入
        user_context: 用户上下文信息（可选）
        config_path: 配置文件路径（可选）

    Returns:
        最终状态对象
    """
    workflow = get_workflow(config_path)
    return workflow.execute_workflow(session_id, user_input, user_context)


if __name__ == "__main__":
    # 简单测试
    print("天文科研Agent工作流模块")
    print("=" * 40)

    # 创建工作流实例
    workflow = AstroWorkflow()

    # 测试系统状态
    status = workflow.get_system_status()
    print(f"系统状态: {status}")

    # 测试简单执行
    test_cases = ["什么是黑洞？", "我需要获取SDSS的星系数据"]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_input}")
        try:
            result = workflow.execute_workflow(f"test_{i}", test_input)
            print(
                f"结果: {result.get('current_step', '未知')} - {result.get('user_type', '未识别')}"
            )
        except Exception as e:
            print(f"错误: {str(e)}")
