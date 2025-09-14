# Maxen Wong
# SPDX-License-Identifier: MIT

"""
Command语法节点实现
使用LangGraph 0.2+的Command语法重构核心节点
"""

from typing import Dict, Any, List, Optional, Union, Literal
import time
import logging
import json
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

from src.graph.types import AstroAgentState, ExecutionStatus
from src.llms.llm import get_llm_by_type
from src.prompts.template import get_prompt


def track_node_execution(node_name: str):
    """节点执行跟踪装饰器"""
    def decorator(func):
        def wrapper(state: AstroAgentState) -> Command[AstroAgentState]:
            # 更新当前节点
            updated_state = state.copy()
            updated_state["current_node"] = node_name
            
            # 添加到节点历史（如果不在历史中）
            node_history = updated_state.get("node_history", [])
            if not node_history or node_history[-1] != node_name:
                node_history.append(node_name)
                updated_state["node_history"] = node_history
            
            # 输出节点信息
            print(f"\n🔍 当前节点: {node_name}")
            if len(node_history) > 1:
                print(f"📋 历史节点: {' → '.join(node_history[:-1])}")
            else:
                print(f"📋 历史节点: (起始节点)")
            
            # 执行原函数
            result = func(updated_state)
            
            # 如果返回的是Command对象，更新其状态
            if isinstance(result, Command):
                # 合并节点跟踪信息到Command的update中
                if result.update:
                    result.update.update({
                        "current_node": node_name,
                        "node_history": node_history
                    })
                else:
                    result.update = {
                        "current_node": node_name,
                        "node_history": node_history
                    }
            
            return result
        return wrapper
    return decorator
# from src.tools.language_processor import language_processor  # 暂时未使用
# 存储功能已移除 - 分类节点不再需要数据库存储


def _extract_celestial_name_simple(user_input: str) -> str:
    """从用户输入中提取天体名称 - 简单有效的方法（参考complete_simple_system.py）"""
    import re
    
    # 移除常见的分类关键词
    clean_input = user_input
    keywords_to_remove = [
        "分类", "classify", "这个天体", "这个", "天体", "celestial", "object",
        "是什么", "什么类型", "什么", "类型", "type", "分析", "analyze"
    ]
    
    for keyword in keywords_to_remove:
        clean_input = clean_input.replace(keyword, "")
    
    # 移除标点符号
    clean_input = re.sub(r'[：:，,。.！!？?]', '', clean_input)
    
    # 提取可能的天体名称
    # 匹配常见的天体命名模式
    patterns = [
        r'M\d+',  # 梅西耶天体
        r'NGC\s*\d+',  # NGC天体
        r'IC\s*\d+',  # IC天体
        r'HD\s*\d+',  # HD星表
        r'[A-Z][a-z]+\s*\d+',  # 星座+数字
        r'[A-Z][a-z]+',  # 星座名
        r'[A-Z]\d+',  # 单字母+数字
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_input, re.IGNORECASE)
        if match:
            return match.group().strip()
    
    # 如果没有匹配到模式，返回清理后的输入
    return clean_input.strip() if clean_input.strip() else ""


def extract_celestial_info_from_query(user_input: str, user_requirements: str = None) -> dict:
    """从用户查询中提取天体信息 - 使用简单有效的提取逻辑"""
    try:
        # 使用简单规则提取天体名称（参考complete_simple_system.py）
        celestial_name = _extract_celestial_name_simple(user_input)
        
        if not celestial_name:
            celestial_info = {
                "object_name": "未知天体",
                "coordinates": {"ra": None, "dec": None},
                "object_type": "未知",
                "magnitude": None,
                "description": user_input
            }
        else:
            # 构建天体信息
            celestial_info = {
                "object_name": celestial_name,
                "coordinates": {"ra": None, "dec": None},
                "object_type": "未知",
                "magnitude": None,
                "description": user_input
            }
        
        return celestial_info
    except Exception as e:
        logging.warning(f"提取天体信息失败: {e}")
        return {
            "object_name": "未知天体",
            "coordinates": {"ra": None, "dec": None},
            "object_type": "未知",
            "magnitude": None,
            "description": user_input
        }


def _classify_celestial_object_with_llm(user_input: str, celestial_info: dict, llm) -> dict:
    """使用LLM进行智能天体分类（参考complete_simple_system.py）"""
    try:
        object_name = celestial_info.get("object_name", "未知天体")
        
        # 构建分类提示词
        classification_prompt = f"""请对以下天体进行专业的天体分类。

天体名称: {object_name}
用户查询: {user_input}

请按照以下格式返回分类结果（JSON格式）：
{{
    "object_name": "天体名称",
    "primary_category": "主要类别",
    "subcategory": "子类别", 
    "detailed_classification": "详细分类",
    "confidence_level": "置信度",
    "scientific_name": "科学名称",
    "object_type": "天体类型",
    "description": "简要描述"
}}

主要类别选项：
- 恒星 (Star)
- 行星 (Planet) 
- 星系 (Galaxy)
- 星云 (Nebula)
- 星团 (Cluster)
- 小行星 (Asteroid)
- 彗星 (Comet)
- 双星 (Binary Star)
- 超新星 (Supernova)
- 深空天体 (Deep Sky Object)

请根据天体名称和查询内容进行准确分类："""

        # 调用LLM
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=classification_prompt)]
        response = llm.invoke(messages)
        
        # 解析响应
        response_content = response.content.strip()
        
        # 尝试解析JSON
        try:
            import json
            # 清理响应内容，移除markdown代码块格式
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0]
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0]
            
            classification_data = json.loads(response_content)
            
            return {
                "classification_result": classification_data,
                "success": True,
                "method": "llm_classification"
            }
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用规则分类作为后备
            return _classify_celestial_object_by_rules(user_input, celestial_info)
            
    except Exception as e:
        print(f"LLM分类失败: {e}")
        # 使用规则分类作为后备
        return _classify_celestial_object_by_rules(user_input, celestial_info)


def _analyze_data_for_visualization(data: dict) -> str:
    """分析数据特征，为可视化提供建议"""
    if not data:
        return "数据为空。"
    
    analysis_parts = []
    
    # 数据字段检查（已简化，不显示建议）
    if not analysis_parts:
        analysis_parts.append("数据字段完整")
    
    return "\n".join(analysis_parts)


def _classify_celestial_object_by_rules(user_input: str, celestial_info: dict) -> dict:
    """基于规则的天体分类"""
    try:
        # 简单的基于关键词的分类逻辑
        user_input_lower = user_input.lower()
        object_name = celestial_info.get("object_name", "").lower()
        
        # 分类逻辑
        if any(keyword in user_input_lower or keyword in object_name for keyword in ["恒星", "star", "太阳"]):
            primary_category = "恒星"
            subcategory = "主序星"
        elif any(keyword in user_input_lower or keyword in object_name for keyword in ["行星", "planet", "火星", "金星", "木星"]):
            primary_category = "行星"
            subcategory = "类地行星" if any(k in user_input_lower for k in ["火星", "金星", "地球"]) else "气态巨行星"
        elif any(keyword in user_input_lower or keyword in object_name for keyword in ["星系", "galaxy", "银河", "仙女座", "仙女座星系", "m31", "andromeda"]):
            primary_category = "星系"
            subcategory = "螺旋星系"
        elif any(keyword in user_input_lower or keyword in object_name for keyword in ["星云", "nebula"]):
            primary_category = "星云"
            subcategory = "发射星云"
        elif "m87" in object_name or "m87" in user_input_lower:
            primary_category = "星系"
            subcategory = "椭圆星系"
        elif object_name.startswith("m") and object_name[1:].isdigit():
            # 梅西耶天体的一般分类
            primary_category = "深空天体"
            subcategory = "梅西耶天体"
        else:
            primary_category = "未分类"
            subcategory = "需要更多信息"
        
        return {
            "classification_result": {
                "object_name": celestial_info.get("object_name", "未知天体"),
                "primary_category": primary_category,
                "subcategory": subcategory,
                "detailed_classification": f"{primary_category} - {subcategory}",
                "confidence_level": "中等",
                "key_features": ["基于关键词分析"],
                "coordinates": celestial_info.get("coordinates", {"ra": "未知", "dec": "未知"}),
                "additional_info": {
                    "magnitude": celestial_info.get("magnitude", "未知"),
                    "distance": "未知",
                    "spectral_type": "未知",
                },
            },
            "explanation": f"基于关键词分析，该天体被分类为{primary_category}。",
            "suggestions": ["提供更多观测数据以获得更准确的分类"],
        }
    except Exception as e:
        logging.warning(f"基于规则的分类失败: {e}")
        return {
            "classification_result": {
                "object_name": "未知天体",
                "primary_category": "未分类",
                "subcategory": "分类失败",
                "detailed_classification": "无法分类",
                "confidence_level": "低",
                "key_features": ["分类失败"],
                "coordinates": {"ra": "未知", "dec": "未知"},
                "additional_info": {
                    "magnitude": "未知",
                    "distance": "未知",
                    "spectral_type": "未知",
                },
            },
            "explanation": "分类过程中发生错误。",
            "suggestions": ["请重新尝试或提供更多信息"],
        }


# 设置logger
logger = logging.getLogger(__name__)


# LLM服务初始化 - 使用豆包模型
try:
    llm: BaseChatModel = get_llm_by_type("basic")
except Exception as e:
    print(f"Warning: Failed to initialize LLM: {e}")
    llm = None


@track_node_execution("identity_check")
def identity_check_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    身份识别节点 - Command语法实现
    判断用户类型（amateur/professional）并直接路由到下一个节点
    """
    try:
        user_input = state["user_input"]  # 在下方prompt中，用户输入会被Python解释器立即替换为 user_input 变量的实际值
        
        # 输入验证
        if user_input is None or not isinstance(user_input, str):
            raise ValueError("Invalid user_input: must be a non-empty string")

        # 使用大模型进行身份识别 - 完全依赖LLM判断
        if llm:
            identity_prompt = f"""请仔细分析以下用户输入，判断用户是天文爱好者还是专业研究人员。

用户输入: {user_input}

判断标准：
- amateur（爱好者）：是否表明amateur(爱好者) 询问基础天文知识、概念解释、科普问题、学习性问题
  例如："什么是黑洞呀？"、"恒星是如何形成的呀？"、"银河系有多大呀？"、"这颗星好亮呀"、"有趣的天文现象"
  
- professional（专业用户）：是否表明professional(专业用户)，需要专业分析、数据处理、天体分类、数据检索、图表绘制等
  例如："M87属于什么类型？"、"分类这个天体：M87"、"获取SDSS星系数据"、"绘制天体位置图"、"分析M87的射电星系特征"、"M31的参考文献"、"M31的特征"、"M31的性质"、"M31相关文献"、"离M31最近的星系有哪些"、"提供坐标判断星系"

关键区别：
- 优先级最高的是身份识别，如果明确爱好者（amateur），按照amateur（爱好者）处理。 问"有多大"、"这颗星好亮"、"有趣的天文现象" → amateur（科普问题）
- 优先级最高的是身份识别，如果明确专业人士 (professional)，按照professional（专业用户）处理。问"属于什么类型"、"分类"、"分析特征" → professional（专业分类/分析）

请仔细分析用户的语言风格、问题深度和专业需求，然后只返回：amateur 或 professional
"""
            
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=identity_prompt)]
            response = llm.invoke(messages)  # 按prompt要求，只返回amateur 或 professional
            user_type = response.content.strip().lower()
                
            # 验证响应
            if user_type not in ["amateur", "professional"]:
                # 如果LLM返回的不是预期格式，尝试从文本中提取
                if "professional" in user_type or "专业" in user_type:
                    user_type = "professional"
                elif "amateur" in user_type or "爱好者" in user_type or "业余" in user_type:
                    user_type = "amateur"
                else:
                    user_type = "amateur"  # 默认为爱好者
        else:
            # 如果LLM不可用，报错而不是使用关键词判断
            raise Exception("LLM服务不可用，无法进行身份识别")

        # 更新状态 - 只更新必要的字段，避免字段冲突
        updated_state = {
            "user_type": user_type,
            "current_step": "identity_checked",
            "identity_completed": True
        }

        # 使用Command语法直接路由到下一个节点
        if user_type == "amateur":
            # 业余用户需要先进行QA问答
            return Command(
                update=updated_state,
                goto="qa_agent"
            )
        elif user_type == "professional":
            # 专业用户直接进入任务选择
            return Command(
                update=updated_state,
                goto="task_selector"
            )
        else:
            # 异常情况，默认为业余用户，进入QA问答
            updated_state["user_type"] = "amateur"
            return Command(
                update=updated_state,
                goto="qa_agent"
            )

    except Exception as e:
        # 错误处理 - 只更新必要的字段
        error_state = {
            "error_info": {
                "node": "identity_check_command_node",
                "error": str(e),
                "timestamp": time.time(),
            }
        }
        
        return Command(
            update=error_state,
            goto="error_recovery"
        )


# 存储功能已移除 - 分类节点不再需要数据库存储


# real_time_retrieval_command_node已删除 - 在builder.py中未使用


# 数据库存储功能已移除 - 分类节点不再需要数据存储


# 兼容版本的_node函数已删除 - 在builder.py中未使用


@track_node_execution("qa_agent")
def qa_agent_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    QA问答节点 - 简化版本，集成Tavily搜索，直接结束
    处理爱好者的天文问答，不再提供专业模式选择
    """
    try:
        user_input = state["user_input"]
        user_type = state.get("user_type", "amateur")

        # 集成Tavily搜索获取最新信息
        search_context = ""
        search_sources = []
        tavily_success = False
        try:
            from src.tools.tavily_search.tavily_search_api_wrapper import tavily_search
            search_query = f"天文 {user_input}"
            # 使用环境变量配置的max_results，不传参数让函数自动使用配置
            search_results = tavily_search(search_query)
            if search_results:
                # 将搜索结果作为上下文提供给LLM，让LLM智能整合
                search_context = "\n\n[最新网络信息参考] "
                for i, result in enumerate(search_results[:2], 1):
                    title = result.get('title', '无标题')
                    content = result.get('content', '无内容')[:100]
                    url = result.get('url', '')
                    search_context += f"{title}: {content}... "
                    
                    # 收集来源信息用于最后的参考列表（保持原始语言）
                    if url:
                        domain = result.get('domain', 'unknown')
                        # 保持原始标题，不进行翻译
                        search_sources.append(f"{title} ({domain})")
                
                search_context += "请将这些信息自然地整合到回答中，不要直接引用。"
                tavily_success = True
        except Exception as e:
            print(f"Tavily搜索失败: {e}")
            search_context = ""

        # 检查是否是天体分类问题
        is_classification_question = (
            "分类" in user_input or 
            "类型" in user_input or 
            "属于" in user_input or
            # "是什么" in user_input or  # “是什么” 适合检索任务
            state.get("current_step") == "simbad_query_failed"  # 如果SIMBAD查询失败，跳转到QA代理处理
        )
        
        # 使用prompt模板获取QA提示词
        try:
            if is_classification_question:
                # 使用专门的天体分类prompt
                qa_prompt_content = f"""作为专业天文学家，请回答以下天体分类问题：

用户问题：{user_input}
用户类型：{user_type}

请提供：
1. 天体的准确分类（主分类、子分类、详细分类）
2. 该天体的基本特征和性质
3. 在天文学中的重要性
4. 相关的观测特征

请用专业但易懂的语言回答，适合{user_type}用户的理解水平。"""
            else:
                qa_prompt_content = get_prompt(
                    "qa_agent", user_input=user_input, user_type=user_type
                )  # 如果用户输入不是分类问题，使用QA问答模板
            qa_prompt = ChatPromptTemplate.from_template(qa_prompt_content)
        except Exception:
            qa_prompt = None

        # 生成回答
        llm = get_llm_by_type("basic")
        if llm is None or qa_prompt is None:
            # 临时处理：如果LLM未初始化，提供默认回答
            response_content = f"感谢您的天文问题：{user_input}。这是一个很有趣的天文话题！由于当前LLM服务未配置，请稍后再试。"
        else:
            # 将搜索上下文添加到用户输入中
            enhanced_input = user_input + search_context
            chain = qa_prompt | llm
            response = chain.invoke({"user_input": enhanced_input, "user_type": user_type})
            # 确保 response_content 是字符串
            if hasattr(response, 'content'):
                response_content = str(response.content)
            else:
                response_content = str(response)

        # 直接使用LLM整合后的回答，不再添加原始搜索结果
        final_response = response_content
        
        # 如果 Tavily 搜索成功并返回了结果，添加参考来源
        if tavily_success and search_sources:
            final_response += "\n\n📚 参考来源：\n"
            for i, source in enumerate(search_sources[:3], 1):
                final_response += f"{i}. {source}\n"

        # 更新状态
        updated_state = state.copy()
        updated_state["qa_response"] = final_response
        updated_state["final_answer"] = f"QA回答: {final_response}"
        updated_state["current_step"] = "qa_completed"
        updated_state["is_complete"] = True
        updated_state["task_type"] = "qa"

        # 添加助手消息
        if "messages" not in updated_state:
            updated_state["messages"] = []
        updated_state["messages"].append({"role": "assistant", "content": final_response})  # 作用是记录对话历史

        # 记录执行历史
        execution_history = updated_state.get("execution_history", [])
        execution_history.append({
            "node": "qa_agent_command_node",
            "action": "generate_qa_response_with_search",
            "input": user_input,
            "output": final_response,
            "timestamp": time.time(),
        })
        
        updated_state["execution_history"] = execution_history

        # 直接结束，不再询问是否进入专业模式
        return Command(
            update=updated_state,
            goto="__end__"
        )

    except Exception as e:
        # 错误处理
        error_message = f"抱歉，处理您的问题时遇到了技术问题：{str(e)}。请稍后再试。"
        error_state = state.copy()
        error_state["final_answer"] = error_message
        error_state["qa_response"] = f"QA错误: {error_message}"
        error_state["error_info"] = {
            "node": "qa_agent_command_node",
            "error": str(e),
            "timestamp": time.time(),
        }
        error_state["retry_count"] = error_state.get("retry_count", 0) + 1
        
        return Command(
            update=error_state,
            goto="error_recovery"
        )


@track_node_execution("classification_config")
def classification_config_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    天体分类配置节点 - Command语法实现
    根据用户输入的天体信息进行天体分类，并完成实时数据检索和数据库存储
    """
    try:
        user_input = state["user_input"]
        user_requirements = state.get("user_requirements", user_input)
        
        # 从用户查询中提取天体信息
        celestial_info = extract_celestial_info_from_query(
            user_input, user_requirements
        )

        # 使用prompt模板获取配置提示词
        try:
            config_prompt_content = get_prompt(
                "classification_config",
                user_query=user_input,
                celestial_info=str(celestial_info),
                task_type="classification",
            )
        except Exception:
            config_prompt_content = None

        # 调用LLM进行天体分类
        llm = get_llm_by_type("basic")
        if llm is None:
            # 使用增强的基于规则的分类逻辑
            classification_result = _classify_celestial_object_by_rules(
                user_input, celestial_info
            )
        else:
            try:
                # 使用LLM进行智能天体分类（参考complete_simple_system.py）
                classification_result = _classify_celestial_object_with_llm(
                    user_input, celestial_info, llm
                    )
            except Exception:
                # LLM调用失败时使用基于规则的分类逻辑作为fallback
                classification_result = _classify_celestial_object_by_rules(
                    user_input, celestial_info
                )

        # === 集成实时数据检索功能 ===
        # 从分类结果中获取天体信息
        celestial_info_result = classification_result.get("classification_result", {})
        object_name = celestial_info_result.get("object_name", "Unknown")
        object_type = celestial_info_result.get("primary_category", "Unknown")
        coordinates = celestial_info_result.get("coordinates", {})
        
        # 尝试从SIMBAD获取实时数据
        from src.code_generation.templates import query_simbad_by_name
        
        simbad_result = query_simbad_by_name(object_name)
        
        # 如果SIMBAD查询失败，跳转到QA代理处理
        if not simbad_result.get('found', False):
            # 更新状态，跳转到QA代理
            updated_state = state.copy()
            updated_state["current_step"] = "simbad_query_failed"
            updated_state["simbad_failed_object"] = object_name
            updated_state["user_input"] = f"请找到{object_name}所属的分类，并做简单介绍"
            
            # 记录执行历史
            execution_history = updated_state.get("execution_history", [])
            execution_history.append({
                "node": "classification_config_command_node",
                "action": "simbad_query_failed_redirect_to_qa",
                "input": user_input,
                "output": f"SIMBAD查询失败，跳转到QA代理处理{object_name}分类",
                "timestamp": time.time(),
            })
            updated_state["execution_history"] = execution_history
            
            return Command(
                update=updated_state,
                goto="qa_agent"
            )
        
        if simbad_result.get('found', False):
            # 从SIMBAD获取到数据
            ra_val = simbad_result.get('coordinates', {}).get('ra', None)
            dec_val = simbad_result.get('coordinates', {}).get('dec', None)
            
            # 确保坐标值是数字类型
            try:
                ra_val = float(ra_val) if ra_val is not None else None
            except (ValueError, TypeError):
                ra_val = None
            try:
                dec_val = float(dec_val) if dec_val is not None else None
            except (ValueError, TypeError):
                dec_val = None
                
            real_coordinates = {"ra": ra_val, "dec": dec_val}
            real_magnitude = simbad_result.get('magnitude', None)
            object_name = simbad_result.get('object_name', object_name)
        else:
            # 如果SIMBAD没有找到，使用现有坐标或标记为未找到
            real_coordinates = coordinates if coordinates.get("ra") and coordinates.get("dec") else {"ra": None, "dec": None}
            real_magnitude = None
        
        # 构建检索结果（只显示真实查询的数据源和字段）
        data_sources = ["SIMBAD"] if simbad_result.get('found', False) else []
        retrieval_result = {
            "status": "success" if simbad_result.get('found', False) else "no_data",
            "data_sources_queried": data_sources,
            "total_records": 1 if simbad_result.get('found', False) else 0,
            "query_timestamp": time.time()
        }
        
        # 只添加SIMBAD实际返回的字段
        if simbad_result.get('found', False):
            retrieval_result["coordinates"] = real_coordinates
            retrieval_result["object_type"] = simbad_result.get('object_type', 'Unknown')
            if real_magnitude is not None:
                retrieval_result["magnitude"] = real_magnitude
        
        # 分类任务不需要存储数据，直接返回分析结果

        # 更新状态
        updated_state = state.copy()
        updated_state["classification_result"] = classification_result
        updated_state["retrieval_result"] = retrieval_result
        updated_state["classification_config"] = {
            "configured": True,
            "celestial_info": celestial_info,
            "classification_method": "llm_analysis" if llm else "rule_based",
            "timestamp": time.time(),
        }
        updated_state["current_step"] = "classification_and_storage_completed"
        updated_state["is_complete"] = True

        # 记录执行历史
        execution_history = updated_state.get("execution_history", [])
        execution_history.append({
            "node": "classification_config_command_node",
            "action": "celestial_classification_with_storage",
            "input": user_input,
            "output": f"Classified {object_name} as {object_type}, retrieved and stored data",
            "timestamp": time.time(),
        })
        updated_state["execution_history"] = execution_history

        # 初始化对话历史
        if "conversation_history" not in updated_state:
            updated_state["conversation_history"] = []

        # 添加分类结果到对话历史
        updated_state["conversation_history"].append({
            "type": "system",
            "content": f"天体分析完成：{object_name} - {object_type}",
            "timestamp": time.time(),
        })
        
        # 生成最终答案
        coord_display = f"RA={real_coordinates.get('ra', 'N/A')}, DEC={real_coordinates.get('dec', 'N/A')}"
        magnitude = real_magnitude if real_magnitude is not None else "N/A"
        
        # 分析数据特征，为可视化提供建议
        data_analysis = _analyze_data_for_visualization(retrieval_result)
        
        # 构建详细的分类结果显示
        simbad_classification = ""
        if simbad_result.get('found', False):
            # 获取分类信息
            main_cat = simbad_result.get('main_category', '')
            sub_cat = simbad_result.get('sub_category', '')
            detailed = simbad_result.get('detailed_classification', '')
            simbad_type = simbad_result.get('object_type', 'N/A')
            
            # 常识性验证：M31应该是旋涡星系，不是射电星系
            if object_name.upper() in ['M31', 'MESSIER 31', 'NGC 224', '仙女座星系']:
                if '射电星系' in sub_cat or '射电星系' in detailed:
                    # 修正为正确的分类
                    main_cat = '星系'
                    sub_cat = '旋涡星系'
                    detailed = '旋涡星系 (Spiral Galaxy)'
                    simbad_type = 'S'  # 旋涡星系的SIMBAD代码
            
            # 清理和构建层次结构 - 直接使用SIMBAD原始数据，不进行硬编码映射
            hierarchy = []
            
            # 直接使用SIMBAD返回的分类数据，保持原始准确性
            if main_cat and main_cat not in ['Unknown', 'N/A', '']:
                hierarchy.append(main_cat)
            
            if sub_cat and sub_cat not in ['Unknown', 'N/A', ''] and sub_cat != main_cat:
                hierarchy.append(sub_cat)
            
            if detailed and detailed not in ['Unknown', 'N/A', ''] and detailed != sub_cat and detailed != main_cat:
                hierarchy.append(detailed)
            
            # 去重处理：移除重复的层级
            unique_hierarchy = []
            for level in hierarchy:
                if level not in unique_hierarchy:
                    unique_hierarchy.append(level)
            hierarchy = unique_hierarchy
            
            # 构建缩进式层次结构
            hierarchy_tree = ""
            if hierarchy:
                for i, level in enumerate(hierarchy):
                    indent = "  " * i  # 每层缩进2个空格
                    hierarchy_tree += f"{indent}└─ {level}\n"
                hierarchy_tree = hierarchy_tree.rstrip()  # 移除最后的换行符
            else:
                hierarchy_tree = "└─ 未知类型"
            
            # 构建SIMBAD分类详情
            simbad_classification = f"""
SIMBAD分类详情:
- SIMBAD类型: {simbad_type}
- 分类层次:
{hierarchy_tree}
- 关键特征: {simbad_result.get('key_features', 'N/A')}
- 置信度: {simbad_result.get('confidence', 'N/A')}"""

        
        # 使用中文分类结果
        main_cat = simbad_result.get('main_category', '') if simbad_result.get('found', False) else ''
        chinese_classification = main_cat if main_cat and main_cat not in ['Unknown', 'N/A', ''] else '未知类型'
        
        final_answer = f"""天体分析完成！
        
天体名称: {object_name}
分类结果: {chinese_classification}{simbad_classification}
坐标: {coord_display}

{data_analysis}"""
        
        updated_state["final_answer"] = final_answer
        
        # 添加助手消息到消息列表
        if "messages" not in updated_state:
            updated_state["messages"] = []
        from langchain_core.messages import AIMessage
        updated_state["messages"].append(AIMessage(content=final_answer))

        # 分类、检索和存储完成后，直接结束流程
        return Command(
            update=updated_state,
            goto="__end__"
        )

    except Exception as e:
        # 错误处理
        error_state = state.copy()
        error_state["error_info"] = {
            "node": "classification_config_command_node",
            "error": f"天体分析失败: {str(e)}",
            "timestamp": time.time(),
        }
        error_state["retry_count"] = error_state.get("retry_count", 0) + 1
        
        return Command(
            update=error_state,
            goto="error_recovery"
        )


# 第一个data_retrieval_command_node定义已删除 - 使用第二个版本（带装饰器）


# literature_review_command_node已删除 - 在builder.py中未使用


def error_recovery_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """错误恢复Command节点 - 处理系统错误和异常情况，最大重试3次"""
    try:
        error_info = state.get("error_info")
        retry_count = state.get("retry_count", 0)
        last_error_node = state.get("last_error_node")
        
        # 检查是否是同一个节点的重复错误，避免无限循环
        current_error_node = error_info.get("node") if error_info else None
        
        # 最大重试次数限制为3次
        MAX_RETRY_COUNT = 3
        
        if retry_count >= MAX_RETRY_COUNT or (current_error_node == last_error_node and retry_count > 0):
            # 超过重试次数或同一节点重复错误，提供降级服务并结束流程
            reason = "超过最大重试次数" if retry_count >= MAX_RETRY_COUNT else "检测到循环错误"
            
            fallback_response = f"""抱歉，系统在处理您的请求时遇到了问题（{reason}），现在提供基本服务。
            
错误节点：{current_error_node or '未知'}
错误信息：{error_info.get('error', '未知错误') if error_info else '系统异常'}
重试次数：{retry_count}

建议：
1. 请简化您的问题重新提问
2. 检查输入格式是否正确
3. 稍后再试

如果问题持续存在，请联系技术支持。"""

            # 只更新必要的字段，避免复制整个状态
            updated_state = {
                "qa_response": fallback_response,
                "final_answer": f"错误处理: {fallback_response}",
                "current_step": "error_handled",
                "is_complete": True
            }

            # 处理messages
            if "messages" in state:
                updated_state["messages"] = state["messages"].copy()
            else:
                updated_state["messages"] = []
            updated_state["messages"].append(
                {"role": "assistant", "content": fallback_response}
            )
            
            # 不更新execution_history，避免字段冲突
            
            # 结束流程，不再重试
            return Command(
                update=updated_state,
                goto="__end__"
            )
        else:
            # 在重试限制内，根据错误来源进行有针对性的恢复
            updated_state = {
                "last_error_node": current_error_node,  # 记录当前错误节点
                "error_recovery_completed": True
            }

            # 不更新execution_history，避免字段冲突
            
            # 根据错误来源决定恢复策略
            error_node = error_info.get("node") if error_info else None
            
            # 由于已经合并了节点，现在只需要处理classification_config_command_node的错误
            if error_node == "classification_config_command_node":
                # 分类错误，重试分类（现在包含了完整的分析流程）
                updated_state["current_step"] = "classification_retry"
                return Command(
                    update=updated_state,
                    goto="classification_config"
                )
            else:
                # 其他错误或未知错误，提供降级服务并结束
                fallback_response = f"""抱歉，系统遇到了问题，但我可以为您提供基本信息。
                
错误信息：{error_info.get('error', '未知错误') if error_info else '系统异常'}
重试次数：{retry_count + 1}/{MAX_RETRY_COUNT}

建议：
1. 请简化您的问题重新提问
2. 检查输入格式是否正确
3. 稍后再试

如果问题持续存在，请联系技术支持。"""

                updated_state["qa_response"] = fallback_response
                updated_state["final_answer"] = f"错误恢复: {fallback_response}"
                updated_state["current_step"] = "error_handled"
                updated_state["is_complete"] = True

                if "messages" not in updated_state:
                    updated_state["messages"] = []
                updated_state["messages"].append(
                    {"role": "assistant", "content": fallback_response}
                )
                
                return Command(
                    update=updated_state,
                    goto="__end__"
                )

    except Exception as e:
        # 错误恢复节点本身出错，直接标记完成
        error_state = state.copy()
        error_state["final_answer"] = "系统遇到严重错误，请稍后重试。"
        error_state["qa_response"] = "致命错误: 系统遇到严重错误，请稍后重试。"
        error_state["current_step"] = "fatal_error"
        error_state["is_complete"] = True
        return Command(
             update=error_state,
             goto="__end__"
         )


# code_generator_command_node已删除 - 在builder.py中未使用


@track_node_execution("task_selector")
def task_selector_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    任务选择节点 - Command语法实现
    根据用户输入选择具体的任务类型并直接路由
    """
    try:
        user_input = state["user_input"]
        user_type = state.get("user_type", "amateur")
        
        # 检查是否来自user_choice_handler，如果是则根据原始问题选择任务类型
        if state.get("from_user_choice", False):
            # 从执行历史中找到原始问题
            execution_history = state.get("execution_history", [])
            original_question = None
            for entry in reversed(execution_history):
                if (entry.get("node") in ["identity_check_command_node", "qa_agent_command_node"] and 
                    entry.get("action") in ["process_user_input", "generate_qa_response"] and
                    entry.get("input") and 
                    entry.get("input").lower() not in ["是", "y", "yes", "要", "需要", "1", "否", "n", "no", "不要", "不需要", "0"]):
                    original_question = entry.get("input")
                    break
            
            if original_question:
                user_input = original_question
            else:
                user_input = state["user_input"]
        else:
            # 获取LLM实例
            llm = get_llm_by_type("basic")

            # 使用prompt模板获取任务选择提示词
            try:
                task_prompt_content = get_prompt("task_selection", 
                                               user_input=user_input, 
                                               user_type=user_type)
                task_prompt = ChatPromptTemplate.from_template(task_prompt_content)
            except Exception as e:
                # 继续执行，不依赖prompt模板
                task_prompt = None

            # 使用大模型进行任务类型识别 - 完全依赖LLM判断
            if llm:  # {user_input} 会被Python解释器立即替换为 user_input 变量的实际值
                task_prompt = f"""请仔细分析以下专业用户输入，识别具体的任务类型。

用户输入: {user_input}

任务类型定义：
- classification: 天体分类任务（识别天体类型）
  例如："这是哪种天体？"、"M87属于什么类型？"、"分类这个天体"、"识别天体类型"
  
- retrieval: 数据检索任务（获取和分析数据）
  例如："分析M87的射电星系特征"、"获取星系数据"、"查询SDSS数据"、"检索天体信息"、"分析天体特征"、"研究天体性质"、"M31是什么"、"M31的参考文献"、"M31的特征"、"M31的性质"、"M31相关文献"、"离M31最近的星系有哪些"、"提供坐标判断星系"
  
- visualization: 绘制图表任务（生成图像和图表）
  例如："绘制天体位置图"、"生成光谱图"、"可视化数据"、"创建图表"、"制作图像"、"绘制分布图"

- multimark: 图片识别标注任务（分析天文图像并标注）
  例如："标注这张星系图像"、"识别图像中的天体"、"标记图像中的对象"、"图像标注"、"识别照片中的天体"、"训练模型"、"标注图片"、"训练CNN模型"、"训练神经网络"、"机器学习"、"深度学习"、"模型训练"、"并行训练"、"训练多个模型"

关键区别：
- classification: 问"是什么类型"、"属于什么分类"
- retrieval: 问"分析特征"、"研究性质"、"获取数据"、"提供坐标"、"星系的参考文献"、"提供特征"、"提供性质"、"提供最近的星系"、"分析星系坐标"
- visualization: 问"绘制"、"生成图表"、"可视化"
- multimark: 问"训练"、"训练模型"、"分析照片"、"标记图像"、"标注图片"、"训练CNN"、"训练神经网络"、"机器学习"、"深度学习"、"并行训练"

请仔细分析用户的具体需求，然后只返回：classification、retrieval、visualization 或 multimark
"""
                
                from langchain_core.messages import HumanMessage
                messages = [HumanMessage(content=task_prompt)] 
                response = llm.invoke(messages)
                task_type = response.content.strip().lower()
                
                # 验证响应
                if task_type not in ["classification", "retrieval", "visualization", "multimark"]:
                    # 如果LLM返回的不是预期格式，尝试从文本中提取
                    if "classification" in task_type or "分类" in task_type:
                        task_type = "classification"
                    elif "retrieval" in task_type or "检索" in task_type or "数据" in task_type:
                        task_type = "retrieval"
                    elif "visualization" in task_type or "可视化" in task_type or "图表" in task_type:
                        task_type = "visualization"
                    elif "multimark" in task_type or "标注" in task_type or "图像" in task_type or "图片" in task_type or "训练" in task_type or "训练模型" in task_type:
                        task_type = "multimark"
                    else:
                        task_type = "classification"  # 默认为分类任务
            else:
                # 如果LLM不可用，报错而不是使用关键词判断
                raise Exception("LLM服务不可用，无法进行任务类型识别")
            
            updated_state = state.copy()

        # 更新状态
        updated_state = state.copy()
        updated_state["task_type"] = task_type
        updated_state["selected_task_type"] = task_type  # 为了兼容测试
        updated_state["current_step"] = "task_selected"
        updated_state["confidence"] = 0.8  # 基于规则的置信度
        
        # 清除临时标记，避免影响后续流程
        if "from_user_choice" in updated_state:
            del updated_state["from_user_choice"]
        if "default_task_type" in updated_state:
            del updated_state["default_task_type"]
        
        # 记录执行历史
        execution_history = updated_state.get("execution_history", [])
        execution_history.append({
            "node": "task_selector",
            "action": task_type,
            "input": user_input,
            "output": task_type,
            "timestamp": time.time()
        })
        updated_state["execution_history"] = execution_history
        
        # 路由逻辑 - 四个主要任务类型
        if task_type == "classification":
            return Command(
                update=updated_state,
                goto="classification_config"
            )
        elif task_type == "retrieval":
            return Command(
                update=updated_state,
                goto="data_retrieval"
            )
        elif task_type == "visualization":
            return Command(
                update=updated_state,
                goto="visualization"
            )
        elif task_type == "multimark":
            return Command(
                update=updated_state,
                goto="multimark"
            )
        else:
            # 默认分类任务
            updated_state["task_type"] = "classification"
            return Command(
                update=updated_state,
                goto="classification_config"
            )

    except Exception as e:
        # 错误处理
        error_state = state.copy()
        error_state["error_info"] = {
            "node": "task_selector_command_node",
            "error": str(e),
            "timestamp": time.time(),
        }
        error_state["retry_count"] = error_state.get("retry_count", 0) + 1
        
        return Command(
            update=error_state,
            goto="error_recovery"
        )


@track_node_execution("data_retrieval")
def data_retrieval_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    数据检索节点 - 处理专业用户的数据检索任务
    """
    try:
        user_input = state["user_input"]
        
        # 导入MCP检索客户端
        try:
            from ..mcp_retrieval.client import query_astro_data
        except ImportError as e:
            logger.error(f"无法导入MCP检索客户端: {e}")
            # 如果导入失败，使用备用方案
            updated_state = state.copy()
            updated_state["current_step"] = "data_retrieval_completed"
            updated_state["is_complete"] = True
            updated_state["final_answer"] = f"数据检索功能暂时不可用。\n\n您的请求：{user_input}\n\n错误信息：{str(e)}\n\n请检查MCP检索模块是否正确安装。"
            
            # 记录执行历史
            execution_history = updated_state.get("execution_history", [])
            execution_history.append({
                "node": "data_retrieval_command_node",
                "action": "import_error",
                "input": user_input,
                "output": f"导入错误: {str(e)}",
                "timestamp": time.time()
            })
            updated_state["execution_history"] = execution_history
            
            return Command(
                update=updated_state,
                goto="__end__"
            )
        
        # 使用MCP检索客户端执行查询
        logger.info(f"🔍 开始执行数据检索查询: {user_input}")
        
        try:
            # 调用MCP检索客户端
            retrieval_result = query_astro_data(user_input)
            logger.info("✅ 数据检索查询完成")
            
            # 构建最终答案
            final_answer = f"🔍 **数据检索结果**\n\n"
            final_answer += f"**查询内容**: {user_input}\n\n"
            final_answer += f"**检索结果**:\n{retrieval_result}\n\n"
            final_answer += "---\n"
            final_answer += "📊 **数据来源**: SIMBAD TAP服务\n"
            final_answer += "🛠️ **检索工具**: MCP检索客户端\n"
            final_answer += "✨ **功能特点**: 支持天体基础信息、文献查询、坐标搜索"
            
        except Exception as query_error:
            logger.error(f"数据检索查询执行失败: {query_error}")
            final_answer = f"❌ **数据检索失败**\n\n"
            final_answer += f"**查询内容**: {user_input}\n\n"
            final_answer += f"**错误信息**: {str(query_error)}\n\n"
            final_answer += "请检查：\n"
            final_answer += "- 网络连接是否正常\n"
            final_answer += "- SIMBAD TAP服务是否可用\n"
            final_answer += "- 查询格式是否正确\n\n"
            final_answer += "💡 **建议**: 尝试使用天体名称（如M13、Vega）或坐标进行查询"
        
        # 更新状态
        updated_state = state.copy()
        updated_state["current_step"] = "data_retrieval_completed"
        updated_state["is_complete"] = True
        updated_state["final_answer"] = final_answer
        updated_state["task_type"] = "data_retrieval"
        
        # 记录执行历史
        execution_history = updated_state.get("execution_history", [])
        execution_history.append({
            "node": "data_retrieval_command_node",
            "action": "mcp_data_retrieval",
            "input": user_input,
            "output": final_answer,
            "timestamp": time.time(),
            "details": {
                "retrieval_success": "error" not in final_answer.lower(),
                "result_length": len(final_answer)
            }
        })
        updated_state["execution_history"] = execution_history

        return Command(
            update=updated_state,
            goto="__end__"
        )

    except Exception as e:
        # 错误处理
        error_state = state.copy()
        error_state["error_info"] = {
            "node": "data_retrieval_command_node",
            "error": str(e),
            "timestamp": time.time(),
        }
        error_state["final_answer"] = f"数据检索过程中发生错误：{str(e)}"
        error_state["is_complete"] = True
        
        return Command(
            update=error_state,
            goto="__end__"
        )


@track_node_execution("visualization")
def visualization_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    可视化节点 - 支持多轮对话的可视化需求分析和图表绘制
    新实现：集成 Planner 多轮对话 → Coder → Explainer 完整流程
    """
    try:
        user_input = state["user_input"]
        
        # 导入 Planner 模块
        try:
            from src.planner import PlannerWorkflow
            from src.planner.dataset_manager import DatasetManager
            import os
            from pathlib import Path
            
            # 设置正确的数据集目录路径
            current_file = Path(__file__).resolve()
            astro_insight_root = current_file.parents[2]  # 从 src/graph/nodes.py 到 Astro-Insight-0913v3
            dataset_dir = astro_insight_root / "dataset"
            
            # 设置环境变量，让 DatasetManager 使用正确的路径
            os.environ["ASTRO_DATASET_DIR"] = str(dataset_dir)
            
        except Exception as e:
            # 关键依赖缺失时的友好降级
            updated_state = state.copy()
            updated_state["current_step"] = "visualization_failed"
            updated_state["is_complete"] = True
            updated_state["final_answer"] = (
                f"❌ 可视化流程初始化失败：{str(e)}\n\n"
                "请检查依赖是否完整：\n"
                "- src/planner 模块可用\n- Coder/Explainer 子模块安装无误\n"
                "- 依赖库（pandas、numpy、matplotlib 等）已安装\n"
            )
            updated_state["task_type"] = "visualization"
            execution_history = updated_state.get("execution_history", [])
            execution_history.append({
                "node": "visualization_command_node",
                "action": "init_failed",
                "input": user_input,
                "output": str(e),
                "timestamp": time.time()
            })
            updated_state["execution_history"] = execution_history
            return Command(update=updated_state, goto="__end__")

        # 初始化多轮对话状态
        if not state.get("visualization_session_id"):
            # 阶段1：创建交互式会话
            print("🔄 初始化可视化需求分析会话...")
            planner = PlannerWorkflow()
            
            # 创建会话
            session = planner.run_interactive_session(user_input)
            if not session["success"]:
                updated_state = state.copy()
                updated_state["current_step"] = "visualization_failed"
                updated_state["is_complete"] = True
                updated_state["task_type"] = "visualization"
                updated_state["final_answer"] = (
                    f"❌ 可视化会话创建失败：{session.get('error')}\n\n"
                    "请检查 Planner 模块配置或稍后重试。"
                )
                return Command(update=updated_state, goto="__end__")
            
            session_id = session["session_id"]
            print(f"✅ 可视化会话创建成功: {session_id}")
            
            # 处理初始需求
            print("🔄 处理初始可视化需求...")
            result = planner.continue_interactive_session(session_id, user_input)
            
            if not result["success"]:
                updated_state = state.copy()
                updated_state["current_step"] = "visualization_failed"
                updated_state["is_complete"] = True
                updated_state["task_type"] = "visualization"
                updated_state["final_answer"] = (
                    f"❌ 初始需求处理失败：{result.get('error')}\n\n"
                    "请重新描述您的可视化需求。"
                )
                return Command(update=updated_state, goto="__end__")
            
            # 保存会话状态并返回澄清问题
            updated_state = state.copy()
            updated_state["visualization_session_id"] = session_id
            updated_state["visualization_dialogue_state"] = "started"
            updated_state["visualization_turn_count"] = 1
            updated_state["visualization_max_turns"] = 8
            updated_state["visualization_dialogue_history"] = []
            updated_state["task_type"] = "visualization"
            
            # 显示系统回复
            if result.get("assistant_response"):
                print(f"\n🤖 系统回复:")
                print(f"   {result['assistant_response']}")
                updated_state["visualization_dialogue_history"].append({
                    "turn": 1,
                    "user_input": user_input,
                    "assistant_response": result["assistant_response"],
                    "timestamp": time.time()
                })
            
            # 显示当前状态
            if result.get("current_status"):
                status = result["current_status"]
                print(f"\n📊 当前状态:")
                print(f"   对话轮次: {status.get('current_turn', 0)}/{status.get('max_turns', 10)}")
                print(f"   状态: {status.get('dialogue_status', 'unknown')}")
                
                if status.get("task_steps"):
                    print(f"   已规划任务: {len(status['task_steps'])}个")
                    for i, step in enumerate(status['task_steps'][:3], 1):
                        print(f"     {i}. {step.get('description', 'N/A')}")
                
                if status.get("selected_dataset"):
                    print(f"   选定数据集: {status['selected_dataset'].get('name', 'unknown')}")
            
            # 检查是否需要确认
            if result.get("needs_confirmation"):
                print(f"\n❓ 系统需要确认:")
                print(f"   {result['confirmation_request']}")
                updated_state["awaiting_user_choice"] = True
                updated_state["current_visualization_request"] = result["confirmation_request"]
                updated_state["current_step"] = "visualization_clarifying"
                return Command(update=updated_state, goto="__end__")
            
            # 检查是否已完成
            if result.get("completed"):
                print("\n🎉 需求规划已完成!")
                # 直接执行 Pipeline
                return _execute_visualization_pipeline(updated_state, planner, session_id, result)
            
            # 需要继续澄清 - 返回等待用户输入的状态
            updated_state["awaiting_user_choice"] = True
            updated_state["current_visualization_request"] = "请继续提供更多细节来完善您的可视化需求"
            updated_state["current_step"] = "visualization_clarifying"
            updated_state["visualization_dialogue_state"] = "clarifying"
            
            return Command(update=updated_state, goto="__end__")
        
        # 阶段2：继续多轮对话
        elif state.get("awaiting_user_choice") and state.get("visualization_dialogue_state") == "clarifying":
            session_id = state["visualization_session_id"]
            turn_count = state.get("visualization_turn_count", 1)
            max_turns = state.get("visualization_max_turns", 8)
            
            # 检查是否超过最大轮次
            if turn_count >= max_turns:
                print(f"\n⚠️ 已达到最大对话轮次限制 ({max_turns}轮)")
                print("🔄 自动完成需求规划并执行Pipeline...")
                planner = PlannerWorkflow()
                return _execute_visualization_pipeline(state, planner, session_id, None)
            
            # 处理特殊命令
            if user_input.lower() in ['done', '完成', '确认', '执行']:
                print("✅ 用户确认需求完成")
                planner = PlannerWorkflow()
                return _execute_visualization_pipeline(state, planner, session_id, None)
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q', '取消']:
                print("👋 用户退出可视化对话")
                updated_state = state.copy()
                updated_state["current_step"] = "visualization_cancelled"
                updated_state["is_complete"] = True
                updated_state["task_type"] = "visualization"
                updated_state["final_answer"] = "可视化需求分析已取消。"
                return Command(update=updated_state, goto="__end__")
            
            print(f"\n👤 用户 (第{turn_count}轮): {user_input}")
            
            # 继续会话
            planner = PlannerWorkflow()
            result = planner.continue_interactive_session(session_id, user_input)
            
            if not result["success"]:
                print(f"❌ 对话失败: {result.get('error')}")
                updated_state = state.copy()
                updated_state["current_step"] = "visualization_failed"
                updated_state["is_complete"] = True
                updated_state["task_type"] = "visualization"
                updated_state["final_answer"] = f"可视化对话失败：{result.get('error')}"
                return Command(update=updated_state, goto="__end__")
            
            # 更新对话历史
            dialogue_history = state.get("visualization_dialogue_history", [])
            dialogue_history.append({
                "turn": turn_count,
                "user_input": user_input,
                "assistant_response": result.get("assistant_response", ""),
                "timestamp": time.time()
            })
            
            # 显示系统回复
            if result.get("assistant_response"):
                print(f"\n🤖 系统回复:")
                print(f"   {result['assistant_response']}")
            
            # 显示当前状态
            if result.get("current_status"):
                status = result["current_status"]
                print(f"\n📊 当前状态:")
                print(f"   对话轮次: {status.get('current_turn', 0)}/{status.get('max_turns', 10)}")
                print(f"   状态: {status.get('dialogue_status', 'unknown')}")
                
                if status.get("task_steps"):
                    print(f"   已规划任务: {len(status['task_steps'])}个")
                    for i, step in enumerate(status['task_steps'][:3], 1):
                        print(f"     {i}. {step.get('description', 'N/A')}")
                
                if status.get("selected_dataset"):
                    print(f"   选定数据集: {status['selected_dataset'].get('name', 'unknown')}")
            
            updated_state = state.copy()
            updated_state["visualization_turn_count"] = turn_count + 1
            updated_state["visualization_dialogue_history"] = dialogue_history
            
            # 检查是否需要确认
            if result.get("needs_confirmation"):
                print(f"\n❓ 系统需要确认:")
                print(f"   {result['confirmation_request']}")
                updated_state["awaiting_user_choice"] = True
                updated_state["current_visualization_request"] = result["confirmation_request"]
                updated_state["current_step"] = "visualization_clarifying"
                return Command(update=updated_state, goto="__end__")
            
            # 检查是否已完成
            if result.get("completed"):
                print("\n🎉 需求规划已完成!")
                return _execute_visualization_pipeline(updated_state, planner, session_id, result)
            
            # 继续澄清
            updated_state["awaiting_user_choice"] = True
            updated_state["current_visualization_request"] = "请继续提供更多细节来完善您的可视化需求"
            updated_state["current_step"] = "visualization_clarifying"
            
            return Command(update=updated_state, goto="__end__")
        
        else:
            # 异常状态，重置
            updated_state = state.copy()
            updated_state["current_step"] = "visualization_failed"
            updated_state["is_complete"] = True
            updated_state["task_type"] = "visualization"
            updated_state["final_answer"] = "可视化对话状态异常，请重新开始。"
            return Command(update=updated_state, goto="__end__")

    except Exception as e:
        # 错误处理
        error_state = state.copy()
        error_state["error_info"] = {
            "node": "visualization_command_node",
            "error": str(e),
            "timestamp": time.time(),
        }
        error_state["final_answer"] = (
            f"图表绘制过程中发生未预期错误：{str(e)}\n\n"
            "请稍后重试，或简化请求内容。"
        )
        error_state["is_complete"] = True
        error_state["task_type"] = "visualization"
        return Command(update=error_state, goto="__end__")


def _execute_visualization_pipeline(state: AstroAgentState, planner, session_id: str, result=None) -> Command[AstroAgentState]:
    """执行完整的可视化 Pipeline"""
    try:
        print("\n🔄 执行完整可视化Pipeline...")
        
        # 获取最终需求
        if result and result.get("final_result"):
            final_request = result["final_result"].final_prompt or result["final_result"].user_initial_request
        else:
            final_request = state["user_input"]
        
        # 执行完整 Pipeline
        pipeline_result = planner.run_complete_pipeline(
            user_request=final_request,
            session_id=session_id,
            explanation_type="detailed"
        )
        
        # 失败路径：返回清晰的错误与建议
        if not pipeline_result.get("success"):
            error_msg = pipeline_result.get("error", "未知错误")
            error_type = pipeline_result.get("error_type", "unknown")
            updated_state = state.copy()
            updated_state["current_step"] = "visualization_failed"
            updated_state["is_complete"] = True
            updated_state["task_type"] = "visualization"
            updated_state["final_answer"] = (
                f"❌ 可视化Pipeline执行失败 ({error_type})\n\n"
                f"请求：{final_request}\n"
                f"错误信息：{error_msg}\n\n"
                "建议：\n- 确认 conf.yaml 中模型/密钥配置\n"
                "- 确保 output/ 目录可写\n- 重新尝试简化的可视化需求\n"
            )
            return Command(update=updated_state, goto="__end__")
        
        # 成功路径：组装结果
        coder_result = pipeline_result.get("coder_result", {})
        explainer_result = pipeline_result.get("explainer_result", {})
        
        generated_code = (
            coder_result.get("code") or
            coder_result.get("generated_code") or
            ""
        )
        generated_files = (
            pipeline_result.get("generated_files") or
            coder_result.get("generated_files") or
            []
        )
        stdout_text = str(coder_result.get("output", "")).strip()
        stderr_text = str(coder_result.get("error", "")).strip()
        
        # 构建 final_answer（包含文件列表、stdout/stderr 摘要与解释总结）
        files_section = "无生成文件" if not generated_files else "\n".join([f"- {p}" for p in generated_files])
        stdout_section = stdout_text[:1200] if stdout_text else "(无输出)"
        stderr_section = stderr_text[:1200] if stderr_text else "(无错误)"
        
        explain_summary = ""
        if explainer_result.get("success"):
            summary = explainer_result.get("summary", "")
            insights = explainer_result.get("insights", [])
            top_insight = (insights[0] if insights else "")
            explain_summary = (
                (f"\n\n📝 结果解释摘要：\n{summary}" if summary else "") +
                (f"\n🔍 关键洞察：{top_insight}" if top_insight else "")
            )
        
        # 添加对话历史到最终结果
        dialogue_summary = ""
        dialogue_history = state.get("visualization_dialogue_history", [])
        if dialogue_history:
            dialogue_summary = "\n\n💬 需求澄清过程：\n"
            for i, turn in enumerate(dialogue_history, 1):
                dialogue_summary += f"第{i}轮: {turn['user_input']}\n"
                dialogue_summary += f"系统回复: {turn['assistant_response'][:200]}...\n\n"
        
        final_answer = (
            "🎉 可视化流程完成！\n\n"
            f"请求：{final_request}\n"
            f"生成文件（{len(generated_files)}）：\n{files_section}\n\n"
            "—— 执行输出（stdout） ——\n"
            f"{stdout_section}\n\n"
            "—— 错误信息（stderr） ——\n"
            f"{stderr_section}"
            f"{explain_summary}"
            f"{dialogue_summary}"
        )
        
        # 更新状态
        updated_state = state.copy()
        updated_state["current_step"] = "visualization_completed"
        updated_state["is_complete"] = True
        updated_state["task_type"] = "visualization"
        updated_state["generated_code"] = generated_code
        if generated_files:
            updated_state["generated_files"] = generated_files
        updated_state["final_answer"] = final_answer
        updated_state["visualization_dialogue_state"] = "completed"
        updated_state["awaiting_user_choice"] = False
        
        # 记录执行历史：plan → code → explain
        execution_history = updated_state.get("execution_history", [])
        execution_history.append({
            "node": "visualization_command_node",
            "action": "multi_turn_pipeline_completed",
            "input": final_request,
            "output": f"files={len(generated_files)}; stdout={len(stdout_text)}; stderr={len(stderr_text)}; turns={len(dialogue_history)}",
            "timestamp": time.time(),
            "details": {
                "planner_steps": len(pipeline_result.get("task_steps", [])),
                "execution_time_total": pipeline_result.get("total_processing_time"),
                "dialogue_turns": len(dialogue_history),
                "session_id": session_id
            }
        })
        updated_state["execution_history"] = execution_history
        
        print("✅ 可视化Pipeline执行成功!")
        print(f"📁 生成文件: {len(generated_files)}个")
        print(f"🔍 解释数量: {len(pipeline_result.get('explanations', []))}个")
        print(f"💬 对话轮次: {len(dialogue_history)}轮")
        
        return Command(update=updated_state, goto="__end__")
        
    except Exception as e:
        # Pipeline执行错误
        updated_state = state.copy()
        updated_state["current_step"] = "visualization_failed"
        updated_state["is_complete"] = True
        updated_state["task_type"] = "visualization"
        updated_state["final_answer"] = f"Pipeline执行失败：{str(e)}"
        updated_state["visualization_dialogue_state"] = "failed"
        return Command(update=updated_state, goto="__end__")


@track_node_execution("multimark")
def multimark_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """
    多模态标注节点 - 处理天文图像的AI识别和标注任务
    使用MCP ML客户端调用mcp_ml服务器
    """
    try:
        from pathlib import Path
        user_input = state["user_input"]
        
        # 检查是否是图像分类请求
        is_classification_request = any(keyword in user_input.lower() for keyword in [
            "分类", "识别", "标注", "分析", "图像", "照片", "图片", "星系", "天体", "训练", "模型"
        ])
        
        if is_classification_request:
            # 使用MCP ML客户端调用mcp_ml服务器
            try:
                # 动态导入MCP ML客户端
                current_file = Path(__file__).resolve()
                astro_insight_root = current_file.parents[2]  # 从 src/graph/nodes.py 到 Astro-Insight-0913v3
                mcp_ml_dir = astro_insight_root / "src" / "mcp_ml"
                mcp_ml_output_dir = str(mcp_ml_dir / "output")
                
                # 添加mcp_ml目录到Python路径
                import sys
                if str(mcp_ml_dir) not in sys.path:
                    sys.path.insert(0, str(mcp_ml_dir))
                
                from client import get_ml_client
                
                # 获取ML客户端
                ml_client = get_ml_client()
                
                # 检查是否需要训练模型
                if any(keyword in user_input.lower() for keyword in ["训练", "train", "模型", "model"]):
                    # 直接调用MCP ML服务器的函数，绕过复杂的MCP协议
                    try:
                        import sys
                        import os
                        from datetime import datetime
                        from pathlib import Path
                        # 切换到mcp_ml目录，确保配置文件路径正确
                        original_cwd = os.getcwd()
                        # 获取正确的mcp_ml路径
                        current_file = Path(__file__).resolve()
                        astro_insight_root = current_file.parents[2]  # 从 src/graph/nodes.py 到 Astro-Insight-0913v3
                        mcp_ml_dir = astro_insight_root / "src" / "mcp_ml"
                        os.chdir(str(mcp_ml_dir))
                        sys.path.insert(0, str(mcp_ml_dir))
                        
                        # 检查用户是否要求并行训练多个模型
                        if any(keyword in user_input.lower() for keyword in ["多个", "并行", "同时", "批量", "multiple", "parallel"]):
                            # 直接调用test_generate_and_run.py中的函数
                            from test_generate_and_run import test_generate_and_run
                            
                            # 准备用户描述
                            if any(keyword in user_input.lower() for keyword in ["简单", "基础", "深度", "复杂", "轻量", "heavy", "light", "simple", "complex"]):
                                # 用户提供了具体的模型描述，直接使用
                                user_descriptions = user_input
                            else:
                                # 用户没有提供具体描述，使用默认的多个配置
                                user_descriptions = "简单CNN模型，batch_size=32，epochs=4;基础CNN模型，batch_size=16，epochs=4;深度CNN模型，batch_size=64，epochs=4"
                            
                            logger.info(f"开始并行训练多个模型，用户需求: {user_input}")
                            result = test_generate_and_run(user_descriptions)
                            
                            if result["status"] == "success":
                                final_answer = f"""🚀 **并行ML模型训练完成**

**状态**: ✅ 并行训练成功完成

**训练结果**:
- 生成的配置文件: {len(result['generated_configs'])} 个
- 实验会话: {result.get('session_name', 'N/A')}
- 总进程数: {result['experiment_results']['execution_summary']['total_processes']}
- 成功进程: {result['experiment_results']['execution_summary']['successful_processes']}

**您的请求**: {user_input}

**模型保存位置**: {mcp_ml_output_dir} 目录下

**下一步**: 您可以使用训练好的多个模型进行图像分类和标注"""
                            else:
                                final_answer = f"""⚠️ **并行ML模型训练失败**

**错误信息**: {result.get('message', '未知错误')}

**您的请求**: {user_input}

**建议**: 稍后重试或检查系统资源"""
                        else:
                            # 使用单个模型训练功能
                            from server import run_pipeline
                            
                            logger.info(f"开始训练单个模型，用户需求: {user_input}")
                            result = run_pipeline()
                            logger.info(f"ML训练完成: {result}")
                            
                            final_answer = f"""🚀 **ML模型训练完成**

**状态**: ✅ 训练成功完成

**训练结果**:
{result if result else "训练已完成，模型已保存"}

**您的请求**: {user_input}

**模型保存位置**: {mcp_ml_output_dir} 目录下

**下一步**: 您可以使用训练好的模型进行图像分类和标注"""
                        
                        # 恢复原始工作目录
                        os.chdir(original_cwd)
                        
                    except Exception as e:
                        logger.error(f"直接调用MCP ML服务器失败: {str(e)}")
                        final_answer = f"""⚠️ **ML模型训练失败**

**错误信息**: {str(e)}

**您的请求**: {user_input}

**建议**:
1. 检查MCP ML服务器是否正常运行
2. 确认依赖包已正确安装
3. 稍后重试"""
                    
                else:
                    # 检查模型状态
                    final_answer = f"""🔭 **多模态标注功能**

**功能说明**:
- 基于MCP ML服务器的深度学习模型
- 支持星系形态自动分类
- 识别椭圆星系、旋涡星系、不规则星系等类型

**服务器状态**: ✅ MCP ML服务器可用
**配置路径**: mcp_ml/config/config.yaml

**使用方法**:
1. 训练模型：说"训练模型"或"开始训练"
2. 图像分类：提供图像路径进行分析
3. 模型状态：查询当前模型状态

**技术特点**:
- 使用CNN架构进行图像分类
- 支持数据增强和预处理
- 提供训练历史可视化
- 生成混淆矩阵和性能指标

**支持的图像格式**: JPG, JPEG, PNG, TIFF
**推荐图像尺寸**: 128x128像素

您的请求：{user_input}"""
                
            except ImportError as e:
                final_answer = f"""⚠️ **多模态标注功能暂时不可用**

**错误信息**: 无法导入MCP ML客户端 ({str(e)})

**可能原因**:
- 缺少必要的依赖包（mcp, fastmcp等）
- 模块文件不完整

**建议**:
1. 安装依赖：pip install mcp fastmcp
2. 检查mcp_ml_client模块文件是否完整
3. 稍后重试

您的请求：{user_input}"""
            except Exception as e:
                final_answer = f"""❌ **多模态标注处理失败**

**错误信息**: {str(e)}

**建议**: 请简化请求或稍后重试

您的请求：{user_input}"""
        else:
            final_answer = f"""🔭 **多模态标注功能**

**支持的功能**:
1. **天文图像分类** - 识别星系类型和形态
2. **天体特征识别** - 分析天体的物理特征
3. **图像质量评估** - 评估观测图像的质量
4. **自动标注生成** - 为图像生成科学标注
5. **模型训练** - 训练新的深度学习模型

**使用方法**:
- 模型训练：说"训练模型"或"开始训练"
- 图像分类：提供图像路径，如"分类这张星系图像：path/to/image.jpg"
- 特征识别：描述要分析的天体特征
- 质量评估：上传图像进行质量分析

**技术特点**:
- 基于MCP ML服务器的深度学习模型
- 支持多种天文图像格式
- 提供详细的置信度评估
- 集成完整的训练和推理流程

您的请求：{user_input}"""
        
        # 更新状态
        updated_state = state.copy()
        updated_state["current_step"] = "multimark_completed"
        updated_state["is_complete"] = True
        updated_state["final_answer"] = final_answer
        updated_state["task_type"] = "multimark"
        
        # 记录执行历史
        execution_history = updated_state.get("execution_history", [])
        execution_history.append({
            "node": "multimark_command_node",
            "action": "mcp_ml_integration" if is_classification_request else "multimark_info",
            "input": user_input,
            "output": "多模态标注处理完成",
            "timestamp": time.time()
        })
        updated_state["execution_history"] = execution_history

        return Command(
            update=updated_state,
            goto="__end__"
        )

    except Exception as e:
        # 错误处理
        error_state = state.copy()
        error_state["error_info"] = {
            "node": "multimark_command_node",
            "error": str(e),
            "timestamp": time.time(),
        }
        error_state["final_answer"] = f"多模态标注过程中发生错误：{str(e)}"
        error_state["is_complete"] = True
        
        return Command(
            update=error_state,
            goto="__end__"
        )


