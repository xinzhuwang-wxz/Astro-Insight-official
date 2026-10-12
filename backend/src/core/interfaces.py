#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心接口定义
定义系统的核心接口，实现依赖倒置原则
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from src.graph.types import AstroAgentState


class UserType(Enum):
    """用户类型枚举"""
    AMATEUR = "amateur"
    PROFESSIONAL = "professional"


class TaskType(Enum):
    """任务类型枚举"""
    QA = "qa"
    CLASSIFICATION = "classification"
    DATA_ANALYSIS = "data_analysis"  # 整合数据检索、代码生成、执行
    LITERATURE_REVIEW = "literature_review"
    # 移除单独的 DATA_RETRIEVAL 和 CODE_GENERATION
    # ANALYSIS = "analysis"  # 合并到 DATA_ANALYSIS


class IUserService(ABC):
    """用户服务接口"""
    
    @abstractmethod
    def identify_user_type(self, user_input: str) -> UserType:
        """识别用户类型"""
        pass
    
    @abstractmethod
    def get_user_profile(self, session_id: str) -> Dict[str, Any]:
        """获取用户档案"""
        pass
    
    @abstractmethod
    def update_user_profile(self, session_id: str, profile: Dict[str, Any]) -> bool:
        """更新用户档案"""
        pass


class ITaskService(ABC):
    """任务服务接口"""
    
    @abstractmethod
    def classify_task(self, user_input: str, user_type: UserType) -> TaskType:
        """分类任务类型"""
        pass
    
    @abstractmethod
    def execute_task(self, task_type: TaskType, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        pass
    
    @abstractmethod
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        pass


class IIdentityService(ABC):
    """身份识别服务接口"""
    
    @abstractmethod
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """分析用户输入"""
        pass
    
    @abstractmethod
    def extract_user_intent(self, user_input: str) -> str:
        """提取用户意图"""
        pass
    
    @abstractmethod
    def determine_expertise_level(self, user_input: str) -> str:
        """确定专业水平"""
        pass


class IClassificationService(ABC):
    """分类服务接口"""
    
    @abstractmethod
    def classify_celestial_object(self, query: str) -> Dict[str, Any]:
        """分类天体对象"""
        pass
    
    @abstractmethod
    def get_classification_config(self, user_type: UserType) -> Dict[str, Any]:
        """获取分类配置"""
        pass
    
    @abstractmethod
    def validate_classification_input(self, input_data: Dict[str, Any]) -> bool:
        """验证分类输入"""
        pass


class IDataRetrievalService(ABC):
    """数据检索服务接口"""
    
    @abstractmethod
    def search_astronomical_data(self, query: str) -> Dict[str, Any]:
        """搜索天文数据"""
        pass
    
    @abstractmethod
    def get_data_sources(self) -> List[Dict[str, Any]]:
        """获取数据源列表"""
        pass
    
    @abstractmethod
    def validate_retrieval_query(self, query: str) -> bool:
        """验证检索查询"""
        pass


class ICodeGenerationService(ABC):
    """代码生成服务接口"""
    
    @abstractmethod
    def generate_analysis_code(self, requirements: Dict[str, Any]) -> str:
        """生成分析代码"""
        pass
    
    @abstractmethod
    def validate_generated_code(self, code: str) -> bool:
        """验证生成的代码"""
        pass
    
    @abstractmethod
    def execute_generated_code(self, code: str) -> Dict[str, Any]:
        """执行生成的代码"""
        pass


class IStateManager(ABC):
    """状态管理接口"""
    
    @abstractmethod
    def create_initial_state(self, session_id: str, user_input: str) -> AstroAgentState:
        """创建初始状态"""
        pass
    
    @abstractmethod
    def update_state(self, current_state: AstroAgentState, updates: Dict[str, Any]) -> AstroAgentState:
        """更新状态"""
        pass
    
    @abstractmethod
    def validate_state(self, state: AstroAgentState) -> bool:
        """验证状态"""
        pass
    
    @abstractmethod
    def format_state_output(self, state: AstroAgentState) -> str:
        """格式化状态输出"""
        pass


class IConfigurationManager(ABC):
    """配置管理接口"""
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        pass
    
    @abstractmethod
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        pass
    
    @abstractmethod
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        pass
    
    @abstractmethod
    def reload_config(self) -> bool:
        """重新加载配置"""
        pass


class IErrorHandler(ABC):
    """错误处理接口"""
    
    @abstractmethod
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理错误"""
        pass
    
    @abstractmethod
    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """记录错误"""
        pass
    
    @abstractmethod
    def create_error_context(self, **kwargs) -> Dict[str, Any]:
        """创建错误上下文"""
        pass


class ILogger(ABC):
    """日志接口"""
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        pass


class ICacheManager(ABC):
    """缓存管理接口"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass


class IDatabaseRepository(ABC):
    """数据库仓储接口"""
    
    @abstractmethod
    def save_query_history(self, query_data: Dict[str, Any]) -> bool:
        """保存查询历史"""
        pass
    
    @abstractmethod
    def get_query_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取查询历史"""
        pass
    
    @abstractmethod
    def save_user_session(self, session_data: Dict[str, Any]) -> bool:
        """保存用户会话"""
        pass
    
    @abstractmethod
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取用户会话"""
        pass
