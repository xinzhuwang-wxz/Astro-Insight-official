#!/usr/bin/env python3
"""
LLM模块
提供各种大语言模型的统一接口
"""

from .llm import get_llm_by_type, get_configured_llm_models
from .providers.dashscope import ChatDashscope

__all__ = [
    "get_llm_by_type",
    "get_configured_llm_models", 
    "ChatDashscope",
]

__version__ = "1.0.0"
__author__ = "Astro Insight Team"
__description__ = "大语言模型统一接口"
