"""
输出管理器
负责创建带时间戳的output文件夹结构，管理模型、日志、图片等输出文件
"""
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class OutputManager:
    """输出管理器"""
    
    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = base_output_dir
        self.session_id = None
        self.session_dir = None
        self.subdirs = {}
        
    def create_session(self, session_name: str = None) -> str:
        """创建新的会话目录"""
        try:
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 创建会话ID
            if session_name:
                self.session_id = f"{session_name}_{timestamp}"
            else:
                self.session_id = f"parallel_ml_{timestamp}"
            
            # 创建会话目录
            self.session_dir = os.path.join(self.base_output_dir, self.session_id)
            os.makedirs(self.session_dir, exist_ok=True)
            
            # 创建子目录
            self._create_subdirs()
            
            logger.info(f"创建会话目录: {self.session_dir}")
            return self.session_dir
            
        except Exception as e:
            logger.error(f"创建会话目录失败: {e}")
            raise
    
    def _create_subdirs(self):
        """创建子目录结构"""
        subdirs = {
            'models': 'models',           # 模型文件
            'logs': 'logs',              # 日志文件
            'images': 'images',          # 图片文件
            'configs': 'configs',        # 配置文件
            'results': 'results',        # 结果文件
            'temp': 'temp'               # 临时文件
        }
        
        for key, dirname in subdirs.items():
            subdir_path = os.path.join(self.session_dir, dirname)
            os.makedirs(subdir_path, exist_ok=True)
            self.subdirs[key] = subdir_path
            logger.info(f"创建子目录: {subdir_path}")
    
    def get_path(self, subdir: str, filename: str = None) -> str:
        """获取子目录路径或文件路径"""
        if subdir not in self.subdirs:
            raise ValueError(f"未知的子目录: {subdir}")
        
        if filename:
            return os.path.join(self.subdirs[subdir], filename)
        else:
            return self.subdirs[subdir]
    
    def save_model(self, model_path: str, process_id: int = None) -> str:
        """保存模型文件到models目录"""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
            # 生成新的文件名
            original_name = os.path.basename(model_path)
            name, ext = os.path.splitext(original_name)
            
            if process_id is not None:
                new_name = f"model_process_{process_id}_{name}{ext}"
            else:
                new_name = f"{name}{ext}"
            
            # 目标路径
            target_path = self.get_path('models', new_name)
            
            # 复制文件
            shutil.copy2(model_path, target_path)
            
            logger.info(f"模型文件已保存: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"保存模型文件失败: {e}")
            raise
    
    def save_log(self, log_data: Dict, filename: str = None) -> str:
        """保存日志文件到logs目录"""
        try:
            import json
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"execution_log_{timestamp}.json"
            
            target_path = self.get_path('logs', filename)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"日志文件已保存: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"保存日志文件失败: {e}")
            raise
    
    def save_config(self, config_path: str, process_id: int = None) -> str:
        """保存配置文件到configs目录"""
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
            # 生成新的文件名
            original_name = os.path.basename(config_path)
            
            if process_id is not None:
                name, ext = os.path.splitext(original_name)
                new_name = f"config_process_{process_id}_{name}{ext}"
            else:
                new_name = original_name
            
            # 目标路径
            target_path = self.get_path('configs', new_name)
            
            # 复制文件
            shutil.copy2(config_path, target_path)
            
            logger.info(f"配置文件已保存: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def save_image(self, image_path: str, process_id: int = None, image_type: str = "plot") -> str:
        """保存图片文件到images目录"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 生成新的文件名
            original_name = os.path.basename(image_path)
            name, ext = os.path.splitext(original_name)
            
            if process_id is not None:
                new_name = f"{image_type}_process_{process_id}_{name}{ext}"
            else:
                new_name = f"{image_type}_{name}{ext}"
            
            # 目标路径
            target_path = self.get_path('images', new_name)
            
            # 复制文件
            shutil.copy2(image_path, target_path)
            
            logger.info(f"图片文件已保存: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"保存图片文件失败: {e}")
            raise
    
    def save_result(self, result_data: Dict, filename: str = None) -> str:
        """保存结果文件到results目录"""
        try:
            import json
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.json"
            
            target_path = self.get_path('results', filename)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果文件已保存: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"保存结果文件失败: {e}")
            raise
    
    def get_session_info(self) -> Dict:
        """获取会话信息"""
        return {
            'session_id': self.session_id,
            'session_dir': self.session_dir,
            'subdirs': self.subdirs,
            'created_at': datetime.now().isoformat()
        }
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            temp_dir = self.get_path('temp')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
                logger.info("临时文件清理完成")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
    
    def create_summary_report(self) -> str:
        """创建会话摘要报告"""
        try:
            summary = {
                'session_info': self.get_session_info(),
                'files': self._scan_files(),
                'created_at': datetime.now().isoformat()
            }
            
            report_path = self.get_path('results', 'session_summary.json')
            self.save_result(summary, 'session_summary.json')
            
            logger.info(f"会话摘要报告已创建: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"创建摘要报告失败: {e}")
            raise
    
    def _scan_files(self) -> Dict:
        """扫描会话目录中的文件"""
        files = {}
        
        for subdir_name, subdir_path in self.subdirs.items():
            if os.path.exists(subdir_path):
                files[subdir_name] = []
                for filename in os.listdir(subdir_path):
                    file_path = os.path.join(subdir_path, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        files[subdir_name].append({
                            'name': filename,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2)
                        })
        
        return files
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.session_dir and os.path.exists(self.session_dir):
                logger.info(f"会话目录保留: {self.session_dir}")
                logger.info("如需清理，请手动删除会话目录")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")
