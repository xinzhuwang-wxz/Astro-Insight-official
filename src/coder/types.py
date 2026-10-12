# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import TypedDict, Optional, List, Dict, Any, Literal
from enum import Enum


class CodeComplexity(Enum):
    """代码复杂度枚举"""
    SIMPLE = "simple"           # 简单数据操作：展示前5行、基本统计
    MODERATE = "moderate"       # 中等复杂度：数据可视化、清洗
    COMPLEX = "complex"         # 复杂分析：机器学习、高级统计


class ExecutionStatus(Enum):
    """代码执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class DatasetInfo(TypedDict):
    """数据集信息结构"""
    name: str
    path: str
    description_path: str
    description_content: str
    columns: List[str]
    target_column: Optional[str]
    data_type: str  # csv, json, parquet等


class CodeGenerationRequest(TypedDict):
    """代码生成请求结构"""
    dataset_info: DatasetInfo
    user_requirement: str
    complexity: CodeComplexity
    additional_context: Optional[str]


class CodeExecutionResult(TypedDict):
    """代码执行结果结构"""
    status: ExecutionStatus
    code: str
    output: Optional[str]
    error: Optional[str]
    execution_time: float
    generated_files: List[str]  # 生成的图片文件路径
    generated_texts: List[str]  # 生成的文本类工件（.txt/.log/.md 等）


class CoderAgentState(TypedDict):
    """代码生成Agent状态"""
    # 基础信息
    session_id: str
    user_input: str
    
    # 数据集相关
    available_datasets: List[DatasetInfo]
    selected_dataset: Optional[DatasetInfo]
    
    # 代码生成相关
    generation_request: Optional[CodeGenerationRequest]
    generated_code: Optional[str]
    execution_result: Optional[CodeExecutionResult]
    
    # 执行状态
    current_step: str
    retry_count: int
    max_retries: int
    
    # 错误处理
    error_info: Optional[Dict[str, Any]]
    error_recovery_attempts: int
    
    # 历史记录
    code_history: List[Dict[str, Any]]
    execution_history: List[CodeExecutionResult]
    
    # 时间戳
    timestamp: float
