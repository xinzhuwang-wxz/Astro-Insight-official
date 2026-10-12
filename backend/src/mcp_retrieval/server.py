#!/usr/bin/env python3
"""
天体物理学TAP查询系统 - MCP Server

提供天体物理学数据查询的MCP服务器实现
使用Simbad TAP服务进行天体数据查询
"""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# 导入查询工具
import sys
import os
sys.path.append(os.path.dirname(__file__))

from tools import (
    get_object_by_identifier,
    get_bibliographic_data,
    search_objects_by_coordinates
)
from tap_client import test_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("astrophysics-tap-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    列出可用的工具
    """
    return [
        Tool(
            name="get_object_by_identifier",
            description="根据天体标识符获取基础信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_id": {
                        "type": "string",
                        "description": "天体标识符，如 'M13', 'NGC 6205' 等"
                    }
                },
                "required": ["object_id"]
            }
        ),
        Tool(
            name="get_bibliographic_data",
            description="获取天体的参考文献信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_id": {
                        "type": "string",
                        "description": "天体标识符，如 'M13', 'NGC 6205' 等"
                    }
                },
                "required": ["object_id"]
            }
        ),
        Tool(
            name="search_objects_by_coordinates",
            description="根据坐标搜索附近的天体",
            inputSchema={
                "type": "object",
                "properties": {
                    "ra": {
                        "type": "number",
                        "description": "赤经 (度)"
                    },
                    "dec": {
                        "type": "number",
                        "description": "赤纬 (度)"
                    },
                    "radius": {
                        "type": "number",
                        "description": "搜索半径 (度)，默认0.1度",
                        "default": 0.1
                    }
                },
                "required": ["ra", "dec"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    处理工具调用
    """
    try:
        logger.info(f"工具调用: {name}, 参数: {arguments}")
        
        if name == "get_object_by_identifier":
            object_id = arguments.get("object_id")
            if not object_id:
                logger.error("缺少object_id参数")
                return [TextContent(type="text", text="错误: 缺少object_id参数")]
            
            logger.info(f"查询天体: {object_id}")
            result = get_object_by_identifier(object_id)
            logger.info(f"查询结果: {result}")
            return [TextContent(type="text", text=str(result))]
            
        elif name == "get_bibliographic_data":
            object_id = arguments.get("object_id")
            if not object_id:
                return [TextContent(type="text", text="错误: 缺少object_id参数")]
            
            result = get_bibliographic_data(object_id)
            return [TextContent(type="text", text=str(result))]
            
        elif name == "search_objects_by_coordinates":
            ra = arguments.get("ra")
            dec = arguments.get("dec")
            radius = arguments.get("radius", 0.1)
            
            if ra is None or dec is None:
                return [TextContent(type="text", text="错误: 缺少ra或dec参数")]
            
            result = search_objects_by_coordinates(ra, dec, radius)
            return [TextContent(type="text", text=str(result))]
            
        else:
            return [TextContent(type="text", text=f"错误: 未知工具 {name}")]
            
    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        return [TextContent(type="text", text=f"错误: {str(e)}")]

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """
    列出可用的资源
    """
    logger.info("列出资源被调用")
    return [
        Resource(
            uri="simbad://info",
            name="Simbad TAP服务信息",
            description="关于Simbad TAP服务的基本信息",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    读取资源内容
    """
    # 将 AnyUrl 对象转换为字符串
    uri_str = str(uri)
    logger.info(f"读取资源被调用: {uri_str}")
    
    if uri_str == "simbad://info":
        content = """
Simbad TAP服务信息
==================

服务URL: https://simbad.cds.unistra.fr/simbad/sim-tap/sync
描述: 这是一个连接到Simbad天体数据库的TAP (Table Access Protocol) 服务

可用功能:
1. 根据天体标识符查询基础信息
2. 获取天体的参考文献数据
3. 根据坐标搜索附近的天体

数据来源: CDS (Centre de Données astronomiques de Strasbourg)
"""
        logger.info(f"成功读取资源: {uri_str}")
        return content
    else:
        logger.error(f"未知资源: {uri_str}")
        raise ValueError(f"未知资源: {uri_str}")

async def main():
    """
    主函数
    """
    # 测试TAP连接
    logger.info("启动天体物理学TAP查询MCP服务器...")
    
    try:
        # 测试TAP服务连接
        if await asyncio.get_event_loop().run_in_executor(None, test_connection):
            logger.info("TAP服务连接测试成功")
        else:
            logger.warning("TAP服务连接测试失败，但服务器将继续运行")
    except Exception as e:
        logger.error(f"TAP连接测试出错: {e}")
    
    # 启动服务器
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                 server_name="astrophysics-tap-server",
                 server_version="1.0.0",
                 capabilities=server.get_capabilities(
                     notification_options=NotificationOptions(),
                     experimental_capabilities={}
                 )
             )
        )

if __name__ == "__main__":
    asyncio.run(main())