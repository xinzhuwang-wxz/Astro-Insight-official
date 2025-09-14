#!/usr/bin/env python3
"""
测试字段冲突是否解决
"""

def test_field_conflict():
    print("🧪 测试字段冲突解决...")
    
    try:
        from agent import graph
        print("✅ 图导入成功")
        
        # 创建测试状态
        initial_state = {
            'messages': [{'role': 'user', 'content': '你好，我想了解天文学'}],
            'user_input': '你好，我想了解天文学',
            'ask_human': False,
            'session_id': 'test_session'
        }
        
        # 使用正确的配置
        config = {'configurable': {'thread_id': 'test_thread_123'}}
        
        print("🔧 开始执行图...")
        result = graph.invoke(initial_state, config)
        
        print("✅ 图执行成功！")
        print(f"📊 最终状态键: {list(result.keys())}")
        
        # 检查字段值
        if 'qa_response' in result:
            print(f"📝 qa_response 存在，长度: {len(str(result['qa_response']))} 字符")
        if 'final_answer' in result:
            print(f"📝 final_answer 存在，长度: {len(str(result['final_answer']))} 字符")
            
        print("🎉 字段冲突问题已解决！")
        return True
        
    except Exception as e:
        print(f"❌ 图执行失败: {e}")
        if 'qa_response' in str(e):
            print("⚠️ qa_response 字段冲突仍然存在")
        else:
            print("🔍 其他错误")
        return False

if __name__ == "__main__":
    success = test_field_conflict()
    if success:
        print("\n✨ 测试通过！字段冲突已解决！")
    else:
        print("\n❌ 测试失败！字段冲突仍然存在！")

