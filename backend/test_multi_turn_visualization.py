#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多轮可视化对话功能测试脚本
测试新的 visualization_command_node 多轮对话功能
"""

import sys
import os
from pathlib import Path

# 确保能找到项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_visualization_node():
    """测试可视化节点的多轮对话功能"""
    print("🧪 测试多轮可视化对话功能")
    print("=" * 60)
    
    try:
        # 导入必要的模块
        from src.workflow import AstroWorkflow
        from src.graph.types import create_initial_state
        
        # 创建工作流
        print("🔄 初始化工作流...")
        workflow = AstroWorkflow()
        print("✅ 工作流初始化完成")
        
        # 测试用例1：简单的可视化请求
        print("\n" + "=" * 60)
        print("📋 测试用例1: 简单可视化请求")
        print("=" * 60)
        
        test_input1 = "绘制星等分布图"
        session_id1 = "test_visualization_1"
        
        print(f"👤 用户输入: {test_input1}")
        print("🔄 执行工作流...")
        
        # 创建初始状态
        initial_state = create_initial_state(session_id1, test_input1)
        initial_state["user_type"] = "professional"
        
        # 执行工作流
        result1 = workflow.execute_workflow(session_id1, test_input1, initial_state)
        
        print("📊 执行结果:")
        print(f"   当前步骤: {result1.get('current_step', 'unknown')}")
        print(f"   任务类型: {result1.get('task_type', 'unknown')}")
        print(f"   是否完成: {result1.get('is_complete', False)}")
        print(f"   等待用户选择: {result1.get('awaiting_user_choice', False)}")
        
        if result1.get('visualization_dialogue_state'):
            print(f"   对话状态: {result1['visualization_dialogue_state']}")
            print(f"   对话轮次: {result1.get('visualization_turn_count', 0)}")
            print(f"   最大轮次: {result1.get('visualization_max_turns', 0)}")
        
        if result1.get('current_visualization_request'):
            print(f"   当前请求: {result1['current_visualization_request']}")
        
        # 测试用例2：复杂可视化请求
        print("\n" + "=" * 60)
        print("📋 测试用例2: 复杂可视化请求")
        print("=" * 60)
        
        test_input2 = "分析星系数据并生成可视化图表"
        session_id2 = "test_visualization_2"
        
        print(f"👤 用户输入: {test_input2}")
        print("🔄 执行工作流...")
        
        # 创建初始状态
        initial_state2 = create_initial_state(session_id2, test_input2)
        initial_state2["user_type"] = "professional"
        
        # 执行工作流
        result2 = workflow.execute_workflow(session_id2, test_input2, initial_state2)
        
        print("📊 执行结果:")
        print(f"   当前步骤: {result2.get('current_step', 'unknown')}")
        print(f"   任务类型: {result2.get('task_type', 'unknown')}")
        print(f"   是否完成: {result2.get('is_complete', False)}")
        print(f"   等待用户选择: {result2.get('awaiting_user_choice', False)}")
        
        if result2.get('visualization_dialogue_state'):
            print(f"   对话状态: {result2['visualization_dialogue_state']}")
            print(f"   对话轮次: {result2.get('visualization_turn_count', 0)}")
            print(f"   最大轮次: {result2.get('visualization_max_turns', 0)}")
        
        if result2.get('current_visualization_request'):
            print(f"   当前请求: {result2['current_visualization_request']}")
        
        # 测试用例3：模拟多轮对话
        if result2.get('awaiting_user_choice') and result2.get('visualization_dialogue_state') == 'clarifying':
            print("\n" + "=" * 60)
            print("📋 测试用例3: 模拟多轮对话")
            print("=" * 60)
            
            # 模拟用户回复
            user_response = "使用SDSS数据集，生成散点图展示星系大小和亮度的关系"
            print(f"👤 用户回复: {user_response}")
            
            # 继续对话
            result3 = workflow.continue_workflow(session_id2, user_response)
            
            print("📊 继续对话结果:")
            print(f"   当前步骤: {result3.get('current_step', 'unknown')}")
            print(f"   对话状态: {result3.get('visualization_dialogue_state', 'unknown')}")
            print(f"   对话轮次: {result3.get('visualization_turn_count', 0)}")
            print(f"   等待用户选择: {result3.get('awaiting_user_choice', False)}")
            
            # 模拟用户确认
            if result3.get('awaiting_user_choice'):
                print("\n🔄 模拟用户确认...")
                confirm_response = "done"
                print(f"👤 用户确认: {confirm_response}")
                
                result4 = workflow.continue_workflow(session_id2, confirm_response)
                
                print("📊 确认后结果:")
                print(f"   当前步骤: {result4.get('current_step', 'unknown')}")
                print(f"   是否完成: {result4.get('is_complete', False)}")
                print(f"   等待用户选择: {result4.get('awaiting_user_choice', False)}")
                
                if result4.get('generated_files'):
                    print(f"   生成文件: {len(result4['generated_files'])}个")
                    for file_path in result4['generated_files']:
                        print(f"     - {file_path}")
        
        print("\n✅ 多轮可视化对话功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_state_fields():
    """测试状态字段扩展"""
    print("\n🧪 测试状态字段扩展")
    print("=" * 60)
    
    try:
        from src.graph.types import create_initial_state
        
        # 创建测试状态
        session_id = "test_state_fields"
        user_input = "测试状态字段"
        
        state = create_initial_state(session_id, user_input)
        
        # 测试新增的可视化对话字段
        state["visualization_session_id"] = "test_session_123"
        state["visualization_dialogue_state"] = "started"
        state["current_visualization_request"] = "请详细描述您的可视化需求"
        state["visualization_turn_count"] = 1
        state["visualization_max_turns"] = 8
        state["visualization_dialogue_history"] = []
        
        print("✅ 状态字段扩展测试通过")
        print(f"   可视化会话ID: {state.get('visualization_session_id')}")
        print(f"   对话状态: {state.get('visualization_dialogue_state')}")
        print(f"   当前请求: {state.get('current_visualization_request')}")
        print(f"   对话轮次: {state.get('visualization_turn_count')}")
        print(f"   最大轮次: {state.get('visualization_max_turns')}")
        
    except Exception as e:
        print(f"❌ 状态字段测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🚀 多轮可视化对话功能测试")
    print("=" * 80)
    
    # 测试状态字段扩展
    test_state_fields()
    
    # 测试可视化节点功能
    test_visualization_node()
    
    print("\n" + "=" * 80)
    print("🎉 所有测试完成!")
    print("\n💡 使用说明:")
    print("1. 运行 'python main.py' 进入交互模式")
    print("2. 输入可视化相关请求，如 '绘制星等分布图'")
    print("3. 系统会引导您进行多轮对话来澄清需求")
    print("4. 输入 'done' 或 '完成' 确认需求并执行")
    print("5. 输入 'quit' 或 '退出' 取消对话")

if __name__ == "__main__":
    main()
