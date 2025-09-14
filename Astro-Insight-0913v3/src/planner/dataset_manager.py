# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import os

from .types import DatasetInfo


class DatasetManager:
    """数据集管理器 - 读取和分析可用数据集"""
    
    def __init__(self, dataset_dir: str = None):
        # 优先使用环境变量中的数据集目录
        if dataset_dir is None:
            dataset_dir = os.environ.get("ASTRO_DATASET_DIR", "dataset")
        
        self.dataset_dir = Path(dataset_dir)
        self.available_datasets: List[DatasetInfo] = []
        self._load_available_datasets()
    
    def _load_available_datasets(self):
        """加载所有可用的数据集"""
        if not self.dataset_dir.exists():
            print(f"⚠️ 数据集目录不存在: {self.dataset_dir}")
            return
        
        # 扫描数据集目录
        for dataset_path in self.dataset_dir.rglob("*.csv"):
            try:
                dataset_info = self._analyze_dataset(dataset_path)
                if dataset_info:
                    self.available_datasets.append(dataset_info)
            except Exception as e:
                print(f"❌ 分析数据集失败 {dataset_path}: {e}")
        
        print(f"📊 发现 {len(self.available_datasets)} 个数据集")
    
    def _analyze_dataset(self, file_path: Path) -> Optional[DatasetInfo]:
        """分析单个数据集文件"""
        try:
            # 读取数据集基本信息
            df = pd.read_csv(file_path, nrows=1000)  # 只读前1000行进行快速分析
            
            # 获取列名和数据类型
            columns = df.columns.tolist()
            data_types = df.dtypes.astype(str).to_dict()
            
            # 获取文件大小
            file_size = file_path.stat().st_size
            
            # 获取样本数据（前5行）
            sample_data = df.head(5).to_dict('records')
            
            # 生成描述
            description = self._generate_dataset_description(df, file_path)
            
            return DatasetInfo(
                name=file_path.stem,
                path=str(file_path),
                description=description,
                columns=columns,
                size=file_size,
                file_type="csv",
                sample_data=sample_data,
                data_types=data_types
            )
            
        except Exception as e:
            print(f"❌ 分析数据集失败 {file_path}: {e}")
            return None
    
    def _generate_dataset_description(self, df: pd.DataFrame, file_path: Path) -> str:
        """生成数据集描述"""
        try:
            # 基于文件名和内容生成描述
            filename = file_path.stem.lower()
            
            # 检查是否是天文学相关数据集
            if any(keyword in filename for keyword in ['astro', 'galaxy', 'star', 'sdss', 'cosmic']):
                if 'galaxy' in filename:
                    return "星系分类数据集，包含星系的形态学特征和分类标签"
                elif 'star' in filename:
                    return "恒星分类数据集，包含恒星的物理特征和类型信息"
                elif 'sdss' in filename:
                    return "SDSS (斯隆数字巡天) 数据集，包含天体的观测数据"
                else:
                    return "天文学数据集，包含天体的观测和分类信息"
            
            # 基于列名推断
            columns_str = ' '.join(df.columns).lower()
            if any(keyword in columns_str for keyword in ['magnitude', 'ra', 'dec', 'redshift', 'galaxy', 'star']):
                return "天文学数据集，包含天体的位置、亮度、红移等观测参数"
            
            # 通用描述
            return f"包含 {len(df.columns)} 个特征的数据集，共 {len(df)} 行数据"
            
        except Exception:
            return "数据集信息"
    
    def get_available_datasets(self) -> List[DatasetInfo]:
        """获取所有可用数据集"""
        return self.available_datasets
    
    def get_dataset_by_name(self, name: str) -> Optional[DatasetInfo]:
        """根据名称获取数据集"""
        for dataset in self.available_datasets:
            if dataset.name == name:
                return dataset
        return None
    
    def get_dataset_summary(self) -> str:
        """获取数据集摘要信息（用于LLM选择）"""
        if not self.available_datasets:
            return "没有可用的数据集"
        
        summary = "可用数据集列表：\n\n"
        for i, dataset in enumerate(self.available_datasets, 1):
            summary += f"{i}. **{dataset.name}**\n"
            summary += f"   - 描述: {dataset.description}\n"
            summary += f"   - 列数: {len(dataset.columns)}\n"
            summary += f"   - 文件大小: {self._format_file_size(dataset.size)}\n"
            summary += f"   - 主要列: {', '.join(dataset.columns[:5])}{'...' if len(dataset.columns) > 5 else ''}\n\n"
        
        return summary
    
    def get_detailed_dataset_info(self, dataset_name: str) -> Optional[str]:
        """获取数据集的详细信息"""
        dataset = self.get_dataset_by_name(dataset_name)
        if not dataset:
            return None
        
        info = f"**数据集: {dataset.name}**\n\n"
        info += f"**描述**: {dataset.description}\n\n"
        info += f"**文件路径**: {dataset.path}\n"
        info += f"**文件大小**: {self._format_file_size(dataset.size)}\n"
        info += f"**数据列数**: {len(dataset.columns)}\n\n"
        
        info += "**数据列详情**:\n"
        for col in dataset.columns:
            data_type = dataset.data_types.get(col, 'unknown')
            info += f"- {col} ({data_type})\n"
        
        if dataset.sample_data:
            info += "\n**样本数据** (前3行):\n"
            for i, row in enumerate(dataset.sample_data[:3]):
                info += f"行 {i+1}: {dict(list(row.items())[:3])}...\n"
        
        return info
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def suggest_dataset_for_requirement(self, user_requirement: str) -> Optional[DatasetInfo]:
        """根据用户需求建议最合适的数据集"""
        if not self.available_datasets:
            return None
        
        # 简单的关键词匹配
        requirement_lower = user_requirement.lower()
        
        # 检查是否明确提到了数据集名称
        for dataset in self.available_datasets:
            if dataset.name.lower() in requirement_lower:
                return dataset
        
        # 基于需求内容匹配
        for dataset in self.available_datasets:
            dataset_text = f"{dataset.name} {dataset.description} {' '.join(dataset.columns)}".lower()
            
            # 检查关键词匹配
            if any(keyword in requirement_lower for keyword in ['galaxy', '星系']) and 'galaxy' in dataset_text:
                return dataset
            elif any(keyword in requirement_lower for keyword in ['star', '恒星']) and 'star' in dataset_text:
                return dataset
            elif any(keyword in requirement_lower for keyword in ['sdss']) and 'sdss' in dataset_text:
                return dataset
        
        # 默认返回第一个数据集
        return self.available_datasets[0] if self.available_datasets else None
    
    def refresh_datasets(self):
        """刷新数据集列表"""
        self.available_datasets.clear()
        self._load_available_datasets()
