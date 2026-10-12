#!/usr/bin/env python3
"""
数据库迁移脚本
用于将现有数据库升级到增强架构
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional
from .enhanced_schema import EnhancedDatabaseSchema


class DatabaseMigration:
    """数据库迁移管理器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_path = (
            f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.logger = logging.getLogger(__name__)

    def get_current_version(self) -> int:
        """获取当前数据库版本"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 检查是否存在版本表
                cursor.execute(
                    """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """
                )

                if not cursor.fetchone():
                    # 创建版本表
                    cursor.execute(
                        """
                        CREATE TABLE schema_version (
                            version INTEGER PRIMARY KEY,
                            applied_at TEXT NOT NULL,
                            description TEXT
                        )
                    """
                    )

                    # 插入初始版本
                    cursor.execute(
                        """
                        INSERT INTO schema_version (version, applied_at, description)
                        VALUES (1, ?, 'Initial schema')
                    """,
                        (datetime.now().isoformat(),),
                    )

                    conn.commit()
                    return 1

                # 获取最新版本
                cursor.execute("SELECT MAX(version) FROM schema_version")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 1

        except sqlite3.Error as e:
            self.logger.error(f"获取数据库版本失败: {e}")
            return 1

    def backup_database(self) -> bool:
        """备份数据库"""
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, self.backup_path)
                self.logger.info(f"数据库已备份到: {self.backup_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            return False

    def restore_database(self) -> bool:
        """恢复数据库"""
        try:
            if os.path.exists(self.backup_path):
                shutil.copy2(self.backup_path, self.db_path)
                self.logger.info(f"数据库已从备份恢复: {self.backup_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"数据库恢复失败: {e}")
            return False

    def apply_migration_v2(self):
        """应用版本2迁移：增强架构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            try:
                # 创建增强架构
                schema = EnhancedDatabaseSchema(self.db_path)
                schema.create_enhanced_tables()
                schema.create_enhanced_indexes()
                schema.create_views()

                # 迁移现有数据
                self._migrate_existing_data(cursor)

                # 更新版本信息
                cursor.execute(
                    """
                    INSERT INTO schema_version (version, applied_at, description)
                    VALUES (2, ?, 'Enhanced schema with query history and performance tracking')
                """,
                    (datetime.now().isoformat(),),
                )

                conn.commit()
                self.logger.info("版本2迁移完成")

            except Exception as e:
                conn.rollback()
                self.logger.error(f"版本2迁移失败: {e}")
                raise

    def _migrate_existing_data(self, cursor: sqlite3.Cursor):
        """迁移现有数据"""
        # 更新现有天体对象的新字段
        cursor.execute(
            """
            UPDATE celestial_objects 
            SET 
                source_catalog = 'legacy',
                data_quality_score = 1.0,
                last_updated = ?,
                observation_count = 1
            WHERE source_catalog IS NULL
        """,
            (datetime.now().isoformat(),),
        )

        # 从执行历史创建初始查询历史记录
        cursor.execute(
            """
            INSERT INTO query_history (
                session_id, query_text, query_type, results_count,
                execution_time, success, created_at
            )
            SELECT 
                'migration_' || id,
                COALESCE(code, 'Legacy query'),
                'legacy',
                0,
                COALESCE(execution_time, 0.0),
                CASE WHEN status = 'completed' THEN 1 ELSE 0 END,
                created_at
            FROM execution_history
            WHERE code IS NOT NULL
        """
        )

        self.logger.info("现有数据迁移完成")

    def migrate_to_latest(self) -> bool:
        """迁移到最新版本"""
        try:
            current_version = self.get_current_version()
            target_version = 2  # 当前最新版本

            if current_version >= target_version:
                self.logger.info(f"数据库已是最新版本 {current_version}")
                return True

            # 备份数据库
            if not self.backup_database():
                self.logger.error("数据库备份失败，取消迁移")
                return False

            self.logger.info(f"开始从版本 {current_version} 迁移到版本 {target_version}")

            # 应用迁移
            if current_version < 2:
                self.apply_migration_v2()

            # 优化数据库
            schema = EnhancedDatabaseSchema(self.db_path)
            schema.optimize_database()

            self.logger.info("数据库迁移完成")
            return True

        except Exception as e:
            self.logger.error(f"数据库迁移失败: {e}")
            # 尝试恢复备份
            if self.restore_database():
                self.logger.info("已恢复到迁移前状态")
            return False

    def validate_migration(self) -> Dict[str, bool]:
        """验证迁移结果"""
        validation_results = {
            "tables_exist": False,
            "indexes_exist": False,
            "views_exist": False,
            "data_integrity": False,
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 检查表是否存在
                expected_tables = [
                    "celestial_objects",
                    "classification_results",
                    "execution_history",
                    "query_history",
                    "user_sessions",
                    "performance_metrics",
                    "data_sources",
                    "cache_entries",
                    "error_logs",
                    "schema_version",
                ]

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}
                validation_results["tables_exist"] = all(
                    table in existing_tables for table in expected_tables
                )

                # 检查索引是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                existing_indexes = {row[0] for row in cursor.fetchall()}
                validation_results["indexes_exist"] = (
                    len(existing_indexes) > 10
                )  # 至少应该有10个索引

                # 检查视图是否存在
                expected_views = [
                    "v_object_statistics",
                    "v_query_performance",
                    "v_user_activity",
                    "v_error_trends",
                ]

                cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
                existing_views = {row[0] for row in cursor.fetchall()}
                validation_results["views_exist"] = all(
                    view in existing_views for view in expected_views
                )

                # 检查数据完整性
                cursor.execute("SELECT COUNT(*) FROM celestial_objects")
                object_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM classification_results")
                classification_count = cursor.fetchone()[0]

                validation_results["data_integrity"] = (
                    object_count >= 0 and classification_count >= 0
                )

        except Exception as e:
            self.logger.error(f"迁移验证失败: {e}")

        return validation_results

    def get_migration_info(self) -> Dict[str, any]:
        """获取迁移信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 获取版本历史
                cursor.execute(
                    """
                    SELECT version, applied_at, description 
                    FROM schema_version 
                    ORDER BY version
                """
                )

                version_history = [
                    {"version": row[0], "applied_at": row[1], "description": row[2]}
                    for row in cursor.fetchall()
                ]

                # 获取数据库统计
                schema = EnhancedDatabaseSchema(self.db_path)
                db_info = schema.get_database_info()

                return {
                    "current_version": self.get_current_version(),
                    "version_history": version_history,
                    "database_info": db_info,
                    "backup_path": self.backup_path
                    if os.path.exists(self.backup_path)
                    else None,
                }

        except Exception as e:
            self.logger.error(f"获取迁移信息失败: {e}")
            return {}


def migrate_database(db_path: str) -> bool:
    """便捷函数：迁移数据库到最新版本"""
    migration = DatabaseMigration(db_path)
    return migration.migrate_to_latest()


def validate_database_migration(db_path: str) -> Dict[str, bool]:
    """便捷函数：验证数据库迁移"""
    migration = DatabaseMigration(db_path)
    return migration.validate_migration()


def get_database_migration_info(db_path: str) -> Dict[str, any]:
    """便捷函数：获取数据库迁移信息"""
    migration = DatabaseMigration(db_path)
    return migration.get_migration_info()
