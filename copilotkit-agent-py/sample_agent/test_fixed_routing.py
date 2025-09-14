#!/usr/bin/env python3
"""
测试修复后的路由
"""

def test_fixed_routing():
    print("🧪 测试修复后的路由...")
    
    try:
        from agent import graph
        
        # 测试训练模型请求
        result = graph.invoke({
            'messages': [{'role': 'user', 'content': '我是专业天文学家，请帮我训练一个天体模型'}],
            'user_input': '我是专业天文学家，请帮我训练一个天体模型',
            'ask_human': False,
            'session_id': 'test_fixed_routing'
        }, {'configurable': {'thread_id': 'test_fixed_routing'}})
        
        print(f"📊 最终节点: {result.get('current_node', '未知')}")
        print(f"📊 用户类型: {result.get('user_type', '未知')}")
        print(f"📊 任务类型: {result.get('task_type', '未知')}")
        print(f"📊 节点历史: {result.get('node_history', [])}")
        
        if 'final_answer' in result:
            print(f"\n📝 最终回答 ({len(str(result['final_answer']))} 字符):")
            print("="*60)
            print(result['final_answer'])
            print("="*60)
        
        # 检查是否正确路由到 multimark
        if 'multimark' in result.get('node_history', []):
            print("\n✅ 成功路由到 multimark 节点！")
        else:
            print("\n❌ 未能正确路由到 multimark 节点")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_routing()
    print(f"\n结果: {'成功' if success else '失败'}")
