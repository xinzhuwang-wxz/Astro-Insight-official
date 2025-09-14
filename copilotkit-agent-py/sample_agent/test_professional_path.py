#!/usr/bin/env python3
"""
测试专业节点路径
"""

def test_professional_path():
    print("🧪 测试专业节点路径...")
    
    try:
        from agent import graph
        
        # 测试1: 业余用户路径
        print("\n📝 测试1: 业余用户路径")
        result1 = graph.invoke({
            'messages': [{'role': 'user', 'content': '你好，我是业余爱好者'}],
            'user_input': '你好，我是业余爱好者',
            'ask_human': False,
            'session_id': 'test_amateur'
        }, {'configurable': {'thread_id': 'test_amateur'}})
        
        print("✅ 业余用户路径完成")
        print(f"📊 最终节点: {result1.get('current_node', '未知')}")
        print(f"📊 用户类型: {result1.get('user_type', '未知')}")
        print(f"📊 任务类型: {result1.get('task_type', '未知')}")
        print(f"📊 节点历史: {result1.get('node_history', [])}")
        
        # 测试2: 专业用户路径
        print("\n📝 测试2: 专业用户路径")
        result2 = graph.invoke({
            'messages': [{'role': 'user', 'content': '你好，我是专业天文学家'}],
            'user_input': '你好，我是专业天文学家',
            'ask_human': False,
            'session_id': 'test_professional'
        }, {'configurable': {'thread_id': 'test_professional'}})
        
        print("✅ 专业用户路径完成")
        print(f"📊 最终节点: {result2.get('current_node', '未知')}")
        print(f"📊 用户类型: {result2.get('user_type', '未知')}")
        print(f"📊 任务类型: {result2.get('task_type', '未知')}")
        print(f"📊 节点历史: {result2.get('node_history', [])}")
        
        # 分析结果
        print("\n🔍 路径分析:")
        if 'task_selector' in result2.get('node_history', []):
            print("✅ 专业用户成功走到了 task_selector 节点")
        else:
            print("❌ 专业用户没有走到 task_selector 节点")
            
        if 'qa_agent' in result1.get('node_history', []):
            print("✅ 业余用户成功走到了 qa_agent 节点")
        else:
            print("❌ 业余用户没有走到 qa_agent 节点")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_professional_path()
    print(f"\n结果: {'成功' if success else '失败'}")

