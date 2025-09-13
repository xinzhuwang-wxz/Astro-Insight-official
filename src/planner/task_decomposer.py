# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import re
from typing import List, Dict, Any, Optional
from .types import TaskStep, TaskPriority, TaskComplexity, DatasetInfo


class TaskDecomposer:
    """任务分解器 - 将用户需求分解为具体的可执行任务"""
    
    def __init__(self):
        self.common_patterns = self._init_common_patterns()
    
    def _init_common_patterns(self) -> Dict[str, List[str]]:
        """初始化常见的任务模式"""
        return {
            "data_loading": [
                "加载", "读取", "导入", "打开", "load", "read", "import"
            ],
            "data_cleaning": [
                "清洗", "清理", "预处理", "处理缺失值", "异常值", "clean", "preprocess"
            ],
            "data_exploration": [
                "探索", "查看", "统计", "描述", "基本分析", "explore", "describe", "summary"
            ],
            "data_filtering": [
                "筛选", "过滤", "选择", "条件", "filter", "select", "where"
            ],
            "visualization": [
                "可视化", "图表", "散点图", "直方图", "热力图", "plot", "chart", "graph"
            ],
            "analysis": [
                "分析", "相关性", "聚类", "分类", "预测", "analysis", "correlation", "cluster"
            ],
            "export": [
                "保存", "导出", "输出", "生成报告", "save", "export", "output"
            ]
        }
    
    def decompose_requirements(
        self, 
        requirements: Dict[str, Any], 
        dataset_info: DatasetInfo,
        llm_response: str
    ) -> List[TaskStep]:
        """分解用户需求为具体任务步骤"""
        
        try:
            # 尝试从LLM响应中解析JSON
            task_steps = self._parse_llm_response(llm_response)
            if task_steps:
                return task_steps
            
            # 如果解析失败，使用规则基础的方法
            return self._rule_based_decomposition(requirements, dataset_info)
            
        except Exception as e:
            print(f"❌ 任务分解失败: {e}")
            return self._create_fallback_steps(requirements, dataset_info)
    
    def _parse_llm_response(self, llm_response: str) -> Optional[List[TaskStep]]:
        """解析LLM的JSON响应"""
        try:
            # 提取JSON部分
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\{.*"task_steps".*?\})', llm_response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                task_steps = []
                for step_data in data.get("task_steps", []):
                    task_step = TaskStep(
                        step_id=step_data.get("step_id", f"step_{len(task_steps) + 1}"),
                        description=step_data.get("description", ""),
                        action_type=step_data.get("action_type", "analyze"),
                        details=step_data.get("details", ""),
                        dependencies=step_data.get("dependencies", []),
                        priority=self._parse_priority(step_data.get("priority", "medium"))
                    )
                    task_steps.append(task_step)
                
                return task_steps
            
        except Exception as e:
            print(f"❌ 解析LLM响应失败: {e}")
        
        return None
    
    def _rule_based_decomposition(
        self, 
        requirements: Dict[str, Any], 
        dataset_info: DatasetInfo
    ) -> List[TaskStep]:
        """基于规则的任务分解"""
        
        steps = []
        
        # 1. 数据加载步骤
        steps.append(TaskStep(
            step_id="step_1",
            description=f"加载{dataset_info.name}数据集",
            action_type="load",
            details=f"使用pandas读取CSV文件 {dataset_info.path}，检查数据形状和列名",
            priority=TaskPriority.HIGH
        ))
        
        # 2. 数据清洗步骤
        steps.append(TaskStep(
            step_id="step_2",
            description="数据清洗和预处理",
            action_type="clean",
            details="处理缺失值，转换数据类型，移除异常值，检查数据质量",
            priority=TaskPriority.HIGH,
            dependencies=["step_1"]
        ))
        
        # 3. 根据需求添加特定步骤
        user_text = str(requirements).lower()
        
        # 数据探索
        if any(keyword in user_text for keyword in ["统计", "描述", "探索", "查看"]):
            steps.append(TaskStep(
                step_id="step_3",
                description="数据探索和基本统计",
                action_type="explore",
                details="生成数据的基本统计信息，查看数据分布和特征",
                priority=TaskPriority.MEDIUM,
                dependencies=["step_2"]
            ))
        
        # 数据筛选
        if any(keyword in user_text for keyword in ["筛选", "过滤", "条件"]):
            steps.append(TaskStep(
                step_id=f"step_{len(steps) + 1}",
                description="数据筛选",
                action_type="filter",
                details="根据用户指定的条件筛选数据",
                priority=TaskPriority.MEDIUM,
                dependencies=["step_2"]
            ))
        
        # 可视化
        if any(keyword in user_text for keyword in ["图", "可视化", "散点图", "直方图", "热力图"]):
            viz_steps = self._create_visualization_steps(len(steps) + 1, dataset_info, user_text)
            steps.extend(viz_steps)
        
        # 分析
        if any(keyword in user_text for keyword in ["分析", "相关性", "聚类", "分类"]):
            analysis_step = TaskStep(
                step_id=f"step_{len(steps) + 1}",
                description="数据分析和建模",
                action_type="analyze",
                details="执行用户要求的分析任务（相关性分析、聚类、分类等）",
                priority=TaskPriority.MEDIUM,
                dependencies=[f"step_{len(steps)}"]
            )
            steps.append(analysis_step)
        
        # 4. 结果保存
        steps.append(TaskStep(
            step_id=f"step_{len(steps) + 1}",
            description="保存结果和生成报告",
            action_type="export",
            details="将生成的图表保存到output目录，输出分析结果",
            priority=TaskPriority.LOW,
            dependencies=[f"step_{len(steps)}"]
        ))
        
        return steps
    
    def _create_visualization_steps(
        self, 
        start_id: int, 
        dataset_info: DatasetInfo, 
        user_text: str
    ) -> List[TaskStep]:
        """创建可视化相关的步骤"""
        
        steps = []
        current_id = start_id
        
        # 散点图
        if any(keyword in user_text for keyword in ["散点图", "scatter"]):
            steps.append(TaskStep(
                step_id=f"step_{current_id}",
                description="生成散点图",
                action_type="visualize",
                details=f"创建散点图，展示{dataset_info.columns[:2]}之间的关系",
                priority=TaskPriority.MEDIUM
            ))
            current_id += 1
        
        # 直方图
        if any(keyword in user_text for keyword in ["直方图", "分布", "histogram"]):
            steps.append(TaskStep(
                step_id=f"step_{current_id}",
                description="生成直方图",
                action_type="visualize",
                details="创建直方图，展示数据的分布情况",
                priority=TaskPriority.MEDIUM
            ))
            current_id += 1
        
        # 热力图
        if any(keyword in user_text for keyword in ["热力图", "相关性矩阵", "heatmap"]):
            steps.append(TaskStep(
                step_id=f"step_{current_id}",
                description="生成相关性热力图",
                action_type="visualize",
                details="创建热力图，展示变量间的相关性",
                priority=TaskPriority.MEDIUM
            ))
            current_id += 1
        
        # 如果没有指定具体图表类型，默认创建散点图
        if not steps:
            steps.append(TaskStep(
                step_id=f"step_{current_id}",
                description="生成数据可视化图表",
                action_type="visualize",
                details="创建散点图和其他合适的图表来展示数据特征",
                priority=TaskPriority.MEDIUM
            ))
        
        return steps
    
    def _create_fallback_steps(
        self, 
        requirements: Dict[str, Any], 
        dataset_info: DatasetInfo
    ) -> List[TaskStep]:
        """创建备用步骤（当分解失败时）"""
        
        return [
            TaskStep(
                step_id="step_1",
                description=f"加载{dataset_info.name}数据集",
                action_type="load",
                details=f"读取数据集文件 {dataset_info.path}",
                priority=TaskPriority.HIGH
            ),
            TaskStep(
                step_id="step_2",
                description="数据预处理",
                action_type="clean",
                details="处理数据，准备分析",
                priority=TaskPriority.HIGH,
                dependencies=["step_1"]
            ),
            TaskStep(
                step_id="step_3",
                description="数据分析和可视化",
                action_type="analyze",
                details="执行用户需求的数据分析任务",
                priority=TaskPriority.MEDIUM,
                dependencies=["step_2"]
            ),
            TaskStep(
                step_id="step_4",
                description="保存结果",
                action_type="export",
                details="保存分析结果和图表",
                priority=TaskPriority.LOW,
                dependencies=["step_3"]
            )
        ]
    
    def _parse_priority(self, priority_str: str) -> TaskPriority:
        """解析优先级字符串"""
        priority_str = priority_str.lower()
        if priority_str in ["high", "高"]:
            return TaskPriority.HIGH
        elif priority_str in ["low", "低"]:
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM
    
    def analyze_task_complexity(self, task_steps: List[TaskStep]) -> TaskComplexity:
        """分析任务复杂度"""
        if len(task_steps) <= 3:
            return TaskComplexity.SIMPLE
        elif len(task_steps) <= 6:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.COMPLEX
    
    def validate_task_steps(self, task_steps: List[TaskStep]) -> List[str]:
        """验证任务步骤的有效性"""
        errors = []
        
        # 检查步骤ID唯一性
        step_ids = [step.step_id for step in task_steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("存在重复的步骤ID")
        
        # 检查依赖关系
        valid_ids = set(step_ids)
        for step in task_steps:
            for dep in step.dependencies:
                if dep not in valid_ids:
                    errors.append(f"步骤 {step.step_id} 的依赖 {dep} 不存在")
        
        # 检查是否有循环依赖
        # 这里可以添加更复杂的循环检测逻辑
        
        return errors
