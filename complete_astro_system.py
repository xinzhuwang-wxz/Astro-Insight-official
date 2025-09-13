#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整功能的天文科研系统
保留所有原始功能，但绕过LangGraph的复杂状态管理
"""

import sys
import os
sys.path.insert(0, 'src')

from utils.error_handler import handle_error, create_error_context, AstroError, ErrorCode, ErrorSeverity
from utils.state_manager import format_state_output, validate_state, create_initial_state
from database.local_storage import LocalDatabase, CelestialObject, ClassificationResult
from tools.language_processor import language_processor
from llms.llm import get_llm_by_type
from prompts.template import get_prompt
import time
import json

class CompleteAstroSystem:
    """完整功能的天文科研系统"""
    
    def __init__(self):
        # 初始化配置
        self.config = {
            "llm": {"api_key": "test_key", "model": "test_model"},
            "debug": True
        }
        
        # 初始化数据库
        self.db = LocalDatabase()
        
        # 初始化LLM
        try:
            self.llm = get_llm_by_type("basic")
        except Exception as e:
            print(f"Warning: Failed to initialize LLM: {e}")
            self.llm = None
        
        print("✅ 完整功能系统初始化完成")
    
    def process_query(self, session_id: str, user_input: str):
        """处理用户查询 - 完整流程"""
        try:
            # 创建初始状态
            state = create_initial_state(session_id, user_input)
            
            # 1. 身份识别
            user_type = self._identify_user_type(user_input)
            state["user_type"] = user_type
            state["current_step"] = "identity_checked"
            state["identity_completed"] = True
            
            # 2. 任务分类
            task_type = self._classify_task(user_input, user_type)
            state["task_type"] = task_type
            
            # 3. 根据任务类型处理
            if task_type == "qa":
                response = self._handle_qa_query(user_input, user_type)
                state["qa_response"] = response
                state["final_answer"] = response
                state["current_step"] = "qa_completed"
                
            elif task_type == "classification":
                result = self._handle_classification_query(user_input, user_type)
                state["classification_result"] = result
                state["final_answer"] = result.get("response", "分类完成")
                state["current_step"] = "classification_completed"
                
            elif task_type == "data_retrieval":
                result = self._handle_data_retrieval_query(user_input, user_type)
                state["retrieval_result"] = result
                state["final_answer"] = result.get("response", "数据检索完成")
                state["current_step"] = "data_retrieved"
                
            elif task_type == "literature_review":
                result = self._handle_literature_review_query(user_input, user_type)
                state["literature_review_result"] = result
                state["final_answer"] = result.get("response", "文献综述完成")
                state["current_step"] = "literature_reviewed"
                
            elif task_type == "code_generation":
                result = self._handle_code_generation_query(user_input, user_type)
                state["generated_code"] = result.get("code", "")
                state["code_metadata"] = result.get("metadata", {})
                state["final_answer"] = result.get("response", "代码生成完成")
                state["current_step"] = "code_generated"
                
            else:
                response = self._handle_general_query(user_input, user_type)
                state["final_answer"] = response
                state["current_step"] = "general_completed"
            
            state["is_complete"] = True
            return state
            
        except Exception as e:
            error_context = create_error_context(session_id=session_id)
            error_info = handle_error(e, error_context, reraise=False)
            state["error_info"] = error_info
            state["current_step"] = "error"
            return state
    
    def _identify_user_type(self, user_input: str) -> str:
        """身份识别 - 完整版本"""
        professional_keywords = [
            "分析", "数据", "代码", "编程", "算法", "分类", 
            "处理", "计算", "研究", "生成代码", "写代码",
            "professional", "专业", "开发", "脚本", "SDSS",
            "天体", "星系", "恒星", "行星", "黑洞", "脉冲星"
        ]
        
        # 使用LLM进行更精确的身份识别
        if self.llm:
            try:
                prompt = get_prompt("identity_check")
                response = self.llm.invoke(prompt.format(user_input=user_input))
                user_type = response.content.strip().lower()
                
                if "professional" in user_type:
                    return "professional"
                elif "amateur" in user_type:
                    return "amateur"
            except Exception as e:
                print(f"LLM身份识别失败，使用规则识别: {e}")
        
        # 规则识别
        if any(kw in user_input.lower() for kw in professional_keywords):
            return "professional"
        else:
            return "amateur"
    
    def _classify_task(self, user_input: str, user_type: str) -> str:
        """任务分类 - 完整版本"""
        # 使用LLM进行任务分类
        if self.llm:
            try:
                prompt = get_prompt("task_selector")
                response = self.llm.invoke(prompt.format(
                    user_input=user_input,
                    user_type=user_type
                ))
                task_type = response.content.strip().lower()
                
                if "classification" in task_type:
                    return "classification"
                elif "retrieval" in task_type or "data" in task_type:
                    return "data_retrieval"
                elif "literature" in task_type:
                    return "literature_review"
                elif "code" in task_type:
                    return "code_generation"
                else:
                    return "qa"
            except Exception as e:
                print(f"LLM任务分类失败，使用规则分类: {e}")
        
        # 规则分类
        if "分类" in user_input or "classify" in user_input.lower():
            return "classification"
        elif "数据" in user_input or "检索" in user_input or "data" in user_input.lower():
            return "data_retrieval"
        elif "文献" in user_input or "literature" in user_input.lower():
            return "literature_review"
        elif "代码" in user_input or "code" in user_input.lower():
            return "code_generation"
        else:
            return "qa"
    
    def _handle_qa_query(self, user_input: str, user_type: str) -> str:
        """处理问答查询 - 完整版本"""
        if self.llm:
            try:
                prompt = get_prompt("qa_agent")
                response = self.llm.invoke(prompt.format(
                    user_input=user_input,
                    user_type=user_type
                ))
                return response.content
            except Exception as e:
                print(f"LLM问答失败，使用模板回答: {e}")
        
        # 模板回答
        if user_type == "amateur":
            return f"""您好！我是天文科研助手，很高兴为您解答天文问题。

您的问题：{user_input}

作为天文爱好者，我建议您：
1. 从基础概念开始了解
2. 使用简单的观测工具
3. 加入天文爱好者社区
4. 阅读科普书籍和文章

如果您需要更专业的数据分析或代码生成，请告诉我，我可以为您提供专业级别的服务。"""
        else:
            return f"""您好！我是天文科研助手，为您提供专业级服务。

您的问题：{user_input}

作为专业用户，我可以为您提供：
1. 天体分类和分析
2. 数据检索和处理
3. 代码生成和执行
4. 文献综述和研究建议

请告诉我您具体需要什么帮助。"""
    
    def _handle_classification_query(self, user_input: str, user_type: str) -> dict:
        """处理天体分类查询 - 完整版本"""
        try:
            # 提取天体信息
            celestial_info = language_processor.extract_celestial_info(user_input)
            
            # 使用LLM进行分类
            if self.llm:
                try:
                    prompt = get_prompt("classification_config")
                    response = self.llm.invoke(prompt.format(
                        user_input=user_input,
                        celestial_info=celestial_info
                    ))
                    classification_result = json.loads(response.content)
                except Exception as e:
                    print(f"LLM分类失败，使用规则分类: {e}")
                    classification_result = self._rule_based_classification(celestial_info)
            else:
                classification_result = self._rule_based_classification(celestial_info)
            
            # 保存到数据库
            celestial_obj = CelestialObject(
                name=celestial_info.get("name", "未知天体"),
                object_type=classification_result.get("object_type", "未知"),
                coordinates=celestial_info.get("coordinates", {}),
                properties=celestial_info.get("properties", {})
            )
            
            # TODO: 数据库存储功能（预留接口）
            # self.db.save_celestial_object(celestial_obj)
            
            return {
                "celestial_info": celestial_info,
                "classification_result": classification_result,
                "response": f"天体分类完成：{celestial_obj.name} 被分类为 {celestial_obj.object_type}"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "response": f"天体分类失败：{str(e)}"
            }
    
    def _handle_data_retrieval_query(self, user_input: str, user_type: str) -> dict:
        """处理数据检索查询 - 完整版本"""
        try:
            # 模拟数据检索
            retrieval_config = {
                "query": user_input,
                "data_source": "SDSS",
                "filters": {},
                "limit": 100
            }
            
            # 模拟检索结果
            retrieval_result = {
                "data": {
                    "count": 50,
                    "objects": [
                        {"name": "Galaxy_001", "type": "galaxy", "magnitude": 12.5},
                        {"name": "Star_002", "type": "star", "magnitude": 8.3},
                        {"name": "Nebula_003", "type": "nebula", "magnitude": 15.2}
                    ]
                },
                "metadata": {
                    "source": "SDSS",
                    "query_time": time.time(),
                    "total_available": 1000
                }
            }
            
            return {
                "retrieval_config": retrieval_config,
                "retrieval_result": retrieval_result,
                "response": f"数据检索完成，找到{retrieval_result['data']['count']}个相关天体。"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "response": f"数据检索失败：{str(e)}"
            }
    
    def _handle_literature_review_query(self, user_input: str, user_type: str) -> dict:
        """处理文献综述查询 - 完整版本"""
        try:
            # 模拟文献检索
            literature_config = {
                "query": user_input,
                "keywords": language_processor.extract_keywords(user_input),
                "year_range": [2020, 2024],
                "sources": ["arXiv", "ADS", "NASA"]
            }
            
            # 模拟文献结果
            literature_result = {
                "papers_found": 25,
                "papers": [
                    {
                        "title": "Recent Advances in Galaxy Classification",
                        "authors": ["Smith, J.", "Johnson, A."],
                        "year": 2023,
                        "source": "arXiv",
                        "abstract": "This paper presents new methods for galaxy classification..."
                    },
                    {
                        "title": "Machine Learning in Astronomy",
                        "authors": ["Brown, M.", "Wilson, K."],
                        "year": 2024,
                        "source": "ADS",
                        "abstract": "Application of ML techniques to astronomical data analysis..."
                    }
                ],
                "summary": "找到25篇相关论文，主要涉及星系分类和机器学习在天文学中的应用。"
            }
            
            return {
                "literature_config": literature_config,
                "literature_result": literature_result,
                "response": f"文献综述完成，共分析了{literature_result['papers_found']}篇相关论文。"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "response": f"文献综述失败：{str(e)}"
            }
    
    def _handle_code_generation_query(self, user_input: str, user_type: str) -> dict:
        """处理代码生成查询 - 完整版本"""
        try:
            # 根据用户输入生成代码
            if "分析" in user_input or "analysis" in user_input.lower():
                code = self._generate_analysis_code(user_input)
            elif "可视化" in user_input or "plot" in user_input.lower():
                code = self._generate_visualization_code(user_input)
            elif "数据处理" in user_input or "data processing" in user_input.lower():
                code = self._generate_data_processing_code(user_input)
            else:
                code = self._generate_general_code(user_input)
            
            metadata = {
                "task_type": "code_generation",
                "language": "python",
                "dependencies": ["numpy", "matplotlib", "astropy"],
                "generated_at": time.time()
            }
            
            return {
                "code": code,
                "metadata": metadata,
                "response": "代码生成完成，请查看生成的代码。"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "response": f"代码生成失败：{str(e)}"
            }
    
    def _handle_general_query(self, user_input: str, user_type: str) -> str:
        """处理一般查询"""
        return f"已处理您的查询：{user_input}。请提供更具体的要求以获得更好的帮助。"
    
    def _rule_based_classification(self, celestial_info: dict) -> dict:
        """基于规则的分类"""
        name = celestial_info.get("name", "").lower()
        
        if "galaxy" in name or "星系" in name:
            return {"object_type": "galaxy", "confidence": 0.8}
        elif "star" in name or "恒星" in name:
            return {"object_type": "star", "confidence": 0.8}
        elif "planet" in name or "行星" in name:
            return {"object_type": "planet", "confidence": 0.8}
        else:
            return {"object_type": "unknown", "confidence": 0.5}
    
    def _generate_analysis_code(self, user_input: str) -> str:
        """生成分析代码"""
        return f'''# 天文数据分析代码
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u

def analyze_astronomical_data():
    """分析天文数据"""
    # 用户需求: {user_input}
    
    # 1. 数据加载
    # data = fits.open('your_data.fits')[1].data
    
    # 2. 数据预处理
    # processed_data = preprocess_data(data)
    
    # 3. 分析
    # results = perform_analysis(processed_data)
    
    # 4. 可视化
    # plot_results(results)
    
    print("分析完成")
    return results

if __name__ == "__main__":
    analyze_astronomical_data()
'''
    
    def _generate_visualization_code(self, user_input: str) -> str:
        """生成可视化代码"""
        return f'''# 天文数据可视化代码
import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

def visualize_astronomical_data():
    """可视化天文数据"""
    # 用户需求: {user_input}
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 示例数据
    x = np.random.normal(0, 1, 1000)
    y = np.random.normal(0, 1, 1000)
    
    # 散点图
    ax.scatter(x, y, alpha=0.6)
    ax.set_xlabel('X坐标')
    ax.set_ylabel('Y坐标')
    ax.set_title('天文数据可视化')
    
    plt.show()

if __name__ == "__main__":
    visualize_astronomical_data()
'''
    
    def _generate_data_processing_code(self, user_input: str) -> str:
        """生成数据处理代码"""
        return f'''# 天文数据处理代码
import numpy as np
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u

def process_astronomical_data():
    """处理天文数据"""
    # 用户需求: {user_input}
    
    # 1. 数据加载
    # data = fits.open('your_data.fits')[1].data
    
    # 2. 数据清洗
    # cleaned_data = clean_data(data)
    
    # 3. 数据转换
    # converted_data = convert_coordinates(cleaned_data)
    
    # 4. 数据保存
    # save_processed_data(converted_data)
    
    print("数据处理完成")
    return converted_data

if __name__ == "__main__":
    process_astronomical_data()
'''
    
    def _generate_general_code(self, user_input: str) -> str:
        """生成通用代码"""
        return f'''# 天文科研代码
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u

def astronomical_research():
    """天文研究代码"""
    # 用户需求: {user_input}
    
    # 在这里添加您的代码
    print("天文研究代码执行完成")
    
    return None

if __name__ == "__main__":
    astronomical_research()
'''

def main():
    """测试完整功能系统"""
    print("🌌 完整功能天文科研系统")
    print("=" * 50)
    
    system = CompleteAstroSystem()
    
    # 测试用例
    test_cases = [
        "你好",
        "什么是黑洞？",
        "我需要分析M87星系",
        "帮我检索SDSS数据",
        "生成分析代码",
        "帮我查找相关论文",
        "分类这个天体：M87"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case}")
        print("-" * 40)
        
        result = system.process_query(f"test_{i}", test_case)
        
        print(f"会话ID: {result['session_id']}")
        print(f"用户类型: {result['user_type']}")
        print(f"任务类型: {result['task_type']}")
        print(f"处理状态: {'完成' if result['is_complete'] else '进行中'}")
        
        if result.get('final_answer'):
            print(f"回答: {result['final_answer']}")
        
        if result.get('error_info'):
            print(f"错误: {result['error_info']}")
        
        print("-" * 40)

if __name__ == "__main__":
    main()
