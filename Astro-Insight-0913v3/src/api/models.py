#!/usr/bin/env python3
"""
API模型定义
包含所有API请求和响应的数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


# 枚举定义
class QueryType(Enum):
    """查询类型枚举"""
    CLASSIFICATION = "classification"
    DATA_RETRIEVAL = "data_retrieval"
    LITERATURE_REVIEW = "literature_review"
    CODE_GENERATION = "code_generation"
    QA = "qa"
    HEALTH_CHECK = "health_check"


class ResponseStatus(Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    PENDING = "pending"


class ConfidenceLevel(Enum):
    """置信度等级枚举"""
    VERY_HIGH = "very_high"  # >0.9
    HIGH = "high"           # 0.7-0.9
    MEDIUM = "medium"       # 0.5-0.7
    LOW = "low"             # 0.3-0.5
    VERY_LOW = "very_low"   # <0.3


class UserType(Enum):
    """用户类型枚举"""
    AMATEUR = "amateur"
    PROFESSIONAL = "professional"


class TaskType(Enum):
    """任务类型枚举"""
    CLASSIFICATION = "classification"
    DATA_RETRIEVAL = "data_retrieval"
    LITERATURE_REVIEW = "literature_review"
    CODE_GENERATION = "code_generation"


# 基础数据类
@dataclass
class APIRequest:
    """API请求基类"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class APIResponse:
    """API响应基类"""
    status: ResponseStatus
    request_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time: Optional[float] = None


# 天体对象数据类
@dataclass
class CelestialObject:
    """天体对象"""
    name: str
    object_type: str
    coordinates: Optional[Dict[str, float]] = None
    magnitude: Optional[float] = None
    distance: Optional[float] = None
    spectral_class: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassificationResult:
    """分类结果"""
    object_name: str
    object_type: str
    confidence: float
    confidence_level: ConfidenceLevel
    coordinates: Optional[Dict[str, float]] = None
    magnitude: Optional[float] = None
    distance: Optional[float] = None
    spectral_class: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "classification_engine"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 请求数据类
@dataclass
class ClassificationRequest(APIRequest):
    """分类请求"""
    query: str = ""
    language: str = "auto"
    include_metadata: bool = True
    confidence_threshold: float = 0.5
    max_results: int = 10


@dataclass
class BatchRequest(APIRequest):
    """批量请求"""
    queries: List[str] = field(default_factory=list)
    language: str = "auto"
    include_metadata: bool = True
    confidence_threshold: float = 0.5
    max_results_per_query: int = 10


@dataclass
class HistoryRequest(APIRequest):
    """历史记录请求"""
    limit: int = 50
    offset: int = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    query_type: Optional[QueryType] = None


@dataclass
class DataRetrievalRequest(APIRequest):
    """数据检索请求"""
    query: str = ""
    data_sources: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 100


@dataclass
class LiteratureReviewRequest(APIRequest):
    """文献综述请求"""
    topic: str = ""
    keywords: List[str] = field(default_factory=list)
    date_range: Optional[Dict[str, str]] = None
    max_papers: int = 50


@dataclass
class CodeGenerationRequest(APIRequest):
    """代码生成请求"""
    description: str = ""
    language: str = "python"
    framework: Optional[str] = None
    requirements: List[str] = field(default_factory=list)


# 响应数据类
@dataclass
class ClassificationResponse(APIResponse):
    """分类响应"""
    results: List[ClassificationResult] = field(default_factory=list)
    query: str = ""
    total_results: int = 0
    confidence_threshold: float = 0.5

    def __post_init__(self):
        if not self.total_results:
            self.total_results = len(self.results)


@dataclass
class BatchResponse(APIResponse):
    """批量响应"""
    results: List[ClassificationResponse] = field(default_factory=list)
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0

    def __post_init__(self):
        if not self.total_queries:
            self.total_queries = len(self.results)
            self.successful_queries = sum(1 for r in self.results if r.status == ResponseStatus.SUCCESS)
            self.failed_queries = self.total_queries - self.successful_queries


@dataclass
class HistoryEntry:
    """历史记录条目"""
    id: int
    query: str
    query_type: QueryType
    results_count: int
    timestamp: str
    execution_time: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class HistoryResponse(APIResponse):
    """历史记录响应"""
    entries: List[HistoryEntry] = field(default_factory=list)
    total_count: int = 0
    limit: int = 50
    offset: int = 0

    def __post_init__(self):
        if not self.total_count:
            self.total_count = len(self.entries)


@dataclass
class DataRetrievalResponse(APIResponse):
    """数据检索响应"""
    data: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    sources: List[str] = field(default_factory=list)
    query: str = ""


@dataclass
class LiteratureReviewResponse(APIResponse):
    """文献综述响应"""
    summary: str = ""
    papers: List[Dict[str, Any]] = field(default_factory=list)
    total_papers: int = 0
    topic: str = ""


@dataclass
class CodeGenerationResponse(APIResponse):
    """代码生成响应"""
    code: str = ""
    language: str = "python"
    dependencies: List[str] = field(default_factory=list)
    documentation: str = ""
    test_code: Optional[str] = None


@dataclass
class HealthCheckResponse(APIResponse):
    """健康检查响应"""
    service_status: str = "unknown"
    database_status: str = "unknown"
    api_version: str = "1.0.0"
    uptime: float = 0.0
    memory_usage: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorResponse(APIResponse):
    """错误响应"""
    error_code: str = ""
    error_message: str = ""
    error_details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.status = ResponseStatus.ERROR


# 工作流状态数据类
@dataclass
class WorkflowState:
    """工作流状态"""
    session_id: str
    user_type: Optional[UserType] = None
    task_type: Optional[TaskType] = None
    current_node: str = "identity_check"
    user_input: str = ""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 辅助函数
def create_error_response(
    error_code: str,
    error_message: str,
    request_id: Optional[str] = None,
    error_details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """创建错误响应"""
    return ErrorResponse(
        status=ResponseStatus.ERROR,
        request_id=request_id,
        error_code=error_code,
        error_message=error_message,
        error_details=error_details or {}
    )


def create_success_response(
    data: Any,
    request_id: Optional[str] = None,
    execution_time: Optional[float] = None
) -> APIResponse:
    """创建成功响应"""
    if isinstance(data, list) and data and isinstance(data[0], ClassificationResult):
        return ClassificationResponse(
            status=ResponseStatus.SUCCESS,
            request_id=request_id,
            execution_time=execution_time,
            results=data,
            query="",
            confidence_threshold=0.5
        )
    else:
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            request_id=request_id,
            execution_time=execution_time
        )


def get_confidence_level(confidence: float) -> ConfidenceLevel:
    """根据置信度数值获取置信度等级"""
    if confidence >= 0.9:
        return ConfidenceLevel.VERY_HIGH
    elif confidence >= 0.7:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.5:
        return ConfidenceLevel.MEDIUM
    elif confidence >= 0.3:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.VERY_LOW