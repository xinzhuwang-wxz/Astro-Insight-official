"""
演示完整的输出结构功能
包括模型、日志、图片、配置文件的正确保存
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

def demo_complete_output():
    """演示完整的输出结构功能"""
    print("=" * 70)
    print("🚀 完整输出结构功能演示")
    print("=" * 70)
    
    try:
        # 1. 显示配置信息
        configs = ["src/mcp_ml/config/config1.yaml", "src/mcp_ml/config/config2.yaml"]
        print(f"\n📋 使用配置文件:")
        for i, config in enumerate(configs):
            print(f"   进程 {i}: {config}")
        
        # 2. 创建并行执行器
        session_name = "complete_demo"
        print(f"\n🔧 创建并行执行器 (会话: {session_name})...")
        executor = ParallelMLExecutor(configs, session_name=session_name)
        
        # 3. 显示会话信息
        session_info = executor.output_manager.get_session_info()
        print(f"\n📁 会话信息:")
        print(f"   会话ID: {session_info['session_id']}")
        print(f"   会话目录: {session_info['session_dir']}")
        print(f"   创建时间: {session_info['created_at']}")
        
        # 4. 开始并行训练
        print(f"\n🏃 开始并行ML训练...")
        start_time = time.time()
        
        results = executor.run_parallel()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 5. 显示训练结果
        print(f"\n✅ 训练完成！耗时: {duration:.2f}秒")
        print("=" * 70)
        print("📈 训练结果摘要")
        print("=" * 70)
        
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
        
        # 7. 显示关键文件路径
        print(f"\n🔗 关键文件路径:")
        if 'log_file' in results:
            print(f"   执行日志: {results['log_file']}")
        if 'results_file' in results:
            print(f"   结果文件: {results['results_file']}")
        if 'summary_file' in results:
            print(f"   摘要报告: {results['summary_file']}")
        
        # 8. 验证模型文件
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
        
        # 9. 验证图片文件
        print(f"\n🖼️ 图片文件验证:")
        if session_dir and os.path.exists(session_dir):
            images_dir = os.path.join(session_dir, 'images')
            if os.path.exists(images_dir):
                image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
                if image_files:
                    print(f"   ✅ 找到 {len(image_files)} 个图片文件:")
                    for image_file in image_files:
                        file_path = os.path.join(images_dir, image_file)
                        file_size = os.path.getsize(file_path) / (1024 * 1024)
                        print(f"      🖼️ {image_file} ({file_size:.1f} MB)")
                else:
                    print("   ❌ 没有找到图片文件")
            else:
                print("   ❌ Images目录不存在")
        
        print("\n" + "=" * 70)
        print("🎉 完整输出结构功能演示完成！")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = demo_complete_output()
    
    if success:
        print("\n✅ 完整输出结构功能演示成功！")
        print("\n💡 功能总结:")
        print("   🗂️ 带时间戳的会话目录管理")
        print("   🤖 模型文件自动保存到models/目录")
        print("   🖼️ 训练图片自动保存到images/目录")
        print("   📝 详细日志保存到logs/目录")
        print("   ⚙️ 配置文件保存到configs/目录")
        print("   📊 结果文件保存到results/目录")
        print("   🗑️ 临时文件自动清理")
        print("   📈 完整的文件统计和摘要报告")
    else:
        print("\n❌ 完整输出结构功能演示失败！")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
