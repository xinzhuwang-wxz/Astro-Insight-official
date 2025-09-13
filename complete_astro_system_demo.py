#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的天文数据分析系统演示
集成Planner、Coder、Explainer三个模块

功能：
1. 多轮对话收集用户需求（Planner）
2. 生成和执行数据分析代码（Coder）
3. 解释分析结果和图表（Explainer）
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

# 确保能找到项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_separator(title="", char="=", width=80):
    """打印分隔线"""
    if title:
        title_line = f" {title} "
        padding = (width - len(title_line)) // 2
        print(char * padding + title_line + char * padding)
    else:
        print(char * width)

def display_step(step_num, title, status="进行中"):
    """显示步骤信息"""
    status_emoji = {
        "进行中": "🔄",
        "成功": "✅", 
        "失败": "❌",
        "警告": "⚠️",
        "完成": "🎉"
    }
    emoji = status_emoji.get(status, "🔄")
    print(f"\n{emoji} 步骤 {step_num}: {title}")
    print("-" * 60)

def display_user_input(user_input):
    """展示用户输入"""
    print_separator("用户需求", "=")
    print(f"📝 用户需求: {user_input}")
    print(f"🕒 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def display_planner_result(planner_result):
    """展示Planner结果"""
    print_separator("需求规划结果", "=")
    
    if planner_result.success:
        print("✅ 需求规划完成")
        print(f"📋 会话ID: {planner_result.session_id}")
        print(f"💬 对话轮次: {planner_result.turns_used}")
        print(f"⏱️ 规划时间: {planner_result.processing_time:.2f}秒")
        
        if planner_result.task_steps:
            print(f"\n🔧 任务步骤 ({len(planner_result.task_steps)}个):")
            for i, step in enumerate(planner_result.task_steps, 1):
                print(f"  {i}. {step.description}")
                print(f"     类型: {step.action_type}")
                print(f"     详情: {step.details}")
        
        if planner_result.selected_dataset:
            print(f"\n📊 选定数据集: {planner_result.selected_dataset.name}")
            print(f"   描述: {planner_result.selected_dataset.description}")
            print(f"   列数: {len(planner_result.selected_dataset.columns)}")
        
        if planner_result.final_prompt:
            print(f"\n📝 最终需求描述:")
            print("=" * 40)
            print(planner_result.final_prompt)
            print("=" * 40)
    else:
        print(f"❌ 需求规划失败: {planner_result.error_message}")

def display_coder_result(coder_result):
    """展示Coder结果"""
    print_separator("代码生成和执行结果", "=")
    
    if coder_result.get("success"):
        print("✅ 代码生成和执行成功")
        print(f"📊 使用数据集: {coder_result.get('dataset_used', 'Unknown')}")
        print(f"🎯 复杂度: {coder_result.get('complexity', 'Unknown')}")
        print(f"⏱️ 执行时间: {coder_result.get('execution_time', 0):.2f}秒")
        print(f"🔄 重试次数: {coder_result.get('retry_count', 0)}")
        
        if coder_result.get('generated_files'):
            print(f"\n📁 生成的文件 ({len(coder_result['generated_files'])}个):")
            for file_path in coder_result['generated_files']:
                print(f"  - {file_path}")
        
        if coder_result.get('output'):
            print(f"\n📋 程序输出:")
            print("=" * 40)
            output_lines = coder_result['output'].split('\n')
            for line in output_lines[:10]:  # 只显示前10行
                if line.strip():
                    print(f"   {line}")
            if len(output_lines) > 10:
                print(f"   ... (还有 {len(output_lines) - 10} 行输出)")
            print("=" * 40)
    else:
        print(f"❌ 代码生成失败: {coder_result.get('error', '未知错误')}")
        print(f"错误类型: {coder_result.get('error_type', 'unknown')}")

def display_explainer_result(explainer_result):
    """展示Explainer结果"""
    print_separator("结果解释和分析", "=")
    
    if explainer_result.get("success"):
        print("✅ 结果解释完成")
        print(f"⏱️ 解释时间: {explainer_result.get('processing_time', 0):.2f}秒")
        print(f"🔍 VLM调用次数: {explainer_result.get('vlm_calls', 0)}")
        
        if explainer_result.get('summary'):
            print(f"\n📊 整体总结:")
            print("=" * 40)
            print(explainer_result['summary'])
            print("=" * 40)
        
        if explainer_result.get('explanations'):
            print(f"\n🔍 详细解释 ({len(explainer_result['explanations'])}个):")
            for i, explanation in enumerate(explainer_result['explanations'], 1):
                print(f"\n  图片 {i}: {explanation.get('image_name', f'Image_{i}')}")
                print(f"    解释: {explanation.get('explanation', 'N/A')[:100]}...")
                if explanation.get('key_findings'):
                    print(f"    关键发现: {len(explanation['key_findings'])}个")
        
        if explainer_result.get('insights'):
            print(f"\n💡 关键洞察 ({len(explainer_result['insights'])}个):")
            for insight in explainer_result['insights'][:3]:  # 只显示前3个
                print(f"  - {insight}")
        
        if explainer_result.get('output_file'):
            print(f"\n📄 解释报告: {explainer_result['output_file']}")
    else:
        print(f"❌ 结果解释失败: {explainer_result.get('error', '未知错误')}")

def display_final_summary(final_result):
    """展示最终总结"""
    print_separator("完整Pipeline执行总结", "=")
    
    if final_result.get("success"):
        print("🎉 完整Pipeline执行成功!")
        print(f"📋 会话ID: {final_result.get('session_id')}")
        print(f"⏱️ 总处理时间: {final_result.get('total_processing_time', 0):.2f}秒")
        print(f"📁 生成文件数: {len(final_result.get('generated_files', []))}")
        print(f"🔍 解释数量: {len(final_result.get('explanations', []))}")
        
        # 各模块处理时间
        planner_time = final_result.get('planner_result', {}).get('processing_time', 0)
        coder_time = final_result.get('coder_result', {}).get('execution_time', 0)
        explainer_time = final_result.get('explainer_result', {}).get('processing_time', 0)
        
        print(f"\n⏱️ 各模块处理时间:")
        print(f"  Planner: {planner_time:.2f}秒")
        print(f"  Coder: {coder_time:.2f}秒")
        print(f"  Explainer: {explainer_time:.2f}秒")
        
        if final_result.get('warnings'):
            print(f"\n⚠️ 警告信息 ({len(final_result['warnings'])}个):")
            for warning in final_result['warnings']:
                print(f"  - {warning}")
    else:
        print("❌ Pipeline执行失败")
        print(f"错误: {final_result.get('error')}")
        print(f"错误类型: {final_result.get('error_type')}")

def run_complete_pipeline_demo(user_request: str):
    """运行完整的Pipeline演示"""
    print_separator("完整天文数据分析系统演示", "=")
    
    # 显示用户输入
    display_user_input(user_request)
    
    try:
        from src.planner import PlannerWorkflow
        
        # 创建Planner工作流
        display_step(1, "初始化Planner工作流")
        planner = PlannerWorkflow()
        print("✅ Planner工作流创建成功")
        
        # 运行完整Pipeline
        display_step(2, "执行完整Pipeline (Planner → Coder → Explainer)")
        print("🚀 开始处理用户请求...")
        
        # 运行完整pipeline
        result = planner.run_complete_pipeline(user_request)
        
        # 显示各模块结果
        if result.get("success"):
            display_step(3, "Pipeline执行完成", "成功")
            
            # 显示Planner结果
            if result.get("planner_result"):
                display_planner_result(result["planner_result"])
            
            # 显示Coder结果
            if result.get("coder_result"):
                display_coder_result(result["coder_result"])
            
            # 显示Explainer结果
            if result.get("explainer_result"):
                display_explainer_result(result["explainer_result"])
            
            # 显示最终总结
            display_final_summary(result)
        else:
            display_step(3, "Pipeline执行", "失败")
            print(f"❌ Pipeline执行失败: {result.get('error')}")
            print(f"错误类型: {result.get('error_type')}")
        
        return result
        
    except Exception as e:
        display_step(3, "Pipeline执行", "失败")
        print(f"❌ 发生异常: {str(e)}")
        import traceback
        print("\n🔍 详细错误信息:")
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def run_interactive_planner_demo(user_request: str):
    """运行交互式Planner演示"""
    print_separator("交互式需求规划演示", "=")
    
    display_user_input(user_request)
    
    try:
        from src.planner import PlannerWorkflow
        
        # 创建Planner工作流
        display_step(1, "初始化Planner工作流")
        planner = PlannerWorkflow()
        print("✅ Planner工作流创建成功")
        
        # 开始交互式会话
        display_step(2, "开始交互式需求规划")
        session = planner.run_interactive_session(user_request)
        
        if not session["success"]:
            print(f"❌ 会话创建失败: {session.get('error')}")
            return
        
        session_id = session["session_id"]
        print(f"✅ 交互式会话已创建: {session_id}")
        
        # 模拟多轮对话
        dialogue_turns = [
            "我想分析星系数据",
            "使用SDSS数据集",
            "生成散点图展示星系的大小和亮度关系",
            "分析星系的分类情况",
            "确认，开始执行"
        ]
        
        for i, user_input in enumerate(dialogue_turns, 1):
            print(f"\n💬 第 {i} 轮对话:")
            print(f"用户: {user_input}")
            
            # 继续会话
            result = planner.continue_interactive_session(session_id, user_input)
            
            if result["success"]:
                if result.get("completed"):
                    print("✅ 会话已完成")
                    
                    # 运行完整pipeline
                    display_step(3, "执行完整Pipeline")
                    pipeline_result = planner.run_complete_pipeline(
                        result["final_result"].user_initial_request,
                        session_id
                    )
                    
                    if pipeline_result.get("success"):
                        display_final_summary(pipeline_result)
                    else:
                        print(f"❌ Pipeline执行失败: {pipeline_result.get('error')}")
                    break
                    
                elif result.get("needs_confirmation"):
                    print("❓ 需要确认:")
                    print(result["confirmation_request"])
                    
                    # 模拟用户确认
                    confirmation_result = planner.handle_confirmation(
                        session_id, "确认，开始执行"
                    )
                    if confirmation_result["success"]:
                        display_final_summary(confirmation_result)
                    break
                else:
                    print("🔄 会话继续...")
            else:
                print(f"❌ 对话失败: {result.get('error')}")
                break
        
    except Exception as e:
        print(f"❌ 交互式演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def run_step_by_step_demo(user_request: str):
    """运行分步演示"""
    print_separator("分步系统演示", "=")
    
    display_user_input(user_request)
    
    try:
        # Step 1: Planner
        display_step(1, "Planner - 需求规划和任务分解")
        from src.planner import PlannerAgent
        
        planner_agent = PlannerAgent()
        planner_result = planner_agent.run_complete_session(user_request)
        
        if not planner_result.success:
            print(f"❌ Planner失败: {planner_result.error_message}")
            return
        
        display_planner_result(planner_result)
        
        # Step 2: Coder
        display_step(2, "Coder - 代码生成和执行")
        from src.coder.workflow import CodeGenerationWorkflow
        
        coder_workflow = CodeGenerationWorkflow()
        coder_result = coder_workflow.run(planner_result.final_prompt)
        
        display_coder_result(coder_result)
        
        if not coder_result.get("success"):
            print("❌ Coder失败，无法继续Explainer")
            return
        
        # Step 3: Explainer
        display_step(3, "Explainer - 结果解释和分析")
        from src.explainer.workflow import ExplainerWorkflow
        
        explainer_workflow = ExplainerWorkflow()
        explainer_result = explainer_workflow.explain_from_coder_workflow(
            coder_result=coder_result,
            user_input=planner_result.final_prompt
        )
        
        display_explainer_result(explainer_result)
        
        # Final Summary
        display_step(4, "分步演示完成", "完成")
        
        total_time = (
            planner_result.processing_time + 
            coder_result.get("execution_time", 0) + 
            explainer_result.get("processing_time", 0)
        )
        
        print(f"⏱️ 总处理时间: {total_time:.2f}秒")
        print(f"📁 生成文件: {len(coder_result.get('generated_files', []))}个")
        print(f"🔍 解释数量: {len(explainer_result.get('explanations', []))}个")
        
        return True
        
    except Exception as e:
        print(f"❌ 分步演示失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def display_request_history(request_history):
    """显示需求历史记录"""
    if not request_history:
        print("📋 暂无历史需求记录")
        return
    
    print_separator("需求历史记录", "=")
    for i, item in enumerate(request_history, 1):
        status_emoji = {
            'pending': '⏳',
            'completed': '✅',
            'failed': '❌',
            'error': '💥'
        }
        emoji = status_emoji.get(item['status'], '❓')
        print(f"{emoji} {i}. [{item['timestamp']}] {item['request']}")
        print(f"   状态: {item['status']}")
    print(f"\n📊 总计: {len(request_history)} 个需求")

def run_complete_pipeline_with_confirmation(user_request: str, request_history: list):
    """运行完整Pipeline并支持交互式确认"""
    print_separator("完整Pipeline演示 (带确认)", "=")
    
    display_user_input(user_request)
    
    try:
        from src.planner import PlannerWorkflow
        
        # 创建Planner工作流
        display_step(1, "初始化Planner工作流")
        planner = PlannerWorkflow()
        print("✅ Planner工作流创建成功")
        
        # 询问是否需要交互式确认
        print("\n🤔 是否需要交互式确认每个步骤?")
        print("1. 是 - 每步都确认")
        print("2. 否 - 自动执行")
        
        confirm_choice = input("请选择 (1/2，默认2): ").strip()
        interactive_confirm = (confirm_choice == "1")
        
        if interactive_confirm:
            # 运行交互式Pipeline
            display_step(2, "执行交互式Pipeline")
            
            # 第一步：需求规划
            print("\n🔍 步骤1: 需求规划...")
            planner_result = planner.run_complete_pipeline(user_request)
            
            if not planner_result.get("success"):
                print(f"❌ 需求规划失败: {planner_result.get('error')}")
                return False
            
            # 显示规划结果并确认
            display_planner_result(planner_result["planner_result"])
            confirm = input("\n✅ 确认继续执行代码生成? (y/n，默认y): ").strip().lower()
            if confirm in ['n', 'no', '否']:
                print("❌ 用户取消执行")
                return False
            
            # 第二步：代码生成和执行
            print("\n🔍 步骤2: 代码生成和执行...")
            coder_result = planner_result.get("coder_result")
            if coder_result:
                display_coder_result(coder_result)
                
                if coder_result.get("success"):
                    confirm = input("\n✅ 确认继续执行结果解释? (y/n，默认y): ").strip().lower()
                    if confirm in ['n', 'no', '否']:
                        print("❌ 用户取消执行")
                        return False
                    
                    # 第三步：结果解释
                    print("\n🔍 步骤3: 结果解释...")
                    explainer_result = planner_result.get("explainer_result")
                    if explainer_result:
                        display_explainer_result(explainer_result)
            
            # 显示最终总结
            display_final_summary(planner_result)
            return planner_result.get("success", False)
        else:
            # 运行完整Pipeline
            display_step(2, "执行完整Pipeline (Planner → Coder → Explainer)")
            result = planner.run_complete_pipeline(user_request)
            
            if result.get("success"):
                display_step(3, "Pipeline执行完成", "成功")
                
                # 显示各模块结果
                if result.get("planner_result"):
                    display_planner_result(result["planner_result"])
                if result.get("coder_result"):
                    display_coder_result(result["coder_result"])
                if result.get("explainer_result"):
                    display_explainer_result(result["explainer_result"])
                
                display_final_summary(result)
            else:
                display_step(3, "Pipeline执行", "失败")
                print(f"❌ Pipeline执行失败: {result.get('error')}")
            
            return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return False

def run_interactive_planner_with_confirmation(user_request: str, request_history: list):
    """运行真正的多轮对话交互式Planner"""
    print_separator("多轮对话交互式需求规划", "=")
    
    display_user_input(user_request)
    
    try:
        from src.planner import PlannerWorkflow
        
        # 创建Planner工作流
        display_step(1, "初始化Planner工作流")
        planner = PlannerWorkflow()
        print("✅ Planner工作流创建成功")
        
        # 开始交互式会话
        display_step(2, "开始多轮对话需求规划")
        session = planner.run_interactive_session(user_request)
        
        if not session["success"]:
            print(f"❌ 会话创建失败: {session.get('error')}")
            return False
        
        session_id = session["session_id"]
        print(f"✅ 交互式会话已创建: {session_id}")
        
        # 真正的多轮对话循环
        turn_count = 0
        max_turns = 10
        
        while turn_count < max_turns:
            turn_count += 1
            
            print(f"\n{'='*60}")
            print(f"💬 第 {turn_count} 轮对话")
            print(f"{'='*60}")
            
            # 获取用户输入
            user_input = input(f"🎯 请输入你的需求或反馈 (第{turn_count}轮): ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 用户退出对话")
                return False
            
            if user_input.lower() == 'done' or user_input.lower() == '完成':
                print("✅ 用户确认需求完成")
                break
            
            if not user_input:
                print("⚠️ 请输入有效的需求")
                continue
            
            print(f"\n👤 用户: {user_input}")
            
            # 继续会话
            result = planner.continue_interactive_session(session_id, user_input)
            
            if result["success"]:
                if result.get("completed"):
                    print("\n🎉 需求规划已完成!")
                    
                    # 显示最终规划结果
                    if result.get("final_result"):
                        final_result = result["final_result"]
                        print(f"\n📋 最终规划结果:")
                        print(f"   会话ID: {final_result.session_id}")
                        print(f"   对话轮次: {final_result.turns_used}")
                        print(f"   处理时间: {final_result.processing_time:.2f}秒")
                        
                        if final_result.task_steps:
                            print(f"\n🔧 最终任务步骤 ({len(final_result.task_steps)}个):")
                            for i, step in enumerate(final_result.task_steps, 1):
                                print(f"   {i}. {step.description}")
                                print(f"      类型: {step.action_type}")
                                print(f"      详情: {step.details}")
                        
                        if final_result.selected_dataset:
                            print(f"\n📊 选定数据集: {final_result.selected_dataset.name}")
                        
                        if final_result.final_prompt:
                            print(f"\n📝 最终用户需求描述:")
                            print("=" * 50)
                            print(final_result.final_prompt)
                            print("=" * 50)
                    
                    # 询问是否执行完整Pipeline
                    confirm = input("\n🚀 确认执行完整Pipeline? (y/n，默认y): ").strip().lower()
                    if confirm in ['n', 'no', '否']:
                        print("❌ 用户取消Pipeline执行")
                        return False
                    
                    # 运行完整pipeline
                    display_step(3, "执行完整Pipeline")
                    pipeline_result = planner.run_complete_pipeline(
                        result["final_result"].user_initial_request,
                        session_id
                    )
                    
                    if pipeline_result.get("success"):
                        display_final_summary(pipeline_result)
                        return True
                    else:
                        print(f"❌ Pipeline执行失败: {pipeline_result.get('error')}")
                        return False
                        
                elif result.get("needs_confirmation"):
                    print(f"\n❓ 系统需要确认:")
                    print(f"   {result['confirmation_request']}")
                    
                    # 获取用户确认
                    confirm = input("\n✅ 请确认 (y/n，默认y): ").strip().lower()
                    confirmation_input = "确认" if confirm not in ['n', 'no', '否'] else "取消"
                    
                    confirmation_result = planner.handle_confirmation(
                        session_id, confirmation_input
                    )
                    if confirmation_result["success"]:
                        display_final_summary(confirmation_result)
                        return True
                    break
                    
                else:
                    # 显示系统回复
                    if result.get("assistant_response"):
                        print(f"\n🤖 系统回复:")
                        print(f"   {result['assistant_response']}")
                    
                    # 显示当前状态
                    if result.get("current_status"):
                        status = result["current_status"]
                        print(f"\n📊 当前状态:")
                        print(f"   对话轮次: {status.get('current_turn', 0)}/{status.get('max_turns', 10)}")
                        print(f"   状态: {status.get('dialogue_status', 'unknown')}")
                        
                        if status.get("task_steps"):
                            print(f"   已规划任务: {len(status['task_steps'])}个")
                        
                        if status.get("selected_dataset"):
                            print(f"   选定数据集: {status['selected_dataset'].get('name', 'unknown')}")
            else:
                print(f"❌ 对话失败: {result.get('error')}")
                return False
        
        if turn_count >= max_turns:
            print(f"\n⚠️ 已达到最大对话轮次限制 ({max_turns}轮)")
            print("💡 建议使用 'done' 命令完成需求规划")
        
        return False
        
    except Exception as e:
        print(f"❌ 多轮对话演示失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_quick_demo(user_request: str):
    """运行快速演示 - 简化输出"""
    print_separator("快速演示模式", "=")
    
    try:
        from src.planner import PlannerWorkflow
        
        print(f"🚀 快速处理: {user_request}")
        
        # 创建Planner工作流
        planner = PlannerWorkflow()
        
        # 运行完整pipeline
        result = planner.run_complete_pipeline(user_request)
        
        if result.get("success"):
            print("✅ 快速演示完成!")
            print(f"📋 会话ID: {result.get('session_id')}")
            print(f"⏱️ 总时间: {result.get('total_processing_time', 0):.2f}秒")
            print(f"📁 生成文件: {len(result.get('generated_files', []))}个")
            print(f"🔍 解释数量: {len(result.get('explanations', []))}个")
            
            # 显示生成的文件
            generated_files = result.get('generated_files', [])
            if generated_files:
                print(f"\n📁 生成的文件:")
                for file_path in generated_files:
                    print(f"   - {file_path}")
            
            return True
        else:
            print(f"❌ 快速演示失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 快速演示失败: {str(e)}")
        return False

def interactive_mode():
    """交互模式 - 支持多次需求输入和真正的多轮对话"""
    print_separator("交互式完整系统演示", "=")
    print("🤖 欢迎使用完整的天文数据分析系统!")
    print("💡 系统包含三个模块:")
    print("   1. Planner - 多轮对话收集和规划需求")
    print("   2. Coder - 生成和执行数据分析代码")
    print("   3. Explainer - 解释分析结果和图表")
    print("\n🎯 支持的需求类型:")
    print("   • 星系数据分析 (SDSS数据集)")
    print("   • 恒星分类分析 (6_class_csv)")
    print("   • 数据可视化 (散点图、饼图、直方图等)")
    print("   • 统计分析 (相关性、聚类等)")
    print("\n💬 多轮对话功能:")
    print("   • 模式2: 真正的多轮对话 - 用户可以多次输入需求")
    print("   • 模型会回复并逐步完善计划")
    print("   • 支持实时调整和确认需求")
    print("   • 输入 'done' 完成需求规划")
    print("\n🚪 输入 'quit' 或 'exit' 退出程序")
    print("📋 输入 'history' 查看历史需求")
    print("🔄 输入 'retry' 重新运行上一个需求")
    
    request_history = []
    last_request = None
    
    while True:
        try:
            print("\n" + "=" * 80)
            user_input = input("🎯 请输入你的数据分析需求: ").strip()
            
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！感谢使用天文数据分析系统!")
                break
            
            if user_input.lower() == 'history':
                display_request_history(request_history)
                continue
                
            if user_input.lower() == 'retry' and last_request:
                print(f"🔄 重新运行: {last_request}")
                user_input = last_request
            elif user_input.lower() == 'retry':
                print("⚠️ 没有可重试的需求，请先输入一个需求")
                continue
            
            if not user_input:
                print("⚠️ 请输入有效的需求")
                continue
            
            # 添加到历史记录
            request_history.append({
                'request': user_input,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'pending'
            })
            last_request = user_input
            
            print(f"\n🔄 正在处理: {user_input}")
            print(f"📊 历史需求数量: {len(request_history)}")
            
            # 询问用户选择演示模式
            print("\n选择演示模式:")
            print("1. 完整Pipeline (推荐) - 自动运行所有模块")
            print("2. 交互式Planner - 体验多轮对话规划")
            print("3. 分步演示 - 查看每个模块的详细过程")
            print("4. 快速演示 - 简化输出，快速执行")
            
            mode_choice = input("请选择 (1/2/3/4，默认1): ").strip()
            
            # 执行选择的功能
            success = False
            if mode_choice == "2":
                success = run_interactive_planner_with_confirmation(user_input, request_history)
            elif mode_choice == "3":
                success = run_step_by_step_demo(user_input)
            elif mode_choice == "4":
                success = run_quick_demo(user_input)
            else:
                success = run_complete_pipeline_with_confirmation(user_input, request_history)
            
            # 更新历史记录状态
            if request_history:
                request_history[-1]['status'] = 'completed' if success else 'failed'
            
            # 询问是否继续
            print("\n" + "=" * 60)
            continue_choice = input("🔄 是否继续测试其他需求? (y/n/history，默认y): ").strip().lower()
            if continue_choice in ['n', 'no', '否']:
                print("👋 再见！")
                break
            elif continue_choice == 'history':
                display_request_history(request_history)
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            if request_history:
                request_history[-1]['status'] = 'error'

def main():
    """主函数"""
    print("🚀 完整天文数据分析系统演示")
    
    # 预设的演示需求
    demo_requests = [
        "分析星系数据，生成散点图展示星系的大小和亮度关系",
        "分析恒星分类数据，生成饼图展示恒星类型分布",
        "分析SDSS数据集，进行相关性分析和可视化"
    ]
    
    print("\n选择运行模式:")
    print("1. 交互模式 - 自定义输入需求")
    print("2. 演示模式 - 运行预设示例")
    
    choice = input("请选择 (1/2，默认1): ").strip()
    
    if choice == "2":
        print_separator("预设演示模式", "=")
        for i, request in enumerate(demo_requests, 1):
            print(f"\n🎯 演示 {i}/{len(demo_requests)}: {request}")
            result = run_complete_pipeline_demo(request)
            
            if i < len(demo_requests):
                input("\n按回车键继续下一个演示...")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
