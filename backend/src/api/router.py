#!/usr/bin/env python3
"""
API路由器
提供API路由注册和请求分发功能
"""

import json
from typing import Dict, Any, Callable, Optional, Union
from urllib.parse import urlparse, parse_qs

from .models import (
    QueryType,
    ResponseStatus,
    APIRequest,
    APIResponse,
    ClassificationRequest,
    ClassificationResponse,
    BatchRequest,
    BatchResponse,
    HistoryRequest,
    HistoryResponse,
    DataRetrievalRequest,
    DataRetrievalResponse,
    LiteratureReviewRequest,
    LiteratureReviewResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
    HealthCheckResponse,
    ErrorResponse,
    WorkflowState,
    create_error_response
)

from .handlers import (
    APIHandler,
    api_handler,
    handle_classification_request,
    handle_batch_request,
    handle_history_request,
    handle_health_check
)


class APIRouter:
    """API路由器"""
    
    def __init__(self, handler: Optional[APIHandler] = None):
        self.handler = handler or api_handler
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware: list = []
        self._register_default_routes()
    
    def _register_default_routes(self):
        """注册默认路由"""
        # 分类相关路由
        self.add_route("/api/classify", "POST", self._handle_classification)
        self.add_route("/api/classification", "POST", self._handle_classification)
        
        # 批量处理路由
        self.add_route("/api/batch", "POST", self._handle_batch)
        self.add_route("/api/batch/classify", "POST", self._handle_batch)
        
        # 历史记录路由
        self.add_route("/api/history", "GET", self._handle_history)
        self.add_route("/api/history", "POST", self._handle_history)
        
        # 数据检索路由
        self.add_route("/api/data", "POST", self._handle_data_retrieval)
        self.add_route("/api/retrieve", "POST", self._handle_data_retrieval)
        
        # 文献综述路由
        self.add_route("/api/literature", "POST", self._handle_literature_review)
        self.add_route("/api/review", "POST", self._handle_literature_review)
        
        # 代码生成路由
        self.add_route("/api/code", "POST", self._handle_code_generation)
        self.add_route("/api/generate", "POST", self._handle_code_generation)
        
        # 工作流状态路由
        self.add_route("/api/workflow", "GET", self._handle_workflow_get)
        self.add_route("/api/workflow", "POST", self._handle_workflow_update)
        
        # 健康检查路由
        self.add_route("/api/health", "GET", self._handle_health_check)
        self.add_route("/health", "GET", self._handle_health_check)
        self.add_route("/ping", "GET", self._handle_ping)
        
        # 根路径
        self.add_route("/", "GET", self._handle_root)
        self.add_route("/api", "GET", self._handle_api_info)
    
    def add_route(self, path: str, method: str, handler: Callable):
        """添加路由"""
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method.upper()] = handler
    
    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self.middleware.append(middleware)
    
    def get_route(self, path: str, method: str = "GET") -> Optional[Callable]:
        """获取路由处理器"""
        route_handlers = self.routes.get(path, {})
        return route_handlers.get(method.upper())
    
    async def handle_request(self, path: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, query_params: Optional[Dict[str, Any]] = None) -> Union[APIResponse, ErrorResponse]:
        """处理HTTP请求"""
        try:
            # 应用中间件
            for middleware in self.middleware:
                result = await middleware(path, method, data, query_params)
                if isinstance(result, (APIResponse, ErrorResponse)):
                    return result
            
            # 获取路由处理器
            handler = self.get_route(path, method)
            if not handler:
                return create_error_response(
                    error_code="ROUTE_NOT_FOUND",
                    error_message=f"Route {method} {path} not found"
                )
            
            # 调用处理器
            if data or query_params:
                return await handler(data or query_params)
            else:
                return await handler()
                
        except Exception as e:
            return create_error_response(
                error_code="REQUEST_HANDLING_ERROR",
                error_message=f"Request handling failed: {str(e)}"
            )
    
    async def _handle_classification(self, data: Dict[str, Any]) -> Union[ClassificationResponse, ErrorResponse]:
        """处理分类请求"""
        try:
            request = ClassificationRequest(**data)
            return await self.handler.handle_classification(request)
        except Exception as e:
            return create_error_response(
                error_code="CLASSIFICATION_REQUEST_ERROR",
                error_message=f"Invalid classification request: {str(e)}"
            )
    
    async def _handle_batch(self, data: Dict[str, Any]) -> Union[BatchResponse, ErrorResponse]:
        """处理批量请求"""
        try:
            request = BatchRequest(**data)
            return await self.handler.handle_batch(request)
        except Exception as e:
            return create_error_response(
                error_code="BATCH_REQUEST_ERROR",
                error_message=f"Invalid batch request: {str(e)}"
            )
    
    async def _handle_history(self, data: Optional[Dict[str, Any]] = None) -> Union[HistoryResponse, ErrorResponse]:
        """处理历史记录请求"""
        try:
            request_data = data or {}
            request = HistoryRequest(**request_data)
            return await self.handler.handle_history(request)
        except Exception as e:
            return create_error_response(
                error_code="HISTORY_REQUEST_ERROR",
                error_message=f"Invalid history request: {str(e)}"
            )
    
    async def _handle_data_retrieval(self, data: Dict[str, Any]) -> Union[DataRetrievalResponse, ErrorResponse]:
        """处理数据检索请求"""
        try:
            request = DataRetrievalRequest(**data)
            return await self.handler.handle_data_retrieval(request)
        except Exception as e:
            return create_error_response(
                error_code="DATA_RETRIEVAL_REQUEST_ERROR",
                error_message=f"Invalid data retrieval request: {str(e)}"
            )
    
    async def _handle_literature_review(self, data: Dict[str, Any]) -> Union[LiteratureReviewResponse, ErrorResponse]:
        """处理文献综述请求"""
        try:
            request = LiteratureReviewRequest(**data)
            return await self.handler.handle_literature_review(request)
        except Exception as e:
            return create_error_response(
                error_code="LITERATURE_REVIEW_REQUEST_ERROR",
                error_message=f"Invalid literature review request: {str(e)}"
            )
    
    async def _handle_code_generation(self, data: Dict[str, Any]) -> Union[CodeGenerationResponse, ErrorResponse]:
        """处理代码生成请求"""
        try:
            request = CodeGenerationRequest(**data)
            return await self.handler.handle_code_generation(request)
        except Exception as e:
            return create_error_response(
                error_code="CODE_GENERATION_REQUEST_ERROR",
                error_message=f"Invalid code generation request: {str(e)}"
            )
    
    async def _handle_workflow_get(self, data: Optional[Dict[str, Any]] = None) -> Union[APIResponse, ErrorResponse]:
        """获取工作流状态"""
        try:
            # 这里应该从数据库或缓存中获取工作流状态
            # 目前返回模拟数据
            workflow_state = WorkflowState(
                session_id=data.get("session_id", "default_session") if data else "default_session",
                current_node="identity_check"
            )
            
            return APIResponse(
                status=ResponseStatus.SUCCESS,
                request_id=data.get("request_id") if data else None
            )
        except Exception as e:
            return create_error_response(
                error_code="WORKFLOW_GET_ERROR",
                error_message=f"Failed to get workflow state: {str(e)}"
            )
    
    async def _handle_workflow_update(self, data: Dict[str, Any]) -> Union[APIResponse, ErrorResponse]:
        """更新工作流状态"""
        try:
            workflow_state = WorkflowState(**data)
            updated_state = await self.handler.handle_workflow_state(workflow_state)
            
            return APIResponse(
                status=ResponseStatus.SUCCESS,
                request_id=data.get("request_id")
            )
        except Exception as e:
            return create_error_response(
                error_code="WORKFLOW_UPDATE_ERROR",
                error_message=f"Failed to update workflow state: {str(e)}"
            )
    
    async def _handle_health_check(self, data: Optional[Dict[str, Any]] = None) -> HealthCheckResponse:
        """处理健康检查请求"""
        return await self.handler.health_check()
    
    async def _handle_ping(self, data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """处理ping请求"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            request_id=data.get("request_id") if data else None
        )
    
    async def _handle_root(self, data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """处理根路径请求"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            request_id=data.get("request_id") if data else None
        )
    
    async def _handle_api_info(self, data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """处理API信息请求"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            request_id=data.get("request_id") if data else None
        )
    
    def get_routes_info(self) -> Dict[str, Any]:
        """获取路由信息"""
        routes_info = {}
        for path, methods in self.routes.items():
            routes_info[path] = list(methods.keys())
        return routes_info
    
    def register_custom_route(self, path: str, method: str, handler: Callable, middleware: Optional[list] = None):
        """注册自定义路由"""
        self.add_route(path, method, handler)
        if middleware:
            for mw in middleware:
                self.add_middleware(mw)


# CORS中间件
async def cors_middleware(path: str, method: str, data: Optional[Dict[str, Any]], query_params: Optional[Dict[str, Any]]) -> Optional[APIResponse]:
    """CORS中间件"""
    # 这里可以添加CORS处理逻辑
    return None


# 认证中间件
async def auth_middleware(path: str, method: str, data: Optional[Dict[str, Any]], query_params: Optional[Dict[str, Any]]) -> Optional[APIResponse]:
    """认证中间件"""
    # 跳过健康检查和根路径的认证
    if path in ["/health", "/ping", "/", "/api"]:
        return None
    
    # 这里可以添加认证逻辑
    # 例如检查API密钥、JWT令牌等
    return None


# 日志中间件
async def logging_middleware(path: str, method: str, data: Optional[Dict[str, Any]], query_params: Optional[Dict[str, Any]]) -> Optional[APIResponse]:
    """日志中间件"""
    # 这里可以添加请求日志记录
    print(f"API Request: {method} {path}")
    return None


# 创建全局路由器实例
api_router = APIRouter()

# 添加中间件
api_router.add_middleware(cors_middleware)
api_router.add_middleware(auth_middleware)
api_router.add_middleware(logging_middleware)


# 便捷函数
def get_router() -> APIRouter:
    """获取API路由器实例"""
    return api_router


def register_route(path: str, method: str, handler: Callable):
    """注册路由的便捷函数"""
    api_router.add_route(path, method, handler)


def get_route_handler(path: str, method: str = "GET") -> Optional[Callable]:
    """获取路由处理器的便捷函数"""
    return api_router.get_route(path, method)