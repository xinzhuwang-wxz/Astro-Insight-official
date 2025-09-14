from mcp.server.fastmcp import FastMCP
import logging
import json
import argparse
import signal
import sys
from typing import Optional, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the MCP server object
mcp = FastMCP()

# 全局执行器实例
_global_executor = None

import yaml
from data_loading import download_data
from data_preprocessing import load_and_preprocess_data, create_dataset
from model_training import train_model
from result_analysis import evaluate_model
import tensorflow as tf
from config_generator import ConfigGenerator

@mcp.tool()
def run_pipeline():
    """
    Main pipeline script to run the full workflow.
    """
    # Define the path to the configuration file
    config_path = 'config/config.yaml'
    
    # Load configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Step 1: Download data
    # The download path is managed by kagglehub, but we can ensure it's downloaded.
    # download_data()

    # Step 2: Load and preprocess data
    print("Loading and preprocessing data...")
    train_df, val_df, test_df, label_encoder = load_and_preprocess_data(config)
    train_dataset = create_dataset(train_df, config, is_training=True)
    val_dataset = create_dataset(val_df, config, is_training=False)
    test_dataset = create_dataset(test_df, config, is_training=False)
    print("Data ready for training.")

    # Step 3: Train the model
    print("Starting model training...")
    # Handle TPU initialization
    try:
        tpu = tf.distribute.cluster_resolver.TPUClusterResolver()
        tf.config.experimental_connect_to_cluster(tpu)
        tf.tpu.experimental.initialize_tpu_system(tpu)
        strategy = tf.distribute.TPUStrategy(tpu)
        print("TPU initialized successfully! Training with TPU.")
        with strategy.scope():
            model, history = train_model(config)
    except ValueError:
        print("TPU not found. Training on CPU/GPU.")
        model, history = train_model(config)
    
    # Step 4: Evaluate the model and analyze results
    print("Evaluating model and generating analysis...")
    # Load the best performing model saved by ModelCheckpoint
    best_model = tf.keras.models.load_model(config['model_training']['checkpoint']['filepath'])
    evaluate_model(best_model, history, test_dataset, label_encoder, config)
    
    print("Pipeline finished successfully.")


@mcp.tool()
def run_parallel_pipeline(config_paths: str = None, session_name: str = None):
    """
    并行运行多个ML训练流程，使用不同的配置文件。
    支持GPU显存管理和进程监控。
    
    Args:
        config_paths: 配置文件路径列表，用逗号分隔。例如: "config/config1.yaml,config/config2.yaml,config/config3.yaml"
        session_name: 会话名称，用于创建输出目录。如果不提供，将自动生成。
    
    Returns:
        dict: 执行结果，包含状态、消息和结果数据
    """
    global _global_executor
    
    try:
        # 导入并行执行器
        from parallel_executor import ParallelMLExecutor
        
        # 处理配置文件路径
        if config_paths is None:
            # 默认使用config1和config2
            configs = ["config/config1.yaml", "config/config2.yaml"]
        else:
            # 解析传入的配置文件路径
            configs = [path.strip() for path in config_paths.split(',') if path.strip()]
            
            # 验证配置文件是否存在
            import os
            for config in configs:
                if not os.path.exists(config):
                    return {
                        "status": "error",
                        "message": f"配置文件不存在: {config}",
                        "error": f"File not found: {config}"
                    }
        
        logger.info(f"开始并行ML训练流程，配置文件: {configs}")
        logger.info(f"会话名称: {session_name}")
        
        # 创建并行执行器
        _global_executor = ParallelMLExecutor(configs, session_name=session_name)
        
        # 运行并行流程
        results = _global_executor.run_parallel()
        
        logger.info("并行ML训练流程完成")
        return {
            "status": "success",
            "message": "并行ML训练流程执行完成",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"并行ML训练流程失败: {e}")
        return {
            "status": "error",
            "message": f"并行ML训练流程失败: {str(e)}",
            "error": str(e)
        }


@mcp.tool()
def get_parallel_status():
    """
    获取并行ML训练流程的当前状态。
    """
    global _global_executor
    
    try:
        if _global_executor is None:
            return {
                "status": "info",
                "message": "没有正在运行的并行执行器",
                "note": "请先运行 run_parallel_pipeline 来启动并行流程"
            }
        
        # 获取执行器状态
        status = _global_executor.get_status()
        
        return {
            "status": "success",
            "message": "成功获取并行执行器状态",
            "executor_status": status
        }
        
    except Exception as e:
        logger.error(f"获取并行状态失败: {e}")
        return {
            "status": "error",
            "message": f"获取并行状态失败: {str(e)}",
            "error": str(e)
        }


@mcp.tool()
def generate_config_from_description(description: str, config_name: str = None):
    """
    根据自然语言描述生成ML训练配置文件
    
    Args:
        description: 自然语言描述，描述想要的ML训练配置
        config_name: 配置名称，用于生成文件名。如果不提供，将自动生成
    
    Returns:
        dict: 执行结果，包含状态、消息和生成的配置文件路径
    """
    try:
        logger.info(f"开始生成配置: {description}")
        
        # 创建配置生成器
        generator = ConfigGenerator()
        
        # 生成配置
        config = generator.generate_config(description, config_name)
        
        # 生成文件名
        if config_name is None:
            import time
            timestamp = int(time.time())
            config_name = f"generated_config_{timestamp}"
        
        # 保存配置到config目录
        config_path = f"config/{config_name}.yaml"
        saved_path = generator.save_config(config, config_path)
        
        logger.info(f"配置生成成功: {saved_path}")
        return {
            "status": "success",
            "message": f"配置生成成功: {config_name}",
            "config_path": saved_path,
            "config_name": config_name
        }
        
    except Exception as e:
        logger.error(f"配置生成失败: {e}")
        return {
            "status": "error",
            "message": f"配置生成失败: {str(e)}",
            "error": str(e)
        }


@mcp.tool()
def generate_multiple_configs_from_descriptions(descriptions: str, output_dir: str = "config"):
    """
    根据多个自然语言描述生成多个ML训练配置文件
    
    Args:
        descriptions: 配置描述列表，用分号(;)分隔。例如: "简单CNN模型，batch_size=32;复杂深度网络，batch_size=16;轻量级模型，batch_size=64"
        output_dir: 输出目录，默认为"config"
    
    Returns:
        dict: 执行结果，包含状态、消息和生成的配置文件路径列表
    """
    try:
        # 解析描述列表
        description_list = [desc.strip() for desc in descriptions.split(';') if desc.strip()]
        
        if not description_list:
            return {
                "status": "error",
                "message": "没有提供有效的配置描述",
                "error": "Empty descriptions"
            }
        
        logger.info(f"开始生成 {len(description_list)} 个配置")
        
        # 创建配置生成器
        generator = ConfigGenerator()
        
        # 生成多个配置
        config_paths = generator.generate_multiple_configs(description_list, output_dir)
        
        if not config_paths:
            return {
                "status": "error",
                "message": "没有成功生成任何配置文件",
                "error": "No configs generated"
            }
        
        logger.info(f"成功生成 {len(config_paths)} 个配置文件")
        return {
            "status": "success",
            "message": f"成功生成 {len(config_paths)} 个配置文件",
            "config_paths": config_paths,
            "count": len(config_paths)
        }
        
    except Exception as e:
        logger.error(f"批量配置生成失败: {e}")
        return {
            "status": "error",
            "message": f"批量配置生成失败: {str(e)}",
            "error": str(e)
        }


@mcp.tool()
def generate_and_run_parallel_experiments(descriptions: str, session_name: str = None):
    """
    根据自然语言描述生成多个配置文件并立即开始并行训练实验
    
    Args:
        descriptions: 配置描述列表，用分号(;)分隔。例如: "简单CNN模型，batch_size=32;复杂深度网络，batch_size=16;轻量级模型，batch_size=64"
        session_name: 会话名称，用于创建输出目录。如果不提供，将自动生成
    
    Returns:
        dict: 执行结果，包含状态、消息和实验结果
    """
    global _global_executor
    
    try:
        logger.info(f"开始生成并运行并行实验: {descriptions}")
        
        # 1. 生成多个配置文件
        config_result = generate_multiple_configs_from_descriptions(descriptions)
        
        if config_result["status"] != "success":
            return {
                "status": "error",
                "message": f"配置生成失败: {config_result['message']}",
                "error": config_result.get("error", "Config generation failed")
            }
        
        config_paths = config_result["config_paths"]
        logger.info(f"成功生成 {len(config_paths)} 个配置文件")
        
        # 2. 启动并行训练
        from parallel_executor import ParallelMLExecutor
        
        # 创建并行执行器
        _global_executor = ParallelMLExecutor(config_paths, session_name=session_name)
        
        # 运行并行流程
        results = _global_executor.run_parallel()
        
        logger.info("并行实验完成")
        return {
            "status": "success",
            "message": f"成功生成 {len(config_paths)} 个配置并完成并行训练",
            "generated_configs": config_paths,
            "experiment_results": results
        }
        
    except Exception as e:
        logger.error(f"生成并运行并行实验失败: {e}")
        return {
            "status": "error",
            "message": f"生成并运行并行实验失败: {str(e)}",
            "error": str(e)
        }


@mcp.tool()
def stop_parallel_execution():
    """
    停止正在运行的并行ML训练流程。
    """
    global _global_executor
    
    try:
        if _global_executor is None:
            return {
                "status": "info",
                "message": "没有正在运行的并行执行器",
                "note": "请先运行 run_parallel_pipeline 来启动并行流程"
            }
        
        # 停止执行器
        _global_executor.stop_execution()
        
        return {
            "status": "success",
            "message": "并行执行器已停止"
        }
        
    except Exception as e:
        logger.error(f"停止并行执行失败: {e}")
        return {
            "status": "error",
            "message": f"停止并行执行失败: {str(e)}",
            "error": str(e)
        }


def main(argv: Optional[List[str]] = None):
    """Entry point for running the MCP server.

    Accepts a --mode argument (default 'stdio') for flexibility.
    Installs simple signal handlers to enable graceful shutdown.
    """
    parser = argparse.ArgumentParser(description="CNN MCP server")
    parser.add_argument(
        "--mode",
        default="stdio",
        help="MCP run mode (default: stdio).",
    )
    args = parser.parse_args(argv)

    logger.info("Starting CNN server (mode=%s)", args.mode)

    def _shutdown(signum, frame):
        logger.info("Received signal %s, shutting down", signum)
        # allow Clean shutdown if MCP supports it; otherwise exit
        try:
            # If mcp has a stop/close method, call it here (best-effort)
            stop = getattr(mcp, "stop", None)
            if callable(stop):
                stop()
        finally:
            sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        mcp.run(args.mode)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception:
        logger.exception("MCP server exited with an error")
        raise

if __name__ == "__main__":
    main()
