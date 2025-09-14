#!/usr/bin/env python3
"""
测试修复后的可视化功能
"""

def test_visualization_fix():
    print("🧪 测试修复后的可视化功能...")
    
    try:
        from agent import graph
        
        # 测试可视化功能
        result = graph.invoke({
            'messages': [{'role': 'user', 'content': '我是专业天文学家，我想对星系分类数据进行可视化分析'}],
            'user_input': '我是专业天文学家，我想对星系分类数据进行可视化分析',
            'ask_human': False,
            'session_id': 'test_visualization_fixed'
        }, {'configurable': {'thread_id': 'test_visualization_fixed'}})
        
        print(f"📊 最终节点: {result.get('current_node', '未知')}")
        print(f"📊 用户类型: {result.get('user_type', '未知')}")
        print(f"📊 任务类型: {result.get('task_type', '未知')}")
        print(f"📊 节点历史: {result.get('node_history', [])}")
        
        if 'final_answer' in result:
            print(f"\n📝 可视化结果 ({len(str(result['final_answer']))} 字符):")
            print("="*60)
            print(result['final_answer'])
            print("="*60)
        
        # 检查是否找到了数据集
        if 'visualization_dialogue_history' in result:
            dialogue_history = result['visualization_dialogue_history']
            print(f"\n💬 可视化对话历史 ({len(dialogue_history)} 轮):")
            for i, dialogue in enumerate(dialogue_history, 1):
                print(f"📝 第 {i} 轮:")
                print(f"   用户: {dialogue.get('user_input', 'N/A')}")
                print(f"   系统: {dialogue.get('assistant_response', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_visualization_fix()
    print(f"\n结果: {'成功' if success else '失败'}")

