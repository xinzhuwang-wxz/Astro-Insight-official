# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .types import (
    PlannerState, DialogueTurn, DialogueStatus, 
    DatasetInfo, TaskStep, PlannerResult
)


class DialogueManager:
    """对话管理器 - 管理多轮对话的状态和流程"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建对话子目录
        self.dialogue_dir = self.output_dir / "planner_dialogues"
        self.dialogue_dir.mkdir(exist_ok=True)
    
    def create_initial_state(
        self, 
        user_request: str, 
        session_id: str,
        available_datasets: List[DatasetInfo]
    ) -> PlannerState:
        """创建初始对话状态"""
        
        return PlannerState(
            session_id=session_id,
            user_initial_request=user_request,
            dialogue_status=DialogueStatus.INITIAL,
            current_turn=0,
            max_turns=10,
            available_datasets=available_datasets,
            last_activity=time.time()
        )
    
    def add_dialogue_turn(
        self, 
        state: PlannerState, 
        user_input: str, 
        assistant_response: str,
        context_used: Optional[Dict[str, Any]] = None
    ) -> PlannerState:
        """添加一轮对话"""
        
        # 增加轮次计数
        state.current_turn += 1
        
        # 创建对话轮次
        turn = DialogueTurn(
            turn_id=state.current_turn,
            user_input=user_input,
            assistant_response=assistant_response,
            timestamp=time.time(),
            context_used=context_used or {}
        )
        
        # 添加到历史
        state.dialogue_history.append(turn)
        state.last_activity = time.time()
        
        # 更新对话状态
        self._update_dialogue_status(state)
        
        return state
    
    def _update_dialogue_status(self, state: PlannerState):
        """更新对话状态"""
        
        if state.current_turn == 0:
            state.dialogue_status = DialogueStatus.INITIAL
        elif state.current_turn == 1:
            state.dialogue_status = DialogueStatus.COLLECTING
        elif state.current_turn < state.max_turns:
            # 检查是否需要澄清
            last_turn = state.dialogue_history[-1]
            if any(keyword in last_turn.user_input.lower() for keyword in ["确认", "是的", "对", "没错"]):
                state.dialogue_status = DialogueStatus.CONFIRMING
            else:
                state.dialogue_status = DialogueStatus.CLARIFYING
        else:
            # 达到最大轮次
            state.dialogue_status = DialogueStatus.COMPLETED
    
    def should_continue_dialogue(self, state: PlannerState) -> bool:
        """判断是否应该继续对话"""
        
        # 检查轮次限制
        if state.current_turn >= state.max_turns:
            return False
        
        # 检查对话状态
        if state.dialogue_status == DialogueStatus.COMPLETED:
            return False
        
        if state.dialogue_status == DialogueStatus.CANCELLED:
            return False
        
        # 检查最近的用户输入是否表示结束
        if state.dialogue_history:
            last_input = state.dialogue_history[-1].user_input.lower()
            end_keywords = ["结束", "完成", "确认", "开始执行", "开始", "好的"]
            
            if any(keyword in last_input for keyword in end_keywords):
                return False
        
        return True
    
    def extract_requirements_from_dialogue(
        self, 
        state: PlannerState
    ) -> Dict[str, Any]:
        """从对话历史中提取需求信息"""
        
        requirements = {
            "original_request": state.user_initial_request,
            "dataset_preference": None,
            "analysis_type": None,
            "visualization_needs": [],
            "specific_requirements": [],
            "filters": [],
            "output_format": None
        }
        
        # 分析对话历史
        for turn in state.dialogue_history:
            user_text = turn.user_input.lower()
            
            # 数据集偏好
            for dataset in state.available_datasets:
                if dataset.name.lower() in user_text:
                    requirements["dataset_preference"] = dataset.name
            
            # 分析类型
            if any(keyword in user_text for keyword in ["分析", "统计", "探索"]):
                requirements["analysis_type"] = "exploratory"
            elif any(keyword in user_text for keyword in ["预测", "建模", "分类"]):
                requirements["analysis_type"] = "predictive"
            elif any(keyword in user_text for keyword in ["聚类", "分组"]):
                requirements["analysis_type"] = "clustering"
            
            # 可视化需求
            viz_types = {
                "散点图": "scatter",
                "直方图": "histogram", 
                "热力图": "heatmap",
                "线图": "line",
                "柱状图": "bar"
            }
            
            for chinese, english in viz_types.items():
                if chinese in user_text or english in user_text:
                    requirements["visualization_needs"].append(english)
            
            # 具体需求
            if "相关性" in user_text:
                requirements["specific_requirements"].append("correlation_analysis")
            if "分布" in user_text:
                requirements["specific_requirements"].append("distribution_analysis")
            if "异常值" in user_text:
                requirements["specific_requirements"].append("outlier_detection")
            
            # 筛选条件
            if any(keyword in user_text for keyword in ["大于", "小于", "等于", "筛选", "过滤"]):
                requirements["filters"].append(turn.user_input)
        
        # 去重
        requirements["visualization_needs"] = list(set(requirements["visualization_needs"]))
        requirements["specific_requirements"] = list(set(requirements["specific_requirements"]))
        
        return requirements
    
    def determine_selected_dataset(
        self, 
        state: PlannerState
    ) -> Optional[DatasetInfo]:
        """确定用户选择的数据集"""
        
        # 从对话历史中查找数据集提及
        mentioned_datasets = set()
        
        for turn in state.dialogue_history:
            user_text = turn.user_input.lower()
            assistant_text = turn.assistant_response.lower()
            
            # 检查用户输入中的数据集提及
            for dataset in state.available_datasets:
                dataset_name_lower = dataset.name.lower()
                dataset_desc_lower = dataset.description.lower() if dataset.description else ""
                
                # 直接名称匹配
                if dataset_name_lower in user_text:
                    mentioned_datasets.add(dataset.name)
                
                # 关键词匹配
                elif "star" in user_text and ("star" in dataset_name_lower or "star" in dataset_desc_lower):
                    mentioned_datasets.add(dataset.name)
                elif "galaxy" in user_text and ("galaxy" in dataset_name_lower or "galaxy" in dataset_desc_lower):
                    mentioned_datasets.add(dataset.name)
                elif "sdss" in user_text and ("sdss" in dataset_name_lower or "sdss" in dataset_desc_lower):
                    mentioned_datasets.add(dataset.name)
                elif "6_class" in user_text and "6_class" in dataset_name_lower:
                    mentioned_datasets.add(dataset.name)
            
            # 检查助手回应中的数据集推荐
            for dataset in state.available_datasets:
                dataset_name_lower = dataset.name.lower()
                dataset_desc_lower = dataset.description.lower() if dataset.description else ""
                
                # 助手明确推荐的数据集
                if dataset_name_lower in assistant_text:
                    mentioned_datasets.add(dataset.name)
                elif "推荐" in assistant_text and "star" in assistant_text and ("star" in dataset_name_lower or "star" in dataset_desc_lower):
                    mentioned_datasets.add(dataset.name)
                elif "推荐" in assistant_text and "galaxy" in assistant_text and ("galaxy" in dataset_name_lower or "galaxy" in dataset_desc_lower):
                    mentioned_datasets.add(dataset.name)
                elif "推荐" in assistant_text and "sdss" in assistant_text and ("sdss" in dataset_name_lower or "sdss" in dataset_desc_lower):
                    mentioned_datasets.add(dataset.name)
        
        # 如果有明确提及，返回第一个
        if mentioned_datasets:
            selected_name = list(mentioned_datasets)[0]
            for dataset in state.available_datasets:
                if dataset.name == selected_name:
                    return dataset
        
        # 如果没有明确提及，尝试智能匹配
        if state.dialogue_history:
            # 获取所有对话内容
            all_text = " ".join([turn.user_input.lower() + " " + turn.assistant_response.lower() for turn in state.dialogue_history])
            
            # 根据关键词智能匹配
            for dataset in state.available_datasets:
                dataset_name_lower = dataset.name.lower()
                dataset_desc_lower = dataset.description.lower() if dataset.description else ""
                
                # 检查是否匹配
                if ("star" in all_text and "star" in dataset_name_lower) or \
                   ("galaxy" in all_text and "galaxy" in dataset_name_lower) or \
                   ("sdss" in all_text and "sdss" in dataset_name_lower):
                    return dataset
        
        # 默认返回第一个可用数据集
        return state.available_datasets[0] if state.available_datasets else None
    
    def save_dialogue_state(self, state: PlannerState) -> str:
        """保存对话状态"""
        
        session_dir = self.dialogue_dir / state.session_id
        session_dir.mkdir(exist_ok=True)
        
        state_file = session_dir / f"{state.session_id}_state.json"
        
        try:
            # 转换为可序列化的字典
            state_dict = {
                "session_id": state.session_id,
                "user_initial_request": state.user_initial_request,
                "dialogue_status": state.dialogue_status.value,
                "current_turn": state.current_turn,
                "max_turns": state.max_turns,
                "dialogue_history": [
                    {
                        "turn_id": turn.turn_id,
                        "user_input": turn.user_input,
                        "assistant_response": turn.assistant_response,
                        "timestamp": turn.timestamp,
                        "context_used": turn.context_used,
                        "clarification_questions": turn.clarification_questions
                    }
                    for turn in state.dialogue_history
                ],
                "refined_requirements": state.refined_requirements,
                "available_datasets": [
                    {
                        "name": dataset.name,
                        "path": dataset.path,
                        "description": dataset.description,
                        "columns": dataset.columns,
                        "size": dataset.size,
                        "file_type": dataset.file_type,
                        "sample_data": dataset.sample_data,
                        "data_types": dataset.data_types
                    }
                    for dataset in state.available_datasets
                ],
                "selected_dataset": {
                    "name": state.selected_dataset.name,
                    "path": state.selected_dataset.path,
                    "description": state.selected_dataset.description,
                    "columns": state.selected_dataset.columns
                } if state.selected_dataset else None,
                "task_steps": [
                    {
                        "step_id": step.step_id,
                        "description": step.description,
                        "action_type": step.action_type,
                        "details": step.details,
                        "dependencies": step.dependencies,
                        "priority": step.priority.value
                    }
                    for step in state.task_steps
                ],
                "final_prompt": state.final_prompt,
                "user_confirmed": state.user_confirmed,
                "last_activity": state.last_activity
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, ensure_ascii=False, indent=2)
            
            print(f"💾 对话状态已保存: {state_file}")
            return str(state_file)
            
        except Exception as e:
            print(f"❌ 保存对话状态失败: {e}")
            return ""
    
    def load_dialogue_state(self, session_id: str) -> Optional[PlannerState]:
        """加载对话状态"""
        
        state_file = self.dialogue_dir / session_id / f"{session_id}_state.json"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_dict = json.load(f)
            
            # 重建对话历史
            dialogue_history = []
            for turn_data in state_dict.get("dialogue_history", []):
                turn = DialogueTurn(
                    turn_id=turn_data["turn_id"],
                    user_input=turn_data["user_input"],
                    assistant_response=turn_data["assistant_response"],
                    timestamp=turn_data["timestamp"],
                    context_used=turn_data.get("context_used", {}),
                    clarification_questions=turn_data.get("clarification_questions", [])
                )
                dialogue_history.append(turn)
            
            # 重建任务步骤
            task_steps = []
            for step_data in state_dict.get("task_steps", []):
                from .types import TaskPriority
                step = TaskStep(
                    step_id=step_data["step_id"],
                    description=step_data["description"],
                    action_type=step_data["action_type"],
                    details=step_data["details"],
                    dependencies=step_data["dependencies"],
                    priority=TaskPriority(step_data.get("priority", "medium"))
                )
                task_steps.append(step)
            
            # 重建可用数据集信息
            available_datasets = []
            for ds_data in state_dict.get("available_datasets", []):
                dataset = DatasetInfo(
                    name=ds_data["name"],
                    path=ds_data["path"],
                    description=ds_data["description"],
                    columns=ds_data["columns"],
                    size=ds_data.get("size", 0),
                    file_type=ds_data.get("file_type", "csv"),
                    sample_data=ds_data.get("sample_data"),
                    data_types=ds_data.get("data_types")
                )
                available_datasets.append(dataset)
            
            # 重建选定数据集信息
            selected_dataset = None
            if state_dict.get("selected_dataset"):
                ds_data = state_dict["selected_dataset"]
                selected_dataset = DatasetInfo(
                    name=ds_data["name"],
                    path=ds_data["path"],
                    description=ds_data["description"],
                    columns=ds_data["columns"],
                    size=ds_data.get("size", 0),
                    file_type=ds_data.get("file_type", "csv")
                )
            
            # 重建状态
            state = PlannerState(
                session_id=state_dict["session_id"],
                user_initial_request=state_dict["user_initial_request"],
                dialogue_status=DialogueStatus(state_dict["dialogue_status"]),
                current_turn=state_dict["current_turn"],
                max_turns=state_dict["max_turns"],
                dialogue_history=dialogue_history,
                refined_requirements=state_dict.get("refined_requirements", {}),
                available_datasets=available_datasets,
                selected_dataset=selected_dataset,
                task_steps=task_steps,
                final_prompt=state_dict.get("final_prompt"),
                user_confirmed=state_dict.get("user_confirmed", False),
                last_activity=state_dict.get("last_activity", time.time())
            )
            
            return state
            
        except Exception as e:
            print(f"❌ 加载对话状态失败: {e}")
            return None
    
    def create_planner_result(self, state: PlannerState) -> PlannerResult:
        """创建Planner结果"""
        
        # 计算处理时间
        processing_time = 0.0
        if state.dialogue_history:
            # 使用对话历史的时间范围计算
            start_time = state.dialogue_history[0].timestamp
            end_time = state.dialogue_history[-1].timestamp
            processing_time = end_time - start_time
        
        # 确定成功状态和错误消息
        success = state.dialogue_status == DialogueStatus.COMPLETED and state.user_confirmed
        error_message = None
        
        if not success:
            if state.error_info:
                error_message = state.error_info.get("message", "未知错误")
            elif state.dialogue_status == DialogueStatus.CANCELLED:
                error_message = "用户取消了对话"
            elif state.current_turn >= state.max_turns:
                error_message = f"达到最大对话轮次限制 ({state.max_turns}轮)"
            elif not state.task_steps:
                error_message = "任务分解失败"
            elif not state.final_prompt:
                error_message = "最终prompt生成失败"
            else:
                error_message = "用户未确认需求"
        
        return PlannerResult(
            success=success,
            session_id=state.session_id,
            final_prompt=state.final_prompt,
            task_steps=state.task_steps,
            dialogue_history=state.dialogue_history,
            selected_dataset=state.selected_dataset,
            turns_used=state.current_turn,
            processing_time=processing_time,
            error_message=error_message
        )
