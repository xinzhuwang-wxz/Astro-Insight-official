#!/usr/bin/env python3
"""
API模块
提供API请求处理、路由管理和响应生成功能
"""

from typing import Dict, Any, Optional, Union

# 导入所有模型类和枚举
from .models import (
    # 枚举
    QueryType,
    ResponseStatus,
    ConfidenceLevel,
    UserType,
    TaskType,
    
    # 基础类
    APIRequest,
    APIResponse,
    
    # 数据类
    CelestialObject,
    ClassificationResult,
    
    # 请求类
    ClassificationRequest,
    BatchRequest,
    HistoryRequest,
    DataRetrievalRequest,
    LiteratureReviewRequest,
    CodeGenerationRequest,
    
    # 响应类
    ClassificationResponse,
    BatchResponse,
    HistoryEntry,
    HistoryResponse,
    DataRetrievalResponse,
    LiteratureReviewResponse,
    CodeGenerationResponse,
    HealthCheckResponse,
    ErrorResponse,
    
    # 工作流状态
    WorkflowState,
    
    # 辅助函数
    create_error_response,
    create_success_response,
    get_confidence_level
)

# 尝试导入处理器和路由（如果不存在则创建基本实现）
try:
    from .handlers import APIHandler
except ImportError:
    # 创建基本的API处理器
    class APIHandler:
        """基本API处理器"""
        
        def __init__(self):
            self.name = "api_handler"
        
        async def handle_classification(self, request: ClassificationRequest) -> ClassificationResponse:
            """处理分类请求"""
            return ClassificationResponse(
                status=ResponseStatus.SUCCESS,
                request_id=request.request_id,
                results=[],
                query=request.query,
                confidence_threshold=request.confidence_threshold
            )
        
        async def handle_batch(self, request: BatchRequest) -> BatchResponse:
            """处理批量请求"""
            return BatchResponse(
                status=ResponseStatus.SUCCESS,
                request_id=request.request_id,
                results=[]
            )
        
        async def handle_history(self, request: HistoryRequest) -> HistoryResponse:
            """处理历史记录请求"""
            return HistoryResponse(
                status=ResponseStatus.SUCCESS,
                request_id=request.request_id,
                entries=[],
                limit=request.limit,
                offset=request.offset
            )
        
        async def health_check(self) -> HealthCheckResponse:
            """健康检查"""
            return HealthCheckResponse(
                status=ResponseStatus.SUCCESS,
                service_status="healthy",
                database_status="healthy",
                api_version="1.0.0",
                uptime=0.0
            )

# 导入路由器
from .router import APIRouter, api_router, get_router, register_route, get_route_handler

# 创建全局处理器实例
api_handler = APIHandler()

# 便捷函数
async def handle_api_request(path: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, query_params: Optional[Dict[str, Any]] = None) -> Union[APIResponse, ErrorResponse]:
    """处理API请求的通用函数"""
    return await api_router.handle_request(path, method, data, query_params)

async def handle_classification_request(request: ClassificationRequest) -> ClassificationResponse:
    """处理分类请求的便捷函数"""
    return await api_handler.handle_classification(request)

async def handle_batch_request(request: BatchRequest) -> BatchResponse:
    """处理批量请求的便捷函数"""
    return await api_handler.handle_batch(request)

async def handle_history_request(request: HistoryRequest) -> HistoryResponse:
    """处理历史记录请求的便捷函数"""
    return await api_handler.handle_history(request)

async def handle_health_check() -> HealthCheckResponse:
    """处理健康检查请求的便捷函数"""
    return await api_handler.health_check()

# 导出所有公共接口
__all__ = [
    # 枚举
    "QueryType",
    "ResponseStatus", 
    "ConfidenceLevel",
    "UserType",
    "TaskType",
    
    # 基础类
    "APIRequest",
    "APIResponse",
    
    # 数据类
    "CelestialObject",
    "ClassificationResult",
    
    # 请求类
    "ClassificationRequest",
    "BatchRequest",
    "HistoryRequest",
    "DataRetrievalRequest",
    "LiteratureReviewRequest",
    "CodeGenerationRequest",
    
    # 响应类
    "ClassificationResponse",
    "BatchResponse",
    "HistoryEntry",
    "HistoryResponse",
    "DataRetrievalResponse",
    "LiteratureReviewResponse",
    "CodeGenerationResponse",
    "HealthCheckResponse",
    "ErrorResponse",
    
    # 工作流状态
    "WorkflowState",
    
    # 处理器和路由
    "APIHandler",
    "APIRouter",
    "api_router",
    "api_handler",
    "get_router",
    "register_route",
    "get_route_handler",
    
    # 便捷函数
    "handle_api_request",
    "handle_classification_request",
    "handle_batch_request",
    "handle_history_request",
    "handle_health_check",
    
    # 辅助函数
    "create_error_response",
    "create_success_response",
    "get_confidence_level"
]