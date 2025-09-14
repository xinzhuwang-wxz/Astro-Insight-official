#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试multimark节点调用server工具
"""

import sys
import os
sys.path.insert(0, 'src')

def test_multimark_server_call():
    """测试multimark节点调用server工具"""
    print("🧪 测试multimark节点调用server工具")
    print("=" * 60)
    
    try:
        # 1. 测试MCP ML客户端导入
        print("1. 测试MCP ML客户端导入...")
        from src.mcp_ml.client import get_ml_client
        client = get_ml_client()
        print(f"✅ 客户端类型: {type(client)}")
        
        # 2. 测试客户端初始化
        print("\n2. 测试客户端初始化...")
        init_result = client.initialize()
        print(f"初始化结果: {init_result}")
        
        if init_result:
            print("✅ 客户端初始化成功")
            
            # 3. 测试调用run_pipeline工具
            print("\n3. 测试调用run_pipeline工具...")
            try:
                result = client.run_pipeline()
                print(f"✅ run_pipeline调用成功")
                print(f"结果长度: {len(result)} 字符")
                print(f"结果预览: {result[:200]}...")
                
                # 4. 检查结果内容
                print("\n4. 检查结果内容...")
                if "error" in result.lower():
                    print("⚠️ 结果包含错误信息")
                elif "success" in result.lower():
                    print("✅ 结果包含成功信息")
                else:
                    print("ℹ️ 结果内容未知")
                
            except Exception as e:
                print(f"❌ run_pipeline调用失败: {str(e)}")
            
            # 5. 关闭客户端
            print("\n5. 关闭客户端...")
            client.close()
            print("✅ 客户端关闭成功")
            
        else:
            print("❌ 客户端初始化失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_multimark_node_direct():
    """直接测试multimark节点"""
    print("\n🔧 直接测试multimark节点")
    print("=" * 60)
    
    try:
        from src.graph.nodes import multimark_command_node
        from src.graph.types import AstroAgentState
        
        # 创建测试状态
        state = AstroAgentState(
            session_id="test_multimark_server_call",
            user_input="我是专业人士 开始训练模型",
            user_type="professional",
            task_type="multimark",
            current_step="multimark_start",
            is_complete=False,
            messages=[],
            execution_history=[]
        )
        
        print("1. 调用multimark节点...")
        result = multimark_command_node(state)
        
        print(f"✅ 节点执行成功")
        print(f"任务类型: {result.update.get('task_type')}")
        print(f"当前步骤: {result.update.get('current_step')}")
        print(f"是否完成: {result.update.get('is_complete')}")
        print(f"下一步: {result.goto}")
        
        # 显示最终答案
        final_answer = result.update.get('final_answer', '')
        if final_answer:
            print(f"\n📝 最终答案预览:")
            print(f"{final_answer[:300]}...")
        
        # 检查执行历史
        execution_history = result.update.get('execution_history', [])
        if execution_history:
            print(f"\n📋 执行历史: {len(execution_history)}条记录")
            for i, entry in enumerate(execution_history, 1):
                print(f"  {i}. {entry.get('action', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 直接测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multimark_server_call()
    test_multimark_node_direct()
