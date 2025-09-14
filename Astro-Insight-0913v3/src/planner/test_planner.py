# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Planner模块测试文件

测试Planner模块的基本功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.planner import (
    PlannerWorkflow, PlannerAgent, DatasetManager,
    PlannerState, DialogueStatus, TaskComplexity
)


def test_dataset_manager():
    """测试数据集管理器"""
    print("🧪 测试数据集管理器...")
    
    try:
        dm = DatasetManager()
        datasets = dm.get_available_datasets()
        
        print(f"📊 发现 {len(datasets)} 个数据集")
        
        if datasets:
            dataset = datasets[0]
            print(f"✅ 第一个数据集: {dataset.name}")
            print(f"   - 描述: {dataset.description}")
            print(f"   - 列数: {len(dataset.columns)}")
            print(f"   - 路径: {dataset.path}")
            
            # 测试数据集摘要
            summary = dm.get_dataset_summary()
            print(f"📋 数据集摘要长度: {len(summary)} 字符")
            
            return True
        else:
            print("⚠️ 没有找到数据集")
            return False
            
    except Exception as e:
        print(f"❌ 数据集管理器测试失败: {e}")
        return False


def test_planner_agent():
    """测试Planner Agent"""
    print("🧪 测试Planner Agent...")
    
    try:
        agent = PlannerAgent()
        
        # 测试初始状态创建
        user_request = "我想分析星系数据，看看星系的分类情况"
        state = agent.start_planning_session(user_request)
        
        print(f"✅ 初始状态创建成功")
        print(f"   - 会话ID: {state.session_id}")
        print(f"   - 用户请求: {state.user_initial_request}")
        print(f"   - 对话状态: {state.dialogue_status.value}")
        print(f"   - 可用数据集: {len(state.available_datasets)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Planner Agent测试失败: {e}")
        return False


def test_planner_workflow():
    """测试Planner工作流"""
    print("🧪 测试Planner工作流...")
    
    try:
        workflow = PlannerWorkflow()
        
        # 测试交互式会话创建
        user_request = "我想分析星系数据"
        session_result = workflow.run_interactive_session(user_request)
        
        if session_result["success"]:
            print(f"✅ 交互式会话创建成功")
            print(f"   - 会话ID: {session_result['session_id']}")
            print(f"   - 当前轮次: {session_result['current_turn']}")
            print(f"   - 最大轮次: {session_result['max_turns']}")
            return True
        else:
            print(f"❌ 交互式会话创建失败: {session_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Planner工作流测试失败: {e}")
        return False


def test_complete_pipeline():
    """测试完整Pipeline（需要LLM和数据集）"""
    print("🧪 测试完整Pipeline...")
    
    try:
        workflow = PlannerWorkflow()
        
        # 测试完整pipeline
        user_request = "分析星系数据，生成散点图"
        result = workflow.run_complete_pipeline(user_request)
        
        if result["success"]:
            print(f"✅ 完整Pipeline执行成功")
            print(f"   - 会话ID: {result['session_id']}")
            print(f"   - 任务步骤数: {len(result.get('task_steps', []))}")
            print(f"   - 生成文件数: {len(result.get('generated_files', []))}")
            print(f"   - 处理时间: {result.get('total_processing_time', 0):.2f}秒")
            return True
        else:
            print(f"❌ 完整Pipeline执行失败: {result.get('error')}")
            print(f"   错误类型: {result.get('error_type')}")
            return False
            
    except Exception as e:
        print(f"❌ 完整Pipeline测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("🚀 开始测试Planner模块...")
    print("=" * 50)
    
    tests = [
        ("数据集管理器", test_dataset_manager),
        ("Planner Agent", test_planner_agent),
        ("Planner工作流", test_planner_workflow),
        ("完整Pipeline", test_complete_pipeline),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！Planner模块工作正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")


if __name__ == "__main__":
    main()
