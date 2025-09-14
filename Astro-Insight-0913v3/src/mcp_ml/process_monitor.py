"""
进程监控器
负责监控子进程状态、收集训练日志、处理异常情况
"""
import subprocess
import threading
import time
import logging
import queue
import json
import os
from typing import Dict, List, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """进程监控器"""
    
    def __init__(self):
        self.processes = {}
        self.log_queues = {}
        self.monitor_threads = {}
        self.status_callbacks = {}
        self.running = False
    
    def start_process(self, process_id: int, command: List[str], 
                     working_dir: str = None, env_vars: Dict = None) -> subprocess.Popen:
        """启动子进程"""
        try:
            # 准备环境变量
            process_env = os.environ.copy()
            if env_vars:
                process_env.update(env_vars)
            
            # 创建日志队列
            self.log_queues[process_id] = queue.Queue()
            
            # 启动进程
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=working_dir,
                env=process_env
            )
            
            self.processes[process_id] = process
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=self._monitor_process,
                args=(process_id, process),
                daemon=True
            )
            monitor_thread.start()
            self.monitor_threads[process_id] = monitor_thread
            
            logger.info(f"进程 {process_id} 启动成功, PID: {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"启动进程 {process_id} 失败: {e}")
            raise
    
    def _monitor_process(self, process_id: int, process: subprocess.Popen):
        """监控单个进程"""
        log_queue = self.log_queues[process_id]
        
        try:
            while True:
                # 读取进程输出
                line = process.stdout.readline()
                if line:
                    # 添加时间戳和进程ID
                    timestamp = datetime.now().isoformat()
                    log_entry = {
                        'timestamp': timestamp,
                        'process_id': process_id,
                        'pid': process.pid,
                        'message': line.strip(),
                        'type': 'stdout'
                    }
                    log_queue.put(log_entry)
                    
                    # 调用状态回调
                    if process_id in self.status_callbacks:
                        self.status_callbacks[process_id](log_entry)
                
                # 检查进程是否结束
                if process.poll() is not None:
                    # 进程已结束，读取剩余输出
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        for line in remaining_output.split('\n'):
                            if line.strip():
                                timestamp = datetime.now().isoformat()
                                log_entry = {
                                    'timestamp': timestamp,
                                    'process_id': process_id,
                                    'pid': process.pid,
                                    'message': line.strip(),
                                    'type': 'stdout'
                                }
                                log_queue.put(log_entry)
                    
                    # 添加进程结束日志
                    return_code = process.returncode
                    timestamp = datetime.now().isoformat()
                    log_entry = {
                        'timestamp': timestamp,
                        'process_id': process_id,
                        'pid': process.pid,
                        'message': f"进程结束，返回码: {return_code}",
                        'type': 'process_end',
                        'return_code': return_code
                    }
                    log_queue.put(log_entry)
                    break
                
                time.sleep(0.1)  # 避免CPU占用过高
                
        except Exception as e:
            logger.error(f"监控进程 {process_id} 时出错: {e}")
            # 添加错误日志
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'process_id': process_id,
                'message': f"监控错误: {str(e)}",
                'type': 'error'
            }
            log_queue.put(log_entry)
    
    def set_status_callback(self, process_id: int, callback: Callable):
        """设置进程状态回调函数"""
        self.status_callbacks[process_id] = callback
    
    def get_process_logs(self, process_id: int, max_logs: int = 100) -> List[Dict]:
        """获取进程日志"""
        if process_id not in self.log_queues:
            return []
        
        log_queue = self.log_queues[process_id]
        logs = []
        
        try:
            while len(logs) < max_logs:
                try:
                    log_entry = log_queue.get_nowait()
                    logs.append(log_entry)
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(f"获取进程 {process_id} 日志失败: {e}")
        
        return logs
    
    def get_all_logs(self, max_logs_per_process: int = 50) -> Dict[int, List[Dict]]:
        """获取所有进程的日志"""
        all_logs = {}
        for process_id in self.processes.keys():
            all_logs[process_id] = self.get_process_logs(process_id, max_logs_per_process)
        return all_logs
    
    def get_process_status(self, process_id: int) -> Dict:
        """获取进程状态"""
        if process_id not in self.processes:
            return {'status': 'not_found'}
        
        process = self.processes[process_id]
        return {
            'process_id': process_id,
            'pid': process.pid,
            'status': 'running' if process.poll() is None else 'finished',
            'return_code': process.returncode,
            'log_count': self.log_queues[process_id].qsize() if process_id in self.log_queues else 0
        }
    
    def get_all_process_status(self) -> Dict[int, Dict]:
        """获取所有进程状态"""
        status = {}
        for process_id in self.processes.keys():
            status[process_id] = self.get_process_status(process_id)
        return status
    
    def terminate_process(self, process_id: int, timeout: int = 10):
        """终止进程"""
        if process_id not in self.processes:
            logger.warning(f"进程 {process_id} 不存在")
            return
        
        process = self.processes[process_id]
        
        try:
            # 尝试优雅终止
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=timeout)
                logger.info(f"进程 {process_id} 已优雅终止")
            except subprocess.TimeoutExpired:
                # 强制终止
                process.kill()
                process.wait()
                logger.warning(f"进程 {process_id} 被强制终止")
                
        except Exception as e:
            logger.error(f"终止进程 {process_id} 失败: {e}")
    
    def terminate_all_processes(self, timeout: int = 10):
        """终止所有进程"""
        for process_id in list(self.processes.keys()):
            self.terminate_process(process_id, timeout)
    
    def wait_for_all_processes(self, timeout: Optional[int] = None) -> Dict[int, int]:
        """等待所有进程完成"""
        results = {}
        
        for process_id, process in self.processes.items():
            try:
                return_code = process.wait(timeout=timeout)
                results[process_id] = return_code
                logger.info(f"进程 {process_id} 完成，返回码: {return_code}")
            except subprocess.TimeoutExpired:
                logger.warning(f"进程 {process_id} 超时")
                results[process_id] = -1
            except Exception as e:
                logger.error(f"等待进程 {process_id} 时出错: {e}")
                results[process_id] = -1
        
        return results
    
    def cleanup(self):
        """清理资源"""
        try:
            # 终止所有进程
            self.terminate_all_processes()
            
            # 清理日志队列
            self.log_queues.clear()
            
            # 清理进程字典
            self.processes.clear()
            
            # 清理监控线程
            self.monitor_threads.clear()
            
            # 清理回调函数
            self.status_callbacks.clear()
            
            logger.info("进程监控器清理完成")
            
        except Exception as e:
            logger.error(f"清理进程监控器失败: {e}")
    
    def save_logs_to_file(self, filepath: str):
        """保存所有日志到文件"""
        try:
            all_logs = self.get_all_logs()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"日志已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存日志失败: {e}")
