#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astro-Insight CopilotKit Agent包装器

将Astro-Insight的复杂工作流封装为CopilotKit兼容的Agent，
提供标准化的AI对话接口。
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import AIMessage, ToolMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, SecretStr

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_customize_config

# 导入Astro-Insight核心组件
from src.workflow import AstroWorkflow
from src.config import load_yaml_config

# 导入LangChain组件
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AstroState(CopilotKitState):
    """Astro-Insight扩展的CopilotKit状态"""
    ask_human: bool = False
    user_type: Optional[str] = None
    task_type: Optional[str] = None
    session_id: Optional[str] = None


class RequestAssistance(BaseModel):
    """专家协助请求模型"""
    request: str
    user_type: Optional[str] = None
    task_type: Optional[str] = None


class AstroInsightTool(BaseModel):
    """天文洞察工具模型"""
    query: str
    user_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@tool
def astro_insight_tool(query: str, user_type: Optional[str] = None) -> str:
    """天文科研洞察工具 - 调用Astro-Insight核心功能
    
    Args:
        query: 用户查询内容
        user_type: 用户类型 (amateur/professional)
        
    Returns:
        str: 天文科研回答
    """
    logger.info(f"🔍 天文洞察工具被调用")
    logger.info(f"   📝 查询内容: '{query}'")
    logger.info(f"   👤 用户类型: {user_type}")
    
    try:
        # 使用全局工作流实例
        global astro_workflow
        if astro_workflow is None:
            return "❌ 天文工作流未初始化，请稍后重试"
        
        # 生成会话ID
        session_id = f"copilotkit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # 构建用户上下文
        user_context = {}
        if user_type:
            user_context["user_type"] = user_type
        
        # 执行Astro-Insight工作流
        logger.info(f"   🚀 执行天文工作流，会话ID: {session_id}")
        result_state = astro_workflow.execute_workflow(
            session_id=session_id,
            user_input=query,
            user_context=user_context
        )
        
        # 提取回答
        answer = result_state.get("qa_response") or result_state.get("final_answer")
        if not answer:
            answer = "抱歉，我无法为您提供准确的天文信息。请尝试重新表述您的问题。"
        
        # 添加任务类型信息
        task_type = result_state.get("task_type", "unknown")
        if task_type != "unknown":
            answer = f"【{task_type}】{answer}"
        
        logger.info(f"   ✅ 天文工作流执行完成")
        logger.info(f"   📊 回答长度: {len(answer)} 字符")
        
        return answer
        
    except Exception as e:
        logger.error(f"   ❌ 天文洞察工具执行失败: {e}")
        return f"处理天文查询时出现错误: {str(e)}"


@tool  
def expert_assistance_tool(request: str, user_type: Optional[str] = None) -> str:
    """专家协助工具 - 请求专业天文研究支持
    
    Args:
        request: 协助请求内容
        user_type: 用户类型
        
    Returns:
        str: 专家协助响应
    """
    logger.info(f"👨‍🔬 专家协助工具被调用")
    logger.info(f"   📝 请求内容: '{request}'")
    logger.info(f"   👤 用户类型: {user_type}")
    
    # 构建专家协助响应
    response = f"我已收到您的专业协助请求：{request}\n\n"
    
    if user_type == "professional":
        response += "作为专业研究人员，我建议您：\n"
        response += "1. 查阅最新的学术论文和研究成果\n"
        response += "2. 联系相关领域的天文学专家\n"
        response += "3. 使用专业的天文数据分析工具\n"
    else:
        response += "作为天文爱好者，我建议您：\n"
        response += "1. 查阅权威的天文科普资料\n"
        response += "2. 参与天文爱好者的交流社区\n"
        response += "3. 咨询当地的天文台或天文协会\n"
    
    response += "\n如需进一步协助，请提供更详细的问题描述。"
    
    logger.info(f"   ✅ 专家协助响应生成完成")
    return response


# 初始化工具列表
tools = [astro_insight_tool, expert_assistance_tool]
logger.info(f"🛠️ 初始化Astro-Insight工具列表，共 {len(tools)} 个工具")

# 全局工作流实例
astro_workflow: Optional[AstroWorkflow] = None

# 全局LLM实例
llm_instance = None


def load_llm_config():
    """加载LLM配置 - 支持豆包、Ollama等多种配置"""
    global llm_instance
    
    try:
        # 加载Astro-Insight配置文件
        config = load_yaml_config()
        basic_model_config = config.get("BASIC_MODEL", {})
        
        base_url = basic_model_config.get("base_url", "")
        model = basic_model_config.get("model", "")
        api_key = basic_model_config.get("api_key", "")
        
        logger.info(f"🔧 加载LLM配置...")
        logger.info(f"   端点: {base_url}")
        logger.info(f"   模型: {model}")
        
        # 判断是否为本地Ollama
        if "localhost" in base_url or "127.0.0.1" in base_url or "ollama" in base_url.lower():
            logger.info("   🦙 检测到Ollama配置，使用本地模型")
            llm_instance = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key="ollama",  # Ollama不需要真实API key
                temperature=0.7,
                timeout=60,
            )
            
        # 判断是否为豆包
        elif "volces.com" in base_url or "doubao" in model.lower():
            logger.info("   🫘 检测到豆包配置，使用云端模型")
            llm_instance = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                timeout=60,
            )
            
        # 判断是否为OpenAI兼容接口
        elif "openai" in base_url or api_key.startswith("sk-"):
            logger.info("   🤖 检测到OpenAI兼容配置")
            llm_instance = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                timeout=60,
            )
            
        else:
            logger.warning("   ⚠️ 未知的LLM配置，尝试使用默认设置")
            llm_instance = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                timeout=60,
            )
        
        logger.info("   ✅ LLM实例初始化成功")
        return llm_instance
        
    except Exception as e:
        logger.error(f"   ❌ LLM配置加载失败: {e}")
        logger.info("   🔄 尝试使用环境变量回退配置...")
        
        # 回退到环境变量配置
        try:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("未找到API密钥")
                
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            llm_instance = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=0.7,
                timeout=60,
            )
            
            logger.info("   ✅ 环境变量配置回退成功")
            return llm_instance
            
        except Exception as fallback_error:
            logger.error(f"   ❌ 环境变量回退也失败: {fallback_error}")
            raise RuntimeError(f"无法初始化LLM: {fallback_error}")


def get_llm():
    """获取LLM实例"""
    global llm_instance
    if llm_instance is None:
        llm_instance = load_llm_config()
    return llm_instance


def initialize_astro_workflow(config_path: Optional[str] = None):
    """初始化Astro-Insight工作流"""
    global astro_workflow
    try:
        logger.info("🚀 初始化Astro-Insight工作流...")
        astro_workflow = AstroWorkflow(config_path)
        logger.info("✅ Astro-Insight工作流初始化成功")
        return True
    except Exception as e:
        logger.error(f"❌ Astro-Insight工作流初始化失败: {e}")
        return False


def astro_chatbot(state: AstroState, config: RunnableConfig):
    """Astro-Insight聊天机器人节点"""
    logger.info("🤖 Astro-Insight Chatbot 函数被调用")
    logger.info(f"   📥 收到消息数量: {len(state.get('messages', []))}")
    
    if state.get('messages'):
        last_message = state['messages'][-1]
        logger.info(f"   💬 最新消息: {last_message.content[:100]}...")
        logger.info(f"   📋 消息类型: {type(last_message).__name__}")
    
    try:
        # 获取LLM实例
        llm = get_llm()
        logger.info("   🔧 获取LLM实例成功")
        
        # 绑定工具
        llm_with_tools = llm.bind_tools(tools + [RequestAssistance])
        
        # 配置CopilotKit
        config = copilotkit_customize_config(config, emit_tool_calls=["RequestAssistance", "astro_insight_tool"])
        logger.info("   🔧 CopilotKit 配置已定制")
        
        # 调用LLM
        logger.info("   🚀 调用LLM...")
        response = llm_with_tools.invoke(state["messages"], config=config)
        logger.info(f"   📤 LLM响应类型: {type(response).__name__}")
        
        ask_human = False
        
        # 检查是否有工具调用
        if isinstance(response, AIMessage) and hasattr(response, "additional_kwargs"):
            tool_calls = response.additional_kwargs.get("tool_calls", [])
            logger.info(f"   🔧 检测到工具调用: {len(tool_calls)} 个")
            
            if tool_calls:
                for i, tool_call in enumerate(tool_calls):
                    tool_name = tool_call.get("function", {}).get("name", "unknown")
                    logger.info(f"      🛠️ 工具 {i+1}: {tool_name}")
                    
                    if tool_call.get("function", {}).get("name") == "RequestAssistance":
                        ask_human = True
                        logger.info("      👤 触发人工协助请求")
        
        logger.info(f"   🎯 返回状态: ask_human = {ask_human}")
        logger.info("✅ Astro-Insight Chatbot 函数执行完成")
        
        return {"messages": [response], "ask_human": ask_human}
        
    except Exception as e:
        logger.error(f"   ❌ Chatbot执行失败: {e}")
        
        # 回退到简单响应
        user_message = state['messages'][-1].content if state['messages'] else ""
        
        if "专家" in user_message or "专业" in user_message or "协助" in user_message:
            response_content = "我理解您需要专业协助。让我为您联系专家..."
            ask_human = True
        elif "天文" in user_message or "宇宙" in user_message or "星" in user_message:
            response_content = "我将使用天文洞察工具为您查询相关信息..."
            ask_human = False
        else:
            response_content = "我是您的天文科研助手，请问有什么可以帮助您的？"
            ask_human = False
        
        response = AIMessage(content=response_content)
        return {"messages": [response], "ask_human": ask_human}


def create_response(response: str, message: BaseMessage) -> ToolMessage:
    """创建工具响应消息"""
    logger.info(f"🔧 创建工具响应: {response[:50]}...")
    if isinstance(message, AIMessage) and hasattr(message, "additional_kwargs"):
        tool_calls = message.additional_kwargs.get("tool_calls", [])
        if tool_calls:
            tool_call_id = tool_calls[0].get("id", "default_id")
            logger.info(f"   🎯 使用工具调用ID: {tool_call_id}")
            return ToolMessage(
                content=response,
                tool_call_id=tool_call_id,
            )
    logger.info("   ⚠️ 使用默认工具调用ID")
    return ToolMessage(
        content=response,
        tool_call_id="default_id",
    )


def human_node(state: AstroState):
    """人工干预节点"""
    logger.info("👤 Human 节点被调用")
    logger.info(f"   📥 当前状态消息数量: {len(state.get('messages', []))}")
    
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        logger.info("   ⚠️ 最后一条消息不是 ToolMessage，添加占位符响应")
        new_messages.append(
            create_response("人工协助响应：我理解您的需求，正在为您安排专业支持。", state["messages"][-1])
        )
    else:
        logger.info("   ✅ 最后一条消息是 ToolMessage，无需添加占位符")
    
    logger.info(f"   📤 返回消息数量: {len(new_messages)}")
    logger.info("✅ Human 节点执行完成")
    
    return {
        "messages": new_messages,
        "ask_human": False,
    }


def select_next_node(state: AstroState):
    """选择下一个节点"""
    logger.info("🔀 选择下一个节点...")
    logger.info(f"   🔍 ask_human 状态: {state.get('ask_human', False)}")
    
    if state["ask_human"]:
        logger.info("   👤 路由到 human 节点")
        return "human"
    
    # 路由到工具节点
    logger.info("   🛠️ 路由到 tools 节点")
    return "tools"


def build_astro_graph():
    """构建Astro-Insight LangGraph"""
    logger.info("🔗 构建Astro-Insight LangGraph...")
    
    graph_builder = StateGraph(AstroState)
    
    # 添加节点
    graph_builder.add_node("chatbot", astro_chatbot)
    logger.info("   ✅ 添加 chatbot 节点")
    
    graph_builder.add_node("tools", ToolNode(tools=[astro_insight_tool, expert_assistance_tool]))
    logger.info("   ✅ 添加 tools 节点")
    
    graph_builder.add_node("human", human_node)
    logger.info("   ✅ 添加 human 节点")
    
    # 添加边和条件路由
    graph_builder.add_conditional_edges(
        "chatbot",
        select_next_node,
        {"human": "human", "tools": "tools", "__end__": "__end__"},
    )
    logger.info("   ✅ 添加 chatbot 的条件边")
    
    graph_builder.add_edge("tools", "chatbot")
    logger.info("   ✅ 添加 tools -> chatbot 边")
    
    graph_builder.add_edge("human", "chatbot")
    logger.info("   ✅ 添加 human -> chatbot 边")
    
    graph_builder.set_entry_point("chatbot")
    logger.info("   ✅ 设置 chatbot 为入口点")
    
    # 编译图
    memory = MemorySaver()
    logger.info("💾 初始化内存保存器")
    
    graph = graph_builder.compile(
        checkpointer=memory,
        interrupt_before=["human"],
    )
    logger.info("✅ Astro-Insight LangGraph 编译完成")
    
    return graph


# 全局图实例
astro_graph = None


def get_astro_graph():
    """获取Astro-Insight图实例"""
    global astro_graph
    if astro_graph is None:
        astro_graph = build_astro_graph()
    return astro_graph


class AstroAgent:
    """Astro-Insight CopilotKit代理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化Astro代理"""
        self.config_path = config_path
        self.graph = get_astro_graph()
        self.workflow = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """初始化代理"""
        if self.initialized:
            return True
            
        success = initialize_astro_workflow(self.config_path)
        if success:
            self.initialized = True
            # 获取全局工作流实例
            global astro_workflow
            self.workflow = astro_workflow
            logger.info("🎉 AstroAgent 初始化完成！")
        
        return success
    
    def get_graph(self):
        """获取LangGraph实例"""
        if not self.initialized:
            self.initialize()
        return self.graph
    
    def get_workflow(self):
        """获取Astro-Insight工作流实例"""
        if not self.initialized:
            self.initialize()
        return self.workflow


# 创建全局代理实例
astro_agent = AstroAgent()

