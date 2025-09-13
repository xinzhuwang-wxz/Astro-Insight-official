#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心异常定义
定义系统核心异常类
"""


class AstroCoreException(Exception):
    """核心异常基类"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ServiceNotFoundError(AstroCoreException):
    """服务未找到异常"""
    
    def __init__(self, message: str, service_name: str = None):
        super().__init__(message, "SERVICE_NOT_FOUND")
        self.service_name = service_name


class ConfigurationError(AstroCoreException):
    """配置错误异常"""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key


class StateManagementError(AstroCoreException):
    """状态管理错误异常"""
    
    def __init__(self, message: str, state_field: str = None):
        super().__init__(message, "STATE_MANAGEMENT_ERROR")
        self.state_field = state_field


class DependencyInjectionError(AstroCoreException):
    """依赖注入错误异常"""
    
    def __init__(self, message: str, dependency_name: str = None):
        super().__init__(message, "DEPENDENCY_INJECTION_ERROR")
        self.dependency_name = dependency_name


class ServiceInitializationError(AstroCoreException):
    """服务初始化错误异常"""
    
    def __init__(self, message: str, service_name: str = None):
        super().__init__(message, "SERVICE_INITIALIZATION_ERROR")
        self.service_name = service_name


class ValidationError(AstroCoreException):
    """验证错误异常"""
    
    def __init__(self, message: str, field_name: str = None, value: any = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field_name = field_name
        self.value = value


class BusinessLogicError(AstroCoreException):
    """业务逻辑错误异常"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")
        self.operation = operation

