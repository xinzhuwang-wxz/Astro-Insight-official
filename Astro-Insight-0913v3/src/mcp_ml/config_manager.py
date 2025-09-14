"""
配置管理器
负责动态修改配置文件、为每个进程生成独立配置、处理模型保存路径冲突
"""
import yaml
import os
import shutil
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, base_config_dir: str = "config", output_manager=None):
        self.base_config_dir = base_config_dir
        self.output_manager = output_manager
        self.temp_config_dir = "temp_configs"
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self):
        """确保临时配置目录存在"""
        if not os.path.exists(self.temp_config_dir):
            os.makedirs(self.temp_config_dir)
            logger.info(f"创建临时配置目录: {self.temp_config_dir}")
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"成功加载配置文件: {config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败 {config_path}: {e}")
            raise
    
    def create_process_config(self, base_config_path: str, process_id: int, 
                            gpu_allocation: Dict, batch_size_scale: float = 1.0) -> str:
        """为特定进程创建独立的配置文件，只修改路径，保持原始格式"""
        try:
            # 生成时间戳和进程标识
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            process_suffix = f"_process_{process_id}_{timestamp}"
            
            # 生成新的配置文件路径
            base_name = os.path.basename(base_config_path).replace('.yaml', '')
            new_config_path = os.path.join(
                self.temp_config_dir, 
                f"{base_name}{process_suffix}.yaml"
            )
            
            # 直接复制原始配置文件内容，只修改路径
            self._copy_and_modify_paths(base_config_path, new_config_path, process_suffix)
            
            logger.info(f"为进程 {process_id} 创建配置文件: {new_config_path}")
            return new_config_path
            
        except Exception as e:
            logger.error(f"创建进程配置失败: {e}")
            raise
    
    def _copy_and_modify_paths(self, source_path: str, target_path: str, process_suffix: str):
        """复制配置文件并只修改路径，保持原始格式"""
        try:
            # 读取原始配置文件内容
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 只修改模型保存路径，保持其他格式不变
            modified_content = content
            
            # 修改checkpoint路径
            if "filepath: 'best_model.keras'" in modified_content:
                modified_content = modified_content.replace(
                    "filepath: 'best_model.keras'",
                    f"filepath: 'best_model{process_suffix}.keras'"
                )
            
            # 修改result_analysis中的模型路径
            if "model_path: 'best_model.keras'" in modified_content:
                modified_content = modified_content.replace(
                    "model_path: 'best_model.keras'",
                    f"model_path: 'best_model{process_suffix}.keras'"
                )
            
            # 写入新文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
        except Exception as e:
            logger.error(f"复制和修改配置文件失败: {e}")
            raise
    
    
    def create_parallel_configs(self, config_paths: List[str], 
                              gpu_allocations: List[Dict]) -> List[str]:
        """为多个进程创建并行配置文件，只修改路径"""
        process_configs = []
        
        for i, (config_path, gpu_allocation) in enumerate(zip(config_paths, gpu_allocations)):
            # 只修改路径，保持原始配置内容不变
            process_config = self.create_process_config(
                config_path, i, gpu_allocation, 1.0  # 不再调整batch_size
            )
            process_configs.append(process_config)
        
        logger.info(f"创建了 {len(process_configs)} 个并行配置文件")
        return process_configs
    
    def cleanup_temp_configs(self):
        """清理临时配置文件"""
        try:
            if os.path.exists(self.temp_config_dir):
                shutil.rmtree(self.temp_config_dir)
                logger.info("临时配置文件清理完成")
        except Exception as e:
            logger.error(f"清理临时配置文件失败: {e}")
    
    def get_config_summary(self, config_paths: List[str]) -> Dict:
        """获取配置文件摘要信息"""
        summary = {
            'total_configs': len(config_paths),
            'config_details': []
        }
        
        for i, config_path in enumerate(config_paths):
            try:
                config = self.load_config(config_path)
                detail = {
                    'index': i,
                    'path': config_path,
                    'batch_size': config.get('data_preprocessing', {}).get('batch_size', 'N/A'),
                    'epochs': config.get('model_training', {}).get('epochs', 'N/A'),
                    'model_path': config.get('model_training', {}).get('checkpoint', {}).get('filepath', 'N/A')
                }
                summary['config_details'].append(detail)
            except Exception as e:
                logger.error(f"获取配置摘要失败 {config_path}: {e}")
        
        return summary
