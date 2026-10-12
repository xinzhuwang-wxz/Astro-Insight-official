#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块
提供系统的基础接口、抽象类和依赖注入容器
"""

from .interfaces import (
    IUserService,
    ITaskService,
    IIdentityService,
    IClassificationService,
    IDataRetrievalService,
    ICodeGenerationService,
    IStateManager,
    IConfigurationManager,
    IErrorHandler,
    ILogger,
    ICacheManager,
    IDatabaseRepository
)

from .abstractions import (
    BaseService,
    BaseRepository,
    BaseStateManager,
    BaseConfigurationManager
)

from .container import (
    DIContainer,
    ServiceRegistry,
    get_container,
    register_service,
    get_service
)

from .exceptions import (
    ServiceNotFoundError,
    ConfigurationError,
    StateManagementError,
    DependencyInjectionError
)

__all__ = [
    # 接口
    "IUserService",
    "ITaskService", 
    "IIdentityService",
    "IClassificationService",
    "IDataRetrievalService",
    "ICodeGenerationService",
    "IStateManager",
    "IConfigurationManager",
    "IErrorHandler",
    "ILogger",
    "ICacheManager",
    "IDatabaseRepository",
    
    # 抽象类
    "BaseService",
    "BaseRepository",
    "BaseStateManager",
    "BaseConfigurationManager",
    
    # 依赖注入
    "DIContainer",
    "ServiceRegistry",
    "get_container",
    "register_service",
    "get_service",
    
    # 异常
    "ServiceNotFoundError",
    "ConfigurationError",
    "StateManagementError",
    "DependencyInjectionError"
]

