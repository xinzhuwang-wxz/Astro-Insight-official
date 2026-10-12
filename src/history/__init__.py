#!/usr/bin/env python3
"""
查询历史记录模块
提供查询历史的记录、检索、分析和管理功能
"""

from .query_history_manager import (
    # 数据结构
    QueryHistoryEntry,
    QueryStatistics,
    UserQueryProfile,
    # 核心管理器
    QueryHistoryManager,
    query_history_manager,
    # 便捷函数
    record_query,
    get_user_query_history,
    get_recent_queries,
    find_similar_queries,
)

__all__ = [
    # 数据结构
    "QueryHistoryEntry",
    "QueryStatistics",
    "UserQueryProfile",
    # 核心管理器
    "QueryHistoryManager",
    "query_history_manager",
    # 便捷函数
    "record_query",
    "get_user_query_history",
    "get_recent_queries",
    "find_similar_queries",
]

__version__ = "1.0.0"
__author__ = "Astro Insight Team"
__description__ = "查询历史记录管理系统"
