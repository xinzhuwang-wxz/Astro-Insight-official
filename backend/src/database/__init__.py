#!/usr/bin/env python3
"""
数据库模块
提供本地数据存储和API接口功能
"""

from .local_storage import (
    CelestialObject,
    ClassificationResult,
    ExecutionHistory,
    LocalDatabase,
    DataManager,
    data_manager,
)

from .api import DatabaseAPI, db_api

from .enhanced_schema import (
    EnhancedDatabaseSchema,
    QueryHistory,
    UserSession,
    PerformanceMetrics,
    DataSource,
    CacheEntry,
    ErrorLog,
    setup_enhanced_database,
    get_database_statistics,
)
from .migration import (
    DatabaseMigration,
    migrate_database,
    validate_database_migration,
    get_database_migration_info,
)

__all__ = [
    # 数据结构
    "CelestialObject",
    "ClassificationResult",
    "ExecutionHistory",
    # 数据库类
    "LocalDatabase",
    "DataManager",
    "DatabaseAPI",
    # 全局实例
    "data_manager",
    "db_api",
    # 增强模式
    "EnhancedDatabaseSchema",
    "QueryHistory",
    "UserSession",
    "PerformanceMetrics",
    "DataSource",
    "CacheEntry",
    "ErrorLog",
    "setup_enhanced_database",
    "get_database_statistics",
    # 数据库迁移
    "DatabaseMigration",
    "migrate_database",
    "validate_database_migration",
    "get_database_migration_info",
]

# 版本信息
__version__ = "1.0.0"
