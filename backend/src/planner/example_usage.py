# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Planner模块使用示例

展示如何使用Planner模块进行需求规划和任务分解
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.planner import PlannerWorkflow, PlannerAgent


def example_interactive_session():
    """示例：交互式会话"""
    print("🎯 示例：交互式会话")
    print("=" * 40)
    
    # 创建Planner工作流
    planner = PlannerWorkflow()
    
    # 开始交互式会话
    user_request = "我想分析星系数据"
    session = planner.run_interactive_session(user_request)
    
    if not session["success"]:
        print(f"❌ 会话创建失败: {session.get('error')}")
        return
    
    session_id = session["session_id"]
    print(f"✅ 会话已创建: {session_id}")
    
    # 模拟多轮对话
    dialogue_turns = [
        "我想看看星系的分类情况",
        "使用SDSS数据集",
        "生成散点图展示星系的特征",
        "分析星系的大小和亮度关系",
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
                final_result = result["final_result"]
                print(f"📋 最终prompt长度: {len(final_result.final_prompt or '')}")
                print(f"🔧 任务步骤数: {len(final_result.task_steps)}")
                break
            elif result.get("needs_confirmation"):
                print("❓ 需要确认:")
                print(result["confirmation_request"])
                
                # 模拟用户确认
                confirmation_result = planner.handle_confirmation(
                    session_id, "确认，开始执行"
                )
                if confirmation_result["success"]:
                    print("✅ 用户已确认，开始执行完整pipeline")
                break
            else:
                print("🔄 会话继续...")
        else:
            print(f"❌ 对话失败: {result.get('error')}")
            break


def example_complete_pipeline():
    """示例：完整Pipeline"""
    print("\n🎯 示例：完整Pipeline")
    print("=" * 40)
    
    # 创建Planner工作流
    planner = PlannerWorkflow()
    
    # 运行完整pipeline
    user_request = "分析星系数据，生成散点图展示星系的大小和亮度关系"
    
    print(f"📝 用户需求: {user_request}")
    print("🚀 开始执行完整pipeline...")
    
    result = planner.run_complete_pipeline(user_request)
    
    if result["success"]:
        print("✅ Pipeline执行成功！")
        print(f"📊 会话ID: {result['session_id']}")
        print(f"⏱️ 总处理时间: {result.get('total_processing_time', 0):.2f}秒")
        print(f"📁 生成文件数: {len(result.get('generated_files', []))}")
        print(f"🔧 任务步骤数: {len(result.get('task_steps', []))}")
        
        # 显示任务步骤
        print("\n📋 任务步骤:")
        for i, step in enumerate(result.get('task_steps', []), 1):
            print(f"  {i}. {step['description']}")
        
        # 显示生成的文件
        generated_files = result.get('generated_files', [])
        if generated_files:
            print("\n📁 生成的文件:")
            for file_path in generated_files:
                print(f"  - {file_path}")
        
        # 显示解释结果
        explanations = result.get('explanations', [])
        if explanations:
            print(f"\n🔍 生成了 {len(explanations)} 个解释")
        
    else:
        print(f"❌ Pipeline执行失败: {result.get('error')}")
        print(f"错误类型: {result.get('error_type')}")


def example_agent_only():
    """示例：直接使用Agent"""
    print("\n🎯 示例：直接使用Agent")
    print("=" * 40)
    
    # 创建Agent
    agent = PlannerAgent()
    
    # 开始规划会话
    user_request = "我想分析恒星数据"
    state = agent.start_planning_session(user_request)
    
    print(f"✅ 会话已创建: {state.session_id}")
    print(f"📊 可用数据集: {len(state.available_datasets)}")
    
    # 模拟一轮对话
    user_input = "使用恒星分类数据集，分析恒星的类型分布"
    state = agent.process_user_input(state, user_input)
    
    print(f"💬 第 {state.current_turn} 轮对话完成")
    print(f"🔄 对话状态: {state.dialogue_status.value}")
    
    # 检查是否需要确认
    if state.task_steps and state.final_prompt:
        print("📋 任务规划完成，请求用户确认...")
        confirmation_request = agent.request_confirmation(state)
        print(f"确认请求: {confirmation_request[:100]}...")
    
    # 保存会话
    save_path = agent.save_session(state)
    print(f"💾 会话已保存: {save_path}")


def main():
    """运行所有示例"""
    print("🚀 Planner模块使用示例")
    print("=" * 50)
    
    try:
        # 示例1：交互式会话
        example_interactive_session()
        
        # 示例2：完整Pipeline
        example_complete_pipeline()
        
        # 示例3：直接使用Agent
        example_agent_only()
        
        print("\n🎉 所有示例运行完成！")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
