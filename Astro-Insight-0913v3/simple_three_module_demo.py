#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
三模块集成演示
简单展示Planner、Coder、Explainer三个模块的协同工作
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
    print("\n" + "=" * 60)
    print(f" {title} ")
    print("=" * 60)

def print_step(step_num, title, emoji="🔄"):
    """打印步骤"""
    print(f"\n{emoji} 步骤 {step_num}: {title}")
    print("-" * 40)

def demo_three_modules():
    """演示三个模块的集成使用"""
    
    print_header("三模块集成演示")
    print("本演示将展示Planner、Coder、Explainer三个模块的协同工作")
    
    # 用户需求
    user_request = "分析星系数据，生成散点图展示星系的大小和亮度关系"
    print(f"\n📝 用户需求: {user_request}")
    
    try:
        # 1. Planner模块 - 需求规划
        print_step(1, "Planner模块 - 需求规划和任务分解", "📋")
        
        from src.planner import PlannerWorkflow
        planner = PlannerWorkflow()
        
        print("🚀 开始需求规划...")
        planner_result = planner.run_complete_pipeline(user_request)
        
        if not planner_result.get("success"):
            print(f"❌ Planner失败: {planner_result.get('error_message', '未知错误')}")
            return
        
        print("✅ Planner完成")
        print(f"   - 任务步骤: {len(planner_result.get('task_steps', []))}个")
        if planner_result.get('selected_dataset'):
            print(f"   - 选定数据集: {planner_result['selected_dataset'].name}")
        print(f"   - 规划时间: {planner_result.get('processing_time', 0):.2f}秒")
        
        # 显示任务步骤
        print("\n📋 任务步骤:")
        for i, step in enumerate(planner_result.get('task_steps', []), 1):
            print(f"   {i}. {step.description}")
        
        # 2. Coder模块 - 代码生成和执行
        print_step(2, "Coder模块 - 代码生成和执行", "💻")
        
        from src.coder.workflow import CodeGenerationWorkflow
        coder = CodeGenerationWorkflow()
        
        print("🚀 开始代码生成...")
        coder_result = coder.run(planner_result.get('final_prompt', ''))
        
        if not coder_result.get("success"):
            print(f"❌ Coder失败: {coder_result.get('error')}")
            return
        
        print("✅ Coder完成")
        print(f"   - 使用数据集: {coder_result.get('dataset_used')}")
        print(f"   - 执行时间: {coder_result.get('execution_time', 0):.2f}秒")
        print(f"   - 生成文件: {len(coder_result.get('generated_files', []))}个")
        
        # 显示生成的文件
        if coder_result.get('generated_files'):
            print("\n📁 生成的文件:")
            for file_path in coder_result['generated_files']:
                print(f"   - {file_path}")
        
        # 3. Explainer模块 - 结果解释
        print_step(3, "Explainer模块 - 结果解释和分析", "🔍")
        
        from src.explainer.workflow import ExplainerWorkflow
        explainer = ExplainerWorkflow()
        
        print("🚀 开始结果解释...")
        explainer_result = explainer.explain_from_coder_workflow(
            coder_result=coder_result,
            user_input=planner_result.get('final_prompt', '')
        )
        
        if not explainer_result.get("success"):
            print(f"❌ Explainer失败: {explainer_result.get('error')}")
            return
        
        print("✅ Explainer完成")
        print(f"   - 解释时间: {explainer_result.get('processing_time', 0):.2f}秒")
        print(f"   - 解释数量: {len(explainer_result.get('explanations', []))}个")
        print(f"   - VLM调用: {explainer_result.get('vlm_calls', 0)}次")
        
        # 显示解释结果
        if explainer_result.get('summary'):
            print(f"\n📊 整体总结:")
            print(f"   {explainer_result['summary'][:100]}...")
        
        if explainer_result.get('insights'):
            print(f"\n💡 关键洞察 ({len(explainer_result['insights'])}个):")
            for insight in explainer_result['insights'][:3]:
                print(f"   - {insight}")
        
        # 最终总结
        print_step(4, "演示完成", "🎉")
        
        total_time = (
            planner_result.get("processing_time", 0) + 
            coder_result.get("execution_time", 0) + 
            explainer_result.get("processing_time", 0)
        )
        
        print("✅ 三模块协同工作完成!")
        print(f"⏱️ 总处理时间: {total_time:.2f}秒")
        print(f"📁 生成文件: {len(coder_result.get('generated_files', []))}个")
        print(f"🔍 解释结果: {len(explainer_result.get('explanations', []))}个")
        
        # 各模块时间分布
        print(f"\n📊 各模块处理时间:")
        print(f"   Planner: {planner_result.get('processing_time', 0):.2f}秒")
        print(f"   Coder: {coder_result.get('execution_time', 0):.2f}秒")
        print(f"   Explainer: {explainer_result.get('processing_time', 0):.2f}秒")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_simple_pipeline():
    """演示简化的Pipeline使用"""
    
    print_header("简化Pipeline演示")
    print("使用Planner的run_complete_pipeline方法一键完成所有步骤")
    
    user_request = "分析恒星数据，生成饼图展示恒星类型分布"
    print(f"\n📝 用户需求: {user_request}")
    
    try:
        from src.planner import PlannerWorkflow
        
        print_step(1, "运行完整Pipeline", "🚀")
        
        planner = PlannerWorkflow()
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
                for i, step in enumerate(task_steps, 1):
                    if isinstance(step, dict):
                        print(f"   {i}. {step.get('description', 'N/A')}")
                    else:
                        print(f"   {i}. {step.description}")
            
            # 显示生成的文件
            generated_files = result.get('generated_files', [])
            if generated_files:
                print(f"\n📁 生成的文件:")
                for file_path in generated_files:
                    print(f"   - {file_path}")
            
        else:
            print(f"❌ Pipeline执行失败: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 简化Pipeline演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 三模块集成演示系统")
    
    print("\n选择演示模式:")
    print("1. 三模块分步演示 - 详细展示每个模块的工作过程")
    print("2. 简化Pipeline演示 - 一键完成所有步骤")
    
    choice = input("请选择 (1/2，默认1): ").strip()
    
    if choice == "2":
        demo_simple_pipeline()
    else:
        demo_three_modules()
    
    print("\n👋 演示完成！")

if __name__ == "__main__":
    main()
