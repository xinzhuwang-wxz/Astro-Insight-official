#!/usr/bin/env python3
"""
增强的数据库表结构和索引优化
扩展现有数据库架构，添加新的表和优化索引
"""

import sqlite3
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class QueryHistory:
    """查询历史记录"""

    id: Optional[int] = None
    user_id: Optional[str] = None
    session_id: str = ""
    query_text: str = ""
    query_type: str = ""  # search, classification, analysis
    query_params: Dict[str, Any] = field(default_factory=dict)
    results_count: int = 0
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    cache_hit: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UserSession:
    """用户会话记录"""

    id: Optional[int] = None
    session_id: str = ""
    user_id: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_execution_time: float = 0.0
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """性能指标记录"""

    id: Optional[int] = None
    metric_type: str = ""  # query_time, cache_hit_rate, error_rate
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""  # seconds, percentage, count
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DataSource:
    """数据源配置"""

    id: Optional[int] = None
    name: str = ""
    source_type: str = ""  # api, database, file
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    connection_params: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    last_accessed: Optional[str] = None
    success_rate: float = 100.0
    average_response_time: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CacheEntry:
    """缓存条目记录"""

    id: Optional[int] = None
    cache_key: str = ""
    cache_type: str = ""  # query, object, classification
    data_size: int = 0  # bytes
    hit_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ErrorLog:
    """错误日志记录"""

    id: Optional[int] = None
    error_type: str = ""
    error_category: str = ""
    error_severity: str = ""
    error_message: str = ""
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class EnhancedDatabaseSchema:
    """增强的数据库架构管理器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def create_enhanced_tables(self):
        """创建增强的数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建查询历史表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    query_params TEXT,  -- JSON格式
                    results_count INTEGER DEFAULT 0,
                    execution_time REAL DEFAULT 0.0,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    cache_hit BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """
            )

            # 创建用户会话表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_queries INTEGER DEFAULT 0,
                    successful_queries INTEGER DEFAULT 0,
                    failed_queries INTEGER DEFAULT 0,
                    total_execution_time REAL DEFAULT 0.0,
                    user_agent TEXT,
                    ip_address TEXT,
                    metadata TEXT  -- JSON格式
                )
            """
            )

            # 创建性能指标表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    context TEXT,  -- JSON格式
                    timestamp TEXT NOT NULL
                )
            """
            )

            # 创建数据源配置表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    source_type TEXT NOT NULL,
                    endpoint_url TEXT,
                    api_key TEXT,
                    connection_params TEXT,  -- JSON格式
                    is_active BOOLEAN DEFAULT 1,
                    last_accessed TEXT,
                    success_rate REAL DEFAULT 100.0,
                    average_response_time REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )

            # 创建缓存条目表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_type TEXT NOT NULL,
                    data_size INTEGER DEFAULT 0,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed TEXT NOT NULL,
                    expires_at TEXT,
                    created_at TEXT NOT NULL
                )
            """
            )

            # 创建错误日志表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_category TEXT NOT NULL,
                    error_severity TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,  -- JSON格式
                    user_id TEXT,
                    session_id TEXT,
                    resolved BOOLEAN DEFAULT 0,
                    resolution_notes TEXT,
                    created_at TEXT NOT NULL
                )
            """
            )

            # 扩展现有天体对象表
            cursor.execute(
                """
                ALTER TABLE celestial_objects ADD COLUMN source_catalog TEXT DEFAULT 'manual'
            """
            )

            cursor.execute(
                """
                ALTER TABLE celestial_objects ADD COLUMN data_quality_score REAL DEFAULT 1.0
            """
            )

            cursor.execute(
                """
                ALTER TABLE celestial_objects ADD COLUMN last_updated TEXT
            """
            )

            cursor.execute(
                """
                ALTER TABLE celestial_objects ADD COLUMN observation_count INTEGER DEFAULT 0
            """
            )

            conn.commit()
            self.logger.info("增强数据库表结构创建完成")

    def create_enhanced_indexes(self):
        """创建增强的数据库索引"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 现有表的新索引
            indexes = [
                # 天体对象表索引
                "CREATE INDEX IF NOT EXISTS idx_objects_coordinates ON celestial_objects(coordinates)",
                "CREATE INDEX IF NOT EXISTS idx_objects_magnitude ON celestial_objects(magnitude)",
                "CREATE INDEX IF NOT EXISTS idx_objects_spectral ON celestial_objects(spectral_class)",
                "CREATE INDEX IF NOT EXISTS idx_objects_distance ON celestial_objects(distance)",
                "CREATE INDEX IF NOT EXISTS idx_objects_source ON celestial_objects(source_catalog)",
                "CREATE INDEX IF NOT EXISTS idx_objects_quality ON celestial_objects(data_quality_score)",
                "CREATE INDEX IF NOT EXISTS idx_objects_updated ON celestial_objects(last_updated)",
                "CREATE INDEX IF NOT EXISTS idx_objects_composite ON celestial_objects(object_type, magnitude, spectral_class)",
                # 分类结果表索引
                "CREATE INDEX IF NOT EXISTS idx_results_classification ON classification_results(classification)",
                "CREATE INDEX IF NOT EXISTS idx_results_confidence ON classification_results(confidence)",
                "CREATE INDEX IF NOT EXISTS idx_results_method ON classification_results(method)",
                "CREATE INDEX IF NOT EXISTS idx_results_created ON classification_results(created_at)",
                # 执行历史表索引
                "CREATE INDEX IF NOT EXISTS idx_history_status ON execution_history(status)",
                "CREATE INDEX IF NOT EXISTS idx_history_time ON execution_history(execution_time)",
                "CREATE INDEX IF NOT EXISTS idx_history_created ON execution_history(created_at)",
                # 查询历史表索引
                "CREATE INDEX IF NOT EXISTS idx_query_user ON query_history(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_query_session ON query_history(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_query_type ON query_history(query_type)",
                "CREATE INDEX IF NOT EXISTS idx_query_success ON query_history(success)",
                "CREATE INDEX IF NOT EXISTS idx_query_cache ON query_history(cache_hit)",
                "CREATE INDEX IF NOT EXISTS idx_query_created ON query_history(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_query_execution_time ON query_history(execution_time)",
                # 用户会话表索引
                "CREATE INDEX IF NOT EXISTS idx_session_user ON user_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_session_start ON user_sessions(start_time)",
                "CREATE INDEX IF NOT EXISTS idx_session_end ON user_sessions(end_time)",
                # 性能指标表索引
                "CREATE INDEX IF NOT EXISTS idx_metrics_type ON performance_metrics(metric_type)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_name ON performance_metrics(metric_name)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)",
                # 数据源表索引
                "CREATE INDEX IF NOT EXISTS idx_sources_type ON data_sources(source_type)",
                "CREATE INDEX IF NOT EXISTS idx_sources_active ON data_sources(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_sources_accessed ON data_sources(last_accessed)",
                # 缓存条目表索引
                "CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_entries(cache_type)",
                "CREATE INDEX IF NOT EXISTS idx_cache_accessed ON cache_entries(last_accessed)",
                "CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at)",
                "CREATE INDEX IF NOT EXISTS idx_cache_hits ON cache_entries(hit_count)",
                # 错误日志表索引
                "CREATE INDEX IF NOT EXISTS idx_error_type ON error_logs(error_type)",
                "CREATE INDEX IF NOT EXISTS idx_error_category ON error_logs(error_category)",
                "CREATE INDEX IF NOT EXISTS idx_error_severity ON error_logs(error_severity)",
                "CREATE INDEX IF NOT EXISTS idx_error_resolved ON error_logs(resolved)",
                "CREATE INDEX IF NOT EXISTS idx_error_session ON error_logs(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_error_created ON error_logs(created_at)",
            ]

            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        self.logger.warning(f"创建索引时出现警告: {e}")

            conn.commit()
            self.logger.info("增强数据库索引创建完成")

    def create_views(self):
        """创建数据库视图"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 天体对象统计视图
            cursor.execute(
                """
                CREATE VIEW IF NOT EXISTS v_object_statistics AS
                SELECT 
                    object_type,
                    COUNT(*) as total_count,
                    AVG(magnitude) as avg_magnitude,
                    MIN(magnitude) as min_magnitude,
                    MAX(magnitude) as max_magnitude,
                    AVG(data_quality_score) as avg_quality,
                    COUNT(CASE WHEN spectral_class IS NOT NULL THEN 1 END) as with_spectral_class
                FROM celestial_objects
                GROUP BY object_type
            """
            )

            # 查询性能统计视图
            cursor.execute(
                """
                CREATE VIEW IF NOT EXISTS v_query_performance AS
                SELECT 
                    query_type,
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_queries,
                    AVG(execution_time) as avg_execution_time,
                    MAX(execution_time) as max_execution_time,
                    SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits,
                    ROUND(100.0 * SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as cache_hit_rate
                FROM query_history
                GROUP BY query_type
            """
            )

            # 用户活动统计视图
            cursor.execute(
                """
                CREATE VIEW IF NOT EXISTS v_user_activity AS
                SELECT 
                    user_id,
                    COUNT(DISTINCT session_id) as total_sessions,
                    SUM(total_queries) as total_queries,
                    SUM(successful_queries) as successful_queries,
                    AVG(total_execution_time) as avg_session_time,
                    MAX(start_time) as last_activity
                FROM user_sessions
                WHERE user_id IS NOT NULL
                GROUP BY user_id
            """
            )

            # 错误趋势视图
            cursor.execute(
                """
                CREATE VIEW IF NOT EXISTS v_error_trends AS
                SELECT 
                    DATE(created_at) as error_date,
                    error_category,
                    error_severity,
                    COUNT(*) as error_count,
                    SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) as resolved_count
                FROM error_logs
                GROUP BY DATE(created_at), error_category, error_severity
                ORDER BY error_date DESC
            """
            )

            conn.commit()
            self.logger.info("数据库视图创建完成")

    def optimize_database(self):
        """优化数据库性能"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 分析表统计信息
            cursor.execute("ANALYZE")

            # 重建索引
            cursor.execute("REINDEX")

            # 清理数据库
            cursor.execute("VACUUM")

            # 设置性能优化参数
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = 10000")
            cursor.execute("PRAGMA temp_store = MEMORY")
            cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB

            conn.commit()
            self.logger.info("数据库优化完成")

    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 获取表信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # 获取索引信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]

            # 获取视图信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [row[0] for row in cursor.fetchall()]

            # 获取数据库大小
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size = page_count * page_size

            # 获取表行数统计
            table_stats = {}
            for table in tables:
                if not table.startswith("sqlite_"):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_stats[table] = cursor.fetchone()[0]

            return {
                "tables": tables,
                "indexes": indexes,
                "views": views,
                "database_size_bytes": db_size,
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "table_statistics": table_stats,
            }


# 便捷函数
def setup_enhanced_database(db_path: str) -> EnhancedDatabaseSchema:
    """设置增强数据库"""
    schema = EnhancedDatabaseSchema(db_path)
    schema.create_enhanced_tables()
    schema.create_enhanced_indexes()
    schema.create_views()
    schema.optimize_database()
    return schema


def get_database_statistics(db_path: str) -> Dict[str, Any]:
    """获取数据库统计信息"""
    schema = EnhancedDatabaseSchema(db_path)
    return schema.get_database_info()
