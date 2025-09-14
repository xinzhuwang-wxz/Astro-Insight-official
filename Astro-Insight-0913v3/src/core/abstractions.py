#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心抽象类
提供基础抽象类，减少重复代码
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

from .interfaces import (
    IUserService, ITaskService, IIdentityService, IClassificationService,
    IDataRetrievalService, ICodeGenerationService, IStateManager,
    IConfigurationManager, IErrorHandler, ILogger, ICacheManager, IDatabaseRepository
)
from src.graph.types import AstroAgentState


class BaseService(ABC):
    """服务基类"""
    
    def __init__(self, logger: Optional[ILogger] = None, error_handler: Optional[IErrorHandler] = None):
        self.logger = logger or self._get_default_logger()
        self.error_handler = error_handler
    
    def _get_default_logger(self) -> ILogger:
        """获取默认日志器"""
        return DefaultLogger()
    
    def _handle_service_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理服务错误"""
        if self.error_handler:
            return self.error_handler.handle_error(error, context)
        else:
            return {"error": str(error), "context": context}


class BaseRepository(ABC):
    """仓储基类"""
    
    def __init__(self, logger: Optional[ILogger] = None):
        self.logger = logger or self._get_default_logger()
    
    def _get_default_logger(self) -> ILogger:
        """获取默认日志器"""
        return DefaultLogger()


class BaseStateManager(ABC):
    """状态管理基类"""
    
    def __init__(self, logger: Optional[ILogger] = None):
        self.logger = logger or self._get_default_logger()
    
    def _get_default_logger(self) -> ILogger:
        """获取默认日志器"""
        return DefaultLogger()
    
    def _validate_state_fields(self, state: AstroAgentState) -> List[str]:
        """验证状态字段"""
        errors = []
        required_fields = ['session_id', 'user_input', 'messages']
        
        for field in required_fields:
            if not hasattr(state, field) or getattr(state, field) is None:
                errors.append(f"Missing required field: {field}")
        
        return errors


class BaseConfigurationManager(ABC):
    """配置管理基类"""
    
    def __init__(self, logger: Optional[ILogger] = None):
        self.logger = logger or self._get_default_logger()
    
    def _get_default_logger(self) -> ILogger:
        """获取默认日志器"""
        return DefaultLogger()
    
    def _validate_config_section(self, config: Dict[str, Any], required_keys: List[str]) -> List[str]:
        """验证配置节"""
        errors = []
        
        for key in required_keys:
            if key not in config or config[key] is None:
                errors.append(f"Missing required config key: {key}")
        
        return errors


class DefaultLogger(ILogger):
    """默认日志实现"""
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        self._logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        self._logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        self._logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        self._logger.debug(message, extra=kwargs)
