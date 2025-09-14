"""
GPU显存管理器
负责检测可用GPU、分配显存资源、监控显存使用
"""
import tensorflow as tf
import logging
import psutil
import subprocess
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GPUMemoryManager:
    """GPU显存管理器"""
    
    def __init__(self):
        self.available_gpus = []
        self.gpu_memory_info = {}
        self._detect_gpus()
    
    def _detect_gpus(self):
        """检测可用的GPU设备"""
        try:
            # 检测物理GPU
            physical_gpus = tf.config.list_physical_devices('GPU')
            logger.info(f"检测到 {len(physical_gpus)} 个物理GPU")
            
            for i, gpu in enumerate(physical_gpus):
                gpu_info = {
                    'device': gpu,
                    'index': i,
                    'memory_limit': None,
                    'memory_used': 0
                }
                self.available_gpus.append(gpu_info)
                
            # 获取GPU显存信息
            self._get_gpu_memory_info()
            
        except Exception as e:
            logger.error(f"GPU检测失败: {e}")
            self.available_gpus = []
    
    def _get_gpu_memory_info(self):
        """获取GPU显存信息"""
        try:
            # 使用nvidia-smi获取显存信息
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if i < len(self.available_gpus):
                        total, used = map(int, line.split(', '))
                        self.available_gpus[i]['memory_total'] = total
                        self.available_gpus[i]['memory_used'] = used
                        self.available_gpus[i]['memory_free'] = total - used
                        
        except Exception as e:
            logger.warning(f"无法获取GPU显存信息: {e}")
            # 设置默认值
            for gpu_info in self.available_gpus:
                gpu_info['memory_total'] = 8000  # 假设8GB显存
                gpu_info['memory_used'] = 0
                gpu_info['memory_free'] = 8000
    
    def allocate_gpu_memory(self, process_count: int) -> List[Dict]:
        """为多个进程分配GPU显存"""
        if not self.available_gpus:
            logger.warning("没有可用的GPU，将使用CPU")
            return []
        
        allocations = []
        gpu_count = len(self.available_gpus)
        
        logger.info(f"开始为 {process_count} 个进程分配GPU显存，可用GPU数量: {gpu_count}")
        
        if gpu_count == 1:
            # 单GPU情况：为每个进程分配显存比例
            gpu = self.available_gpus[0]
            total_memory = gpu.get('memory_total', 8000)  # 默认8GB
            free_memory = gpu.get('memory_free', total_memory)
            
            # 计算每个进程的显存分配
            # 保留10%的显存作为缓冲，剩余90%分配给进程
            available_memory = int(free_memory * 0.9)
            memory_per_process = available_memory // process_count
            
            # 确保每个进程至少有1GB显存
            min_memory = 1024  # 1GB
            memory_per_process = max(memory_per_process, min_memory)
            
            logger.info(f"单GPU显存分配: 总显存={total_memory}MB, 可用显存={available_memory}MB, "
                       f"每进程显存={memory_per_process}MB")
            
            for i in range(process_count):
                allocation = {
                    'gpu_index': 0,
                    'memory_limit': memory_per_process,
                    'memory_fraction': memory_per_process / total_memory,
                    'process_id': i
                }
                allocations.append(allocation)
                
        else:
            # 多GPU情况：优先每个进程使用不同的GPU
            if process_count <= gpu_count:
                # 进程数 <= GPU数：每个进程使用不同的GPU
                for i in range(process_count):
                    gpu = self.available_gpus[i]
                    total_memory = gpu.get('memory_total', 8000)
                    free_memory = gpu.get('memory_free', total_memory)
                    
                    # 为每个GPU保留10%显存作为缓冲
                    available_memory = int(free_memory * 0.9)
                    
                    allocation = {
                        'gpu_index': i,
                        'memory_limit': available_memory,
                        'memory_fraction': available_memory / total_memory,
                        'process_id': i
                    }
                    allocations.append(allocation)
                    
            else:
                # 进程数 > GPU数：部分进程需要共享GPU
                processes_per_gpu = process_count // gpu_count
                remaining_processes = process_count % gpu_count
                
                process_id = 0
                for gpu_idx in range(gpu_count):
                    gpu = self.available_gpus[gpu_idx]
                    total_memory = gpu.get('memory_total', 8000)
                    free_memory = gpu.get('memory_free', total_memory)
                    
                    # 计算这个GPU需要处理的进程数
                    gpu_process_count = processes_per_gpu
                    if gpu_idx < remaining_processes:
                        gpu_process_count += 1
                    
                    # 为这个GPU分配显存
                    available_memory = int(free_memory * 0.9)
                    memory_per_process = available_memory // gpu_process_count
                    memory_per_process = max(memory_per_process, 1024)  # 至少1GB
                    
                    for _ in range(gpu_process_count):
                        allocation = {
                            'gpu_index': gpu_idx,
                            'memory_limit': memory_per_process,
                            'memory_fraction': memory_per_process / total_memory,
                            'process_id': process_id
                        }
                        allocations.append(allocation)
                        process_id += 1
        
        logger.info(f"GPU显存分配完成，共 {len(allocations)} 个分配:")
        for allocation in allocations:
            logger.info(f"  进程 {allocation['process_id']}: GPU {allocation['gpu_index']}, "
                       f"显存限制 {allocation['memory_limit']}MB, "
                       f"显存比例 {allocation['memory_fraction']:.2%}")
        
        return allocations
    
    def setup_gpu_for_process(self, allocation: Dict):
        """为特定进程设置GPU配置"""
        try:
            gpu_index = allocation['gpu_index']
            memory_limit = allocation['memory_limit']
            
            # 如果没有GPU（gpu_index为-1），跳过GPU配置
            if gpu_index == -1:
                logger.info(f"进程 {allocation['process_id']} 使用CPU训练")
                return
            
            # 设置可见的GPU设备
            os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_index)
            
            # 配置TensorFlow GPU设置
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                gpu = gpus[0]  # 因为设置了CUDA_VISIBLE_DEVICES，只有一个GPU可见
                
                # 启用内存增长
                tf.config.experimental.set_memory_growth(gpu, True)
                
                # 设置显存限制
                if memory_limit:
                    tf.config.experimental.set_virtual_device_configuration(
                        gpu,
                        [tf.config.experimental.VirtualDeviceConfiguration(
                            memory_limit=memory_limit
                        )]
                    )
                
                logger.info(f"进程 {allocation['process_id']} GPU配置完成: "
                          f"GPU {gpu_index}, 显存限制 {memory_limit}MB")
            else:
                logger.warning(f"进程 {allocation['process_id']} 指定的GPU {gpu_index} 不可用，使用CPU")
                
        except Exception as e:
            logger.error(f"GPU配置失败: {e}")
            # 不抛出异常，允许使用CPU训练
            logger.info(f"进程 {allocation['process_id']} 将使用CPU训练")
    
    def get_gpu_status(self) -> Dict:
        """获取当前GPU状态"""
        status = {
            'total_gpus': len(self.available_gpus),
            'gpu_info': []
        }
        
        for gpu_info in self.available_gpus:
            status['gpu_info'].append({
                'index': gpu_info['index'],
                'memory_total': gpu_info.get('memory_total', 0),
                'memory_used': gpu_info.get('memory_used', 0),
                'memory_free': gpu_info.get('memory_free', 0)
            })
        
        return status
    
    def cleanup(self):
        """清理GPU资源"""
        try:
            # 清理TensorFlow会话
            tf.keras.backend.clear_session()
            logger.info("GPU资源清理完成")
        except Exception as e:
            logger.error(f"GPU资源清理失败: {e}")
