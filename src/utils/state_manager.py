#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态管理模块
提供简化的状态管理、验证和输出格式化
"""

import json
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.utils.error_handler import AstroError, ErrorCode, ErrorSeverity, create_error_context


class StateStep(Enum):
    """状态步骤枚举"""
    IDENTITY_CHECK = "identity_check"
    QA_RESPONSE = "qa_response"
    USER_CHOICE = "user_choice"
    TASK_SELECTION = "task_selection"
    CLASSIFICATION = "classification"
    DATA_RETRIEVAL = "data_retrieval"
    LITERATURE_REVIEW = "literature_review"
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    REVIEW_LOOP = "review_loop"
    ERROR_RECOVERY = "error_recovery"
    COMPLETED = "completed"


@dataclass
class StateValidationResult:
    """状态验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class StateManager:
    """状态管理器"""
    
    def __init__(self):
        self.logger = None  # 将在需要时初始化
    
    def validate_state(self, state: Dict[str, Any]) -> StateValidationResult:
        """
        验证状态完整性
        
        Args:
            state: 状态字典
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ["session_id", "user_input", "current_step", "timestamp"]
        for field in required_fields:
            if field not in state:
                errors.append(f"Missing required field: {field}")
        
        # 会话ID验证
        if "session_id" in state and not state["session_id"]:
            errors.append("Session ID cannot be empty")
        
        # 用户输入验证
        if "user_input" in state and not state["user_input"]:
            errors.append("User input cannot be empty")
        
        # 当前步骤验证
        if "current_step" in state:
            valid_steps = [step.value for step in StateStep]
            if state["current_step"] not in valid_steps:
                errors.append(f"Invalid current_step: {state['current_step']}")
        
        # 时间戳验证
        if "timestamp" in state:
            try:
                float(state["timestamp"])
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format")
        
        # 用户类型验证
        if "user_type" in state and state["user_type"]:
            valid_types = ["amateur", "professional"]
            if state["user_type"] not in valid_types:
                warnings.append(f"Unknown user_type: {state['user_type']}")
        
        # 任务类型验证
        if "task_type" in state and state["task_type"]:
            valid_types = ["classification", "retrieval", "literature", "code_generation", "analysis"]
            if state["task_type"] not in valid_types:
                warnings.append(f"Unknown task_type: {state['task_type']}")
        
        return StateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def format_state_output(self, state: Dict[str, Any]) -> str:
        """
        格式化状态输出
        
        Args:
            state: 状态字典
            
        Returns:
            格式化的状态字符串
        """
        try:
            output_parts = []
            
            # 添加分隔线
            output_parts.append("=" * 60)
            
            # 基本信息
            output_parts.append(self._format_basic_info(state))
            
            # 用户类型和任务信息
            output_parts.append(self._format_user_task_info(state))
            
            # 处理状态
            output_parts.append(self._format_processing_status(state))
            
            # 结果信息
            output_parts.append(self._format_results(state))
            
            # 错误信息
            output_parts.append(self._format_errors(state))
            
            # 执行历史
            output_parts.append(self._format_execution_history(state))
            
            # 添加分隔线
            output_parts.append("=" * 60)
            
            return "\n".join(filter(None, output_parts))
            
        except Exception as e:
            error_context = create_error_context(
                session_id=state.get("session_id"),
                additional_info={"state_keys": list(state.keys())}
            )
            raise AstroError(
                f"Failed to format state output: {str(e)}",
                ErrorCode.WORKFLOW_ERROR,
                ErrorSeverity.MEDIUM,
                error_context,
                e
            )
    
    def _format_basic_info(self, state: Dict[str, Any]) -> str:
        """格式化基本信息"""
        parts = []
        
        session_id = state.get("session_id", "未知")
        user_input = state.get("user_input", "未知")
        
        parts.append(f"会话ID: {session_id}")
        parts.append(f"用户输入: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        
        return "\n".join(parts)
    
    def _format_user_task_info(self, state: Dict[str, Any]) -> str:
        """格式化用户和任务信息"""
        parts = []
        
        user_type = state.get("user_type", "未识别")
        task_type = state.get("task_type", "未分类")
        
        parts.append(f"用户类型: {user_type}")
        parts.append(f"任务类型: {task_type}")
        
        return "\n".join(parts)
    
    def _format_processing_status(self, state: Dict[str, Any]) -> str:
        """格式化处理状态"""
        parts = []
        
        current_step = state.get("current_step", "未知")
        is_complete = state.get("is_complete", False)
        awaiting_choice = state.get("awaiting_user_choice", False)
        
        parts.append(f"当前步骤: {current_step}")
        parts.append(f"处理状态: {'完成' if is_complete else '进行中'}")
        
        if awaiting_choice:
            parts.append("等待用户选择: 是")
        
        # 添加可视化对话状态调试信息
        if state.get("task_type") == "visualization":
            viz_state = state.get("visualization_dialogue_state")
            viz_session = state.get("visualization_session_id")
            viz_turn = state.get("visualization_turn_count", 0)
            if viz_state:
                parts.append(f"可视化对话状态: {viz_state}")
            if viz_session:
                parts.append(f"可视化会话ID: {viz_session}")
            if viz_turn > 0:
                parts.append(f"对话轮次: {viz_turn}")
        
        return "\n".join(parts)
    
    def _format_results(self, state: Dict[str, Any]) -> str:
        """格式化结果信息"""
        parts = []
        
        # 最终答案（优先级最高）
        if state.get("final_answer"):
            parts.append("\n【最终结果】")
            parts.append(state["final_answer"])
            return "\n".join(parts)
        
        # QA响应
        if state.get("qa_response"):
            parts.append("\n【QA回答】")
            parts.append(state["qa_response"])
        
        # 分类结果
        classification_result = self._extract_classification_result(state)
        if classification_result:
            parts.append("\n【天体分类结果】")
            parts.append(self._format_classification_result(classification_result))
        
        # 生成的代码
        if state.get("generated_code"):
            parts.append("\n【生成的代码】")
            parts.append(self._format_generated_code(state))
        
        # 执行结果
        if state.get("execution_result"):
            parts.append("\n【执行结果】")
            parts.append(self._format_execution_result(state["execution_result"]))
        
        return "\n".join(parts)
    
    def _extract_classification_result(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提取分类结果"""
        # 检查多个可能的位置
        if state.get("classification_result"):
            return state["classification_result"]
        
        final_answer = state.get("final_answer")
        if isinstance(final_answer, dict) and final_answer.get("classification_result"):
            return final_answer["classification_result"]
        
        # 检查执行历史
        history = state.get("execution_history", [])
        for step in history:
            if (step.get("node") == "classification_config_command_node" and 
                step.get("action") == "celestial_classification" and 
                isinstance(step.get("output"), dict)):
                return step["output"]
        
        return None
    
    def _format_classification_result(self, result: Dict[str, Any]) -> str:
        """格式化分类结果"""
        parts = []
        
        if "classification_result" in result:
            classification = result["classification_result"]
            parts.append(f"天体名称: {classification.get('object_name', '未知')}")
            parts.append(f"主要分类: {classification.get('primary_category', '未分类')}")
            parts.append(f"子分类: {classification.get('subcategory', '未知')}")
            parts.append(f"置信度: {classification.get('confidence_level', '未知')}")
            
            # 关键特征
            key_features = classification.get("key_features", [])
            if key_features:
                parts.append(f"关键特征: {', '.join(key_features)}")
            
            # 坐标信息
            coordinates = classification.get("coordinates", {})
            if coordinates and coordinates.get("ra") != "未知":
                parts.append(f"坐标: RA={coordinates.get('ra', '未知')}, DEC={coordinates.get('dec', '未知')}")
        
        # 解释说明
        if result.get("explanation"):
            parts.append(f"解释: {result['explanation']}")
        
        # 建议
        suggestions = result.get("suggestions", [])
        if suggestions:
            parts.append(f"建议: {', '.join(suggestions)}")
        
        return "\n".join(parts)
    
    def _format_generated_code(self, state: Dict[str, Any]) -> str:
        """格式化生成的代码"""
        parts = []
        
        code = state.get("generated_code", "")
        metadata = state.get("code_metadata", {})
        
        parts.append(f"代码长度: {len(code)} 字符")
        parts.append(f"代码行数: {len(code.splitlines())} 行")
        
        # 显示代码元数据
        if metadata:
            parts.append(f"任务类型: {metadata.get('task_type', '未知')}")
            parts.append(f"优化级别: {metadata.get('optimization_level', '未知')}")
            parts.append(f"语法验证: {'通过' if metadata.get('syntax_valid') else '未通过'}")
        
        # 显示代码内容
        parts.append("\n【代码内容】")
        parts.append("```python")
        parts.append(code)
        parts.append("```")
        
        return "\n".join(parts)
    
    def _format_execution_result(self, result: Dict[str, Any]) -> str:
        """格式化执行结果"""
        parts = []
        
        parts.append(f"执行状态: {result.get('status', '未知')}")
        
        if result.get("output"):
            parts.append(f"输出信息: {result['output']}")
        
        if result.get("error_message"):
            parts.append(f"错误信息: {result['error_message']}")
        
        if result.get("execution_time"):
            exec_time = datetime.fromtimestamp(result["execution_time"])
            parts.append(f"执行时间: {exec_time.strftime('%H:%M:%S')}")
        
        return "\n".join(parts)
    
    def _format_errors(self, state: Dict[str, Any]) -> str:
        """格式化错误信息"""
        if not state.get("error_info"):
            return ""
        
        error = state["error_info"]
        parts = ["\n【错误信息】"]
        parts.append(f"错误类型: {error.get('error_type', '未知')}")
        parts.append(f"错误详情: {error.get('error', '未知错误')}")
        
        return "\n".join(parts)
    
    def _format_execution_history(self, state: Dict[str, Any]) -> str:
        """格式化执行历史"""
        history = state.get("execution_history", [])
        if not history:
            return ""
        
        parts = ["\n【执行历史】"]
        for i, step in enumerate(history, 1):
            node = step.get("node", "未知节点")
            action = step.get("task_type") or step.get("action", "未知操作")
            parts.append(f"  {i}. {node}: {action}")
        
        return "\n".join(parts)
    
    def create_initial_state(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        创建初始状态
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            
        Returns:
            初始状态字典
        """
        return {
            "session_id": session_id,
            "user_input": user_input,
            "messages": [{"role": "user", "content": user_input}],
            "user_type": None,
            "task_type": None,
            "config_data": {"user_input": user_input},
            "current_step": StateStep.IDENTITY_CHECK.value,
            "next_step": None,
            "is_complete": False,
            "awaiting_user_choice": False,
            "user_choice": None,
            "qa_response": None,
            "response": None,
            "final_answer": None,
            "generated_code": None,
            "execution_result": None,
            "error_info": None,
            "retry_count": 0,
            "execution_history": [],
            "timestamp": time.time(),
        }
    
    def update_state(self, state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新状态
        
        Args:
            state: 当前状态
            updates: 更新内容
            
        Returns:
            更新后的状态
        """
        # 创建状态副本
        new_state = state.copy()
        
        # 应用更新
        new_state.update(updates)
        
        # 更新时间戳
        new_state["timestamp"] = time.time()
        
        # 验证更新后的状态
        validation = self.validate_state(new_state)
        if not validation.is_valid:
            error_context = create_error_context(
                session_id=state.get("session_id"),
                additional_info={"validation_errors": validation.errors}
            )
            raise AstroError(
                f"State update validation failed: {'; '.join(validation.errors)}",
                ErrorCode.WORKFLOW_ERROR,
                ErrorSeverity.MEDIUM,
                error_context
            )
        
        return new_state


# 全局状态管理器实例
_state_manager = StateManager()


def get_state_manager() -> StateManager:
    """获取全局状态管理器"""
    return _state_manager


def validate_state(state: Dict[str, Any]) -> StateValidationResult:
    """便捷函数：验证状态"""
    return _state_manager.validate_state(state)


def format_state_output(state: Dict[str, Any]) -> str:
    """便捷函数：格式化状态输出"""
    return _state_manager.format_state_output(state)


def create_initial_state(session_id: str, user_input: str) -> Dict[str, Any]:
    """便捷函数：创建初始状态"""
    return _state_manager.create_initial_state(session_id, user_input)


def update_state(state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """便捷函数：更新状态"""
    return _state_manager.update_state(state, updates)


if __name__ == "__main__":
    # 测试状态管理
    state = create_initial_state("test_session", "测试输入")
    print("初始状态创建成功")
    
    # 测试状态验证
    validation = validate_state(state)
    print(f"状态验证: {'通过' if validation.is_valid else '失败'}")
    if validation.errors:
        print(f"错误: {validation.errors}")
    if validation.warnings:
        print(f"警告: {validation.warnings}")
    
    # 测试状态输出格式化
    output = format_state_output(state)
    print("\n状态输出:")
    print(output)
