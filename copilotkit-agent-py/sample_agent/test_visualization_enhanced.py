#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版多轮对话可视化节点测试
模拟完整的多轮对话流程，包含用户交互模拟、条件判断和错误处理
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加 Astro-Insight 路径
astro_insight_path = Path(__file__).parent.parent.parent / "Astro-Insight-0913v3"
sys.path.insert(0, str(astro_insight_path))

print("🧪 增强版多轮对话可视化节点测试...")
print(f"🔍 添加 Astro-Insight 路径: {astro_insight_path}")
print(f"🔍 路径存在: {astro_insight_path.exists()}")

class VisualizationTestSimulator:
    """可视化测试模拟器 - 模拟多轮对话和用户交互"""
    
    def __init__(self):
        self.test_scenarios = [
            {
                "name": "基础可视化需求",
                "conversation": [
                    "绘制天体位置图",
                    "我想绘制银河系中恒星的位置分布图",
                    "使用红色表示红巨星，蓝色表示蓝巨星，黄色表示主序星",
                    "完成"
                ],
                "expected_outcomes": ["clarifying", "completed"]
            },
            {
                "name": "复杂可视化需求",
                "conversation": [
                    "创建天文数据可视化",
                    "我需要分析星系分类数据",
                    "绘制散点图，x轴是颜色指数，y轴是星等",
                    "添加不同颜色表示不同星系类型",
                    "添加图例和标题",
                    "完成"
                ],
                "expected_outcomes": ["clarifying", "clarifying", "completed"]
            },
            {
                "name": "用户取消场景",
                "conversation": [
                    "绘制天体图",
                    "我想看看恒星数据",
                    "退出"
                ],
                "expected_outcomes": ["clarifying", "cancelled"]
            },
            {
                "name": "达到最大轮次限制",
                "conversation": [
                    "绘制图",
                    "什么图？",
                    "天体图",
                    "什么天体？",
                    "恒星",
                    "什么类型的恒星？",
                    "主序星",
                    "什么颜色？",
                    "蓝色",
                    "什么大小？"
                ],
                "expected_outcomes": ["clarifying"] * 9 + ["completed"]
            }
        ]
        
        self.current_scenario = None
        self.current_state = None
        self.test_results = []
    
    def create_test_state(self, user_input: str, session_id: str = None, dialogue_state: str = None, turn_count: int = 0) -> Dict[str, Any]:
        """创建测试状态"""
        return {
            "session_id": session_id or f"test_session_{int(time.time())}",
            "user_input": user_input,
            "messages": [],
            "user_type": "professional",
            "task_type": "visualization",
            "config_data": {},
            "current_step": "visualization_start",
            "next_step": None,
            "is_complete": False,
            "awaiting_user_choice": False,
            "user_choice": None,
            "qa_response": None,
            "response": None,
            "final_answer": None,
            "generated_code": None,
            "execution_result": None,
            "error_info": None,
            "retry_count": 0,
            "execution_history": [],
            "node_history": [],
            "current_node": None,
            "timestamp": time.time(),
            "visualization_session_id": session_id,
            "visualization_dialogue_state": dialogue_state,
            "current_visualization_request": None,
            "visualization_turn_count": turn_count,
            "visualization_max_turns": 8,
            "visualization_dialogue_history": []
        }
    
    def simulate_user_interaction(self, state: Dict[str, Any]) -> str:
        """模拟用户交互 - 根据当前状态决定用户输入"""
        if not state.get("awaiting_user_choice", False):
            return None
        
        # 模拟用户根据系统提示做出选择
        current_request = state.get("current_visualization_request", "")
        
        # 智能用户模拟 - 根据系统提示选择合适的回复
        if "颜色" in current_request or "color" in current_request.lower():
            return "使用红色表示红巨星，蓝色表示蓝巨星，黄色表示主序星"
        elif "大小" in current_request or "size" in current_request.lower():
            return "使用不同大小的点表示不同的恒星质量"
        elif "类型" in current_request or "type" in current_request.lower():
            return "包含主序星、红巨星、蓝巨星和白矮星"
        elif "数据" in current_request or "dataset" in current_request.lower():
            return "使用恒星分类数据集"
        elif "确认" in current_request or "confirm" in current_request.lower():
            return "确认"
        elif "完成" in current_request or "done" in current_request.lower():
            return "完成"
        else:
            # 默认提供更多细节
            return "请添加图例、标题和坐标轴标签"
    
    def run_test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试场景"""
        print(f"\n{'='*80}")
        print(f"🎯 测试场景: {scenario['name']}")
        print(f"{'='*80}")
        
        conversation = scenario["conversation"]
        expected_outcomes = scenario["expected_outcomes"]
        
        current_state = None
        actual_outcomes = []
        test_passed = True
        
        for i, user_input in enumerate(conversation):
            print(f"\n🔄 第 {i+1} 轮对话")
            print(f"👤 用户输入: {user_input}")
            
            # 创建或更新状态
            if current_state is None:
                current_state = self.create_test_state(user_input)
            else:
                current_state["user_input"] = user_input
                current_state["awaiting_user_choice"] = True
                current_state["visualization_dialogue_state"] = "clarifying"
            
            # 调用可视化节点
            try:
                from src.graph.nodes import visualization_command_node
                result = visualization_command_node(current_state)
                
                print(f"📋 执行结果: {type(result).__name__}")
                print(f"🎯 目标节点: {result.goto if hasattr(result, 'goto') else 'N/A'}")
                
                if hasattr(result, 'update') and result.update:
                    updated_state = result.update
                    current_state = updated_state
                    
                    # 记录实际结果
                    if updated_state.get("is_complete", False):
                        if "cancelled" in updated_state.get("current_step", ""):
                            actual_outcomes.append("cancelled")
                        else:
                            actual_outcomes.append("completed")
                    elif updated_state.get("awaiting_user_choice", False):
                        actual_outcomes.append("clarifying")
                    
                    # 显示状态信息
                    self.display_state_info(updated_state, i+1)
                    
                    # 检查是否完成
                    if updated_state.get("is_complete", False):
                        print(f"\n🎉 可视化流程完成！")
                        break
                    elif updated_state.get("awaiting_user_choice", False):
                        print(f"\n⏳ 等待用户进一步输入...")
                        
                        # 模拟用户交互
                        simulated_input = self.simulate_user_interaction(updated_state)
                        if simulated_input and i < len(conversation) - 1:
                            print(f"🤖 模拟用户回复: {simulated_input}")
                            # 更新用户输入为模拟的回复
                            current_state["user_input"] = simulated_input
                else:
                    print(f"   ❌ 没有更新状态")
                    test_passed = False
                    break
                    
            except Exception as e:
                print(f"❌ 测试失败: {str(e)}")
                import traceback
                traceback.print_exc()
                test_passed = False
                break
        
        # 比较预期结果和实际结果
        outcome_match = actual_outcomes == expected_outcomes[:len(actual_outcomes)]
        
        return {
            "scenario_name": scenario["name"],
            "test_passed": test_passed and outcome_match,
            "expected_outcomes": expected_outcomes,
            "actual_outcomes": actual_outcomes,
            "outcome_match": outcome_match,
            "final_state": current_state
        }
    
    def display_state_info(self, state: Dict[str, Any], turn: int):
        """显示状态信息"""
        print(f"📊 第{turn}轮状态:")
        print(f"   🆔 会话ID: {state.get('visualization_session_id', 'None')}")
        print(f"   🔄 对话状态: {state.get('visualization_dialogue_state', 'None')}")
        print(f"   📊 轮次: {state.get('visualization_turn_count', 0)}")
        print(f"   ⏳ 等待用户选择: {state.get('awaiting_user_choice', False)}")
        print(f"   🔄 当前步骤: {state.get('current_step', 'N/A')}")
        print(f"   ✅ 是否完成: {state.get('is_complete', False)}")
        
        if state.get('error_info'):
            print(f"   ❌ 错误信息: {state['error_info']}")
        
        if state.get('final_answer'):
            answer_preview = state['final_answer'][:200] + "..." if len(state['final_answer']) > 200 else state['final_answer']
            print(f"   📝 最终回答预览: {answer_preview}")
    
    def run_all_tests(self):
        """运行所有测试场景"""
        print("🚀 开始运行所有测试场景...")
        
        for scenario in self.test_scenarios:
            result = self.run_test_scenario(scenario)
            self.test_results.append(result)
            
            # 显示测试结果
            status = "✅ 通过" if result["test_passed"] else "❌ 失败"
            print(f"\n📊 测试结果: {status}")
            print(f"   预期结果: {result['expected_outcomes']}")
            print(f"   实际结果: {result['actual_outcomes']}")
            print(f"   结果匹配: {'✅' if result['outcome_match'] else '❌'}")
        
        # 显示总体测试结果
        self.display_summary()
    
    def display_summary(self):
        """显示测试总结"""
        print(f"\n{'='*80}")
        print("📊 测试总结")
        print(f"{'='*80}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["test_passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {failed_tests} ❌")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["test_passed"]:
                    print(f"   - {result['scenario_name']}")
        
        print(f"\n🎉 增强版多轮对话可视化测试完成！")

def main():
    """主函数"""
    try:
        # 检查依赖
        print("🔍 检查依赖...")
        from src.graph.nodes import visualization_command_node
        from src.graph.types import AstroAgentState
        print("✅ 依赖检查通过")
        
        # 创建测试模拟器
        simulator = VisualizationTestSimulator()
        
        # 运行所有测试
        simulator.run_all_tests()
        
    except Exception as e:
        print(f"❌ 测试初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
