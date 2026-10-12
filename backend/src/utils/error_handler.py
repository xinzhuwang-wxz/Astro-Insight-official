#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理模块
提供标准化的错误处理、日志记录和错误响应机制
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ErrorCode(Enum):
    """错误码枚举"""
    # 系统错误 (1000-1999)
    SYSTEM_ERROR = 1000
    CONFIG_ERROR = 1001
    DATABASE_ERROR = 1002
    NETWORK_ERROR = 1003
    FILE_ERROR = 1004
    
    # 用户输入错误 (2000-2999)
    INVALID_INPUT = 2000
    MISSING_PARAMETER = 2001
    INVALID_FORMAT = 2002
    AUTHENTICATION_ERROR = 2003
    AUTHORIZATION_ERROR = 2004
    
    # 业务逻辑错误 (3000-3999)
    WORKFLOW_ERROR = 3000
    LLM_ERROR = 3001
    DATA_RETRIEVAL_ERROR = 3002
    CODE_GENERATION_ERROR = 3003
    CODE_EXECUTION_ERROR = 3004
    CLASSIFICATION_ERROR = 3005
    
    # 外部服务错误 (4000-4999)
    API_ERROR = 4000
    TIMEOUT_ERROR = 4001
    RATE_LIMIT_ERROR = 4002
    SERVICE_UNAVAILABLE = 4003


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """错误上下文信息"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: str = None
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.additional_info is None:
            self.additional_info = {}


class AstroError(Exception):
    """Astro-Insight系统基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.SYSTEM_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.context = context or ErrorContext()
        self.original_error = original_error
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "context": {
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "timestamp": self.context.timestamp,
                "additional_info": self.context.additional_info
            },
            "details": self.details,
            "original_error": str(self.original_error) if self.original_error else None
        }


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self, logger_name: str = "astro_error"):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_error(
        self,
        error: Union[AstroError, Exception],
        context: Optional[ErrorContext] = None,
        reraise: bool = True
    ) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 错误对象
            context: 错误上下文
            reraise: 是否重新抛出异常
            
        Returns:
            错误信息字典
        """
        # 如果不是AstroError，转换为AstroError
        if not isinstance(error, AstroError):
            error = self._convert_to_astro_error(error, context)
        
        # 记录错误日志
        self._log_error(error)
        
        # 记录到数据库（如果需要）
        self._record_error_to_db(error)
        
        # 返回错误信息
        error_dict = error.to_dict()
        
        if reraise:
            raise error
        
        return error_dict
    
    def _convert_to_astro_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> AstroError:
        """将普通异常转换为AstroError"""
        error_code = self._map_exception_to_error_code(error)
        severity = self._determine_severity(error)
        
        return AstroError(
            message=str(error),
            error_code=error_code,
            severity=severity,
            context=context,
            original_error=error,
            details={"exception_type": type(error).__name__}
        )
    
    def _map_exception_to_error_code(self, error: Exception) -> ErrorCode:
        """映射异常类型到错误码"""
        error_type = type(error).__name__
        
        mapping = {
            "ValueError": ErrorCode.INVALID_INPUT,
            "TypeError": ErrorCode.INVALID_INPUT,
            "KeyError": ErrorCode.MISSING_PARAMETER,
            "AttributeError": ErrorCode.INVALID_INPUT,
            "ConnectionError": ErrorCode.NETWORK_ERROR,
            "TimeoutError": ErrorCode.TIMEOUT_ERROR,
            "FileNotFoundError": ErrorCode.FILE_ERROR,
            "PermissionError": ErrorCode.AUTHORIZATION_ERROR,
            "ImportError": ErrorCode.CONFIG_ERROR,
            "sqlite3.Error": ErrorCode.DATABASE_ERROR,
            "requests.RequestException": ErrorCode.API_ERROR,
        }
        
        return mapping.get(error_type, ErrorCode.SYSTEM_ERROR)
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """确定错误严重程度"""
        error_type = type(error).__name__
        
        critical_errors = ["SystemExit", "KeyboardInterrupt", "MemoryError"]
        high_errors = ["ConnectionError", "TimeoutError", "sqlite3.Error"]
        medium_errors = ["ValueError", "TypeError", "KeyError", "AttributeError"]
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _log_error(self, error: AstroError):
        """记录错误日志"""
        log_level = self._get_log_level(error.severity)
        
        log_message = (
            f"Error {error.error_code.name}: {error.message} "
            f"[Severity: {error.severity.value}] "
            f"[Context: {error.context.session_id}]"
        )
        
        if error.original_error:
            log_message += f" [Original: {type(error.original_error).__name__}]"
        
        self.logger.log(log_level, log_message)
        
        # 记录堆栈跟踪（仅对高严重性错误）
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """获取日志级别"""
        mapping = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.ERROR)
    
    def _record_error_to_db(self, error: AstroError):
        """记录错误到数据库"""
        # TODO: 实现数据库错误记录
        # 这里可以添加将错误信息记录到数据库的逻辑
        pass


# 全局错误处理器实例
error_handler = ErrorHandler()


def handle_error(
    error: Union[AstroError, Exception],
    context: Optional[ErrorContext] = None,
    reraise: bool = True
) -> Dict[str, Any]:
    """
    便捷函数：处理错误
    
    Args:
        error: 错误对象
        context: 错误上下文
        reraise: 是否重新抛出异常
        
    Returns:
        错误信息字典
    """
    return error_handler.handle_error(error, context, reraise)


def create_error_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> ErrorContext:
    """
    便捷函数：创建错误上下文
    
    Args:
        user_id: 用户ID
        session_id: 会话ID
        request_id: 请求ID
        **kwargs: 其他上下文信息
        
    Returns:
        错误上下文对象
    """
    return ErrorContext(
        user_id=user_id,
        session_id=session_id,
        request_id=request_id,
        additional_info=kwargs
    )


# 装饰器：自动错误处理
def error_handler_decorator(reraise: bool = True):
    """
    错误处理装饰器
    
    Args:
        reraise: 是否重新抛出异常
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = create_error_context(
                    session_id=kwargs.get('session_id'),
                    request_id=kwargs.get('request_id')
                )
                return handle_error(e, context, reraise)
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试错误处理
    try:
        # 测试普通异常
        raise ValueError("测试错误")
    except Exception as e:
        context = create_error_context(session_id="test_session")
        error_info = handle_error(e, context, reraise=False)
        print("错误信息:", error_info)
    
    # 测试AstroError
    try:
        raise AstroError(
            "测试AstroError",
            ErrorCode.WORKFLOW_ERROR,
            ErrorSeverity.HIGH,
            create_error_context(session_id="test_session")
        )
    except AstroError as e:
        error_info = handle_error(e, reraise=False)
        print("AstroError信息:", error_info)
