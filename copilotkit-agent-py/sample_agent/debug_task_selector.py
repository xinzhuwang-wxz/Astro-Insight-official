#!/usr/bin/env python3
"""
调试 task_selector 节点的路由逻辑
"""

def debug_task_selector():
    print("🔍 调试 task_selector 节点的路由逻辑...")
    
    try:
        from agent import graph
        
        # 测试不同的输入
        test_cases = [
            "我是专业天文学家，请帮我训练一个天体分类模型",
            "训练一个天体分类模型",
            "训练模型",
            "机器学习",
            "深度学习",
            "标注图像",
            "图像识别"
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n🎯 测试用例 {i}: '{test_input}'")
            
            # 直接调用 task_selector 节点
            result = graph.invoke({
                'messages': [{'role': 'user', 'content': test_input}],
                'user_input': test_input,
                'ask_human': False,
                'session_id': f'debug_task_{i}',
                'user_type': 'professional'  # 直接设置为专业用户
            }, {'configurable': {'thread_id': f'debug_task_{i}'}})
            
            print(f"   📊 最终节点: {result.get('current_node', '未知')}")
            print(f"   📊 任务类型: {result.get('task_type', '未知')}")
            print(f"   📊 节点历史: {result.get('node_history', [])}")
            
            # 检查是否走到了正确的节点
            if 'multimark' in test_input.lower() or '训练' in test_input:
                expected = 'multimark'
                actual = result.get('current_node', '')
                if expected in actual:
                    print(f"   ✅ 正确路由到 {expected}")
                else:
                    print(f"   ❌ 错误路由，期望 {expected}，实际 {actual}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_task_selector()
    print(f"\n结果: {'成功' if success else '失败'}")

