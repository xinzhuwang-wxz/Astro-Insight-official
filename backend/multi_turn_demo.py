#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多轮对话演示
展示真正的多轮对话交互功能
"""

import sys
from pathlib import Path

# 确保能找到项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_separator(title="", char="=", width=60):
    """打印分隔线"""
    if title:
        title_line = f" {title} "
        padding = (width - len(title_line)) // 2
        print(char * padding + title_line + char * padding)
    else:
        print(char * width)

def print_coder_execution_details(coder_result):
    """打印coder执行的详细信息"""
    if not coder_result:
        print("❌ Coder结果为空")
        return
    
    print("\n" + "="*80)
    print("🔧 CODER执行详细信息")
    print("="*80)
    
    # 显示执行状态
    success = coder_result.get("success", False)
    print(f"📊 执行状态: {'✅ 成功' if success else '❌ 失败'}")
    print(f"⏱️  执行时间: {coder_result.get('execution_time', 0):.2f}秒")
    
    # 显示生成的代码
    if coder_result.get("generated_code"):
        print(f"\n📝 生成的代码:")
        print("-" * 60)
        print(coder_result["generated_code"])
        print("-" * 60)
    
    # 显示执行结果
    execution_result = coder_result.get("execution_result")
    if execution_result:
        print(f"\n🔄 代码执行结果:")
        print(f"   状态: {execution_result.get('status', 'unknown')}")
        print(f"   执行时间: {execution_result.get('execution_time', 0):.2f}秒")
        
        # 显示输出
        if execution_result.get("output"):
            print(f"\n📤 程序输出:")
            print("-" * 40)
            print(execution_result["output"])
            print("-" * 40)
        
        # 显示错误信息
        if execution_result.get("error"):
            print(f"\n❌ 错误信息:")
            print("-" * 40)
            print(execution_result["error"])
            print("-" * 40)
        
        # 显示生成的文件
        generated_files = execution_result.get("generated_files", [])
        if generated_files:
            print(f"\n📁 生成的文件 ({len(generated_files)}个):")
            for i, file_path in enumerate(generated_files, 1):
                print(f"   {i}. {file_path}")
        else:
            print(f"\n📁 生成的文件: 无")
    
    # 显示错误信息（如果有）
    if coder_result.get("error"):
        print(f"\n❌ Coder错误:")
        print("-" * 40)
        print(coder_result["error"])
        print("-" * 40)
    
    # 显示执行历史
    execution_history = coder_result.get("execution_history", [])
    if execution_history:
        print(f"\n📚 执行历史 ({len(execution_history)}次尝试):")
        for i, hist in enumerate(execution_history, 1):
            print(f"   尝试 {i}: {hist.get('status', 'unknown')} - {hist.get('error', '无错误')[:100]}...")
    
    print("="*80)

def demo_multi_turn_dialogue():
    """演示多轮对话功能"""
    print_separator("多轮对话交互演示", "=")
    print("🎯 这是一个多轮对话演示，展示如何与Planner进行交互")
    print("💡 你可以:")
    print("   • 提出初始需求")
    print("   • 根据模型回复继续细化需求")
    print("   • 调整和修改计划")
    print("   • 确认最终计划")
    print("\n📝 示例对话流程:")
    print("   第1轮: 用户提出初始需求")
    print("   第2轮: 用户细化需求或回答问题")
    print("   第3轮: 用户确认或修改计划")
    print("   第N轮: 直到用户满意为止")
    
    # 询问是否启用详细输出模式
    print("\n🔧 调试选项:")
    debug_mode = input("是否显示详细的代码执行信息? (y/n，默认n): ").strip().lower()
    show_coder_details = debug_mode in ['y', 'yes', '是', '1']
    
    if show_coder_details:
        print("✅ 已启用详细输出模式 - 将显示所有代码执行细节")
    else:
        print("ℹ️  使用简洁输出模式 - 只显示主要结果")
    
    try:
        from src.planner import PlannerWorkflow
        
        # 创建Planner工作流
        print("\n🔄 初始化Planner...")
        planner = PlannerWorkflow()
        print("✅ Planner初始化完成")
        
        # 获取初始需求
        print("\n" + "="*60)
        initial_request = input("🎯 请输入你的初始数据分析需求: ").strip()
        
        if not initial_request:
            print("❌ 未输入需求，退出演示")
            return
        
        print(f"\n👤 用户初始需求: {initial_request}")
        
        # 开始交互式会话
        print("\n🔄 创建交互式会话...")
        session = planner.run_interactive_session(initial_request)
        
        if not session["success"]:
            print(f"❌ 会话创建失败: {session.get('error')}")
            return
        
        session_id = session["session_id"]
        print(f"✅ 会话创建成功: {session_id}")
        
        # 立即处理初始需求，开始第一轮对话
        print("\n🔄 处理初始需求...")
        result = planner.continue_interactive_session(session_id, initial_request)
        
        if not result["success"]:
            print(f"❌ 初始需求处理失败: {result.get('error')}")
            return
        
        # 显示系统对初始需求的回复
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
                for i, step in enumerate(status['task_steps'][:3], 1):  # 只显示前3个
                    print(f"     {i}. {step.get('description', 'N/A')}")
            
            if status.get("selected_dataset"):
                print(f"   选定数据集: {status['selected_dataset'].get('name', 'unknown')}")
        
        # 检查是否已完成
        if result.get("completed"):
            print("\n🎉 需求规划已完成!")
            # 显示最终结果并询问是否执行Pipeline
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
            
            # 询问是否执行
            confirm = input("\n🚀 是否执行完整Pipeline? (y/n，默认y): ").strip().lower()
            if confirm not in ['n', 'no', '否']:
                print("\n🔄 执行完整Pipeline...")
                final_request = result["final_result"].final_prompt or result["final_result"].user_initial_request
                pipeline_result = planner.run_complete_pipeline(
                    final_request,
                    session_id
                )
                
                if pipeline_result.get("success"):
                    print("✅ Pipeline执行成功!")
                    print(f"📁 生成文件: {len(pipeline_result.get('generated_files', []))}个")
                    print(f"🔍 解释数量: {len(pipeline_result.get('explanations', []))}个")
                    
                    # 显示详细的Coder执行信息
                    if show_coder_details:
                        coder_result = pipeline_result.get("coder_result")
                        if coder_result:
                            print_coder_execution_details(coder_result)
                else:
                    print(f"❌ Pipeline执行失败: {pipeline_result.get('error')}")
                    
                    # 显示详细的错误信息
                    if show_coder_details:
                        coder_result = pipeline_result.get("coder_result")
                        if coder_result:
                            print_coder_execution_details(coder_result)
            
            print("\n🎉 多轮对话演示结束!")
            return
        
        # 多轮对话循环（从第2轮开始）
        turn_count = 1  # 已经完成了第1轮
        max_turns = 8
        
        while turn_count < max_turns:
            turn_count += 1
            
            print(f"\n{'='*60}")
            print(f"💬 第 {turn_count} 轮对话")
            print(f"{'='*60}")
            
            # 获取用户输入
            user_input = input(f"🎯 请继续对话 (第{turn_count}轮): ").strip()
            
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 用户退出对话")
                break
            
            if user_input.lower() in ['done', '完成', '确认']:
                print("✅ 用户确认需求完成")
                # 自动执行完整Pipeline
                print("\n🔄 自动执行完整Pipeline...")
                try:
                    # 使用会话中最终确认的需求，而不是初始需求
                    final_request = result["final_result"].final_prompt or initial_request
                    pipeline_result = planner.run_complete_pipeline(
                        final_request,  # 使用最终确认的需求
                        session_id
                    )
                    
                    if pipeline_result.get("success"):
                        print("✅ Pipeline执行成功!")
                        print(f"📁 生成文件: {len(pipeline_result.get('generated_files', []))}个")
                        print(f"🔍 解释数量: {len(pipeline_result.get('explanations', []))}个")
                        
                        # 显示生成的文件
                        generated_files = pipeline_result.get('generated_files', [])
                        if generated_files:
                            print(f"\n📁 生成的文件:")
                            for file_path in generated_files:
                                print(f"   - {file_path}")
                    else:
                        print(f"❌ Pipeline执行失败: {pipeline_result.get('error')}")
                except Exception as e:
                    print(f"❌ Pipeline执行异常: {str(e)}")
                break
            
            if not user_input:
                print("⚠️ 请输入有效的反馈")
                continue
            
            print(f"\n👤 用户: {user_input}")
            
            # 继续会话
            result = planner.continue_interactive_session(session_id, user_input)
            
            if result["success"]:
                if result.get("completed"):
                    print("\n🎉 需求规划已完成!")
                    
                    # 显示最终结果
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
                    
                    # 询问是否执行
                    confirm = input("\n🚀 是否执行完整Pipeline? (y/n，默认y): ").strip().lower()
                    if confirm not in ['n', 'no', '否']:
                        print("\n🔄 执行完整Pipeline...")
                        # 使用最终确认的需求，而不是初始需求
                        final_request = result["final_result"].final_prompt or result["final_result"].user_initial_request
                        pipeline_result = planner.run_complete_pipeline(
                            final_request,
                            session_id
                        )
                        
                        if pipeline_result.get("success"):
                            print("✅ Pipeline执行成功!")
                            print(f"📁 生成文件: {len(pipeline_result.get('generated_files', []))}个")
                            print(f"🔍 解释数量: {len(pipeline_result.get('explanations', []))}个")
                            
                            # 显示详细的Coder执行信息
                            if show_coder_details:
                                coder_result = pipeline_result.get("coder_result")
                                if coder_result:
                                    print_coder_execution_details(coder_result)
                        else:
                            print(f"❌ Pipeline执行失败: {pipeline_result.get('error')}")
                            
                            # 显示详细的错误信息
                            if show_coder_details:
                                coder_result = pipeline_result.get("coder_result")
                                if coder_result:
                                    print_coder_execution_details(coder_result)
                    
                    break
                    
                elif result.get("needs_confirmation"):
                    print(f"\n❓ 系统需要确认:")
                    print(f"   {result['confirmation_request']}")
                    
                    confirm = input("\n✅ 请确认 (y/n，默认y): ").strip().lower()
                    confirmation_input = "确认" if confirm not in ['n', 'no', '否'] else "取消"
                    
                    confirmation_result = planner.handle_confirmation(
                        session_id, confirmation_input
                    )
                    if confirmation_result["success"]:
                        print("✅ 确认完成，Pipeline执行成功!")
                        break
                    else:
                        print("❌ 确认失败")
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
                            for i, step in enumerate(status['task_steps'][:3], 1):  # 只显示前3个
                                print(f"     {i}. {step.get('description', 'N/A')}")
                        
                        if status.get("selected_dataset"):
                            print(f"   选定数据集: {status['selected_dataset'].get('name', 'unknown')}")
            else:
                print(f"❌ 对话失败: {result.get('error')}")
                break
        
        if turn_count >= max_turns:
            print(f"\n⚠️ 已达到最大对话轮次限制 ({max_turns}轮)")
            print("🔄 自动完成需求规划并执行Pipeline...")
            
            # 自动执行完整Pipeline
            try:
                # 尝试从会话中获取最终需求，如果没有则使用初始需求
                final_request = initial_request  # 默认使用初始需求
                pipeline_result = planner.run_complete_pipeline(
                    final_request,  # 使用最终需求
                    session_id
                )
                
                if pipeline_result.get("success"):
                    print("✅ Pipeline执行成功!")
                    print(f"📁 生成文件: {len(pipeline_result.get('generated_files', []))}个")
                    print(f"🔍 解释数量: {len(pipeline_result.get('explanations', []))}个")
                    
                    # 显示生成的文件
                    generated_files = pipeline_result.get('generated_files', [])
                    if generated_files:
                        print(f"\n📁 生成的文件:")
                        for file_path in generated_files:
                            print(f"   - {file_path}")
                    
                    # 显示详细的Coder执行信息
                    if show_coder_details:
                        coder_result = pipeline_result.get("coder_result")
                        if coder_result:
                            print_coder_execution_details(coder_result)
                else:
                    print(f"❌ Pipeline执行失败: {pipeline_result.get('error')}")
                    
                    # 显示详细的错误信息
                    if show_coder_details:
                        coder_result = pipeline_result.get("coder_result")
                        if coder_result:
                            print_coder_execution_details(coder_result)
            except Exception as e:
                print(f"❌ Pipeline执行异常: {str(e)}")
         
        
        print("\n🎉 多轮对话演示结束!")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 多轮对话交互演示")
    print("\n这个演示展示了如何与Planner进行真正的多轮对话")
    print("你可以逐步完善你的需求，系统会实时回复并调整计划")
    
    demo_multi_turn_dialogue()

if __name__ == "__main__":
    main()
