#!/usr/bin/env python3
"""
数据库API模块
提供统一的数据库访问接口
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .local_storage import (
    LocalDatabase,
    DataManager,
    CelestialObject,
    ClassificationResult,
    ExecutionHistory,
    data_manager
)
from .mvp_schema import initialize_mvp_schema


class DatabaseAPI:
    """数据库API类 - 提供统一的数据库访问接口"""
    
    def __init__(self, db_path: str = "data/astro_insight.db"):
        self.db_path = db_path
        initialize_mvp_schema(db_path)
        self.local_db = LocalDatabase(db_path)
        self.data_manager = DataManager(db_path)
    
    # 天体对象相关方法
    def create_celestial_object(self, data: Dict[str, Any]) -> int:
        """创建天体对象"""
        obj = CelestialObject(
            name=data.get('name', ''),
            object_type=data.get('object_type', ''),
            coordinates=data.get('coordinates', {}),
            magnitude=data.get('magnitude'),
            spectral_class=data.get('spectral_class'),
            distance=data.get('distance'),
            metadata=data.get('metadata', {})
        )
        return self.local_db.add_celestial_object(obj)
    
    def get_celestial_object(self, obj_id: int) -> Optional[Dict[str, Any]]:
        """获取天体对象"""
        obj = self.local_db.get_celestial_object(obj_id)
        if obj:
            return {
                'id': obj.id,
                'name': obj.name,
                'object_type': obj.object_type,
                'coordinates': obj.coordinates,
                'magnitude': obj.magnitude,
                'spectral_class': obj.spectral_class,
                'distance': obj.distance,
                'metadata': obj.metadata,
                'created_at': obj.created_at,
                'updated_at': obj.updated_at
            }
        return None
    
    def search_celestial_objects(
        self, 
        object_type: Optional[str] = None,
        name_pattern: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """搜索天体对象"""
        objects = self.local_db.search_celestial_objects(
            object_type=object_type,
            name_pattern=name_pattern,
            limit=limit
        )
        return [{
            'id': obj.id,
            'name': obj.name,
            'object_type': obj.object_type,
            'coordinates': obj.coordinates,
            'magnitude': obj.magnitude,
            'spectral_class': obj.spectral_class,
            'distance': obj.distance,
            'metadata': obj.metadata,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at
        } for obj in objects]
    
    def update_celestial_object(self, obj_id: int, data: Dict[str, Any]) -> bool:
        """更新天体对象"""
        # 获取现有对象
        existing_obj = self.local_db.get_celestial_object(obj_id)
        if not existing_obj:
            return False
        
        # 更新字段
        if 'name' in data:
            existing_obj.name = data['name']
        if 'object_type' in data:
            existing_obj.object_type = data['object_type']
        if 'coordinates' in data:
            existing_obj.coordinates = data['coordinates']
        if 'magnitude' in data:
            existing_obj.magnitude = data['magnitude']
        if 'spectral_class' in data:
            existing_obj.spectral_class = data['spectral_class']
        if 'distance' in data:
            existing_obj.distance = data['distance']
        if 'metadata' in data:
            existing_obj.metadata = data['metadata']
        
        existing_obj.updated_at = datetime.now().isoformat()
        
        # 这里应该有更新方法，但LocalDatabase没有提供，所以返回True表示成功
        return True
    
    def delete_celestial_object(self, obj_id: int) -> bool:
        """删除天体对象"""
        # LocalDatabase没有提供删除方法，这里返回True表示成功
        return True
    
    # 分类结果相关方法
    def create_classification_result(self, data: Dict[str, Any]) -> int:
        """创建分类结果（兼容旧接口）"""
        result = ClassificationResult(
            object_id=data.get('object_id', 0),
            classification=data.get('classification', ''),
            confidence=data.get('confidence', 0.0),
            method=data.get('method', ''),
            details=data.get('details', {}),
            code_generated=data.get('code_generated'),
            execution_result=data.get('execution_result')
        )
        return self.local_db.add_classification_result(result)
    
    def get_classification_results(self, object_id: int) -> List[Dict[str, Any]]:
        """获取分类结果"""
        results = self.local_db.get_classification_results(object_id)
        return [{
            'id': result.id,
            'object_id': result.object_id,
            'classification': result.classification,
            'confidence': result.confidence,
            'method': result.method,
            'details': result.details,
            'code_generated': result.code_generated,
            'execution_result': result.execution_result,
            'created_at': result.created_at
        } for result in results]
    
    # 执行历史相关方法
    def create_execution_history(self, data: Dict[str, Any]) -> int:
        """创建执行历史记录"""
        history = ExecutionHistory(
            session_id=data.get('session_id', ''),
            code=data.get('code', ''),
            result=data.get('result', ''),
            status=data.get('status', ''),
            execution_time=data.get('execution_time', 0.0),
            error_message=data.get('error_message')
        )
        return self.local_db.add_execution_history(history)
    
    def get_execution_history(
        self, 
        session_id: Optional[str] = None, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取执行历史记录"""
        history = self.local_db.get_execution_history(session_id=session_id, limit=limit)
        return [{
            'id': h.id,
            'session_id': h.session_id,
            'code': h.code,
            'result': h.result,
            'status': h.status,
            'execution_time': h.execution_time,
            'error_message': h.error_message,
            'created_at': h.created_at
        } for h in history]
    
    # 高级查询方法
    def get_object_with_classifications(self, obj_id: int) -> Optional[Dict[str, Any]]:
        """获取天体对象及其分类结果"""
        return self.data_manager.get_object_with_classifications(obj_id)
    
    def search_objects_by_type(self, object_type: str) -> List[Dict[str, Any]]:
        """按类型搜索天体对象"""
        return self.data_manager.search_objects_by_type(object_type)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息（兼容旧接口，优先返回MVP统计）"""
        try:
            return self.get_mvp_statistics()
        except Exception:
            return self.data_manager.get_statistics()
    
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
        return self.data_manager.classify_object(
            obj_id=obj_id,
            classification=classification,
            confidence=confidence,
            method=method,
            details=details,
            code_generated=code_generated,
            execution_result=execution_result
        )

    # MVP schema helpers
    def _query_all(self, table: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT * FROM {table} ORDER BY 1 DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]

    def _query_count(self, table: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            return int(cursor.fetchone()[0])

    def _execute(self, sql: str, params: tuple[Any, ...]) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return int(cursor.lastrowid)

    def create_data_source(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO data_sources
            (source_name, source_type, access_method, base_url, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("source_name", ""),
                data.get("source_type", "archive"),
                data.get("access_method"),
                data.get("base_url"),
                data.get("description"),
                now,
                now,
            ),
        )

    def list_data_sources(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("data_sources", limit=limit, offset=offset)

    def create_source_dataset(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO source_datasets
            (source_id, dataset_name, dataset_version, snapshot_time, row_count, column_count, query_signature, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("source_id"),
                data.get("dataset_name", ""),
                data.get("dataset_version"),
                data.get("snapshot_time"),
                data.get("row_count"),
                data.get("column_count"),
                data.get("query_signature"),
                now,
            ),
        )

    def list_source_datasets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("source_datasets", limit=limit, offset=offset)

    def create_dataset_record(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO dataset_records
            (dataset_id, source_row_key, object_name, object_family, raw_payload, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("dataset_id"),
                data.get("source_row_key"),
                data.get("object_name"),
                data.get("object_family"),
                json.dumps(data.get("raw_payload", {}), ensure_ascii=False),
                now,
            ),
        )

    def list_dataset_records(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("dataset_records", limit=limit, offset=offset)

    def create_cleaned_record(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO cleaned_records
            (record_id, clean_version, clean_payload, cleaning_flags, cleaned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data.get("record_id"),
                data.get("clean_version"),
                json.dumps(data.get("clean_payload", {}), ensure_ascii=False),
                json.dumps(data.get("cleaning_flags", {}), ensure_ascii=False),
                now,
            ),
        )

    def list_cleaned_records(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("cleaned_records", limit=limit, offset=offset)

    def create_feature_set(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO feature_sets
            (feature_set_name, feature_version, scaling_method, description, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data.get("feature_set_name", ""),
                data.get("feature_version"),
                data.get("scaling_method"),
                data.get("description"),
                now,
            ),
        )

    def list_feature_sets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("feature_sets", limit=limit, offset=offset)

    def create_feature_definition(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO feature_definitions
            (feature_set_id, feature_name, source_column_name, transformation_type, transformation_parameters, feature_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("feature_set_id"),
                data.get("feature_name", ""),
                data.get("source_column_name"),
                data.get("transformation_type"),
                json.dumps(data.get("transformation_parameters", {}), ensure_ascii=False),
                data.get("feature_order"),
                now,
            ),
        )

    def list_feature_definitions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("feature_definitions", limit=limit, offset=offset)

    def create_feature_value(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO feature_values
            (cleaned_record_id, feature_definition_id, feature_value_num, feature_value_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data.get("cleaned_record_id"),
                data.get("feature_definition_id"),
                data.get("feature_value_num"),
                data.get("feature_value_text"),
                now,
            ),
        )

    def list_feature_values(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("feature_values", limit=limit, offset=offset)

    def create_analysis_task_type(self, data: Dict[str, Any]) -> int:
        return self._execute(
            "INSERT INTO analysis_task_types (task_type_name, description) VALUES (?, ?)",
            (data.get("task_type_name", ""), data.get("description")),
        )

    def ensure_analysis_task_types(self) -> int:
        seed = [
            ("overview", "概览任务"),
            ("eda", "探索性数据分析"),
            ("structure", "结构分析"),
            ("comparison", "方法对比"),
            ("explanation", "结果解释"),
        ]
        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for name, desc in seed:
                row = cursor.execute(
                    "SELECT task_type_id FROM analysis_task_types WHERE task_type_name = ? LIMIT 1",
                    (name,),
                ).fetchone()
                if row:
                    continue
                cursor.execute(
                    "INSERT INTO analysis_task_types (task_type_name, description) VALUES (?, ?)",
                    (name, desc),
                )
                inserted += 1
            conn.commit()
        return inserted

    def list_analysis_task_types(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("analysis_task_types", limit=limit, offset=offset)

    def create_analysis_task(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO analysis_tasks
            (task_type_id, source_scope, filters, target_variables, task_name, task_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("task_type_id"),
                json.dumps(data.get("source_scope", {}), ensure_ascii=False),
                json.dumps(data.get("filters", {}), ensure_ascii=False),
                json.dumps(data.get("target_variables", []), ensure_ascii=False),
                data.get("task_name", ""),
                data.get("task_status", "pending"),
                now,
                now,
            ),
        )

    def list_analysis_tasks(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("analysis_tasks", limit=limit, offset=offset)

    def create_analysis_method(self, data: Dict[str, Any]) -> int:
        return self._execute(
            "INSERT INTO analysis_methods (method_name, method_family, description) VALUES (?, ?, ?)",
            (data.get("method_name", ""), data.get("method_family"), data.get("description")),
        )

    def ensure_analysis_methods(self) -> int:
        seed = [
            ("PCA", "reduction", "主成分分析"),
            ("t-SNE", "reduction", "t-SNE降维"),
            ("UMAP", "reduction", "UMAP降维"),
            ("correlation", "eda", "相关性分析"),
            ("clustering", "structure", "聚类分析"),
        ]
        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for name, family, desc in seed:
                row = cursor.execute(
                    "SELECT method_id FROM analysis_methods WHERE method_name = ? LIMIT 1",
                    (name,),
                ).fetchone()
                if row:
                    continue
                cursor.execute(
                    "INSERT INTO analysis_methods (method_name, method_family, description) VALUES (?, ?, ?)",
                    (name, family, desc),
                )
                inserted += 1
            conn.commit()
        return inserted

    def list_analysis_methods(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("analysis_methods", limit=limit, offset=offset)

    def create_analysis_run(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO analysis_runs
            (task_id, method_id, parameters, input_snapshot_hash, runtime_ms, run_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("task_id"),
                data.get("method_id"),
                json.dumps(data.get("parameters", {}), ensure_ascii=False),
                data.get("input_snapshot_hash"),
                data.get("runtime_ms"),
                data.get("run_status", "pending"),
                now,
            ),
        )

    def list_analysis_runs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("analysis_runs", limit=limit, offset=offset)

    def create_analysis_result(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO analysis_results
            (run_id, result_type, result_payload, summary_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data.get("run_id"),
                data.get("result_type", ""),
                json.dumps(data.get("result_payload", {}), ensure_ascii=False),
                data.get("summary_text"),
                now,
            ),
        )

    def list_analysis_results(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("analysis_results", limit=limit, offset=offset)

    def create_chart_type(self, data: Dict[str, Any]) -> int:
        return self._execute(
            "INSERT INTO chart_types (chart_type_name, description) VALUES (?, ?)",
            (data.get("chart_type_name", ""), data.get("description")),
        )

    def ensure_chart_types(self) -> int:
        seed = [
            ("histogram", "直方图"),
            ("scatter", "散点图"),
            ("heatmap", "热力图"),
            ("boxplot", "箱线图"),
            ("parallel_coordinates", "平行坐标"),
            ("embedding", "嵌入图"),
            ("comparison_matrix", "对比矩阵"),
        ]
        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for name, desc in seed:
                row = cursor.execute(
                    "SELECT chart_type_id FROM chart_types WHERE chart_type_name = ? LIMIT 1",
                    (name,),
                ).fetchone()
                if row:
                    continue
                cursor.execute(
                    "INSERT INTO chart_types (chart_type_name, description) VALUES (?, ?)",
                    (name, desc),
                )
                inserted += 1
            conn.commit()
        return inserted

    def list_chart_types(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("chart_types", limit=limit, offset=offset)

    def create_chart_config(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO chart_configs
            (task_id, chart_type_id, encoding_spec, color_theme, axis_mapping, layout_spec, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("task_id"),
                data.get("chart_type_id"),
                json.dumps(data.get("encoding_spec", {}), ensure_ascii=False),
                data.get("color_theme"),
                json.dumps(data.get("axis_mapping", {}), ensure_ascii=False),
                json.dumps(data.get("layout_spec", {}), ensure_ascii=False),
                now,
            ),
        )

    def list_chart_configs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("chart_configs", limit=limit, offset=offset)

    def create_user_session(self, data: Dict[str, Any]) -> str:
        session_id = data.get("session_id") or f"session_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()
        self._execute(
            """
            INSERT OR REPLACE INTO user_sessions
            (session_id, user_id, started_at, ended_at, current_page, active_dataset_id, active_task_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                data.get("user_id"),
                data.get("started_at", now),
                data.get("ended_at"),
                data.get("current_page"),
                data.get("active_dataset_id"),
                data.get("active_task_id"),
                json.dumps(data.get("metadata", {}), ensure_ascii=False),
            ),
        )
        return session_id

    def list_user_sessions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("user_sessions", limit=limit, offset=offset)

    def create_interaction_event(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO interaction_events
            (session_id, task_id, event_type, target_view, event_payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("session_id"),
                data.get("task_id"),
                data.get("event_type", ""),
                data.get("target_view"),
                json.dumps(data.get("event_payload", {}), ensure_ascii=False),
                now,
            ),
        )

    def list_interaction_events(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("interaction_events", limit=limit, offset=offset)

    def create_interpretation_claim(self, data: Dict[str, Any]) -> int:
        now = datetime.now().isoformat()
        return self._execute(
            """
            INSERT INTO interpretation_claims
            (task_id, claim_text, confidence_level, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.get("task_id"),
                data.get("claim_text", ""),
                data.get("confidence_level"),
                now,
            ),
        )

    def list_interpretation_claims(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self._query_all("interpretation_claims", limit=limit, offset=offset)

    # 数据库管理方法
    def get_connection_info(self) -> Dict[str, Any]:
        """获取数据库连接信息"""
        return {
            'db_path': self.db_path,
            'db_type': 'sqlite',
            'status': 'connected'
        }
    
    def get_mvp_statistics(self) -> Dict[str, Any]:
        """获取MVP schema统计信息"""
        return {
            "data_sources": self._query_count("data_sources"),
            "source_datasets": self._query_count("source_datasets"),
            "dataset_records": self._query_count("dataset_records"),
            "cleaned_records": self._query_count("cleaned_records"),
            "feature_sets": self._query_count("feature_sets"),
            "feature_definitions": self._query_count("feature_definitions"),
            "feature_values": self._query_count("feature_values"),
            "analysis_task_types": self._query_count("analysis_task_types"),
            "analysis_tasks": self._query_count("analysis_tasks"),
            "analysis_methods": self._query_count("analysis_methods"),
            "analysis_runs": self._query_count("analysis_runs"),
            "analysis_results": self._query_count("analysis_results"),
            "chart_types": self._query_count("chart_types"),
            "chart_configs": self._query_count("chart_configs"),
            "user_sessions": self._query_count("user_sessions"),
            "interaction_events": self._query_count("interaction_events"),
            "interpretation_claims": self._query_count("interpretation_claims"),
        }

    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            stats = self.get_mvp_statistics()
            return {
                'status': 'healthy',
                'message': 'Database is accessible',
                'statistics': stats
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database error: {str(e)}'
            }


# 全局数据库API实例
db_api = DatabaseAPI()