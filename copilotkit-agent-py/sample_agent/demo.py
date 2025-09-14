"""Demo"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv 
load_dotenv()

print("🚀 CopilotKit Demo 启动中...")
print("=" * 50)

# pylint: disable=wrong-import-position
from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent

print("📦 导入 agent 模块...")
from agent import graph
print("✅ Agent 模块导入成功")
print(f"🕸️ Graph 类型: {type(graph)}")

app = FastAPI()
print("🌐 FastAPI 应用初始化完成")

sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="quickstart_agent",
            description="Quickstart agent.",
            graph=graph,
        ),
    ],
)
print("🤖 CopilotKit SDK 初始化完成")
print("   📝 Agent 名称: quickstart_agent")
print("   📋 Agent 描述: Quickstart agent.")

add_fastapi_endpoint(app, sdk, "/copilotkit")
print("🔗 FastAPI 端点添加完成: /copilotkit")

# add new route for health check
@app.get("/health")
def health():
    """Health check."""
    print("🏥 健康检查端点被访问")
    return {"status": "ok"}

print("🏥 健康检查端点添加完成: /health")


def main():
    """Run the uvicorn server."""
    try:
        port = int(os.getenv("PORT", "8000"))
        print(f"🌐 启动服务器...")
        print(f"   📍 主机: 0.0.0.0")
        print(f"   🔌 端口: {port}")
        print(f"   🔗 CopilotKit 端点: http://localhost:{port}/copilotkit")
        print(f"   🏥 健康检查: http://localhost:{port}/health")
        print("=" * 50)
        print("🎉 服务器启动中... 按 Ctrl+C 停止")
        
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()