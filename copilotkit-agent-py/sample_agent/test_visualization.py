#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试可视化节点功能
"""

import sys
import os
from pathlib import Path

# 添加 Astro-Insight 路径
astro_insight_path = Path(__file__).parent.parent.parent / "Astro-Insight-0913v3"
sys.path.insert(0, str(astro_insight_path))

print("🧪 测试可视化节点...")
print(f"🔍 添加 Astro-Insight 路径: {astro_insight_path}")
print(f"🔍 路径存在: {astro_insight_path.exists()}")

try:
    from src.graph.builder import build_graph
    from src.graph.types import AstroAgentState
    from langchain_core.messages import HumanMessage
    
    print("🛠️ 初始化工具列表，共 1 个工具")
    
    # 创建 Agent
    print("🔧 Agent 初始化中...")
    agent = build_graph()
    print("🎉 Agent 初始化完成！")
    
    # 测试可视化请求
    test_messages = [
        "我是专业天文学家，请帮我绘制一个星系分布图",
        "生成一个M87星系的光谱图",
        "可视化银河系的结构图"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试 {i}: {message}")
        print(f"{'='*60}")
        
        try:
            # 创建测试状态
            test_state = {
                "messages": [HumanMessage(content=message)],
                "user_input": message,
                "current_node": "chatbot",
                "node_history": [],
                "execution_history": [],
                "user_type": "professional",
                "task_type": "visualization",
                "current_step": "start",
                "is_complete": False,
                "final_answer": "",
                "ask_human": False
            }
            
            print(f"🤖 处理消息: {message}")
            
            # 运行 Agent
            result = agent.invoke(test_state)
            
            print(f"📊 最终节点: {result.get('current_node', 'unknown')}")
            print(f"📊 用户类型: {result.get('user_type', 'unknown')}")
            print(f"📊 任务类型: {result.get('task_type', 'unknown')}")
            print(f"📊 节点历史: {result.get('node_history', [])}")
            print(f"📊 是否完成: {result.get('is_complete', False)}")
            
            if result.get('final_answer'):
                answer = result['final_answer']
                print(f"\n📝 最终回答 ({len(answer)} 字符):")
                print("="*60)
                print(answer)
                print("="*60)
            
            print(f"✅ 测试 {i} 完成")
            
        except Exception as e:
            print(f"❌ 测试 {i} 失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 所有可视化测试完成！")
    
except Exception as e:
    print(f"❌ 初始化失败: {str(e)}")
    import traceback
    traceback.print_exc()
