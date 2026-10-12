# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional, Any, TypedDict
from enum import Enum
from pathlib import Path


class ExplanationComplexity(Enum):
    """解释复杂度级别"""
    BASIC = "basic"           # 基础描述
    DETAILED = "detailed"     # 详细分析  
    PROFESSIONAL = "professional"  # 专业解读


class ExplanationStatus(Enum):
    """解释状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"


class ImageInfo(TypedDict):
    """图片信息结构"""
    file_path: str
    file_name: str
    file_size: int
    created_time: float
    image_type: str  # png, jpg, svg等


class CoderOutput(TypedDict):
    """Coder模块输出结构（接收用）"""
    success: bool
    code: str
    output: str
    execution_time: float
    generated_files: List[str]  # 图片文件路径列表
    generated_texts: List[str]  # 文本工件路径列表
    dataset_used: str
    complexity: str
    retry_count: int
    user_input: str  # 用户原始需求


class ExplainerRequest(TypedDict):
    """解释器请求结构"""
    # 来自Coder的完整输出
    coder_output: CoderOutput
    
    # 额外的解释需求
    explanation_type: ExplanationComplexity
    focus_aspects: Optional[List[str]]  # 关注的方面：["数据分布", "趋势分析", "异常检测"]
    target_audience: Optional[str]      # 目标受众：研究人员、学生、公众
    
    # 数据集上下文
    dataset_description: Optional[str]
    additional_context: Optional[str]


class ExplainerResult(TypedDict):
    """解释器结果结构"""
    status: ExplanationStatus
    
    # 解释内容
    explanations: List[Dict[str, Any]]  # 每张图片的解释
    summary: str                        # 整体总结
    insights: List[str]                # 关键洞察
    
    # 技术信息
    images_analyzed: List[ImageInfo]
    processing_time: float
    vlm_calls: int
    
    # 错误信息
    error: Optional[str]
    warnings: List[str]


class DialogueRecord(TypedDict):
    """对话记录结构"""
    session_id: str
    timestamp: float
    user_request: str
    coder_output: CoderOutput
    explainer_result: ExplainerResult
    conversation_context: Dict[str, Any]


class ExplainerState(TypedDict):
    """解释器Agent状态"""
    # 基础信息
    session_id: str
    request: ExplainerRequest
    
    # 处理状态
    current_step: str
    processed_images: List[ImageInfo]
    pending_images: List[str]
    
    # 分析上下文（必须在各节点间保留）
    analysis_context: Dict[str, Any]
    
    # VLM处理
    vlm_responses: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    
    # 最终结果
    explanation_result: Optional[ExplainerResult]
    
    # 错误处理
    error_info: Optional[Dict[str, Any]]
    retry_count: int
    max_retries: int
    
    # 对话管理
    dialogue_record: Optional[DialogueRecord]
    output_file_path: Optional[str]
    
    # 时间戳
    timestamp: float


class VLMRequest(TypedDict):
    """VLM请求结构"""
    image_path: str
    prompt: str
    context: Dict[str, Any]


class VLMResponse(TypedDict):
    """VLM响应结构"""
    success: bool
    content: str
    error: Optional[str]
    processing_time: float
    model_used: str
