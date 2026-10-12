#!/usr/bin/env python3
"""
Astro Insight 项目主模块
提供天体分类检索的完整功能套件
"""

# 核心工具模块 - 暂时注释掉未使用的模块
# from .tools import (
#     # 语言检测和翻译
#     language_processor,
#     translate_text,
#     LanguageDetectionResult,
#     TranslationResult,
#     # 天体名称提取
#     enhanced_name_extractor,
#     extract_celestial_names,
#     ExtractedCelestialObject,
#     # 并发查询
#     query_manager,
#     celestial_query_engine,
#     QueryResult,
#     ConcurrentQueryManager,
#     # 缓存管理
#     cache_manager,
#     CacheEntry,
#     LRUCache,
#     CacheManager,
#     # 错误处理
#     error_handler,
#     with_retry,
#     ErrorCategory,
#     RetryConfig,
#     ErrorHandler,
# )

# 数据库模块
from .database import (
    DatabaseAPI,
    QueryHistory,
    UserSession,
    PerformanceMetrics,
    EnhancedDatabaseSchema,
    DatabaseMigration,
    migrate_database,
    get_database_migration_info,
    setup_enhanced_database,
    get_database_statistics,
)

# 模板模块
from .templates import (
    ClassificationRequest,
    ClassificationResult,
    EnhancedClassificationEngine,
    get_classification_engine,
    create_classification_template,
)

# 历史记录模块
from .history import (
    QueryHistoryEntry,
    QueryStatistics,
    UserQueryProfile,
    QueryHistoryManager,
    query_history_manager,
    record_query,
    get_user_query_history,
    get_recent_queries,
    find_similar_queries,
)

# API模块
from .api import (
    QueryType,
    ResponseStatus,
    ConfidenceLevel,
    APIRequest,
    ClassificationRequest,
    BatchRequest,
    HistoryRequest,
    APIResponse,
    ClassificationResponse,
    BatchResponse,
    HistoryResponse,
    HealthCheckResponse,
    ErrorResponse,
    CelestialObject,
    ClassificationResult,
    APIRouter,
    api_router,
    handle_api_request,
    handle_classification_request,
    handle_batch_request,
    handle_history_request,
    handle_health_check,
)

__all__ = [
    # 工具模块 - 已移除翻译相关功能
    "enhanced_name_extractor",
    "extract_celestial_names",
    "ExtractedCelestialObject",
    "query_manager",
    "celestial_query_engine",
    "QueryResult",
    "ConcurrentQueryManager",
    "cache_manager",
    "CacheEntry",
    "LRUCache",
    "CacheManager",
    "error_handler",
    "with_retry",
    "ErrorCategory",
    "RetryConfig",
    "ErrorHandler",
    # 数据库模块
    "DatabaseAPI",
    "QueryHistory",
    "UserSession",
    "PerformanceMetrics",
    "EnhancedDatabaseSchema",
    "DatabaseMigration",
    "migrate_database",
    "get_database_migration_info",
    "setup_enhanced_database",
    "get_database_statistics",
    # 模板模块
    "ClassificationRequest",
    "ClassificationResult",
    "EnhancedClassificationEngine",
    "get_classification_engine",
    "create_classification_template",
    # 历史记录模块
    "QueryHistoryEntry",
    "QueryStatistics",
    "UserQueryProfile",
    "QueryHistoryManager",
    "query_history_manager",
    "record_query",
    "get_user_query_history",
    "get_recent_queries",
    "find_similar_queries",
    # API模块
    "QueryType",
    "ResponseStatus",
    "ConfidenceLevel",
    "APIRequest",
    "ClassificationRequest",
    "BatchRequest",
    "HistoryRequest",
    "APIResponse",
    "ClassificationResponse",
    "BatchResponse",
    "HistoryResponse",
    "HealthCheckResponse",
    "ErrorResponse",
    "CelestialObject",
    "ClassificationResult",
    "APIRouter",
    "api_router",
    "handle_api_request",
    "handle_classification_request",
    "handle_batch_request",
    "handle_history_request",
    "handle_health_check",
]

__version__ = "2.0.0"
__author__ = "Astro Insight Team"
__description__ = "Enhanced Astronomical Object Classification and Retrieval System"

# 便捷导入别名
from .database import DatabaseAPI as DB