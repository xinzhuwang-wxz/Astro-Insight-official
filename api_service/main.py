#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版天文科研Agent API服务
专注于核心功能：标准输出和前端对接
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import asyncio

# 导入现有的工作流系统
from src.workflow import AstroWorkflow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Astro-Insight API",
    description="简化版天文科研助手API - 专注于前端对接",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件，支持前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局工作流实例
workflow: Optional[AstroWorkflow] = None

# ==================== 数据模型 ====================

class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str = Field(..., description="用户查询内容", min_length=1)
    user_type: Optional[str] = Field(None, description="用户类型: amateur/professional")
    session_id: Optional[str] = Field(None, description="会话ID，用于继续对话")

class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Dict[str, Any] = Field(..., description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")
    execution_time: float = Field(..., description="执行时间（秒）")

class SystemStatusResponse(BaseModel):
    """系统状态响应模型"""
    status: str = Field(..., description="系统状态")
    message: str = Field(..., description="状态描述")
    timestamp: str = Field(..., description="检查时间戳")

# ==================== 工具函数 ====================

# 已移除token_usage相关功能

# ==================== 应用生命周期 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化工作流"""
    global workflow
    try:
        logger.info("正在初始化AstroWorkflow...")
        workflow = AstroWorkflow()
        logger.info("AstroWorkflow初始化成功")
    except Exception as e:
        logger.error(f"AstroWorkflow初始化失败: {e}")
        raise RuntimeError(f"无法启动API服务: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("API服务正在关闭...")

# ==================== API端点 ====================

@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径，返回API信息"""
    return {
        "message": "Astro-Insight API 服务运行中",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/status"
    }

@app.get("/status", response_model=SystemStatusResponse)
async def get_status():
    """获取系统状态"""
    if workflow is None:
        return SystemStatusResponse(
            status="error",
            message="工作流未初始化",
            timestamp=datetime.now().isoformat()
        )
    
    try:
        # 获取系统状态
        system_status = workflow.get_system_status()
        return SystemStatusResponse(
            status="healthy",
            message="系统运行正常",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return SystemStatusResponse(
            status="error",
            message=f"系统状态检查失败: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """处理天文查询请求"""
    if workflow is None:
        raise HTTPException(
            status_code=503,
            detail="工作流未初始化，请稍后重试"
        )
    
    start_time = datetime.now()
    session_id = request.session_id or f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    try:
        logger.info(f"处理查询: {request.query[:50]}...")
        
        # 构建用户上下文
        user_context = {}
        if request.user_type:
            user_context["user_type"] = request.user_type
        
        # 执行工作流
        result_state = await asyncio.to_thread(
            workflow.execute_workflow,
            session_id,
            request.query,
            user_context
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 构建响应数据
        response_data = {
            "query": request.query,
            "session_id": session_id,
            "user_type": result_state.get("user_type"),
            "task_type": result_state.get("task_type"),
            "current_step": result_state.get("current_step"),
            "is_complete": result_state.get("is_complete", False),
            "answer": result_state.get("qa_response") or result_state.get("final_answer") or "暂无回答",
            "generated_code": result_state.get("generated_code"),
            "execution_history": result_state.get("execution_history", []),
            "error_info": result_state.get("error_info")
        }
        
        return QueryResponse(
            success=True,
            message="查询处理成功",
            data=response_data,
            timestamp=end_time.isoformat(),
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"查询处理失败: {e}", exc_info=True)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return QueryResponse(
            success=False,
            message=f"查询处理失败: {str(e)}",
            data={
                "query": request.query,
                "session_id": session_id,
                "error": str(e)
            },
            timestamp=end_time.isoformat(),
            execution_time=execution_time
        )

# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("API_DEBUG", "False").lower() == "true"
    
    logger.info(f"启动API服务: {host}:{port}")
    logger.info(f"调试模式: {debug}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 