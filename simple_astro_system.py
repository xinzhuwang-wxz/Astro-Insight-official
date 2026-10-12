#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的天文科研系统
绕过LangGraph的复杂状态管理，直接使用我们的改进功能
"""

import sys
import os
sys.path.insert(0, 'src')

from utils.error_handler import handle_error, create_error_context, AstroError, ErrorCode, ErrorSeverity
from utils.state_manager import format_state_output, validate_state, create_initial_state

class SimpleAstroSystem:
    """简化的天文科研系统"""
    
    def __init__(self):
        # 简化配置，不依赖外部配置
        self.config = {
            "llm": {"api_key": "test_key", "model": "test_model"},
            "debug": True
        }
        print("✅ 简化系统初始化完成")
    
    def process_query(self, session_id: str, user_input: str):
        """处理用户查询"""
        try:
            # 创建初始状态
            state = create_initial_state(session_id, user_input)
            
            # 身份识别
            user_type = self._identify_user_type(user_input)
            state["user_type"] = user_type
            
            # 任务分类
            task_type = self._classify_task(user_input, user_type)
            state["task_type"] = task_type
            
            # 处理任务
            if task_type == "qa":
                response = self._handle_qa_query(user_input, user_type)
                state["qa_response"] = response
                state["final_answer"] = response
            elif task_type == "classification":
                response = self._handle_classification_query(user_input)
                state["final_answer"] = response
            elif task_type == "data_retrieval":
                response = self._handle_data_retrieval_query(user_input)
                state["final_answer"] = response
            else:
                response = self._handle_general_query(user_input)
                state["final_answer"] = response
            
            state["current_step"] = "completed"
            state["is_complete"] = True
            
            return state
            
        except Exception as e:
            error_context = create_error_context(session_id=session_id)
            error_info = handle_error(e, error_context, reraise=False)
            state["error_info"] = error_info
            state["current_step"] = "error"
            return state
    
    def _identify_user_type(self, user_input: str) -> str:
        """识别用户类型"""
        professional_keywords = [
            "分析", "数据", "代码", "编程", "算法", "分类", 
            "处理", "计算", "研究", "生成代码", "写代码",
            "professional", "专业", "开发", "脚本"
        ]
        
        if any(kw in user_input.lower() for kw in professional_keywords):
            return "professional"
        else:
            return "amateur"
    
    def _classify_task(self, user_input: str, user_type: str) -> str:
        """分类任务类型"""
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
        """处理问答查询"""
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
    
    def _handle_classification_query(self, user_input: str) -> str:
        """处理分类查询"""
        return f"""天体分类分析：

查询：{user_input}

基于您的输入，我识别到这可能涉及：
- 恒星分类
- 星系分类  
- 行星分类
- 其他天体分类

由于这是简化版本，我无法进行实际的分类分析。
在完整版本中，我会：
1. 提取天体信息
2. 调用分类算法
3. 生成详细报告
4. 提供可视化结果"""
    
    def _handle_data_retrieval_query(self, user_input: str) -> str:
        """处理数据检索查询"""
        return f"""数据检索服务：

查询：{user_input}

您需要的数据检索服务包括：
- SDSS数据库查询
- 天体坐标检索
- 光谱数据获取
- 观测数据下载

由于这是简化版本，我无法进行实际的数据检索。
在完整版本中，我会：
1. 解析您的查询需求
2. 连接相关数据库
3. 执行检索操作
4. 格式化返回结果"""
    
    def _handle_general_query(self, user_input: str) -> str:
        """处理一般查询"""
        return f"""感谢您的查询：{user_input}

我是天文科研助手，可以帮您：
1. 回答天文问题
2. 进行天体分类
3. 检索天文数据
4. 生成分析代码
5. 提供文献综述

请告诉我您具体需要什么帮助，我会为您提供相应的服务。"""

def main():
    """主函数"""
    print("简化天文科研系统")
    print("=" * 50)
    
    system = SimpleAstroSystem()
    
    # 测试查询
    test_queries = [
        "你好",
        "什么是黑洞？",
        "我需要分析M87星系",
        "帮我检索SDSS数据",
        "生成分析代码"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {query}")
        print("-" * 30)
        
        result = system.process_query(f"test_{i}", query)
        
        # 使用我们的状态管理器格式化输出
        output = format_state_output(result)
        print(output)

if __name__ == "__main__":
    main()
