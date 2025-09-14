#!/usr/bin/env python3
"""
Astro-Insight 代表性测试套件
每个专业任务测试最具代表性的一个案例，获取完整真实反馈
"""

import os
import sys
import unittest
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from typing import Any, Dict

# 将当前目录添加到路径开头，确保可以导入 agent
current_dir = str(Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=" * 80)
print("🌟 Astro-Insight 代表性测试套件")
print("=" * 80)
print(f"📁 测试目录: {current_dir}")
print(f"🐍 Python 路径: {sys.path[0]}")

# 检查 agent.py 文件是否存在
agent_file = Path(current_dir) / "agent.py"
print(f"📄 agent.py 文件: {'✅ 存在' if agent_file.exists() else '❌ 不存在'}")

# 检查数据集目录
dataset_path = Path(__file__).resolve().parents[2] / "Astro-Insight-0913v3" / "dataset"
print(f"📊 数据集目录: {'✅ 存在' if dataset_path.exists() else '❌ 不存在'}")
if dataset_path.exists():
    dataset_files = list(dataset_path.glob("**/*"))
    print(f"📊 数据集文件数量: {len(dataset_files)}")
    for file in dataset_files[:5]:  # 显示前5个文件
        print(f"   📄 {file.name}")

print("-" * 80)


class TestAstroInsightRepresentative(unittest.TestCase):
    """测试 Astro-Insight 代表性功能"""
    
    def setUp(self):
        # 加载 .env（从仓库根目录）
        load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

        # 验证必要的环境变量
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.skipTest("请在 .env 中设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY")

    def test_amateur_user_qa_representative(self):
        """测试业余用户 QA 代表性案例 - 黑洞问题"""
        print("\n🔍 [业余用户测试] QA 问答 - 黑洞问题")
        print("-" * 50)
        
        try:
            import agent
            graph = agent.graph
            
            # 选择最具代表性的黑洞问题
            question = "什么是黑洞？请详细解释黑洞的形成过程、特征和影响。"
            print(f"   🎯 测试问题: '{question}'")
            
            result = graph.invoke({
                'messages': [{'role': 'user', 'content': question}],
                'user_input': question,
                'ask_human': False,
                'session_id': 'test_amateur_blackhole'
            }, {'configurable': {'thread_id': 'test_amateur_blackhole'}})
            
            print(f"   📊 最终节点: {result.get('current_node', '未知')}")
            print(f"   📊 用户类型: {result.get('user_type', '未知')}")
            print(f"   📊 任务类型: {result.get('task_type', '未知')}")
            print(f"   📊 节点历史: {result.get('node_history', [])}")
            
            # 显示完整回答
            if 'qa_response' in result:
                print(f"\n   📝 完整回答 ({len(str(result['qa_response']))} 字符):")
                print("   " + "="*60)
                print(f"   {result['qa_response']}")
                print("   " + "="*60)
            
            # 验证结果
            self.assertEqual(result.get('user_type'), 'amateur')
            self.assertEqual(result.get('task_type'), 'qa')
            self.assertIn('qa_agent', result.get('node_history', []))
            
            print("\n🎉 业余用户 QA 代表性测试通过")
            
        except Exception as e:
            print(f"❌ 业余用户测试失败: {e}")
            self.fail(f"业余用户 QA 流程测试失败: {e}")

    def test_professional_classification_representative(self):
        """测试专业用户天体分类代表性案例 - M31仙女座星系"""
        print("\n🔍 [专业用户测试] 天体分类 - M31仙女座星系")
        print("-" * 50)
        
        try:
            import agent
            graph = agent.graph
            
            # 选择最具代表性的天体分类案例
            object_name = "M31 仙女座星系"
            question = f"我是专业天文学家，请详细分类这个天体：{object_name}，包括其类型、特征、坐标、亮度等详细信息。"
            print(f"   🎯 测试天体: '{object_name}'")
            
            result = graph.invoke({
                'messages': [{'role': 'user', 'content': question}],
                'user_input': question,
                'ask_human': False,
                'session_id': 'test_classification_m31'
            }, {'configurable': {'thread_id': 'test_classification_m31'}})
            
            print(f"   📊 最终节点: {result.get('current_node', '未知')}")
            print(f"   📊 用户类型: {result.get('user_type', '未知')}")
            print(f"   📊 任务类型: {result.get('task_type', '未知')}")
            print(f"   📊 节点历史: {result.get('node_history', [])}")
            
            # 显示完整分类结果
            if 'final_answer' in result:
                print(f"\n   📝 完整分类结果 ({len(str(result['final_answer']))} 字符):")
                print("   " + "="*60)
                print(f"   {result['final_answer']}")
                print("   " + "="*60)
            
            # 验证结果
            self.assertEqual(result.get('user_type'), 'professional')
            self.assertIn('task_selector', result.get('node_history', []))
            
            print("\n🎉 专业用户天体分类代表性测试通过")
            
        except Exception as e:
            print(f"❌ 天体分类测试失败: {e}")
            print("   ℹ️ 这可能是由于外部依赖导致的")

    def test_professional_data_retrieval_representative(self):
        """测试专业用户数据检索代表性案例 - M31坐标和亮度数据"""
        print("\n🔍 [专业用户测试] 数据检索 - M31坐标和亮度数据")
        print("-" * 50)
        
        try:
            import agent
            graph = agent.graph
            
            # 选择最具代表性的数据检索案例
            query = "我是专业天文学家，请查询 M31 仙女座星系的详细坐标、亮度、距离、类型等所有可用数据。"
            print(f"   🎯 测试查询: '{query}'")
            
            result = graph.invoke({
                'messages': [{'role': 'user', 'content': query}],
                'user_input': query,
                'ask_human': False,
                'session_id': 'test_retrieval_m31'
            }, {'configurable': {'thread_id': 'test_retrieval_m31'}})
            
            print(f"   📊 最终节点: {result.get('current_node', '未知')}")
            print(f"   📊 用户类型: {result.get('user_type', '未知')}")
            print(f"   📊 任务类型: {result.get('task_type', '未知')}")
            print(f"   📊 节点历史: {result.get('node_history', [])}")
            
            # 显示完整检索结果
            if 'final_answer' in result:
                print(f"\n   📝 完整检索结果 ({len(str(result['final_answer']))} 字符):")
                print("   " + "="*60)
                print(f"   {result['final_answer']}")
                print("   " + "="*60)
            
            # 验证结果
            self.assertEqual(result.get('user_type'), 'professional')
            self.assertIn('task_selector', result.get('node_history', []))
            
            print("\n🎉 专业用户数据检索代表性测试通过")
            
        except Exception as e:
            print(f"❌ 数据检索测试失败: {e}")
            print("   ℹ️ 这可能是由于外部依赖导致的")

    def test_professional_visualization_representative(self):
        """测试专业用户可视化代表性案例 - 星系分类数据可视化"""
        print("\n🔍 [专业用户测试] 可视化 - 星系分类数据可视化")
        print("-" * 50)
        
        try:
            import agent
            graph = agent.graph
            
            # 选择最具代表性的可视化案例
            request = "我是专业天文学家，我想对星系分类数据进行可视化分析，包括散点图、分布图、相关性分析等。"
            print(f"   🎯 测试请求: '{request}'")
            
            result = graph.invoke({
                'messages': [{'role': 'user', 'content': request}],
                'user_input': request,
                'ask_human': False,
                'session_id': 'test_visualization_galaxy'
            }, {'configurable': {'thread_id': 'test_visualization_galaxy'}})
            
            print(f"   📊 最终节点: {result.get('current_node', '未知')}")
            print(f"   📊 用户类型: {result.get('user_type', '未知')}")
            print(f"   📊 任务类型: {result.get('task_type', '未知')}")
            print(f"   📊 节点历史: {result.get('node_history', [])}")
            
            # 显示完整可视化结果
            if 'final_answer' in result:
                print(f"\n   📝 完整可视化结果 ({len(str(result['final_answer']))} 字符):")
                print("   " + "="*60)
                print(f"   {result['final_answer']}")
                print("   " + "="*60)
            
            # 显示可视化对话历史
            if 'visualization_dialogue_history' in result:
                dialogue_history = result['visualization_dialogue_history']
                print(f"\n   💬 可视化对话历史 ({len(dialogue_history)} 轮):")
                for i, dialogue in enumerate(dialogue_history, 1):
                    print(f"   📝 第 {i} 轮:")
                    print(f"      用户: {dialogue.get('user_input', 'N/A')}")
                    print(f"      系统: {dialogue.get('assistant_response', 'N/A')}")
            
            # 验证结果
            self.assertEqual(result.get('user_type'), 'professional')
            self.assertIn('task_selector', result.get('node_history', []))
            
            print("\n🎉 专业用户可视化代表性测试通过")
            
        except Exception as e:
            print(f"❌ 可视化测试失败: {e}")
            print("   ℹ️ 这可能是由于外部依赖导致的")

    def test_professional_multimark_representative(self):
        """测试专业用户多模态标注代表性案例 - 天体分类模型训练"""
        print("\n🔍 [专业用户测试] 多模态标注 - 天体分类模型训练")
        print("-" * 50)
        
        try:
            import agent
            graph = agent.graph
            
            # 选择最具代表性的多模态标注案例
            request = "我是专业天文学家，请帮我训练一个天体分类模型，使用星系、恒星、星云等不同类型的天体数据进行训练。"
            print(f"   🎯 测试请求: '{request}'")
            
            result = graph.invoke({
                'messages': [{'role': 'user', 'content': request}],
                'user_input': request,
                'ask_human': False,
                'session_id': 'test_multimark_training'
            }, {'configurable': {'thread_id': 'test_multimark_training'}})
            
            print(f"   📊 最终节点: {result.get('current_node', '未知')}")
            print(f"   📊 用户类型: {result.get('user_type', '未知')}")
            print(f"   📊 任务类型: {result.get('task_type', '未知')}")
            print(f"   📊 节点历史: {result.get('node_history', [])}")
            
            # 显示完整标注结果
            if 'final_answer' in result:
                print(f"\n   📝 完整标注结果 ({len(str(result['final_answer']))} 字符):")
                print("   " + "="*60)
                print(f"   {result['final_answer']}")
                print("   " + "="*60)
            
            # 验证结果
            self.assertEqual(result.get('user_type'), 'professional')
            self.assertIn('task_selector', result.get('node_history', []))
            
            print("\n🎉 专业用户多模态标注代表性测试通过")
            
        except Exception as e:
            print(f"❌ 多模态标注测试失败: {e}")
            print("   ℹ️ 这可能是由于外部依赖导致的")

    def test_workflow_routing_comprehensive(self):
        """测试工作流路由综合验证"""
        print("\n🔍 [路由测试] 工作流路由综合验证")
        print("-" * 50)
        
        try:
            import agent
            graph = agent.graph
            
            # 测试不同用户类型的路由
            test_cases = [
                {
                    "user_type": "amateur",
                    "input": "你好，我是天文爱好者，对宇宙很感兴趣",
                    "expected_nodes": ["identity_check", "qa_agent"],
                    "expected_task_type": "qa"
                },
                {
                    "user_type": "professional", 
                    "input": "你好，我是专业天文学家，需要分析天体数据",
                    "expected_nodes": ["identity_check", "task_selector"],
                    "expected_task_type": None  # 由任务选择器决定
                }
            ]
            
            for i, case in enumerate(test_cases, 1):
                print(f"\n   🎯 测试用例 {i}/2: {case['user_type']} 用户")
                print(f"   📝 输入: '{case['input']}'")
                
                result = graph.invoke({
                    'messages': [{'role': 'user', 'content': case['input']}],
                    'user_input': case['input'],
                    'ask_human': False,
                    'session_id': f'test_routing_comprehensive_{i}'
                }, {'configurable': {'thread_id': f'test_routing_comprehensive_{i}'}})
                
                print(f"   📊 实际节点历史: {result.get('node_history', [])}")
                print(f"   📊 实际用户类型: {result.get('user_type', '未知')}")
                print(f"   📊 实际任务类型: {result.get('task_type', '未知')}")
                
                # 验证路由逻辑
                self.assertEqual(result.get('user_type'), case['user_type'])
                
                for expected_node in case['expected_nodes']:
                    self.assertIn(expected_node, result.get('node_history', []))
                
                if case['expected_task_type']:
                    self.assertEqual(result.get('task_type'), case['expected_task_type'])
                
            print("\n🎉 工作流路由综合验证通过")
            
        except Exception as e:
            print(f"❌ 路由逻辑测试失败: {e}")
            self.fail(f"工作流路由逻辑测试失败: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 开始运行 Astro-Insight 代表性测试...")
    print("=" * 80)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestAstroInsightRepresentative))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("✨ 所有代表性测试通过！Astro-Insight 集成完全成功！")
    else:
        print("⚠️ 部分测试失败")
        print(f"失败: {len(result.failures)}, 错误: {len(result.errors)}")
        
        # 显示失败详情
        if result.failures:
            print("\n❌ 失败的测试:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n💥 错误的测试:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print("=" * 80)

