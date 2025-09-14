"""
Astro-Insight CopilotKit API集成模块

将Astro-Insight的专业天文科研功能封装为CopilotKit兼容的API接口，
提供标准化的AI对话服务供前端调用。

主要组件：
- AstroAgent: 核心代理包装器
- CopilotKitState: 状态管理
- FastAPI集成: RESTful API服务
"""

__version__ = "1.0.0"
__author__ = "Astro-Insight Team"

from .agent import AstroAgent, AstroState
from .server import app, create_astro_sdk

__all__ = [
    "AstroAgent",
    "AstroState", 
    "app",
    "create_astro_sdk"
]

