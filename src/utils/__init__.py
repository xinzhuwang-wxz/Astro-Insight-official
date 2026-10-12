#!/usr/bin/env python3
"""
工具模块
提供错误处理、状态管理等通用工具
"""

from .error_handler import (
    ErrorCode,
    ErrorSeverity, 
    ErrorContext,
    AstroError,
    ErrorHandler,
    handle_error,
    create_error_context,
    error_handler_decorator,
)

from .state_manager import (
    StateStep,
    StateValidationResult,
    StateManager,
    get_state_manager,
    validate_state,
    format_state_output,
    create_initial_state,
    update_state,
)

# JSON工具模块暂时为空，待实现

__all__ = [
    # 错误处理
    "ErrorCode",
    "ErrorSeverity",
    "ErrorContext", 
    "AstroError",
    "ErrorHandler",
    "handle_error",
    "create_error_context",
    "error_handler_decorator",
    # 状态管理
    "StateStep",
    "StateValidationResult",
    "StateManager",
    "get_state_manager",
    "validate_state",
    "format_state_output",
    "create_initial_state",
    "update_state",
    # JSON工具暂时为空
]

__version__ = "1.0.0"
__author__ = "Astro Insight Team"
__description__ = "通用工具模块"
