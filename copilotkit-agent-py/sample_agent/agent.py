import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage, ChatMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import SecretStr
# NOTE: you must use langchain-core >= 0.3 with Pydantic v2
from pydantic import BaseModel
from typing import Annotated, List, Dict, Any, Optional, Literal
from langgraph.graph.message import add_messages
from operator import add

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_customize_config

# 添加 Astro-Insight 路径
astro_insight_path = Path(__file__).resolve().parents[2] / "Astro-Insight-0913v3"
sys.path.insert(0, str(astro_insight_path))
print(f"🔍 添加 Astro-Insight 路径: {astro_insight_path}")
print(f"🔍 路径存在: {astro_insight_path.exists()}")

# 导入 Astro-Insight 的节点和状态
from src.graph.nodes import (
    identity_check_command_node,
    qa_agent_command_node,
    task_selector_command_node,
    classification_config_command_node,
    data_retrieval_command_node,
    visualization_command_node,
    multimark_command_node,
    error_recovery_command_node
)
from src.graph.types import AstroAgentState
from src.graph.builder import route_after_identity_check, route_after_task_selection, route_after_error_recovery


class State(CopilotKitState):
    # CopilotKit 原有字段
    ask_human: bool
    
    # Astro-Insight 兼容字段 - 使用 Annotated 类型避免并发更新冲突
    user_type: Optional[Literal["amateur", "professional"]] = "amateur"
    task_type: Optional[Literal["classification", "retrieval", "visualization", "qa"]] = "classification"
    retry_count: int = 0
    error_info: Optional[Dict[str, Any]] = None
    current_step: str = "identity_check"
    next_step: Optional[str] = None
    is_complete: bool = False
    awaiting_user_choice: bool = False
    user_choice: Optional[str] = None
    
    # 使用正确的 LangGraph 状态定义，避免并发更新冲突
    # 对于可能被多个节点更新的字段，使用 Annotated 类型
    qa_response: Annotated[Optional[str], lambda x, y: y if y is not None else x] = None
    response: Optional[str] = None
    final_answer: Annotated[Optional[str], lambda x, y: y if y is not None else x] = None
    generated_code: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    execution_history: Annotated[List[Dict[str, Any]], add] = []
    node_history: Annotated[List[str], add] = []
    current_node: Optional[str] = None
    timestamp: float = 0.0
    config_data: Dict[str, Any] = {}
    
    # 添加 Astro-Insight 需要的额外字段
    session_id: str = ""
    user_input: str = ""
    
    # 添加 Astro-Insight 需要的其他字段
    visualization_session_id: Optional[str] = None
    visualization_dialogue_state: Optional[Literal["started", "clarifying", "completed", "failed"]] = None
    current_visualization_request: Optional[str] = None
    visualization_turn_count: int = 0
    visualization_max_turns: int = 5
    visualization_dialogue_history: Annotated[List[Dict[str, Any]], add] = []


class RequestAssistance(BaseModel):
    """Escalate the conversation to an expert. Use this if you are unable to assist directly or if the user requires support beyond your permissions.

    To use this function, relay the user's 'request' so the expert can provide the right guidance.
    """

    request: str


@tool
def search_tool(query: str) -> str:
    """搜索相关信息的工具。
    
    Args:
        query: 搜索查询字符串
        
    Returns:
        str: 搜索结果
    """
    print(f"🔍 搜索工具被调用")
    print(f"   📝 搜索查询: '{query}'")
    
    # 简化的搜索工具，返回固定的结果
    result = f"关于 '{query}' 的搜索结果：这是一个模拟的搜索结果。在实际应用中，这里会连接到真实的搜索API。"
    
    print(f"   📊 搜索结果长度: {len(result)} 字符")
    print(f"   ✅ 搜索工具执行完成")
    
    return result

tools = [search_tool]
print(f"🛠️ 初始化工具列表，共 {len(tools)} 个工具")

# 加载环境变量
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

# 优先使用 OPENROUTER_API_KEY；没有则回落到 OPENAI_API_KEY
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("请在 .env 中设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY")

base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

print("🔧 Agent 初始化中...")
print(f"   🎯 使用模型: {model}")
print(f"   🔗 API 端点: {base_url}")
print(f"   🔑 API 密钥: {api_key[:10] if api_key else 'None'}...")

# 使用 ChatOpenAI 指向 OpenRouter
llm = ChatOpenAI(
    model=model,
    api_key=SecretStr(api_key),
    base_url=base_url,
    temperature=0.7,
    timeout=60,
    max_tokens=1000,  # 限制最大 token 数
)
print("✅ LLM 初始化完成")

# We can bind the llm to a tool definition, a pydantic model, or a json schema
llm_with_tools = llm.bind_tools(tools + [RequestAssistance])
print(f"🛠️ 工具绑定完成，共 {len(tools + [RequestAssistance])} 个工具")


def chatbot(state: State, config: RunnableConfig):
    print("🤖 Chatbot 函数被调用")
    print(f"   📥 收到消息数量: {len(state.get('messages', []))}")
    if state.get('messages'):
        last_message = state['messages'][-1]
        print(f"   💬 最新消息: {last_message.content[:100]}...")
        print(f"   📋 消息类型: {type(last_message).__name__}")
    
    # 从最新消息中提取用户输入
    user_input = ""
    if state.get('messages'):
        user_input = state['messages'][-1].content
        print(f"   📝 提取的用户输入: {user_input[:50]}...")
    
    # 所有问答都直接跳转到 Astro-Insight 的 Qwen 模型
    if user_input:
        print("   🎯 所有问答都交由 Astro-Insight 的 Qwen 模型处理")
        # 返回一个简单的确认消息，让 Astro-Insight 处理
        response = AIMessage(content="好的，我来帮您处理这个问题。")
        return {"messages": [response], "ask_human": False, "user_input": user_input}
    
    config = copilotkit_customize_config(config, emit_tool_calls="RequestAssistance")
    print("   🔧 CopilotKit 配置已定制")
    
    print("   🚀 调用 LLM...")
    response = llm_with_tools.invoke(state["messages"], config=config)
    print(f"   📤 LLM 响应类型: {type(response).__name__}")
    print(f"   📝 LLM 响应内容: {response.content[:100] if response.content else 'None'}...")
    
    ask_human = False
    
    # Check if response is AIMessage and has additional_kwargs with tool_calls
    if isinstance(response, AIMessage) and hasattr(response, "additional_kwargs"):
        tool_calls = response.additional_kwargs.get("tool_calls", [])
        print(f"   🔧 检测到工具调用: {len(tool_calls)} 个")
        
        if tool_calls:
            for i, tool_call in enumerate(tool_calls):
                tool_name = tool_call.get("function", {}).get("name", "unknown")
                print(f"      🛠️ 工具 {i+1}: {tool_name}")
                
                if tool_call.get("name") == RequestAssistance.__name__:
                    ask_human = True
                    print("      👤 触发人工协助请求")
    
    print(f"   🎯 返回状态: ask_human = {ask_human}")
    print("✅ Chatbot 函数执行完成")
    
    return {"messages": [response], "ask_human": ask_human, "user_input": user_input}


graph_builder = StateGraph(State)

print("🔗 构建 LangGraph...")
graph_builder.add_node("chatbot", chatbot)
print("   ✅ 添加 chatbot 节点")

# 添加 Astro-Insight 节点
graph_builder.add_node("identity_check", identity_check_command_node)
print("   ✅ 添加 identity_check 节点")

graph_builder.add_node("qa_agent", qa_agent_command_node)
print("   ✅ 添加 qa_agent 节点")

graph_builder.add_node("task_selector", task_selector_command_node)
print("   ✅ 添加 task_selector 节点")

graph_builder.add_node("classification_config", classification_config_command_node)
print("   ✅ 添加 classification_config 节点")

graph_builder.add_node("data_retrieval", data_retrieval_command_node)
print("   ✅ 添加 data_retrieval 节点")

graph_builder.add_node("visualization", visualization_command_node)
print("   ✅ 添加 visualization 节点")

graph_builder.add_node("multimark", multimark_command_node)
print("   ✅ 添加 multimark 节点")

graph_builder.add_node("error_recovery", error_recovery_command_node)
print("   ✅ 添加 error_recovery 节点")

# 删除 tools 节点，因为现在直接跳转到 Astro-Insight


# 删除不再需要的工具和人工节点函数


# 删除 human 节点，因为现在直接跳转到 Astro-Insight


def select_next_node(state: State):
    print("🔀 选择下一个节点...")
    print(f"   🔍 ask_human 状态: {state.get('ask_human', False)}")
    
    # 直接跳转到 Astro-Insight 的 identity_check 节点
    print("   🚀 直接跳转到 Astro-Insight identity_check...")
    return "identity_check"


print("🔗 添加图的边和条件路由...")
# 从 chatbot 直接跳转到 identity_check
graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {"identity_check": "identity_check"},
)
print("   ✅ 添加 chatbot 到 identity_check 的条件边")

# 从 identity_check 到其他 Astro-Insight 节点
graph_builder.add_conditional_edges(
    "identity_check",
    route_after_identity_check,
    {
        "qa_agent": "qa_agent",
        "task_selector": "task_selector",
        "error_recovery": "error_recovery"
    }
)
print("   ✅ 添加 identity_check 的条件边")

# 从 task_selector 到专业功能节点
graph_builder.add_conditional_edges(
    "task_selector",
    route_after_task_selection,
    {
        "classification_config": "classification_config",
        "data_retrieval": "data_retrieval",
        "visualization": "visualization",
        "multimark": "multimark",
        "error_recovery": "error_recovery"
    }
)
print("   ✅ 添加 task_selector 的条件边")

# 从 error_recovery 到结束
graph_builder.add_conditional_edges(
    "error_recovery",
    route_after_error_recovery,
    {
        "__end__": "__end__"
    }
)
print("   ✅ 添加 error_recovery 的条件边")

# 所有专业功能节点都直接结束
graph_builder.add_edge("qa_agent", "__end__")
print("   ✅ 添加 qa_agent -> __end__ 边")

graph_builder.add_edge("classification_config", "__end__")
print("   ✅ 添加 classification_config -> __end__ 边")

graph_builder.add_edge("data_retrieval", "__end__")
print("   ✅ 添加 data_retrieval -> __end__ 边")

graph_builder.add_edge("visualization", "__end__")
print("   ✅ 添加 visualization -> __end__ 边")

graph_builder.add_edge("multimark", "__end__")
print("   ✅ 添加 multimark -> __end__ 边")

# 删除原有的工具和人工节点边，因为现在直接跳转到 Astro-Insight

graph_builder.set_entry_point("chatbot")
print("   ✅ 设置 chatbot 为入口点")

memory = MemorySaver()
print("💾 初始化内存保存器")

graph = graph_builder.compile(
    checkpointer=memory,
)
print("✅ LangGraph 编译完成")
print("🎉 Agent 初始化完成！")