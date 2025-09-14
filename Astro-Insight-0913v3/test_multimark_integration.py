#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试multimark集成是否真正工作
"""

import sys
import os
import time
sys.path.insert(0, 'src')

def test_multimark_integration():
    """测试multimark集成"""
    print("🧪 测试multimark集成")
    print("=" * 50)
    
    try:
        # 1. 测试MCP ML客户端
        print("1. 测试MCP ML客户端...")
        from src.mcp_ml.client import get_ml_client
        
        client = get_ml_client()
        print(f"✅ 客户端类型: {type(client)}")
        
        # 2. 测试初始化
        print("\n2. 测试客户端初始化...")
        init_result = client.initialize()
        print(f"初始化结果: {init_result}")
        
        if init_result:
            print("✅ 客户端初始化成功")
            
            # 3. 测试调用run_pipeline
            print("\n3. 测试调用run_pipeline...")
            print("开始调用run_pipeline...")
            
            # 设置超时
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("调用超时")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30秒超时
            
            try:
                result = client.run_pipeline()
                print(f"✅ run_pipeline调用成功")
                print(f"结果: {result[:200]}...")
            except TimeoutError:
                print("❌ run_pipeline调用超时")
            except Exception as e:
                print(f"❌ run_pipeline调用失败: {str(e)}")
            finally:
                signal.alarm(0)  # 取消超时
            
            # 4. 检查服务器进程
            print("\n4. 检查服务器进程...")
            import subprocess
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            print(f"Python进程: {result.stdout}")
            
        else:
            print("❌ 客户端初始化失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multimark_integration()
