#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式天文数据分析系统Demo
支持用户自定义输入多种需求，完整运行Planner→Coder→Explainer流程
"""

import sys
from pathlib import Path
import time

# 确保能找到项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f" {title} ")
    print("=" * 80)

def print_step(step_num, title, emoji="🔄"):
    """打印步骤"""
    print(f"\n{emoji} 步骤 {step_num}: {title}")
    print("-" * 60)

def run_complete_pipeline_demo():
    """运行完整的Pipeline演示"""
    
    print_header("🚀 完整天文数据分析系统")
    print("💡 系统包含三个模块:")
    print("   1. Planner - 多轮对话收集和规划需求")
    print("   2. Coder - 生成和执行数据分析代码") 
    print("   3. Explainer - 解释分析结果和图表")
    print("\n🎯 支持的需求类型:")
    print("   • 星系数据分析")
    print("   • 恒星分类分析") 
    print("   • SDSS数据集分析")
    print("   • 数据可视化")
    print("   • 统计分析")
    
    # 预设一些示例需求
    example_requests = [
        "分析星系数据，生成散点图展示星系的大小和亮度关系",
        "分析恒星分类数据，生成饼图展示恒星类型分布",
        "分析SDSS数据集，进行相关性分析和可视化",
        "对6_class_csv数据集进行基本统计分析"
    ]
    
    print(f"\n📝 示例需求:")
    for i, req in enumerate(example_requests, 1):
        print(f"   {i}. {req}")
    
    try:
        from src.planner import PlannerWorkflow
        
        # 创建Planner工作流
        print_step(1, "初始化系统")
        planner = PlannerWorkflow()
        print("✅ 系统初始化完成")
        
        # 运行示例需求
        for i, user_request in enumerate(example_requests, 1):
            print_header(f"🎯 示例 {i}: {user_request}")
            
            print(f"📝 用户需求: {user_request}")
            print(f"🕒 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 运行完整pipeline
            print_step(2, "执行完整Pipeline (Planner → Coder → Explainer)")
            result = planner.run_complete_pipeline(user_request)
            
            if result.get("success"):
                print("✅ Pipeline执行成功!")
                print(f"📋 会话ID: {result.get('session_id')}")
                print(f"⏱️ 总时间: {result.get('total_processing_time', 0):.2f}秒")
                print(f"📁 生成文件: {len(result.get('generated_files', []))}个")
                print(f"🔍 解释数量: {len(result.get('explanations', []))}个")
                
                # 显示任务步骤
                task_steps = result.get('task_steps', [])
                if task_steps:
                    print(f"\n📋 任务步骤 ({len(task_steps)}个):")
                    for j, step in enumerate(task_steps, 1):
                        if isinstance(step, dict):
                            print(f"   {j}. {step.get('description', 'N/A')}")
                        else:
                            print(f"   {j}. {step.description}")
                
                # 显示生成的文件
                generated_files = result.get('generated_files', [])
                if generated_files:
                    print(f"\n📁 生成的文件:")
                    for file_path in generated_files:
                        print(f"   - {file_path}")
                
                # 显示解释结果
                explanations = result.get('explanations', [])
                if explanations:
                    print(f"\n🔍 解释结果 ({len(explanations)}个):")
                    for j, explanation in enumerate(explanations, 1):
                        print(f"   {j}. {explanation.get('image_name', f'Image_{j}')}")
                
                # 各模块时间分布
                planner_time = result.get('planner_result', {}).get('processing_time', 0)
                coder_time = result.get('coder_result', {}).get('execution_time', 0)
                explainer_time = result.get('explainer_result', {}).get('processing_time', 0)
                
                print(f"\n📊 各模块处理时间:")
                print(f"   Planner: {planner_time:.2f}秒")
                print(f"   Coder: {coder_time:.2f}秒")
                print(f"   Explainer: {explainer_time:.2f}秒")
                
            else:
                print(f"❌ Pipeline执行失败: {result.get('error')}")
                print(f"错误类型: {result.get('error_type')}")
            
            # 在示例之间添加分隔
            if i < len(example_requests):
                print("\n" + "="*60)
                print(f"⏳ 准备运行下一个示例...")
                time.sleep(2)
        
        print_header("🎉 所有示例运行完成！")
        print("✅ 系统演示成功完成")
        print("💡 你可以修改 example_requests 列表来测试其他需求")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def run_custom_demo():
    """运行自定义需求演示"""
    
    print_header("🎯 自定义需求演示")
    
    # 自定义需求列表
    custom_requests = [
        "分析星系数据，生成散点图展示星系的大小和亮度关系",
        "分析恒星数据，生成直方图展示恒星温度分布",
        "对SDSS数据集进行聚类分析并可视化结果"
    ]
    
    try:
        from src.planner import PlannerWorkflow
        
        planner = PlannerWorkflow()
        
        for i, user_request in enumerate(custom_requests, 1):
            print(f"\n🎯 自定义需求 {i}: {user_request}")
            
            # 运行完整pipeline
            result = planner.run_complete_pipeline(user_request)
            
            if result.get("success"):
                print(f"✅ 需求 {i} 执行成功")
                print(f"   - 处理时间: {result.get('total_processing_time', 0):.2f}秒")
                print(f"   - 生成文件: {len(result.get('generated_files', []))}个")
            else:
                print(f"❌ 需求 {i} 执行失败: {result.get('error')}")
        
        print("\n🎉 自定义演示完成！")
        
    except Exception as e:
        print(f"❌ 自定义演示失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 天文数据分析系统演示")
    print("\n选择演示类型:")
    print("1. 完整示例演示 (推荐)")
    print("2. 自定义需求演示")
    print("3. 简化Pipeline演示")
    
    # 直接运行完整示例演示
    print("\n🎯 运行完整示例演示...")
    run_complete_pipeline_demo()

if __name__ == "__main__":
    main()

