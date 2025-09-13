# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import pandas as pd
from typing import List, Optional, Dict, Any
from pathlib import Path

from .types import DatasetInfo


class DatasetSelector:
    """数据集选择器 - 管理多个数据集的选择和信息获取"""
    
    def __init__(self, base_dataset_path: str = "dataset", base_description_path: str = "dataset/full_description"):
        self.base_dataset_path = Path(base_dataset_path)
        self.base_description_path = Path(base_description_path) 
        self.available_datasets: List[DatasetInfo] = []
        self._discover_datasets()
    
    def _discover_datasets(self) -> None:
        """自动发现可用的数据集"""
        self.available_datasets = []
        
        # 扫描description目录，找到所有.txt文件
        if self.base_description_path.exists():
            for desc_file in self.base_description_path.glob("*.txt"):
                dataset_info = self._parse_dataset_from_description(desc_file)
                if dataset_info:
                    self.available_datasets.append(dataset_info)
    
    def _parse_dataset_from_description(self, desc_path: Path) -> Optional[DatasetInfo]:
        """从描述文件解析数据集信息"""
        try:
            with open(desc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析数据集基本信息
            lines = content.split('\n')
            name = ""
            data_path = ""
            columns = []
            target_column = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('数据集：'):
                    name = line.replace('数据集：', '').strip()
                elif line.startswith('数据集路径'):
                    # 提取路径信息
                    if '"' in line:
                        data_path = line.split('"')[1]
                    elif 'dataset' in line.lower():
                        # 从描述中推断路径
                        data_path = self._infer_dataset_path(desc_path.stem)
                elif line.startswith('列名如下：') or '列名' in line:
                    # 开始解析列名
                    continue
                elif line.startswith('目标列：'):
                    # 解析目标列
                    continue
                elif ',' in line and not line.startswith('数据集') and not line.startswith('文件'):
                    # 这可能是列名行
                    potential_columns = [col.strip() for col in line.split(',') if col.strip()]
                    if potential_columns:
                        columns.extend(potential_columns)
            
            # 如果没有解析到路径，尝试推断
            if not data_path:
                data_path = self._infer_dataset_path(desc_path.stem)
            
            # 验证数据文件是否存在（尝试绝对路径和相对路径）
            actual_data_path = data_path
            if data_path and not os.path.exists(data_path):
                # 如果绝对路径不存在，尝试推断相对路径
                actual_data_path = self._infer_dataset_path(desc_path.stem)
            
            if actual_data_path and os.path.exists(actual_data_path):
                # 优先从实际文件获取列信息，而不是描述文件
                actual_columns = self._get_columns_from_file(actual_data_path)
                if actual_columns:
                    columns = actual_columns
                elif not columns:
                    columns = self._get_columns_from_file(actual_data_path)
                
                return DatasetInfo(
                    name=name or desc_path.stem,
                    path=actual_data_path,
                    description_path=str(desc_path),
                    description_content=content,
                    columns=columns,
                    target_column=target_column,
                    data_type=self._infer_data_type(actual_data_path)
                )
            
        except Exception as e:
            print(f"解析数据集描述文件出错 {desc_path}: {e}")
            
        return None
    
    def _infer_dataset_path(self, desc_name: str) -> str:
        """推断数据集文件路径"""
        # 常见的数据文件扩展名
        extensions = ['.csv', '.json', '.parquet', '.xlsx']
        
        # 在dataset目录下查找
        dataset_dir = self.base_dataset_path / "dataset"
        if dataset_dir.exists():
            # 首先尝试直接匹配
            for ext in extensions:
                potential_path = dataset_dir / f"{desc_name}{ext}"
                if potential_path.exists():
                    return str(potential_path)
                
                # 也尝试一些常见的变体
                for variant in [desc_name.lower(), desc_name.replace(' ', '_'), desc_name.replace(' ', '-')]:
                    potential_path = dataset_dir / f"{variant}{ext}"
                    if potential_path.exists():
                        return str(potential_path)
            
            # 如果直接匹配失败，搜索包含关键词的文件
            for file_path in dataset_dir.glob("*.csv"):
                file_name = file_path.stem.lower()
                desc_lower = desc_name.lower()
                
                # 检查是否包含关键词 - 改进的匹配逻辑
                keyword_mappings = {
                    'sdss': ['sdss', 'galaxy'],
                    'galaxy': ['sdss', 'galaxy'],
                    'star': ['star', '6_class', 'classification'],
                    'classification': ['star', 'class', '6_class'],
                    'predict': ['star', '6_class']
                }
                
                # 如果描述名包含某个关键词，优先匹配对应的文件
                for desc_keyword, file_keywords in keyword_mappings.items():
                    if desc_keyword in desc_lower:
                        for file_keyword in file_keywords:
                            if file_keyword in file_name:
                                return str(file_path)
                
                # 如果没有精确匹配，使用原来的逻辑
                basic_keywords = ['sdss', 'galaxy', 'star', 'classification', '6_class']
                if any(keyword in file_name for keyword in basic_keywords):
                    return str(file_path)
        
        # 默认返回csv路径（即使不存在）
        return str(self.base_dataset_path / "dataset" / f"{desc_name}.csv")
    
    def _get_columns_from_file(self, file_path: str) -> List[str]:
        """从数据文件获取列名"""
        try:
            if file_path.endswith('.csv'):
                # 尝试不同的读取方式
                try:
                    # 首先尝试标准读取
                    df = pd.read_csv(file_path, nrows=0)
                    if len(df.columns) > 1:
                        return list(df.columns)
                except:
                    pass
                
                # 如果标准读取失败或只有一列，尝试跳过第一行
                try:
                    df = pd.read_csv(file_path, skiprows=1, nrows=0)
                    if len(df.columns) > 1:
                        return list(df.columns)
                except:
                    pass
                
                # 最后尝试读取一行来推断
                try:
                    df = pd.read_csv(file_path, skiprows=1, nrows=1)
                    return list(df.columns)
                except:
                    pass
                    
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path, lines=True, nrows=1)
                return list(df.columns)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
                return list(df.columns)
        except Exception as e:
            print(f"读取文件列名出错 {file_path}: {e}")
        
        return []
    
    def _infer_data_type(self, file_path: str) -> str:
        """推断数据文件类型"""
        return Path(file_path).suffix.lower().replace('.', '')
    
    def get_available_datasets(self) -> List[DatasetInfo]:
        """获取所有可用数据集"""
        return self.available_datasets.copy()
    
    def select_dataset_by_name(self, name: str) -> Optional[DatasetInfo]:
        """根据名称选择数据集"""
        for dataset in self.available_datasets:
            if dataset["name"].lower() == name.lower():
                return dataset
        return None
    
    def select_dataset_by_index(self, index: int) -> Optional[DatasetInfo]:
        """根据索引选择数据集"""
        if 0 <= index < len(self.available_datasets):
            return self.available_datasets[index]
        return None
    
    def get_dataset_summary(self) -> str:
        """获取所有数据集的摘要信息"""
        if not self.available_datasets:
            return "未找到可用的数据集"
        
        summary = "可用数据集：\n"
        for i, dataset in enumerate(self.available_datasets):
            summary += f"{i+1}. {dataset['name']}\n"
            summary += f"   路径: {dataset['path']}\n"
            summary += f"   列数: {len(dataset['columns'])}\n"
            if dataset['columns']:
                summary += f"   主要列: {', '.join(dataset['columns'][:5])}{'...' if len(dataset['columns']) > 5 else ''}\n"
            summary += "\n"
        
        return summary
    
    def refresh_datasets(self) -> None:
        """刷新数据集列表"""
        self._discover_datasets()
