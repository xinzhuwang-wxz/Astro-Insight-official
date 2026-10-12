#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入容器
实现依赖注入模式，管理服务生命周期
"""

from typing import Dict, Any, Type, TypeVar, Callable, Optional, Union
import threading
from functools import wraps

from .interfaces import (
    IUserService, ITaskService, IIdentityService, IClassificationService,
    IDataRetrievalService, ICodeGenerationService, IStateManager,
    IConfigurationManager, IErrorHandler, ILogger, ICacheManager, IDatabaseRepository
)
from .exceptions import ServiceNotFoundError, DependencyInjectionError

T = TypeVar('T')


class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = threading.RLock()
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """注册服务实例"""
        with self._lock:
            self._services[interface] = instance
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """注册服务工厂"""
        with self._lock:
            self._factories[interface] = factory
    
    def register_singleton(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """注册单例服务"""
        with self._lock:
            self._factories[interface] = factory
            self._singletons[interface] = None  # 标记为单例
    
    def get(self, interface: Type[T]) -> T:
        """获取服务"""
        with self._lock:
            # 首先检查已注册的实例
            if interface in self._services:
                return self._services[interface]
            
            # 检查单例
            if interface in self._singletons:
                if self._singletons[interface] is None:
                    # 创建单例实例
                    if interface in self._factories:
                        self._singletons[interface] = self._factories[interface]()
                    else:
                        raise ServiceNotFoundError(f"Factory not found for singleton: {interface.__name__}")
                return self._singletons[interface]
            
            # 检查工厂
            if interface in self._factories:
                return self._factories[interface]()
            
            raise ServiceNotFoundError(f"Service not found: {interface.__name__}")
    
    def is_registered(self, interface: Type[T]) -> bool:
        """检查服务是否已注册"""
        with self._lock:
            return (interface in self._services or 
                   interface in self._factories or 
                   interface in self._singletons)


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._registry = ServiceRegistry()
        self._lock = threading.RLock()
    
    def register_instance(self, interface: Type[T], instance: T) -> 'DIContainer':
        """注册服务实例"""
        self._registry.register_instance(interface, instance)
        return self
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> 'DIContainer':
        """注册服务工厂"""
        self._registry.register_factory(interface, factory)
        return self
    
    def register_singleton(self, interface: Type[T], factory: Callable[[], T]) -> 'DIContainer':
        """注册单例服务"""
        self._registry.register_singleton(interface, factory)
        return self
    
    def get(self, interface: Type[T]) -> T:
        """获取服务"""
        return self._registry.get(interface)
    
    def is_registered(self, interface: Type[T]) -> bool:
        """检查服务是否已注册"""
        return self._registry.is_registered(interface)
    
    def clear(self) -> None:
        """清空容器"""
        with self._lock:
            self._registry = ServiceRegistry()


# 全局容器实例
_container: Optional[DIContainer] = None
_container_lock = threading.RLock()


def get_container() -> DIContainer:
    """获取全局容器实例"""
    global _container
    with _container_lock:
        if _container is None:
            _container = DIContainer()
        return _container


def register_service(interface: Type[T], implementation: Union[T, Callable[[], T]], 
                    singleton: bool = False) -> None:
    """注册服务到全局容器"""
    container = get_container()
    
    if callable(implementation) and not singleton:
        container.register_factory(interface, implementation)
    elif callable(implementation) and singleton:
        container.register_singleton(interface, implementation)
    else:
        container.register_instance(interface, implementation)


def get_service(interface: Type[T]) -> T:
    """从全局容器获取服务"""
    container = get_container()
    return container.get(interface)


def inject(interface: Type[T]):
    """依赖注入装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查参数中是否已经有该接口的实现
            for arg in args:
                if isinstance(arg, interface):
                    return func(*args, **kwargs)
            
            # 从容器获取服务
            service = get_service(interface)
            
            # 将服务作为第一个参数注入
            return func(service, *args, **kwargs)
        return wrapper
    return decorator


def configure_default_services(container: DIContainer) -> None:
    """配置默认服务"""
    from src.utils.error_handler import ErrorHandler
    from src.utils.state_manager import StateManager
    from src.config.enhanced_config import ConfigManager
    from .implementations import (
        DefaultUserService, DefaultTaskService, DefaultIdentityService,
        DefaultClassificationService, DefaultDataRetrievalService,
        DefaultCodeGenerationService, DefaultCacheManager, DefaultDatabaseRepository
    )
    
    # 注册核心服务
    from .abstractions import DefaultLogger
    container.register_singleton(ILogger, lambda: DefaultLogger())
    container.register_singleton(IErrorHandler, lambda: ErrorHandler())
    container.register_singleton(IStateManager, lambda: StateManager())
    container.register_singleton(IConfigurationManager, lambda: ConfigManager())
    
    # 注册业务服务
    container.register_singleton(IUserService, lambda: DefaultUserService(
        logger=container.get(ILogger),
        error_handler=container.get(IErrorHandler)
    ))
    
    container.register_singleton(ITaskService, lambda: DefaultTaskService(
        logger=container.get(ILogger),
        error_handler=container.get(IErrorHandler)
    ))
    
    container.register_singleton(IIdentityService, lambda: DefaultIdentityService(
        logger=container.get(ILogger),
        error_handler=container.get(IErrorHandler)
    ))
    
    container.register_singleton(IClassificationService, lambda: DefaultClassificationService(
        logger=container.get(ILogger),
        error_handler=container.get(IErrorHandler)
    ))
    
    container.register_singleton(IDataRetrievalService, lambda: DefaultDataRetrievalService(
        logger=container.get(ILogger),
        error_handler=container.get(IErrorHandler)
    ))
    
    container.register_singleton(ICodeGenerationService, lambda: DefaultCodeGenerationService(
        logger=container.get(ILogger),
        error_handler=container.get(IErrorHandler)
    ))
    
    container.register_singleton(ICacheManager, lambda: DefaultCacheManager())
    container.register_singleton(IDatabaseRepository, lambda: DefaultDatabaseRepository(
        logger=container.get(ILogger)
    ))
