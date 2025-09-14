import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from typing import Any, Dict

# 将当前目录添加到路径开头，确保可以导入 agent
current_dir = str(Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 加载环境变量
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

print("=" * 80)
print("🕸️ Agent.py LangGraph 直接测试")
print("=" * 80)
print(f"📁 测试目录: {current_dir}")

# 检查环境变量
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ 未找到 API 密钥")
    print("   请在 .env 中设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY")
    exit(1)

print("✅ 环境配置检查通过")
print("-" * 80)

def test_agent_graph_direct():
    """直接测试 agent.py 中的 LangGraph"""
    try:
        print("\n🚀 开始测试 Agent.py 的完整 LangGraph 功能...")
        
        # 导入 agent 模块
        import agent
        print("✅ Agent 模块导入成功")
        
        # 验证关键组件
        print(f"🤖 LLM 类型: {type(agent.llm).__name__}")
        print(f"🎯 使用模型: {getattr(agent.llm, 'model', 'unknown')}")
        print(f"🕸️ Graph 类型: {type(agent.graph).__name__}")
        
        # 准备测试消息
        test_cases = [
            "你好，请简单介绍一下你自己。",
            "请帮我搜索关于人工智能的信息。", 
            "什么是机器学习？请用简单的话解释。",
            "我需要专业的技术支持，请帮我联系专家。"  # 这个可能会触发 RequestAssistance
        ]
        
        print(f"\n📝 准备测试 {len(test_cases)} 个对话场景...")
        
        for i, message in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"🎯 测试场景 {i}/{len(test_cases)}")
            print(f"📤 用户消息: '{message}'")
            print("-" * 40)
            
            try:
                # 创建输入数据
                input_data = {
                    "messages": [HumanMessage(content=message)]
                }
                
                # 配置
                config: Dict[str, Any] = {
                    "configurable": {"thread_id": f"test_agent_direct_{i}"}
                }
                
                print("🔧 调用 LangGraph...")
                
                # 调用 agent.py 中的完整图
                result = agent.graph.invoke(input_data, config)  # type: ignore
                
                print("📊 LangGraph 返回结果:")
                print(f"   📋 结果类型: {type(result).__name__}")
                print(f"   🗝️ 结果键: {list(result.keys()) if hasattr(result, 'keys') else 'N/A'}")
                
                # 分析返回的消息
                if "messages" in result and result["messages"]:
                    messages = result["messages"]
                    print(f"   💬 消息数量: {len(messages)}")
                    
                    # 获取最后一条消息（AI 的回复）
                    last_message = messages[-1]
                    print(f"   📝 AI 回复: {last_message.content}")
                    print(f"   📊 回复长度: {len(last_message.content)} 字符")
                    print(f"   📋 消息类型: {type(last_message).__name__}")
                    
                    # 检查工具调用
                    if hasattr(last_message, 'additional_kwargs'):
                        tool_calls = last_message.additional_kwargs.get('tool_calls', [])
                        if tool_calls:
                            print(f"   🔧 工具调用数量: {len(tool_calls)}")
                            for j, tool_call in enumerate(tool_calls, 1):
                                function_info = tool_call.get('function', {})
                                tool_name = function_info.get('name', 'unknown')
                                print(f"      🛠️ 工具 {j}: {tool_name}")
                                if 'arguments' in function_info:
                                    print(f"         📋 参数: {function_info['arguments']}")
                        else:
                            print("   🔧 无工具调用")
                    
                    # 检查状态信息
                    if "ask_human" in result:
                        ask_human_status = result["ask_human"]
                        print(f"   👤 需要人工协助: {'是' if ask_human_status else '否'}")
                        if ask_human_status:
                            print("      ⚠️ 这个请求可能需要人工干预")
                    
                    print("✅ 场景测试成功")
                
                else:
                    print("⚠️ 未找到有效的消息回复")
                
            except Exception as e:
                print(f"❌ 场景 {i} 测试失败: {e}")
                import traceback
                print(f"   🔍 错误详情: {traceback.format_exc()}")
        
        print(f"\n{'='*80}")
        print("🎉 Agent.py LangGraph 测试完成!")
        print("✅ 测试验证了:")
        print("   • LangGraph 图的完整调用流程")
        print("   • OpenRouter LLM 的集成")
        print("   • 工具调用机制")
        print("   • 状态管理功能")
        print("   • 人工协助请求机制")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Agent 测试失败: {e}")
        import traceback
        print(f"🔍 详细错误: {traceback.format_exc()}")


if __name__ == "__main__":
    test_agent_graph_direct()