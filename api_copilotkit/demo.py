#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astro-Insight CopilotKit 演示服务器

提供完整的演示环境，展示Astro-Insight与CopilotKit的集成功能。
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import uvicorn

from api_copilotkit.server import app, setup_copilotkit_endpoints, astro_agent

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """运行演示服务器"""
    try:
        print("🚀 Astro-Insight CopilotKit 演示服务器")
        print("=" * 60)
        
        # 检查配置
        print("🔧 检查配置...")
        
        # 检查conf.yaml文件是否存在
        conf_file = project_root / "conf.yaml"
        if not conf_file.exists():
            print(f"❌ 配置文件不存在: {conf_file}")
            print("请确保项目根目录存在conf.yaml配置文件")
            return
        
        print(f"✅ 找到配置文件: {conf_file}")
        
        # 尝试加载配置
        try:
            from src.config.loader import load_yaml_config
            config = load_yaml_config()
            basic_model_config = config.get("BASIC_MODEL", {})
            
            if not basic_model_config:
                print("❌ conf.yaml中缺少BASIC_MODEL配置")
                return
                
            print(f"✅ 配置加载成功")
            print(f"   模型: {basic_model_config.get('model', 'unknown')}")
            print(f"   端点: {basic_model_config.get('base_url', 'unknown')}")
            
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return
        
        # 初始化Astro代理
        print("🤖 初始化Astro代理...")
        if not astro_agent.initialize():
            print("❌ Astro代理初始化失败")
            return
        
        print("✅ Astro代理初始化成功")
        
        # 设置CopilotKit端点
        print("🔗 设置CopilotKit端点...")
        try:
            setup_copilotkit_endpoints()
            print("✅ CopilotKit端点设置完成")
        except Exception as e:
            print(f"⚠️ CopilotKit端点设置失败: {e}")
            print("   服务器仍可启动，但CopilotKit功能可能不可用")
        
        # 获取服务器配置
        host = os.getenv("ASTRO_API_HOST", "0.0.0.0")
        port = int(os.getenv("ASTRO_API_PORT", "8001"))
        debug = os.getenv("ASTRO_API_DEBUG", "True").lower() == "true"
        
        print("\n🌐 服务器配置:")
        print(f"   📍 主机: {host}")
        print(f"   🔌 端口: {port}")
        print(f"   🔧 调试模式: {debug}")
        print(f"   🔗 CopilotKit端点: http://{host}:{port}/copilotkit")
        print(f"   📚 API文档: http://{host}:{port}/docs")
        print(f"   🏥 健康检查: http://{host}:{port}/health")
        print(f"   🔍 系统状态: http://{host}:{port}/status")
        
        print("\n" + "=" * 60)
        print("🎉 演示服务器启动中...")
        print("💡 提示: 按 Ctrl+C 停止服务器")
        print("=" * 60)
        
        # 启动服务器
        uvicorn.run(
            "api_copilotkit.server:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 演示服务器已停止")
    except Exception as e:
        print(f"❌ 演示服务器启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

