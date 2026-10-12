#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理模块测试
"""
ni
import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.error_handler import (
    AstroError, ErrorCode, ErrorSeverity, ErrorContext,
    ErrorHandler, handle_error, create_error_context
)


class TestAstroError:
    """测试AstroError类"""
    
    def test_astro_error_creation(self):
        """测试AstroError创建"""
        error = AstroError(
            "测试错误",
            ErrorCode.SYSTEM_ERROR,
            ErrorSeverity.HIGH
        )
        
        assert error.message == "测试错误"
        assert error.error_code == ErrorCode.SYSTEM_ERROR
        assert error.severity == ErrorSeverity.HIGH
        assert error.timestamp is not None
    
    def test_astro_error_to_dict(self):
        """测试AstroError转换为字典"""
        context = ErrorContext(
            user_id="test_user",
            session_id="test_session"
        )
        
        error = AstroError(
            "测试错误",
            ErrorCode.WORKFLOW_ERROR,
            ErrorSeverity.MEDIUM,
            context
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error_code"] == ErrorCode.WORKFLOW_ERROR.value
        assert error_dict["message"] == "测试错误"
        assert error_dict["severity"] == ErrorSeverity.MEDIUM.value
        assert error_dict["context"]["user_id"] == "test_user"
        assert error_dict["context"]["session_id"] == "test_session"


class TestErrorHandler:
    """测试ErrorHandler类"""
    
    def setup_method(self):
        """测试前准备"""
        self.error_handler = ErrorHandler("test_logger")
    
    def test_handle_astro_error(self):
        """测试处理AstroError"""
        error = AstroError(
            "测试错误",
            ErrorCode.SYSTEM_ERROR,
            ErrorSeverity.HIGH
        )
        
        result = self.error_handler.handle_error(error, reraise=False)
        
        assert result["error_code"] == ErrorCode.SYSTEM_ERROR.value
        assert result["message"] == "测试错误"
    
    def test_handle_regular_exception(self):
        """测试处理普通异常"""
        try:
            raise ValueError("测试值错误")
        except Exception as e:
            result = self.error_handler.handle_error(e, reraise=False)
            
            assert result["error_code"] == ErrorCode.INVALID_INPUT.value
            assert "测试值错误" in result["message"]
    
    def test_map_exception_to_error_code(self):
        """测试异常类型映射"""
        # 测试ValueError
        error = ValueError("测试")
        error_code = self.error_handler._map_exception_to_error_code(error)
        assert error_code == ErrorCode.INVALID_INPUT
        
        # 测试ConnectionError
        error = ConnectionError("测试")
        error_code = self.error_handler._map_exception_to_error_code(error)
        assert error_code == ErrorCode.NETWORK_ERROR
        
        # 测试未知异常
        error = Exception("测试")
        error_code = self.error_handler._map_exception_to_error_code(error)
        assert error_code == ErrorCode.SYSTEM_ERROR
    
    def test_determine_severity(self):
        """测试严重程度确定"""
        # 测试严重错误
        error = MemoryError("测试")
        severity = self.error_handler._determine_severity(error)
        assert severity == ErrorSeverity.CRITICAL
        
        # 测试高严重性错误
        error = ConnectionError("测试")
        severity = self.error_handler._determine_severity(error)
        assert severity == ErrorSeverity.HIGH
        
        # 测试中等严重性错误
        error = ValueError("测试")
        severity = self.error_handler._determine_severity(error)
        assert severity == ErrorSeverity.MEDIUM


class TestErrorContext:
    """测试ErrorContext类"""
    
    def test_error_context_creation(self):
        """测试ErrorContext创建"""
        context = ErrorContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request"
        )
        
        assert context.user_id == "test_user"
        assert context.session_id == "test_session"
        assert context.request_id == "test_request"
        assert context.timestamp is not None
        assert context.additional_info == {}


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_handle_error_function(self):
        """测试handle_error便捷函数"""
        try:
            raise ValueError("测试错误")
        except Exception as e:
            result = handle_error(e, reraise=False)
            assert result["error_code"] == ErrorCode.INVALID_INPUT.value
    
    def test_create_error_context_function(self):
        """测试create_error_context便捷函数"""
        context = create_error_context(
            user_id="test_user",
            session_id="test_session",
            test_param="test_value"
        )
        
        assert context.user_id == "test_user"
        assert context.session_id == "test_session"
        assert context.additional_info["test_param"] == "test_value"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
