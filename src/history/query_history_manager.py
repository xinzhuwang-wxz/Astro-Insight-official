#!/usr/bin/env python3
"""
查询历史记录管理模块
提供查询历史的记录、检索、分析和管理功能
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path


@dataclass
class QueryHistoryEntry:
    """查询历史条目"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_text: str = ""
    query_type: str = "general"  # general, classification, search, analysis
    query_language: Optional[str] = None
    translated_query: Optional[str] = None
    extracted_names: List[str] = field(default_factory=list)
    search_parameters: Dict[str, Any] = field(default_factory=dict)
    results_count: int = 0
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    cache_hit: bool = False
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    user_feedback: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QueryStatistics:
    """查询统计信息"""

    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_execution_time: float = 0.0
    cache_hit_rate: float = 0.0
    most_common_query_types: List[Tuple[str, int]] = field(default_factory=list)
    most_active_users: List[Tuple[str, int]] = field(default_factory=list)
    query_trends: Dict[str, List[int]] = field(default_factory=dict)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class UserQueryProfile:
    """用户查询档案"""

    user_id: str
    total_queries: int = 0
    successful_queries: int = 0
    favorite_query_types: List[str] = field(default_factory=list)
    average_execution_time: float = 0.0
    most_searched_objects: List[str] = field(default_factory=list)
    preferred_language: Optional[str] = None
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())
    query_patterns: Dict[str, Any] = field(default_factory=dict)


class QueryHistoryManager:
    """查询历史管理器"""

    def __init__(self, db_path: str = "query_history.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 创建查询历史表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS query_history (
                        id TEXT PRIMARY KEY,
                        user_id TEXT,
                        session_id TEXT NOT NULL,
                        query_text TEXT NOT NULL,
                        query_type TEXT DEFAULT 'general',
                        query_language TEXT,
                        translated_query TEXT,
                        extracted_names TEXT,  -- JSON array
                        search_parameters TEXT,  -- JSON object
                        results_count INTEGER DEFAULT 0,
                        execution_time REAL DEFAULT 0.0,
                        success BOOLEAN DEFAULT 1,
                        error_message TEXT,
                        cache_hit BOOLEAN DEFAULT 0,
                        performance_metrics TEXT,  -- JSON object
                        user_feedback TEXT,  -- JSON object
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """
                )

                # 创建用户档案表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        total_queries INTEGER DEFAULT 0,
                        successful_queries INTEGER DEFAULT 0,
                        favorite_query_types TEXT,  -- JSON array
                        average_execution_time REAL DEFAULT 0.0,
                        most_searched_objects TEXT,  -- JSON array
                        preferred_language TEXT,
                        last_active TEXT NOT NULL,
                        query_patterns TEXT,  -- JSON object
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """
                )

                # 创建会话表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS query_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        total_queries INTEGER DEFAULT 0,
                        session_duration REAL DEFAULT 0.0,
                        session_metadata TEXT,  -- JSON object
                        created_at TEXT NOT NULL
                    )
                """
                )

                # 创建索引
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query_user_id ON query_history(user_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query_session_id ON query_history(session_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query_type ON query_history(query_type)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query_created_at ON query_history(created_at)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query_success ON query_history(success)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_session_user_id ON query_sessions(user_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_session_start_time ON query_sessions(start_time)"
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise

    def add_query_history(self, entry: QueryHistoryEntry) -> bool:
        """添加查询历史记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO query_history (
                        id, user_id, session_id, query_text, query_type,
                        query_language, translated_query, extracted_names,
                        search_parameters, results_count, execution_time,
                        success, error_message, cache_hit, performance_metrics,
                        user_feedback, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        entry.id,
                        entry.user_id,
                        entry.session_id,
                        entry.query_text,
                        entry.query_type,
                        entry.query_language,
                        entry.translated_query,
                        json.dumps(entry.extracted_names),
                        json.dumps(entry.search_parameters),
                        entry.results_count,
                        entry.execution_time,
                        entry.success,
                        entry.error_message,
                        entry.cache_hit,
                        json.dumps(entry.performance_metrics),
                        json.dumps(entry.user_feedback)
                        if entry.user_feedback
                        else None,
                        entry.created_at,
                        entry.updated_at,
                    ),
                )

                conn.commit()

                # 更新用户档案
                if entry.user_id:
                    self._update_user_profile(entry)

                return True

        except Exception as e:
            self.logger.error(f"添加查询历史失败: {e}")
            return False

    def get_query_history(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        query_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[QueryHistoryEntry]:
        """获取查询历史记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 构建查询条件
                conditions = []
                params = []

                if user_id:
                    conditions.append("user_id = ?")
                    params.append(user_id)

                if session_id:
                    conditions.append("session_id = ?")
                    params.append(session_id)

                if query_type:
                    conditions.append("query_type = ?")
                    params.append(query_type)

                if start_date:
                    conditions.append("created_at >= ?")
                    params.append(start_date.isoformat())

                if end_date:
                    conditions.append("created_at <= ?")
                    params.append(end_date.isoformat())

                if success_only:
                    conditions.append("success = 1")

                where_clause = " AND ".join(conditions) if conditions else "1=1"

                query = f"""
                    SELECT * FROM query_history 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """

                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # 转换为QueryHistoryEntry对象
                entries = []
                for row in rows:
                    entry = QueryHistoryEntry(
                        id=row[0],
                        user_id=row[1],
                        session_id=row[2],
                        query_text=row[3],
                        query_type=row[4],
                        query_language=row[5],
                        translated_query=row[6],
                        extracted_names=json.loads(row[7]) if row[7] else [],
                        search_parameters=json.loads(row[8]) if row[8] else {},
                        results_count=row[9],
                        execution_time=row[10],
                        success=bool(row[11]),
                        error_message=row[12],
                        cache_hit=bool(row[13]),
                        performance_metrics=json.loads(row[14]) if row[14] else {},
                        user_feedback=json.loads(row[15]) if row[15] else None,
                        created_at=row[16],
                        updated_at=row[17],
                    )
                    entries.append(entry)

                return entries

        except Exception as e:
            self.logger.error(f"获取查询历史失败: {e}")
            return []

    def get_query_statistics(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> QueryStatistics:
        """获取查询统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 构建基础查询条件
                conditions = []
                params = []

                if user_id:
                    conditions.append("user_id = ?")
                    params.append(user_id)

                if start_date:
                    conditions.append("created_at >= ?")
                    params.append(start_date.isoformat())

                if end_date:
                    conditions.append("created_at <= ?")
                    params.append(end_date.isoformat())

                where_clause = " AND ".join(conditions) if conditions else "1=1"

                # 基础统计
                cursor.execute(
                    f"""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        AVG(execution_time) as avg_time,
                        AVG(CASE WHEN cache_hit = 1 THEN 1.0 ELSE 0.0 END) as cache_rate
                    FROM query_history WHERE {where_clause}
                """,
                    params,
                )

                row = cursor.fetchone()
                total_queries = row[0] or 0
                successful_queries = row[1] or 0
                failed_queries = total_queries - successful_queries
                avg_execution_time = row[2] or 0.0
                cache_hit_rate = row[3] or 0.0

                # 查询类型统计
                cursor.execute(
                    f"""
                    SELECT query_type, COUNT(*) as count
                    FROM query_history WHERE {where_clause}
                    GROUP BY query_type
                    ORDER BY count DESC
                    LIMIT 10
                """,
                    params,
                )

                most_common_query_types = cursor.fetchall()

                # 活跃用户统计（如果不是特定用户查询）
                most_active_users = []
                if not user_id:
                    cursor.execute(
                        f"""
                        SELECT user_id, COUNT(*) as count
                        FROM query_history WHERE {where_clause} AND user_id IS NOT NULL
                        GROUP BY user_id
                        ORDER BY count DESC
                        LIMIT 10
                    """,
                        params,
                    )

                    most_active_users = cursor.fetchall()

                return QueryStatistics(
                    total_queries=total_queries,
                    successful_queries=successful_queries,
                    failed_queries=failed_queries,
                    average_execution_time=avg_execution_time,
                    cache_hit_rate=cache_hit_rate,
                    most_common_query_types=most_common_query_types,
                    most_active_users=most_active_users,
                )

        except Exception as e:
            self.logger.error(f"获取查询统计失败: {e}")
            return QueryStatistics()

    def get_user_profile(self, user_id: str) -> Optional[UserQueryProfile]:
        """获取用户查询档案"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM user_profiles WHERE user_id = ?
                """,
                    (user_id,),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                return UserQueryProfile(
                    user_id=row[0],
                    total_queries=row[1],
                    successful_queries=row[2],
                    favorite_query_types=json.loads(row[3]) if row[3] else [],
                    average_execution_time=row[4],
                    most_searched_objects=json.loads(row[5]) if row[5] else [],
                    preferred_language=row[6],
                    last_active=row[7],
                    query_patterns=json.loads(row[8]) if row[8] else {},
                )

        except Exception as e:
            self.logger.error(f"获取用户档案失败: {e}")
            return None

    def _update_user_profile(self, entry: QueryHistoryEntry):
        """更新用户档案"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 获取现有档案或创建新档案
                cursor.execute(
                    """
                    SELECT * FROM user_profiles WHERE user_id = ?
                """,
                    (entry.user_id,),
                )

                existing = cursor.fetchone()

                if existing:
                    # 更新现有档案
                    total_queries = existing[1] + 1
                    successful_queries = existing[2] + (1 if entry.success else 0)

                    # 计算新的平均执行时间
                    old_avg = existing[4]
                    new_avg = (
                        (old_avg * existing[1]) + entry.execution_time
                    ) / total_queries

                    cursor.execute(
                        """
                        UPDATE user_profiles SET
                            total_queries = ?,
                            successful_queries = ?,
                            average_execution_time = ?,
                            last_active = ?,
                            updated_at = ?
                        WHERE user_id = ?
                    """,
                        (
                            total_queries,
                            successful_queries,
                            new_avg,
                            entry.created_at,
                            datetime.now().isoformat(),
                            entry.user_id,
                        ),
                    )
                else:
                    # 创建新档案
                    cursor.execute(
                        """
                        INSERT INTO user_profiles (
                            user_id, total_queries, successful_queries,
                            favorite_query_types, average_execution_time,
                            most_searched_objects, preferred_language,
                            last_active, query_patterns, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            entry.user_id,
                            1,
                            1 if entry.success else 0,
                            json.dumps([entry.query_type]),
                            entry.execution_time,
                            json.dumps(entry.extracted_names),
                            entry.query_language,
                            entry.created_at,
                            json.dumps({}),
                            datetime.now().isoformat(),
                            datetime.now().isoformat(),
                        ),
                    )

                conn.commit()

        except Exception as e:
            self.logger.error(f"更新用户档案失败: {e}")

    def search_similar_queries(
        self, query_text: str, user_id: Optional[str] = None, limit: int = 10
    ) -> List[QueryHistoryEntry]:
        """搜索相似查询"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 简单的文本相似性搜索（可以改进为更复杂的算法）
                conditions = ["query_text LIKE ?"]
                params = [f"%{query_text}%"]

                if user_id:
                    conditions.append("user_id = ?")
                    params.append(user_id)

                where_clause = " AND ".join(conditions)

                cursor.execute(
                    f"""
                    SELECT * FROM query_history
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    params + [limit],
                )

                rows = cursor.fetchall()

                # 转换为QueryHistoryEntry对象
                entries = []
                for row in rows:
                    entry = QueryHistoryEntry(
                        id=row[0],
                        user_id=row[1],
                        session_id=row[2],
                        query_text=row[3],
                        query_type=row[4],
                        query_language=row[5],
                        translated_query=row[6],
                        extracted_names=json.loads(row[7]) if row[7] else [],
                        search_parameters=json.loads(row[8]) if row[8] else {},
                        results_count=row[9],
                        execution_time=row[10],
                        success=bool(row[11]),
                        error_message=row[12],
                        cache_hit=bool(row[13]),
                        performance_metrics=json.loads(row[14]) if row[14] else {},
                        user_feedback=json.loads(row[15]) if row[15] else None,
                        created_at=row[16],
                        updated_at=row[17],
                    )
                    entries.append(entry)

                return entries

        except Exception as e:
            self.logger.error(f"搜索相似查询失败: {e}")
            return []

    def add_user_feedback(self, query_id: str, feedback: Dict[str, Any]) -> bool:
        """添加用户反馈"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE query_history SET
                        user_feedback = ?,
                        updated_at = ?
                    WHERE id = ?
                """,
                    (json.dumps(feedback), datetime.now().isoformat(), query_id),
                )

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"添加用户反馈失败: {e}")
            return False

    def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """清理旧记录"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM query_history
                    WHERE created_at < ?
                """,
                    (cutoff_date.isoformat(),),
                )

                deleted_count = cursor.rowcount
                conn.commit()

                self.logger.info(f"清理了 {deleted_count} 条旧记录")
                return deleted_count

        except Exception as e:
            self.logger.error(f"清理旧记录失败: {e}")
            return 0

    def export_history(
        self,
        output_path: str,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
    ) -> bool:
        """导出查询历史"""
        try:
            entries = self.get_query_history(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                limit=10000,  # 大量导出
            )

            if format.lower() == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [asdict(entry) for entry in entries],
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )
            else:
                raise ValueError(f"不支持的导出格式: {format}")

            return True

        except Exception as e:
            self.logger.error(f"导出查询历史失败: {e}")
            return False


# 全局实例
query_history_manager = QueryHistoryManager()


# 便捷函数
def record_query(
    query_text: str,
    query_type: str = "general",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs,
) -> str:
    """记录查询历史"""
    entry = QueryHistoryEntry(
        query_text=query_text,
        query_type=query_type,
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        **kwargs,
    )

    query_history_manager.add_query_history(entry)
    return entry.id


def get_user_query_history(user_id: str, limit: int = 50) -> List[QueryHistoryEntry]:
    """获取用户查询历史"""
    return query_history_manager.get_query_history(user_id=user_id, limit=limit)


def get_recent_queries(hours: int = 24, limit: int = 100) -> List[QueryHistoryEntry]:
    """获取最近查询"""
    start_date = datetime.now() - timedelta(hours=hours)
    return query_history_manager.get_query_history(start_date=start_date, limit=limit)


def find_similar_queries(
    query_text: str, user_id: Optional[str] = None
) -> List[QueryHistoryEntry]:
    """查找相似查询"""
    return query_history_manager.search_similar_queries(query_text, user_id)
