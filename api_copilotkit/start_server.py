#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astro-Insight CopilotKit 服务器启动脚本

提供便捷的服务器启动方式，支持不同的运行模式。
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Astro-Insight CopilotKit 服务器启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python start_server.py                    # 默认配置启动
  python start_server.py --port 8001       # 指定端口
  python start_server.py --debug            # 调试模式
  python start_server.py --host 127.0.0.1  # 指定主机
  python start_server.py --demo             # 演示模式
        """
    )
    
    parser.add_argument(
        "--host",
        default=os.getenv("ASTRO_API_HOST", "0.0.0.0"),
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("ASTRO_API_PORT", "8001")),
        help="服务器端口 (默认: 8001)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("ASTRO_API_DEBUG", "False").lower() == "true",
        help="启用调试模式 (自动重载)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="运行演示模式 (包含详细的启动信息)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="指定配置文件路径"
    )
    
    return parser.parse_args()


def check_environment():
    """检查运行环境"""
    print("🔧 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查conf.yaml配置文件
    project_root = Path(__file__).parent.parent
    conf_file = project_root / "conf.yaml"
    if not conf_file.exists():
        print(f"❌ 配置文件不存在: {conf_file}")
        print("请确保项目根目录存在conf.yaml配置文件")
        return False
    
    print(f"✅ 找到配置文件: {conf_file}")
    
    # 尝试加载配置
    try:
        from src.config.loader import load_yaml_config
        config = load_yaml_config()
        basic_model_config = config.get("BASIC_MODEL", {})
        
        if not basic_model_config:
            print("❌ conf.yaml中缺少BASIC_MODEL配置")
            return False
            
        print(f"✅ 配置加载成功")
        print(f"   模型: {basic_model_config.get('model', 'unknown')}")
        print(f"   端点: {basic_model_config.get('base_url', 'unknown')}")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    # 检查项目结构
    required_files = [
        "src/workflow.py",
        "src/config/loader.py",
        "conf.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少必要的项目文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 项目结构检查通过")
    
    return True


def main():
    """主函数"""
    args = parse_arguments()
    
    print("🚀 Astro-Insight CopilotKit 服务器启动器")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        sys.exit(1)
    
    print("\n✅ 环境检查通过")
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 显示配置信息
    print(f"\n🌐 服务器配置:")
    print(f"   📍 主机: {args.host}")
    print(f"   🔌 端口: {args.port}")
    print(f"   🔧 调试模式: {args.debug}")
    print(f"   📊 日志级别: {args.log_level}")
    print(f"   📁 配置文件: {args.config or '默认'}")
    
    if args.demo:
        print(f"   🎭 运行模式: 演示模式")
    else:
        print(f"   🎭 运行模式: 生产模式")
    
    print(f"\n🔗 服务端点:")
    print(f"   CopilotKit: http://{args.host}:{args.port}/copilotkit")
    print(f"   API文档: http://{args.host}:{args.port}/docs")
    print(f"   健康检查: http://{args.host}:{args.port}/health")
    print(f"   系统状态: http://{args.host}:{args.port}/status")
    
    print("\n" + "=" * 60)
    
    try:
        if args.demo:
            # 演示模式
            print("🎉 启动演示服务器...")
            from api_copilotkit.demo import main as demo_main
            # 设置环境变量
            os.environ["ASTRO_API_HOST"] = args.host
            os.environ["ASTRO_API_PORT"] = str(args.port)
            os.environ["ASTRO_API_DEBUG"] = str(args.debug)
            demo_main()
        else:
            # 生产模式
            print("🎉 启动生产服务器...")
            import uvicorn
            from api_copilotkit.server import app, setup_copilotkit_endpoints, astro_agent
            
            # 初始化Astro代理
            print("🤖 初始化Astro代理...")
            if not astro_agent.initialize():
                print("❌ Astro代理初始化失败")
                sys.exit(1)
            
            # 设置CopilotKit端点
            setup_copilotkit_endpoints()
            
            # 启动服务器
            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                reload=args.debug,
                log_level=args.log_level.lower()
            )
            
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

