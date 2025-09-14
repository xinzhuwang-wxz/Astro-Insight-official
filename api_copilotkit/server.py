#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astro-Insight CopilotKit FastAPI服务器

提供CopilotKit兼容的API接口，将Astro-Insight的专业功能
封装为标准化服务供前端调用。
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent

from api_copilotkit.agent import AstroAgent, astro_agent, get_astro_graph

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Astro-Insight CopilotKit API",
    description="天文科研助手CopilotKit集成API - 专业天文功能的前端接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态
astro_sdk: Optional[CopilotKitSDK] = None


# ==================== 数据模型 ====================

class AstroQueryRequest(BaseModel):
    """天文查询请求模型"""
    query: str = Field(..., description="用户查询内容", min_length=1)
    user_type: Optional[str] = Field(None, description="用户类型: amateur/professional")
    session_id: Optional[str] = Field(None, description="会话ID，用于继续对话")


class AstroQueryResponse(BaseModel):
    """天文查询响应模型"""
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
    copilotkit_status: str = Field(..., description="CopilotKit状态")


# ==================== 应用生命周期 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global astro_sdk
    
    try:
        logger.info("🚀 正在启动Astro-Insight CopilotKit服务...")
        
        # 初始化Astro代理
        logger.info("🤖 初始化Astro代理...")
        if not astro_agent.initialize():
            raise RuntimeError("Astro代理初始化失败")
        
        # 创建CopilotKit SDK
        logger.info("🔧 创建CopilotKit SDK...")
        astro_sdk = create_astro_sdk()
        
        logger.info("✅ Astro-Insight CopilotKit服务启动成功")
        
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise RuntimeError(f"无法启动CopilotKit服务: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("🛑 Astro-Insight CopilotKit服务正在关闭...")


# ==================== API端点 ====================

@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径，返回API信息"""
    return {
        "message": "Astro-Insight CopilotKit API 服务运行中",
        "version": "1.0.0",
        "description": "天文科研助手CopilotKit集成服务",
        "docs": "/docs",
        "status": "/status",
        "copilotkit": "/copilotkit",
        "health": "/health"
    }


@app.get("/status", response_model=SystemStatusResponse)
async def get_status():
    """获取系统状态"""
    try:
        # 检查Astro代理状态
        astro_status = "healthy" if astro_agent.initialized else "error"
        astro_message = "Astro代理运行正常" if astro_agent.initialized else "Astro代理未初始化"
        
        # 检查CopilotKit状态
        copilotkit_status = "healthy" if astro_sdk is not None else "error"
        
        overall_status = "healthy" if astro_status == "healthy" and copilotkit_status == "healthy" else "error"
        overall_message = "系统运行正常" if overall_status == "healthy" else "系统存在问题"
        
        return SystemStatusResponse(
            status=overall_status,
            message=overall_message,
            timestamp=datetime.now().isoformat(),
            copilotkit_status=copilotkit_status
        )
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return SystemStatusResponse(
            status="error",
            message=f"系统状态检查失败: {str(e)}",
            timestamp=datetime.now().isoformat(),
            copilotkit_status="unknown"
        )


@app.post("/query", response_model=AstroQueryResponse)
async def process_astro_query(request: AstroQueryRequest):
    """处理天文查询请求 - 直接调用Astro-Insight功能"""
    start_time = datetime.now()
    
    try:
        logger.info(f"🔍 处理天文查询: {request.query[:50]}...")
        
        if not astro_agent.initialized:
            raise HTTPException(
                status_code=503,
                detail="Astro代理未初始化，请稍后重试"
            )
        
        # 生成会话ID
        session_id = request.session_id or f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 构建用户上下文
        user_context = {}
        if request.user_type:
            user_context["user_type"] = request.user_type
        
        # 执行Astro-Insight工作流
        result_state = astro_agent.workflow.execute_workflow(
            session_id=session_id,
            user_input=request.query,
            user_context=user_context
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
        
        return AstroQueryResponse(
            success=True,
            message="天文查询处理成功",
            data=response_data,
            timestamp=end_time.isoformat(),
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"天文查询处理失败: {e}", exc_info=True)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return AstroQueryResponse(
            success=False,
            message=f"天文查询处理失败: {str(e)}",
            data={
                "query": request.query,
                "error": str(e)
            },
            timestamp=end_time.isoformat(),
            execution_time=execution_time
        )


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok", 
        "timestamp": datetime.now().isoformat(),
        "service": "Astro-Insight CopilotKit API",
        "astro_initialized": astro_agent.initialized,
        "copilotkit_ready": astro_sdk is not None
    }


# ==================== CopilotKit集成 ====================

def create_astro_sdk() -> CopilotKitSDK:
    """创建Astro-Insight CopilotKit SDK"""
    logger.info("🔧 创建Astro-Insight CopilotKit SDK...")
    
    # 获取Astro图实例
    astro_graph = get_astro_graph()
    
    # 创建LangGraph代理
    astro_langgraph_agent = LangGraphAgent(
        name="astro_insight_agent",
        description="专业的天文科研助手，能够回答天文问题、生成分析代码、提供科研建议",
        graph=astro_graph,
    )
    
    # 创建SDK
    sdk = CopilotKitSDK(
        agents=[astro_langgraph_agent],
    )
    
    logger.info("✅ CopilotKit SDK 创建成功")
    logger.info(f"   📝 代理名称: {astro_langgraph_agent.name}")
    logger.info(f"   📋 代理描述: {astro_langgraph_agent.description}")
    
    return sdk


# 添加CopilotKit端点
def setup_copilotkit_endpoints():
    """设置CopilotKit端点"""
    global astro_sdk
    
    if astro_sdk is not None:
        add_fastapi_endpoint(app, astro_sdk, "/copilotkit")
        logger.info("🔗 CopilotKit端点添加完成: /copilotkit")
        return True
    else:
        logger.warning("⚠️ 无法添加CopilotKit端点：SDK未初始化")
        return False


# ==================== 启动配置 ====================

def main():
    """启动CopilotKit服务器"""
    try:
        # 设置CopilotKit端点
        setup_copilotkit_endpoints()
        
        # 从环境变量获取配置
        host = os.getenv("ASTRO_API_HOST", "0.0.0.0")
        port = int(os.getenv("ASTRO_API_PORT", "8001"))
        debug = os.getenv("ASTRO_API_DEBUG", "False").lower() == "true"
        
        logger.info(f"🌐 启动Astro-Insight CopilotKit服务器...")
        logger.info(f"   📍 主机: {host}")
        logger.info(f"   🔌 端口: {port}")
        logger.info(f"   🔗 CopilotKit端点: http://{host}:{port}/copilotkit")
        logger.info(f"   📚 API文档: http://{host}:{port}/docs")
        logger.info(f"   🏥 健康检查: http://{host}:{port}/health")
        logger.info(f"   🔍 系统状态: http://{host}:{port}/status")
        logger.info("=" * 60)
        logger.info("🎉 服务器启动中... 按 Ctrl+C 停止")
        
        uvicorn.run(
            "server:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

