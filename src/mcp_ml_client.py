
#!/usr/bin/env python3
"""
MCP ML客户端 - 专门用于调用mcp_ml服务器的机器学习功能

这个客户端用于与mcp_ml服务器通信，执行机器学习相关的任务：
- 模型训练
- 图像分类
- 结果分析
"""

import asyncio
import logging
import os
import subprocess
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPMLClient:
    """MCP ML客户端，用于调用mcp_ml服务器"""
    
    def __init__(self):
        self.server_process = None
        self.initialized = False
        self.server_path = None
        
    async def start_server(self):
        """启动mcp_ml服务器"""
        try:
            # 获取mcp_ml目录路径
            current_dir = Path(__file__).parent
            self.server_path = current_dir.parent / "mcp_ml"
            
            if not self.server_path.exists():
                raise FileNotFoundError(f"mcp_ml目录不存在: {self.server_path}")
            
            logger.info(f"启动MCP ML服务器: {self.server_path}")
            
            # 启动MCP服务器子进程（使用虚拟环境）
            if os.name == 'nt':  # Windows
                python_exe = str(self.server_path / ".venv" / "Scripts" / "python.exe")
            else:  # Unix/Linux
                python_exe = str(self.server_path / ".venv" / "bin" / "python")
            
            # 检查虚拟环境是否存在
            if not os.path.exists(python_exe):
                # 回退到系统Python
                python_exe = 'python'
                logger.warning("虚拟环境不存在，使用系统Python")
            
            self.server_process = subprocess.Popen(
                [python_exe, 'main.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.server_path)
            )
            
            logger.info("MCP ML服务器子进程已启动")
            
            # 等待服务器启动
            await asyncio.sleep(3)
            
            # 初始化MCP连接
            await self._initialize_connection()
            
            return True
            
        except Exception as e:
            logger.error(f"启动MCP ML服务器失败: {str(e)}")
            return False
    
    async def _initialize_connection(self):
        """初始化MCP连接"""
        try:
            # 发送MCP初始化请求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-ml-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # 发送初始化请求
            init_json = json.dumps(init_request) + "\n"
            self.server_process.stdin.write(init_json)
            self.server_process.stdin.flush()
            
            # 等待响应
            await asyncio.sleep(1)
            
            # 发送initialized通知
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            initialized_json = json.dumps(initialized_notification) + "\n"
            self.server_process.stdin.write(initialized_json)
            self.server_process.stdin.flush()
            
            self.initialized = True
            logger.info("MCP ML连接初始化完成")
            
        except Exception as e:
            logger.error(f"MCP ML连接初始化失败: {str(e)}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """调用MCP ML工具"""
        try:
            if not self.initialized:
                return "MCP ML连接未初始化"
            
            if arguments is None:
                arguments = {}
            
            # 构建MCP请求
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # 发送请求到MCP服务器
            if self.server_process and self.server_process.stdin:
                request_json = json.dumps(request) + "\n"
                self.server_process.stdin.write(request_json)
                self.server_process.stdin.flush()
                
                # 读取响应
                response_line = self.server_process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        # 处理MCP工具调用结果
                        result = response["result"]
                        if "content" in result and isinstance(result["content"], list) and len(result["content"]) > 0:
                            # 提取文本内容
                            content = result["content"][0].get("text", str(result))
                            return content
                        else:
                            return str(result)
                    elif "error" in response:
                        return f"错误: {response['error']}"
                    else:
                        return "未知响应格式"
                else:
                    return "无响应"
            else:
                return "MCP ML服务器未运行"
                
        except Exception as e:
            logger.error(f"调用MCP ML工具失败: {str(e)}")
            return f"工具调用失败: {str(e)}"
    
    async def run_pipeline(self) -> str:
        """运行完整的ML训练流程"""
        logger.info("开始运行ML训练流程...")
        result = await self.call_tool("run_pipeline")
        logger.info("ML训练流程完成")
        return result
    
    async def stop_server(self):
        """停止MCP ML服务器"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                logger.info("MCP ML服务器子进程已停止")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.warning("强制终止MCP ML服务器子进程")
            except Exception as e:
                logger.error(f"停止MCP ML服务器时出错: {str(e)}")
    
    def get_available_tools(self) -> list:
        """获取可用工具列表"""
        return ["run_pipeline"]

class MCPMLClientWrapper:
    """MCP ML客户端包装器，提供同步接口"""
    
    def __init__(self):
        self.client = MCPMLClient()
        self.initialized = False
    
    def initialize(self):
        """同步初始化"""
        try:
            result = asyncio.run(self.client.start_server())
            self.initialized = result
            return result
        except Exception as e:
            logger.error(f"初始化MCP ML客户端失败: {str(e)}")
            return False
    
    def run_pipeline(self) -> str:
        """同步运行ML训练流程"""
        if not self.initialized:
            if not self.initialize():
                return "MCP ML客户端初始化失败"
        
        try:
            result = asyncio.run(self.client.run_pipeline())
            return result
        except Exception as e:
            logger.error(f"运行ML训练流程失败: {str(e)}")
            return f"ML训练流程失败: {str(e)}"
    
    def close(self):
        """关闭客户端"""
        if self.initialized:
            asyncio.run(self.client.stop_server())
            self.initialized = False

# 全局客户端实例
_ml_client = None

def get_ml_client() -> MCPMLClientWrapper:
    """获取全局ML客户端实例"""
    global _ml_client
    if _ml_client is None:
        _ml_client = MCPMLClientWrapper()
    return _ml_client

def run_ml_pipeline() -> str:
    """
    运行ML训练流程的便捷函数
    
    Returns:
        str: 训练结果
    """
    client = get_ml_client()
    return client.run_pipeline()

def close_ml_client():
    """关闭全局ML客户端"""
    global _ml_client
    if _ml_client:
        _ml_client.close()
        _ml_client = None

# 测试函数
async def test_ml_client():
    """测试MCP ML客户端"""
    print("=" * 60)
    print("🧪 测试MCP ML客户端")
    print("=" * 60)
    
    client = MCPMLClient()
    
    try:
        # 启动服务器
        print("🚀 启动MCP ML服务器...")
        if await client.start_server():
            print("✅ MCP ML服务器启动成功")
            
            # 测试工具调用
            print("🔧 测试工具调用...")
            result = await client.run_pipeline()
            print(f"📋 训练结果: {result[:200]}...")
            
        else:
            print("❌ MCP ML服务器启动失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    finally:
        # 清理
        await client.stop_server()
        print("🧹 清理完成")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_ml_client())
