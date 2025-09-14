"""
测试生成配置并运行并行实验功能
"""
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_generate_and_run(user_descriptions=None):
    """测试生成配置并运行并行实验"""
    print("🧪 测试生成配置并运行并行实验...")
    
    try:
        from server import generate_and_run_parallel_experiments
        
        # 如果提供了用户描述，使用用户描述；否则使用默认描述
        if user_descriptions:
            descriptions = user_descriptions
            print(f"\n📝 使用用户提供的描述: {descriptions}")
        else:
            descriptions = "简单CNN模型，batch_size=32，epochs=4;基础CNN模型，batch_size=16，epochs=4"
            print(f"\n📝 使用默认描述列表:")
        print(f"\n📝 配置描述列表:")
        desc_list = descriptions.split(';')
        for i, desc in enumerate(desc_list, 1):
            print(f"   {i}. {desc.strip()}")
        
        # 生成配置并运行实验
        session_name = f"config_generation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n🏃 开始生成配置并运行并行实验 (会话: {session_name})...")
        
        result = generate_and_run_parallel_experiments(descriptions, session_name)
        
        if result["status"] == "success":
            print(f"\n✅ 实验完成!")
            print(f"   生成的配置文件: {len(result['generated_configs'])} 个")
            print(f"   实验会话: {session_name}")
            
            # 显示生成的配置文件
            print(f"\n📄 生成的配置文件:")
            for i, config_path in enumerate(result['generated_configs'], 1):
                print(f"   {i}. {config_path}")
                if os.path.exists(config_path):
                    print(f"      ✅ 文件存在")
                    
                    # 显示配置文件内容预览
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"      📝 内容预览 (前10行):")
                    lines = content.splitlines()[:10]
                    for line_num, line in enumerate(lines, 1):
                        print(f"         {line_num:2d}| {line}")
                    if len(content.splitlines()) > 10:
                        print(f"         ... (共{len(content.splitlines())}行)")
                else:
                    print(f"      ❌ 文件不存在")
            
            # 显示实验结果摘要
            experiment_results = result['experiment_results']
            if 'execution_summary' in experiment_results:
                summary = experiment_results['execution_summary']
                print(f"\n📊 实验结果摘要:")
                print(f"   总进程数: {summary.get('total_processes', 0)}")
                print(f"   成功进程: {summary.get('successful_processes', 0)}")
                print(f"   失败进程: {summary.get('failed_processes', 0)}")
                print(f"   会话目录: {summary.get('session_dir', 'N/A')}")
                
                # 检查输出文件
                session_dir = summary.get('session_dir')
                if session_dir and os.path.exists(session_dir):
                    print(f"\n📁 输出文件检查:")
                    
                    # 检查实际运行时配置文件 (保留用于debug)
                    configs_dir = os.path.join(session_dir, 'configs')
                    if os.path.exists(configs_dir):
                        config_files = [f for f in os.listdir(configs_dir) if f.endswith('.yaml')]
                        print(f"   ⚙️ 实际运行时配置文件: {len(config_files)} 个 (保留用于debug)")
                        for config_file in config_files:
                            config_path = os.path.join(configs_dir, config_file)
                            print(f"      📄 {config_file}")
                            
                            # 显示实际运行时配置文件内容预览
                            try:
                                with open(config_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                print(f"         📝 内容预览 (前8行):")
                                lines = content.splitlines()[:8]
                                for line_num, line in enumerate(lines, 1):
                                    print(f"            {line_num:2d}| {line}")
                                if len(content.splitlines()) > 8:
                                    print(f"            ... (共{len(content.splitlines())}行)")
                            except Exception as e:
                                print(f"         ❌ 读取失败: {e}")
                    
                    # 检查模型文件
                    models_dir = os.path.join(session_dir, 'models')
                    if os.path.exists(models_dir):
                        model_files = [f for f in os.listdir(models_dir) if f.endswith('.keras')]
                        print(f"   🤖 模型文件: {len(model_files)} 个")
                        for model_file in model_files:
                            print(f"      📄 {model_file}")
                    
                    # 检查图片文件
                    images_dir = os.path.join(session_dir, 'images')
                    if os.path.exists(images_dir):
                        image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
                        print(f"   🖼️ 图片文件: {len(image_files)} 个")
                        for image_file in image_files:
                            print(f"      🖼️ {image_file}")
                    
                    # 检查结果文件
                    results_dir = os.path.join(session_dir, 'results')
                    if os.path.exists(results_dir):
                        result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
                        print(f"   📊 结果文件: {len(result_files)} 个")
                        for result_file in result_files:
                            print(f"      📄 {result_file}")
                    
                    # 显示debug信息
                    print(f"\n🔍 Debug信息:")
                    print(f"   会话目录: {session_dir}")
                    print(f"   ⚙️ 实际运行时配置文件保存在: {configs_dir}")
                    print(f"   💡 您可以查看这些配置文件来debug训练过程")
        else:
            print(f"❌ 实验失败: {result['message']}")
            if 'error' in result:
                print(f"   错误详情: {result['error']}")
            return False
        
        return result  # 返回结果而不是True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = test_generate_and_run()
    if isinstance(result, dict) and result.get("status") == "success":
        print("\n🎉 生成配置并运行并行实验测试通过！")
    else:
        print("\n❌ 生成配置并运行并行实验测试失败！")
    sys.exit(0 if (isinstance(result, dict) and result.get("status") == "success") else 1)
