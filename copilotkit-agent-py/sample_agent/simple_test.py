#!/usr/bin/env python3
"""
简单测试字段冲突
"""

def main():
    print("🧪 简单测试字段冲突...")
    
    try:
        from agent import graph
        print("✅ 导入成功")
        
        # 测试
        result = graph.invoke({
            'messages': [{'role': 'user', 'content': '你好'}],
            'user_input': '你好',
            'ask_human': False,
            'session_id': 'test'
        }, {'configurable': {'thread_id': 'test'}})
        
        print("✅ 执行成功！")
        print(f"状态键: {list(result.keys())}")
        
        if 'qa_response' in result and 'final_answer' in result:
            print("✅ 两个字段都存在")
            print(f"qa_response: {str(result['qa_response'])[:50]}...")
            print(f"final_answer: {str(result['final_answer'])[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n结果: {'成功' if success else '失败'}")

