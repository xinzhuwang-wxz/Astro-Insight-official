#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
架构化主程序
使用新的架构设计，展示依赖注入和服务层
"""

import sys
import os
import time
from typing import Dict, Any
sys.path.insert(0, 'src')

from core.container import get_container, configure_default_services
from core.interfaces import IUserService, ITaskService, IStateManager, ILogger
from core.exceptions import ServiceNotFoundError, ConfigurationError
from graph.types import AstroAgentState


class ArchitecturalAstroSystem:
    """架构化天文科研系统"""
    
    def __init__(self):
        self.container = get_container()
        self._setup_services()
        self.logger = self.container.get(ILogger)
        self.logger.info("架构化天文科研系统初始化完成")
    
    def _setup_services(self):
        """设置服务"""
        try:
            # 配置默认服务
            configure_default_services(self.container)
            self.logger = self.container.get(ILogger)
            self.logger.info("服务配置完成")
        except Exception as e:
            print(f"服务配置失败: {e}")
            raise
    
    def process_query(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """处理用户查询"""
        try:
            # 获取服务
            user_service = self.container.get(IUserService)
            task_service = self.container.get(ITaskService)
            state_manager = self.container.get(IStateManager)
            
            # 创建初始状态
            state = state_manager.create_initial_state(session_id, user_input)
            
            # 身份识别
            user_type = user_service.identify_user_type(user_input)
            state["user_type"] = user_type.value
            
            # 任务分类
            task_type = task_service.classify_task(user_input, user_type)
            state["task_type"] = task_type.value
            
            # 执行任务
            task_context = {
                "user_input": user_input,
                "user_type": user_type,
                "session_id": session_id
            }
            
            task_result = task_service.execute_task(task_type, task_context)
            
            # 更新状态
            state["qa_response"] = task_result.get("response", "")
            state["final_answer"] = task_result.get("response", "")
            state["current_step"] = "completed"
            state["is_complete"] = True
            
            self.logger.info(f"查询处理完成: {session_id}")
            return state
            
        except ServiceNotFoundError as e:
            self.logger.error(f"服务未找到: {e}")
            return self._create_error_state(session_id, f"服务错误: {e}")
        except Exception as e:
            self.logger.error(f"查询处理失败: {e}")
            return self._create_error_state(session_id, f"处理错误: {e}")
    
    def _create_error_state(self, session_id: str, error_message: str) -> Dict[str, Any]:
        """创建错误状态"""
        return {
            "session_id": session_id,
            "user_input": "",
            "messages": [],
            "user_type": None,
            "task_type": None,
            "current_step": "error",
            "is_complete": True,
            "error_info": {
                "error": error_message,
                "timestamp": time.time()
            }
        }


def main():
    """主函数"""
    print("🏗️ 架构化天文科研系统")
    print("=" * 50)
    
    try:
        # 创建系统实例
        system = ArchitecturalAstroSystem()
        
        # 测试查询
        test_queries = [
            "你好",
            "什么是黑洞？",
            "我需要分析M87星系",
            "帮我检索SDSS数据",
            "生成分析代码"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 测试 {i}: {query}")
            print("-" * 30)
            
            result = system.process_query(f"arch_test_{i}", query)
            
            # 显示结果
            print(f"用户类型: {result.get('user_type', 'unknown')}")
            print(f"任务类型: {result.get('task_type', 'unknown')}")
            print(f"处理状态: {'完成' if result.get('is_complete') else '进行中'}")
            
            if result.get('final_answer'):
                print(f"回答: {result['final_answer'][:100]}...")
            
            if result.get('error_info'):
                print(f"❌ 错误: {result['error_info'].get('error', '未知错误')}")
        
        print(f"\n✅ 架构化系统测试完成！")
        
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
