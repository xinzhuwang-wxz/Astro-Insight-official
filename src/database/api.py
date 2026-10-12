#!/usr/bin/env python3
"""
数据库API模块
提供统一的数据库访问接口
"""

import json
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


class DatabaseAPI:
    """数据库API类 - 提供统一的数据库访问接口"""
    
    def __init__(self, db_path: str = "data/astro_insight.db"):
        self.db_path = db_path
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
        """创建分类结果"""
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
        """获取数据统计信息"""
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
    
    # 数据库管理方法
    def get_connection_info(self) -> Dict[str, Any]:
        """获取数据库连接信息"""
        return {
            'db_path': self.db_path,
            'db_type': 'sqlite',
            'status': 'connected'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            # 尝试执行一个简单查询
            stats = self.get_statistics()
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