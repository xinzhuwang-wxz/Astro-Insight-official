"""
测试3个模型并行训练功能
验证新的参数化 run_parallel_pipeline 工具
"""
import os
import sys
import logging
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parallel_executor import ParallelMLExecutor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_three_parallel_models():
    """测试3个模型并行训练"""
    print("=" * 80)
    print("🚀 3个模型并行训练测试")
    print("=" * 80)
    
    try:
        # 1. 显示配置信息
        configs = [
            "C:/Users/32830/Desktop/heckathon/Astro-Insight/src/mcp_ml/config/config.yaml",  # batch_size: 64, 基础网络
            "C:/Users/32830/Desktop/heckathon/Astro-Insight/src/mcp_ml/config/config1.yaml",  # batch_size: 32, 基础网络
            "C:/Users/32830/Desktop/heckathon/Astro-Insight/src/mcp_ml/config/config2.yaml",
            "C:/Users/32830/Desktop/heckathon/Astro-Insight/src/mcp_ml/config/config3.yaml",   # batch_size: 16, 更深网络, RMSprop优化器
        ]
        
        print(f"\n📋 使用配置文件:")
        for i, config in enumerate(configs):
            print(f"   进程 {i}: {config}")
        
        # 2. 创建并行执行器
        session_name = "three_parallel_test"
        print(f"\n🔧 创建并行执行器 (会话: {session_name})...")
        executor = ParallelMLExecutor(configs, session_name=session_name)
        
        # 3. 显示会话信息
        session_info = executor.output_manager.get_session_info()
        print(f"\n📁 会话信息:")
        print(f"   会话ID: {session_info['session_id']}")
        print(f"   会话目录: {session_info['session_dir']}")
        print(f"   创建时间: {session_info['created_at']}")
        
        # 4. 开始并行训练
        print(f"\n🏃 开始3个模型并行训练...")
        start_time = time.time()
        
        results = executor.run_parallel()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 5. 显示训练结果
        print(f"\n✅ 训练完成！耗时: {duration:.2f}秒")
        print("=" * 80)
        print("📈 训练结果摘要")
        print("=" * 80)
        
        execution_summary = results.get('execution_summary', {})
        print(f"总进程数: {execution_summary.get('total_processes', 0)}")
        print(f"成功进程: {execution_summary.get('successful_processes', 0)}")
        print(f"失败进程: {execution_summary.get('failed_processes', 0)}")
        print(f"会话目录: {execution_summary.get('session_dir', 'N/A')}")
        
        # 6. 详细文件分析
        print(f"\n🔍 详细文件分析:")
        session_dir = execution_summary.get('session_dir')
        if session_dir and os.path.exists(session_dir):
            
            # 分析每个目录
            directories = {
                'models': '🤖 模型文件',
                'logs': '📝 日志文件', 
                'images': '🖼️ 图片文件',
                'configs': '⚙️ 配置文件',
                'results': '📊 结果文件',
                'temp': '🗑️ 临时文件'
            }
            
            total_files = 0
            total_size = 0
            
            for dir_name, dir_desc in directories.items():
                dir_path = os.path.join(session_dir, dir_name)
                if os.path.exists(dir_path):
                    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
                    dir_size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in files)
                    
                    print(f"\n   {dir_desc} ({dir_name}/):")
                    print(f"     文件数量: {len(files)}")
                    print(f"     总大小: {dir_size / (1024 * 1024):.1f} MB")
                    
                    if files:
                        for file in files[:3]:  # 只显示前3个文件
                            file_path = os.path.join(dir_path, file)
                            file_size = os.path.getsize(file_path) / (1024 * 1024)
                            print(f"       📄 {file} ({file_size:.1f} MB)")
                        if len(files) > 3:
                            print(f"       ... 还有 {len(files) - 3} 个文件")
                    else:
                        print("       (空目录)")
                    
                    total_files += len(files)
                    total_size += dir_size
                else:
                    print(f"\n   {dir_desc} ({dir_name}/): 目录不存在")
            
            print(f"\n📊 总体统计:")
            print(f"   总文件数: {total_files}")
            print(f"   总大小: {total_size / (1024 * 1024):.1f} MB")
        
        # 7. 验证模型文件
        print(f"\n✅ 模型文件验证:")
        if session_dir and os.path.exists(session_dir):
            models_dir = os.path.join(session_dir, 'models')
            if os.path.exists(models_dir):
                model_files = [f for f in os.listdir(models_dir) if f.endswith('.keras')]
                if model_files:
                    print(f"   ✅ 找到 {len(model_files)} 个模型文件:")
                    for model_file in model_files:
                        file_path = os.path.join(models_dir, model_file)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)
                        print(f"      🤖 {model_file} ({file_size:.1f} MB)")
                else:
                    print("   ❌ 没有找到模型文件")
            else:
                print("   ❌ Models目录不存在")
        
        # 8. 验证图片文件
        print(f"\n🖼️ 图片文件验证:")
        if session_dir and os.path.exists(session_dir):
            images_dir = os.path.join(session_dir, 'images')
            if os.path.exists(images_dir):
                image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
                if image_files:
                    print(f"   ✅ 找到 {len(image_files)} 个图片文件:")
                    
                    # 按类型分组显示
                    training_history_files = [f for f in image_files if 'training_history' in f]
                    confusion_matrix_files = [f for f in image_files if 'confusion_matrix' in f]
                    
                    print(f"      📈 训练历史图片 ({len(training_history_files)} 个):")
                    for img_file in training_history_files:
                        file_path = os.path.join(images_dir, img_file)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)
                        print(f"         🖼️ {img_file} ({file_size:.1f} MB)")
                    
                    print(f"      📊 混淆矩阵图片 ({len(confusion_matrix_files)} 个):")
                    for img_file in confusion_matrix_files:
                        file_path = os.path.join(images_dir, img_file)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)
                        print(f"         🖼️ {img_file} ({file_size:.1f} MB)")
                else:
                    print("   ❌ 没有找到图片文件")
            else:
                print("   ❌ Images目录不存在")
        
        print("\n" + "=" * 80)
        print("🎉 3个模型并行训练测试完成！")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameterized_tool():
    """测试参数化的 run_parallel_pipeline 工具"""
    print("\n" + "=" * 80)
    print("🔧 测试参数化的 run_parallel_pipeline 工具")
    print("=" * 80)
    
    try:
        # 模拟调用参数化的工具
        from server import run_parallel_pipeline
        
        # 测试1: 使用默认配置
        print("\n📋 测试1: 使用默认配置")
        result1 = run_parallel_pipeline()
        print(f"   结果: {result1['status']}")
        print(f"   消息: {result1['message']}")
        
        # 测试2: 使用2个配置文件
        print("\n📋 测试2: 使用2个配置文件")
        configs_2 = "config/config1.yaml,config/config2.yaml"
        result2 = run_parallel_pipeline(config_paths=configs_2, session_name="test_2_configs")
        print(f"   结果: {result2['status']}")
        print(f"   消息: {result2['message']}")
        
        # 测试3: 使用3个配置文件
        print("\n📋 测试3: 使用3个配置文件")
        configs_3 = "config/config1.yaml,config/config2.yaml,config/config3.yaml"
        result3 = run_parallel_pipeline(config_paths=configs_3, session_name="test_3_configs")
        print(f"   结果: {result3['status']}")
        print(f"   消息: {result3['message']}")
        
        # 测试4: 测试错误处理（不存在的配置文件）
        print("\n📋 测试4: 测试错误处理（不存在的配置文件）")
        configs_error = "config/config1.yaml,config/nonexistent.yaml"
        result4 = run_parallel_pipeline(config_paths=configs_error)
        print(f"   结果: {result4['status']}")
        print(f"   消息: {result4['message']}")
        
        print("\n✅ 参数化工具测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 参数化工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始3个模型并行训练功能测试")
    
    # 测试1: 直接使用ParallelMLExecutor
    success1 = test_three_parallel_models()
    
    # 测试2: 测试参数化的工具
    success2 = test_parameterized_tool()
    
    if success1 and success2:
        print("\n✅ 所有测试通过！")
        print("\n💡 功能总结:")
        print("   🎯 支持任意数量的配置文件")
        print("   🔧 参数化的 run_parallel_pipeline 工具")
        print("   🤖 3个模型并行训练")
        print("   🖼️ 完整的图片生成（训练历史 + 混淆矩阵）")
        print("   📁 带时间戳的输出目录管理")
        print("   ⚡ 灵活的配置管理")
    else:
        print("\n❌ 部分测试失败！")
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
