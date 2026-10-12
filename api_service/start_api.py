#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务启动脚本
专注于核心功能，便于学习和前端对接
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("api_service.log", encoding="utf-8")
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="天文科研Agent API服务")
    
    # 服务器配置
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="开发模式，自动重载")
    
    # 日志配置
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("天文科研Agent API服务")
    logger.info("=" * 50)
    logger.info(f"服务器地址: {args.host}:{args.port}")
    logger.info(f"开发模式: {'是' if args.reload else '否'}")
    logger.info(f"日志级别: {args.log_level}")
    logger.info("=" * 50)
    logger.info("API文档地址:")
    logger.info(f"  - Swagger UI: http://{args.host}:{args.port}/docs")
    logger.info(f"  - ReDoc: http://{args.host}:{args.port}/redoc")
    logger.info("=" * 50)
    
    try:
        # 切换到api_service目录
        api_service_dir = Path(__file__).parent
        os.chdir(api_service_dir)
        
        # 启动服务器
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            access_log=True,
            app_dir=str(api_service_dir)
        )
    except KeyboardInterrupt:
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
