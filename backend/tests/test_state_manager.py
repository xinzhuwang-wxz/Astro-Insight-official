#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态管理模块测试
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.state_manager import (
    StateManager, StateStep, StateValidationResult,
    validate_state, format_state_output, create_initial_state, update_state
)


class TestStateManager:
    """测试StateManager类"""
    
    def setup_method(self):
        """测试前准备"""
        self.state_manager = StateManager()
    
    def test_validate_state_valid(self):
        """测试有效状态验证"""
        state = {
            "session_id": "test_session",
            "user_input": "测试输入",
            "current_step": "identity_check",
            "timestamp": 1234567890.0
        }
        
        result = self.state_manager.validate_state(state)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_state_invalid(self):
        """测试无效状态验证"""
        state = {
            "session_id": "",
            "user_input": "",
            "current_step": "invalid_step"
        }
        
        result = self.state_manager.validate_state(state)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Session ID cannot be empty" in result.errors
        assert "User input cannot be empty" in result.errors
        assert "Invalid current_step" in result.errors
    
    def test_validate_state_missing_fields(self):
        """测试缺失字段验证"""
        state = {
            "session_id": "test_session"
        }
        
        result = self.state_manager.validate_state(state)
        
        assert result.is_valid is False
        assert "Missing required field: user_input" in result.errors
        assert "Missing required field: current_step" in result.errors
        assert "Missing required field: timestamp" in result.errors
    
    def test_create_initial_state(self):
        """测试创建初始状态"""
        state = self.state_manager.create_initial_state("test_session", "测试输入")
        
        assert state["session_id"] == "test_session"
        assert state["user_input"] == "测试输入"
        assert state["current_step"] == StateStep.IDENTITY_CHECK.value
        assert state["is_complete"] is False
        assert state["timestamp"] is not None
    
    def test_update_state(self):
        """测试更新状态"""
        initial_state = self.state_manager.create_initial_state("test_session", "测试输入")
        
        updates = {
            "user_type": "professional",
            "task_type": "classification",
            "current_step": "task_selection"
        }
        
        updated_state = self.state_manager.update_state(initial_state, updates)
        
        assert updated_state["user_type"] == "professional"
        assert updated_state["task_type"] == "classification"
        assert updated_state["current_step"] == "task_selection"
        assert updated_state["timestamp"] > initial_state["timestamp"]
    
    def test_update_state_invalid(self):
        """测试无效状态更新"""
        initial_state = self.state_manager.create_initial_state("test_session", "测试输入")
        
        updates = {
            "current_step": "invalid_step"
        }
        
        with pytest.raises(Exception):  # 应该抛出AstroError
            self.state_manager.update_state(initial_state, updates)
    
    def test_format_state_output(self):
        """测试状态输出格式化"""
        state = self.state_manager.create_initial_state("test_session", "测试输入")
        state["user_type"] = "professional"
        state["task_type"] = "classification"
        
        output = self.state_manager.format_state_output(state)
        
        assert "会话ID: test_session" in output
        assert "用户输入: 测试输入" in output
        assert "用户类型: professional" in output
        assert "任务类型: classification" in output
        assert "当前步骤: identity_check" in output


class TestStateValidationResult:
    """测试StateValidationResult类"""
    
    def test_validation_result_creation(self):
        """测试验证结果创建"""
        result = StateValidationResult(
            is_valid=True,
            errors=["错误1", "错误2"],
            warnings=["警告1"]
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 2
        assert len(result.warnings) == 1


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_validate_state_function(self):
        """测试validate_state便捷函数"""
        state = {
            "session_id": "test_session",
            "user_input": "测试输入",
            "current_step": "identity_check",
            "timestamp": 1234567890.0
        }
        
        result = validate_state(state)
        assert result.is_valid is True
    
    def test_create_initial_state_function(self):
        """测试create_initial_state便捷函数"""
        state = create_initial_state("test_session", "测试输入")
        
        assert state["session_id"] == "test_session"
        assert state["user_input"] == "测试输入"
    
    def test_format_state_output_function(self):
        """测试format_state_output便捷函数"""
        state = create_initial_state("test_session", "测试输入")
        output = format_state_output(state)
        
        assert "会话ID: test_session" in output
        assert "用户输入: 测试输入" in output
    
    def test_update_state_function(self):
        """测试update_state便捷函数"""
        state = create_initial_state("test_session", "测试输入")
        
        updates = {
            "user_type": "amateur",
            "current_step": "qa_response"
        }
        
        updated_state = update_state(state, updates)
        
        assert updated_state["user_type"] == "amateur"
        assert updated_state["current_step"] == "qa_response"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
