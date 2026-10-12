#!/usr/bin/env python3
"""
本地数据存储模块
提供天体数据的CRUD操作和分类结果存储功能
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CelestialObject:
    """天体对象数据结构"""

    id: Optional[int] = None
    name: str = ""
    object_type: str = ""  # star, galaxy, nebula, supernova, etc.
    coordinates: Dict[str, float] = None  # {"ra": 0.0, "dec": 0.0}
    magnitude: Optional[float] = None
    spectral_class: Optional[str] = None
    distance: Optional[float] = None  # 距离（光年）
    metadata: Dict[str, Any] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        # 验证输入数据
        self._validate_data()

        if self.coordinates is None:
            self.coordinates = {"ra": 0.0, "dec": 0.0}
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def _validate_data(self):
        """验证数据有效性"""
        # 验证名称
        if not self.name or not self.name.strip():
            raise ValueError("天体名称不能为空")

        # 验证对象类型 - 支持中英文类型
        valid_types = [
            "star",
            "galaxy",
            "nebula",
            "supernova",
            "planet",
            "asteroid",
            "comet",
            "binary_star",
        ]
        chinese_type_mapping = {
            "恒星": "star",
            "星系": "galaxy",
            "星云": "nebula",
            "超新星": "supernova",
            "行星": "planet",
            "小行星": "asteroid",
            "彗星": "comet",
            "双星": "binary_star",
        }

        # 如果是中文类型，转换为英文
        if self.object_type in chinese_type_mapping:
            self.object_type = chinese_type_mapping[self.object_type]
        elif self.object_type not in valid_types:
            raise ValueError(
                f"无效的天体类型: {self.object_type}。有效类型: {', '.join(valid_types)}"
            )

        # 验证坐标
        if self.coordinates:
            ra = self.coordinates.get("ra")
            dec = self.coordinates.get("dec")

            # 转换坐标为数值类型进行验证
            try:
                if ra is not None:
                    # 如果是数值类型，直接验证
                    if isinstance(ra, (int, float)):
                        ra_val = float(ra)
                    # 如果是字符串，尝试转换
                    elif isinstance(ra, str):
                        # 跳过天文学格式的坐标（如 "00h 42m 44s"）
                        if (
                            "h" in ra
                            or "m" in ra
                            or "s" in ra
                            or "°" in ra
                            or "'" in ra
                            or '"' in ra
                        ):
                            ra_val = None  # 跳过验证
                        else:
                            ra_val = float(ra)
                    else:
                        ra_val = float(ra)

                    if ra_val is not None and (ra_val < 0 or ra_val >= 360):
                        raise ValueError(f"赤经必须在0-360度之间，当前值: {ra_val}")

                if dec is not None:
                    # 如果是数值类型，直接验证
                    if isinstance(dec, (int, float)):
                        dec_val = float(dec)
                    # 如果是字符串，尝试转换
                    elif isinstance(dec, str):
                        # 跳过天文学格式的坐标（如 "+41° 16' 09\""）
                        if (
                            "h" in dec
                            or "m" in dec
                            or "s" in dec
                            or "°" in dec
                            or "'" in dec
                            or '"' in dec
                        ):
                            dec_val = None  # 跳过验证
                        else:
                            dec_val = float(dec)
                    else:
                        dec_val = float(dec)

                    if dec_val is not None and (dec_val < -90 or dec_val > 90):
                        raise ValueError(f"赤纬必须在-90到90度之间，当前值: {dec_val}")
            except (ValueError, TypeError) as e:
                if "could not convert" in str(e) or "invalid literal" in str(e):
                    # 对于无法转换的坐标格式，只在明显错误时报错
                    if not any(
                        char in str(ra) + str(dec)
                        for char in ["h", "m", "s", "°", "'", '"']
                    ):
                        raise ValueError(f"坐标必须是有效的数值: ra={ra}, dec={dec}")
                else:
                    raise

        # 验证星等
        if self.magnitude is not None and (self.magnitude < -30 or self.magnitude > 30):
            raise ValueError(f"星等超出合理范围(-30到30)，当前值: {self.magnitude}")

        # 验证距离
        if self.distance is not None and self.distance < 0:
            raise ValueError(f"距离不能为负数，当前值: {self.distance}")


@dataclass
class ClassificationResult:
    """分类结果数据结构"""

    id: Optional[int] = None
    object_id: int = 0
    classification: str = ""
    confidence: float = 0.0
    method: str = ""  # rule_based, ml_model, llm_analysis
    details: Dict[str, Any] = None
    code_generated: Optional[str] = None
    execution_result: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class ExecutionHistory:
    """代码执行历史记录"""

    id: Optional[int] = None
    session_id: str = ""
    code: str = ""
    result: str = ""
    status: str = ""  # success, error, timeout
    execution_time: float = 0.0
    error_message: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class LocalDatabase:
    """本地SQLite数据库管理器"""

    def __init__(self, db_path: str = "data/astro_insight.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建天体对象表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS celestial_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    object_type TEXT NOT NULL,
                    coordinates TEXT,  -- JSON格式存储坐标
                    magnitude REAL,
                    spectral_class TEXT,
                    distance REAL,
                    metadata TEXT,  -- JSON格式存储元数据
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )

            # 创建分类结果表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS classification_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id INTEGER,
                    classification TEXT NOT NULL,
                    confidence REAL,
                    method TEXT,
                    details TEXT,  -- JSON格式存储详细信息
                    code_generated TEXT,
                    execution_result TEXT,
                    created_at TEXT,
                    FOREIGN KEY (object_id) REFERENCES celestial_objects (id)
                )
            """
            )

            # 创建执行历史表
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    code TEXT,
                    result TEXT,
                    status TEXT,
                    execution_time REAL,
                    error_message TEXT,
                    created_at TEXT
                )
            """
            )

            # 创建索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_objects_type ON celestial_objects(object_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_objects_name ON celestial_objects(name)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_object ON classification_results(object_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_history_session ON execution_history(session_id)"
            )

            conn.commit()

    def add_celestial_object(self, obj: CelestialObject) -> int:
        """添加天体对象"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 处理coordinates字段 - 如果已经是字符串就直接使用，否则序列化
            coordinates_str = obj.coordinates if isinstance(obj.coordinates, str) else json.dumps(obj.coordinates)
            
            # 处理metadata字段 - 如果已经是字符串就直接使用，否则序列化
            metadata_str = obj.metadata if isinstance(obj.metadata, str) else json.dumps(obj.metadata)
            
            cursor.execute(
                """
                INSERT INTO celestial_objects 
                (name, object_type, coordinates, magnitude, spectral_class, distance, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    obj.name,
                    obj.object_type,
                    coordinates_str,
                    obj.magnitude,
                    obj.spectral_class,
                    obj.distance,
                    metadata_str,
                    obj.created_at,
                    obj.updated_at,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_celestial_object(self, obj_id: int) -> Optional[CelestialObject]:
        """获取天体对象"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM celestial_objects WHERE id = ?", (obj_id,))
            row = cursor.fetchone()

            if row:
                return CelestialObject(
                    id=row[0],
                    name=row[1],
                    object_type=row[2],
                    coordinates=json.loads(row[3]) if row[3] else {},
                    magnitude=row[4],
                    spectral_class=row[5],
                    distance=row[6],
                    metadata=json.loads(row[7]) if row[7] else {},
                    created_at=row[8],
                    updated_at=row[9],
                )
            return None

    def search_celestial_objects(
        self,
        object_type: Optional[str] = None,
        name_pattern: Optional[str] = None,
        limit: int = 100,
    ) -> List[CelestialObject]:
        """搜索天体对象"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM celestial_objects WHERE 1=1"
            params = []

            if object_type:
                query += " AND object_type = ?"
                params.append(object_type)

            if name_pattern:
                query += " AND name LIKE ?"
                params.append(f"%{name_pattern}%")

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            objects = []
            for row in rows:
                objects.append(
                    CelestialObject(
                        id=row[0],
                        name=row[1],
                        object_type=row[2],
                        coordinates=json.loads(row[3]) if row[3] else {},
                        magnitude=row[4],
                        spectral_class=row[5],
                        distance=row[6],
                        metadata=json.loads(row[7]) if row[7] else {},
                        created_at=row[8],
                        updated_at=row[9],
                    )
                )

            return objects

    def add_classification_result(self, result: ClassificationResult) -> int:
        """添加分类结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO classification_results 
                (object_id, classification, confidence, method, details, code_generated, execution_result, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.object_id,
                    result.classification,
                    result.confidence,
                    result.method,
                    json.dumps(result.details),
                    result.code_generated,
                    result.execution_result,
                    result.created_at,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_classification_results(self, object_id: int) -> List[ClassificationResult]:
        """获取天体的分类结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM classification_results 
                WHERE object_id = ? 
                ORDER BY created_at DESC
            """,
                (object_id,),
            )
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append(
                    ClassificationResult(
                        id=row[0],
                        object_id=row[1],
                        classification=row[2],
                        confidence=row[3],
                        method=row[4],
                        details=json.loads(row[5]) if row[5] else {},
                        code_generated=row[6],
                        execution_result=row[7],
                        created_at=row[8],
                    )
                )

            return results

    def add_execution_history(self, history: ExecutionHistory) -> int:
        """添加执行历史记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO execution_history 
                (session_id, code, result, status, execution_time, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    history.session_id,
                    history.code,
                    history.result,
                    history.status,
                    history.execution_time,
                    history.error_message,
                    history.created_at,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_execution_history(
        self, session_id: Optional[str] = None, limit: int = 50
    ) -> List[ExecutionHistory]:
        """获取执行历史记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if session_id:
                cursor.execute(
                    """
                    SELECT * FROM execution_history 
                    WHERE session_id = ? 
                    ORDER BY created_at DESC LIMIT ?
                """,
                    (session_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM execution_history 
                    ORDER BY created_at DESC LIMIT ?
                """,
                    (limit,),
                )

            rows = cursor.fetchall()

            history = []
            for row in rows:
                history.append(
                    ExecutionHistory(
                        id=row[0],
                        session_id=row[1],
                        code=row[2],
                        result=row[3],
                        status=row[4],
                        execution_time=row[5],
                        error_message=row[6],
                        created_at=row[7],
                    )
                )

            return history


class DataManager:
    """数据管理器 - 提供高级数据操作接口"""

    def __init__(self, db_path: str = "data/astro_insight.db"):
        self.db = LocalDatabase(db_path)
        self._init_sample_data()

    def _init_sample_data(self):
        """初始化示例数据"""
        # 检查是否已有数据
        existing_objects = self.db.search_celestial_objects(limit=1)
        if existing_objects:
            return

        # 添加一些示例天体数据
        sample_objects = [
            CelestialObject(
                name="M31",
                object_type="galaxy",
                coordinates={"ra": 10.6847, "dec": 41.2687},
                magnitude=3.4,
                distance=2537000,
                metadata={"common_name": "Andromeda Galaxy", "galaxy_type": "spiral"},
            ),
            CelestialObject(
                name="M42",
                object_type="nebula",
                coordinates={"ra": 83.8221, "dec": -5.3911},
                magnitude=4.0,
                distance=1344,
                metadata={"common_name": "Orion Nebula", "nebula_type": "emission"},
            ),
            CelestialObject(
                name="Sirius",
                object_type="star",
                coordinates={"ra": 101.2871, "dec": -16.7161},
                magnitude=-1.46,
                spectral_class="A1V",
                distance=8.6,
                metadata={"common_name": "Dog Star", "binary_system": True},
            ),
        ]

        for obj in sample_objects:
            self.db.add_celestial_object(obj)

    def classify_object(
        self,
        obj_id: int,
        classification: str,
        confidence: float,
        method: str,
        details: Dict[str, Any] = None,
        code_generated: str = None,
        execution_result: str = None,
    ) -> int:
        """为天体对象添加分类结果"""
        result = ClassificationResult(
            object_id=obj_id,
            classification=classification,
            confidence=confidence,
            method=method,
            details=details or {},
            code_generated=code_generated,
            execution_result=execution_result,
        )
        return self.db.add_classification_result(result)

    def get_object_with_classifications(self, obj_id: int) -> Dict[str, Any]:
        """获取天体对象及其分类结果"""
        obj = self.db.get_celestial_object(obj_id)
        if not obj:
            return None

        classifications = self.db.get_classification_results(obj_id)

        return {
            "object": asdict(obj),
            "classifications": [asdict(c) for c in classifications],
        }

    def search_objects_by_type(self, object_type: str) -> List[Dict[str, Any]]:
        """按类型搜索天体对象"""
        objects = self.db.search_celestial_objects(object_type=object_type)
        return [asdict(obj) for obj in objects]

    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()

            # 天体对象统计
            cursor.execute(
                "SELECT object_type, COUNT(*) FROM celestial_objects GROUP BY object_type"
            )
            object_stats = dict(cursor.fetchall())

            # 分类结果统计
            cursor.execute(
                "SELECT method, COUNT(*) FROM classification_results GROUP BY method"
            )
            classification_stats = dict(cursor.fetchall())

            # 执行历史统计
            cursor.execute(
                "SELECT status, COUNT(*) FROM execution_history GROUP BY status"
            )
            execution_stats = dict(cursor.fetchall())

            return {
                "objects_by_type": object_stats,
                "classifications_by_method": classification_stats,
                "executions_by_status": execution_stats,
            }


# 全局数据管理器实例
data_manager = DataManager()
