# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import time
import uuid
from typing import Dict, Any, List, Optional

from src.agents.provider_runtime import AgentRuntime

from .types import (
    PlannerState, DialogueStatus, DatasetInfo, TaskStep, 
    PlannerResult, DialogueTurn
)
from .dataset_manager import DatasetManager
from .dialogue_manager import DialogueManager
from .task_decomposer import TaskDecomposer
from .prompts import PlannerPrompts


class PlannerAgent:
    """Planner核心Agent - 管理多轮对话和任务规划"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.dataset_manager = DatasetManager()
        self.dialogue_manager = DialogueManager()
        self.task_decomposer = TaskDecomposer()
        self.prompts = PlannerPrompts()
        
        # 获取LLM实例
        self.llm = AgentRuntime().llm
    
    def start_planning_session(
        self, 
        user_request: str, 
        session_id: Optional[str] = None
    ) -> PlannerState:
        """开始规划会话"""
        
        session_id = session_id or str(uuid.uuid4())
        available_datasets = self.dataset_manager.get_available_datasets()
        
        # 创建初始状态
        state = self.dialogue_manager.create_initial_state(
            user_request, session_id, available_datasets
        )
        
        print(f"🚀 开始规划会话: {session_id}")
        print(f"📊 发现 {len(available_datasets)} 个可用数据集")
        
        return state
    
    def process_user_input(
        self, 
        state: PlannerState, 
        user_input: str
    ) -> PlannerState:
        """处理用户输入"""
        
        try:
            # 检查对话是否应该继续
            if not self.dialogue_manager.should_continue_dialogue(state):
                print("⚠️ 对话已达到结束条件")
                return state
            
            # 生成助手回应
            assistant_response = self._generate_response(state, user_input)
            
            # 添加对话轮次
            state = self.dialogue_manager.add_dialogue_turn(
                state, user_input, assistant_response
            )
            
            print(f"💬 第 {state.current_turn} 轮对话完成")
            
            # 检查是否需要更新状态
            self._update_state_from_dialogue(state)
            
            return state
            
        except Exception as e:
            print(f"❌ 处理用户输入失败: {e}")
            state.error_info = {
                "type": "input_processing_error",
                "message": str(e)
            }
            return state
    
    def _generate_response(self, state: PlannerState, user_input: str) -> str:
        """生成助手回应"""
        
        try:
            if state.current_turn == 0:
                # 第一轮对话 - 初始分析
                prompt = self.prompts.get_initial_analysis_prompt(
                    user_input, state.available_datasets
                )
            else:
                # 后续对话 - 澄清需求
                selected_dataset = self.dialogue_manager.determine_selected_dataset(state)
                
                # 确保有可用的数据集
                if not selected_dataset and state.available_datasets:
                    selected_dataset = state.available_datasets[0]
                elif not selected_dataset:
                    return "抱歉，没有可用的数据集进行分析。"
                
                prompt = self.prompts.get_clarification_prompt(
                    user_input,
                    state.dialogue_history,
                    selected_dataset,
                    state.current_turn,
                    state.max_turns
                )
            
            # 调用LLM生成回应
            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            print(f"❌ 生成回应失败: {e}")
            return f"抱歉，处理您的输入时出现了错误: {str(e)}"
    
    def _update_state_from_dialogue(self, state: PlannerState):
        """从对话中更新状态信息"""
        
        # 提取需求信息
        state.refined_requirements = self.dialogue_manager.extract_requirements_from_dialogue(state)
        
        # 确定选择的数据集
        selected_dataset = self.dialogue_manager.determine_selected_dataset(state)
        if selected_dataset:
            state.selected_dataset = selected_dataset
            print(f"📊 已选择数据集: {selected_dataset.name}")
        elif state.available_datasets and not state.selected_dataset:
            # 如果没有明确选择，使用第一个可用数据集
            state.selected_dataset = state.available_datasets[0]
            print(f"📊 默认选择数据集: {state.selected_dataset.name}")
        
        # 检查是否可以进行任务分解
        if self._should_decompose_tasks(state):
            self._perform_task_decomposition(state)
        
        # 检查是否可以生成最终prompt
        if self._should_generate_final_prompt(state):
            self._generate_final_prompt(state)
    
    def _should_decompose_tasks(self, state: PlannerState) -> bool:
        """判断是否应该进行任务分解"""
        
        # 如果已经有任务步骤，不需要重新分解
        if state.task_steps:
            return False
        
        # 如果对话轮次太少，信息不够
        if state.current_turn < 2:
            return False
        
        # 检查用户是否提供了足够的信息
        requirements = state.refined_requirements
        if requirements.get("analysis_type") and state.selected_dataset:
            return True
        
        return False
    
    def _should_generate_final_prompt(self, state: PlannerState) -> bool:
        """判断是否应该生成最终prompt"""
        
        # 如果已经有最终prompt，不需要重新生成
        if state.final_prompt:
            return False
        
        # 如果任务步骤不完整，不能生成prompt
        if not state.task_steps:
            return False
        
        # 检查用户是否确认了需求
        if state.dialogue_history:
            last_input = state.dialogue_history[-1].user_input.lower()
            if any(keyword in last_input for keyword in ["确认", "是的", "对", "开始", "执行"]):
                return True
        
        return False
    
    def _perform_task_decomposition(self, state: PlannerState):
        """执行任务分解"""
        
        try:
            print("🔧 开始任务分解...")
            
            # 使用LLM进行任务分解
            prompt = self.prompts.get_task_decomposition_prompt(
                state.refined_requirements,
                state.selected_dataset,
                state.dialogue_history
            )
            
            response = self.llm.invoke(prompt)
            
            # 使用任务分解器解析结果
            task_steps = self.task_decomposer.decompose_requirements(
                state.refined_requirements,
                state.selected_dataset,
                response.content
            )
            
            # 分析复杂度
            complexity = self.task_decomposer.analyze_task_complexity(task_steps)
            
            # 验证任务步骤
            errors = self.task_decomposer.validate_task_steps(task_steps)
            if errors:
                print(f"⚠️ 任务步骤验证警告: {errors}")
            
            state.task_steps = task_steps
            state.task_complexity = complexity
            
            print(f"✅ 任务分解完成，共 {len(task_steps)} 个步骤")
            print(f"📊 任务复杂度: {complexity.value}")
            
        except Exception as e:
            print(f"❌ 任务分解失败: {e}")
            # 使用备用任务步骤
            state.task_steps = self.task_decomposer._create_fallback_steps(
                state.refined_requirements,
                state.selected_dataset
            )
    
    def _generate_final_prompt(self, state: PlannerState):
        """生成最终prompt"""
        
        try:
            print("📝 生成最终用户需求描述...")
            
            prompt = self.prompts.get_final_prompt_generation_prompt(
                state.task_steps,
                state.selected_dataset,
                state.refined_requirements
            )
            
            response = self.llm.invoke(prompt)
            final_prompt = response.content.strip()
            
            state.final_prompt = final_prompt
            
            print("✅ 最终prompt生成完成")
            print(f"📋 Prompt长度: {len(final_prompt)} 字符")
            
        except Exception as e:
            print(f"❌ 生成最终prompt失败: {e}")
            # 生成备用prompt
            state.final_prompt = self._create_fallback_prompt(state)
    
    def _create_fallback_prompt(self, state: PlannerState) -> str:
        """创建备用prompt"""
        
        dataset_name = state.selected_dataset.name if state.selected_dataset else "数据集"
        
        return f"""请帮我分析{dataset_name}。

需求描述：
{state.user_initial_request}

分析步骤：
1. 加载数据集
2. 数据清洗和预处理
3. 数据探索和可视化
4. 生成分析结果

请生成完整的Python代码来完成这个分析任务。"""
    
    def request_confirmation(self, state: PlannerState) -> str:
        """请求用户确认"""
        
        if not state.task_steps or not state.final_prompt:
            return "抱歉，任务规划尚未完成，无法请求确认。"
        
        try:
            confirmation_prompt = self.prompts.get_confirmation_prompt(
                state.task_steps,
                state.selected_dataset,
                state.final_prompt
            )
            
            return confirmation_prompt
            
        except Exception as e:
            print(f"❌ 生成确认请求失败: {e}")
            return "请确认是否开始执行分析任务？"
    
    def handle_confirmation(self, state: PlannerState, user_response: str) -> PlannerState:
        """处理用户确认"""
        
        user_response_lower = user_response.lower()
        
        if any(keyword in user_response_lower for keyword in ["确认", "是的", "对", "开始", "执行"]):
            state.user_confirmed = True
            state.dialogue_status = DialogueStatus.COMPLETED
            print("✅ 用户已确认，准备执行任务")
        elif any(keyword in user_response_lower for keyword in ["修改", "否", "不", "重新"]):
            state.user_confirmed = False
            # 清除之前的规划结果，允许重新规划
            state.task_steps = []
            state.final_prompt = None
            print("🔄 用户要求修改，重新规划")
        else:
            # 其他回复，当作修改请求
            state.user_confirmed = False
            print("❓ 用户回复不明确，当作修改请求")
        
        return state
    
    def get_final_result(self, state: PlannerState) -> PlannerResult:
        """获取最终结果"""
        
        return self.dialogue_manager.create_planner_result(state)
    
    def save_session(self, state: PlannerState) -> str:
        """保存会话状态"""
        
        return self.dialogue_manager.save_dialogue_state(state)
    
    def load_session(self, session_id: str) -> Optional[PlannerState]:
        """加载会话状态"""
        
        return self.dialogue_manager.load_dialogue_state(session_id)
    
    def run_complete_session(
        self, 
        user_request: str, 
        session_id: Optional[str] = None
    ) -> PlannerResult:
        """运行完整的规划会话（一次性处理）"""
        
        # 开始会话
        state = self.start_planning_session(user_request, session_id)
        
        # 模拟多轮对话（实际使用中应该由用户交互）
        # 这里只是演示流程
        try:
            # 第一轮：初始分析
            state = self.process_user_input(state, user_request)
            
            # 强制进行任务分解（简化版）
            if not state.task_steps:
                print("🔧 开始任务分解...")
                # 确保数据集已选择
                if not state.selected_dataset and state.available_datasets:
                    state.selected_dataset = state.available_datasets[0]
                    print(f"📊 自动选择数据集: {state.selected_dataset.name}")
                
                # 确保需求信息已提取
                if not state.refined_requirements:
                    state.refined_requirements = self.dialogue_manager.extract_requirements_from_dialogue(state)
                    print("📋 提取需求信息完成")
                
                self._perform_task_decomposition(state)
            
            # 生成最终prompt
            if state.task_steps and not state.final_prompt:
                print("📝 生成最终prompt...")
                self._generate_final_prompt(state)
            
            # 自动确认
            if state.task_steps and state.final_prompt:
                print("✅ 自动确认需求...")
                state.user_confirmed = True
                state.dialogue_status = DialogueStatus.COMPLETED
            
        except Exception as e:
            print(f"❌ 会话执行失败: {e}")
            state.error_info = {
                "type": "session_error",
                "message": str(e)
            }
        
        # 保存会话
        self.save_session(state)
        
        # 返回结果
        return self.get_final_result(state)
