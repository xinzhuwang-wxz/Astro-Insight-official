"""
?????
?????????????????????????
"""
import os
import sys
import logging
import time
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from gpu_manager import GPUMemoryManager
from config_manager import ConfigManager
from process_monitor import ProcessMonitor
from output_manager import OutputManager

logger = logging.getLogger(__name__)

class ParallelMLExecutor:
    """??ML???"""
    
    def __init__(self, config_paths: List[str], working_dir: str = None, session_name: str = None):
        self.config_paths = config_paths
        self.working_dir = working_dir or os.getcwd()
        
        # ????????
        self.output_manager = OutputManager()
        self.session_dir = self.output_manager.create_session(session_name)
        
        # ?????
        self.gpu_manager = GPUMemoryManager()
        self.config_manager = ConfigManager(output_manager=self.output_manager)
        self.process_monitor = ProcessMonitor()
        
        # ????
        self.is_running = False
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        logger.info(f"??ML?????????????: {config_paths}")
        logger.info(f"????: {self.session_dir}")
    
    def run_parallel(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """??????ML????"""
        try:
            self.start_time = datetime.now()
            self.is_running = True
            
            logger.info("????ML????")
            
            # 1. ??GPU??
            gpu_status = self.gpu_manager.get_gpu_status()
            logger.info(f"GPU??: {gpu_status}")
            
            # 2. ??GPU??
            gpu_allocations = self.gpu_manager.allocate_gpu_memory(len(self.config_paths))
            logger.info(f"GPU??: {gpu_allocations}")
            
            # ????GPU???CPU??
            if not gpu_allocations:
                gpu_allocations = [
                    {'gpu_index': -1, 'memory_limit': None, 'memory_fraction': 1.0, 'process_id': i}
                    for i in range(len(self.config_paths))
                ]
                logger.info(f"??CPU??: {gpu_allocations}")
            
            # 3. ????????
            process_configs = self.config_manager.create_parallel_configs(
                self.config_paths, gpu_allocations
            )
            logger.info(f"??????: {process_configs}")
            
            # 3.5. ????????????configs?????debug?
            for i, process_config_path in enumerate(process_configs):
                try:
                    self.output_manager.save_config(process_config_path, i)
                except Exception as e:
                    logger.warning(f"???? {i} ??????: {e}")
            
            # 4. ??????
            self._start_parallel_processes(process_configs, gpu_allocations)
            
            # 5. ??????
            self._monitor_execution(timeout)
            
            # 6. ????
            results = self._collect_results()
            
            self.end_time = datetime.now()
            self.is_running = False
            
            logger.info("??ML??????")
            return results
            
        except Exception as e:
            logger.error(f"??????: {e}")
            self._cleanup()
            raise
        finally:
            self._cleanup()
    
    def _start_parallel_processes(self, process_configs: List[str], 
                                gpu_allocations: List[Dict]):
        """??????"""
        for i, (config_path, gpu_allocation) in enumerate(zip(process_configs, gpu_allocations)):
            try:
                # ????
                command = self._build_process_command(config_path, i)
                
                # ??????
                env_vars = self._build_environment_variables(gpu_allocation, i)
                
                # ????
                process = self.process_monitor.start_process(
                    process_id=i,
                    command=command,
                    working_dir=self.working_dir,
                    env_vars=env_vars
                )
                
                # ??????
                self.process_monitor.set_status_callback(i, self._process_status_callback)
                
                logger.info(f"?? {i} ?????????: {config_path}")
                
            except Exception as e:
                logger.error(f"???? {i} ??: {e}")
                raise
    
    def _build_process_command(self, config_path: str, process_id: int) -> List[str]:
        """??????"""
        # ?????????
        script_path = self._create_process_script(config_path, process_id)
        
        return [sys.executable, script_path]
    
    def _create_process_script(self, config_path: str, process_id: int) -> str:
        """??????????????"""
        script_content = f'''
import sys
import os
import logging
import yaml
import tensorflow as tf

# ??mcp_ml???Python??
current_dir = os.path.dirname(os.path.abspath(__file__))
# ???????????????src/mcp_ml??
mcp_ml_dir = os.path.join(current_dir, 'src', 'mcp_ml')
sys.path.insert(0, mcp_ml_dir)

from data_loading import download_data
from data_preprocessing import load_and_preprocess_data, create_dataset
from model_training import train_model
from result_analysis import evaluate_model
from gpu_manager import GPUMemoryManager

# ????
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - Process {process_id} - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("?? {process_id} ????")
        
        # ????
        with open('{config_path}', 'r') as file:
            config = yaml.safe_load(file)
        
        logger.info("?? {process_id} ??????")
        
        # ??GPU
        gpu_manager = GPUMemoryManager()
        gpu_allocation = config.get('process_info', dict()).get('gpu_allocation', dict())
        if gpu_allocation:
            gpu_manager.setup_gpu_for_process(gpu_allocation)
        
        # ??????
        logger.info("?? {process_id} ???????")
        train_df, val_df, test_df, label_encoder = load_and_preprocess_data(config)
        train_dataset = create_dataset(train_df, config, is_training=True)
        val_dataset = create_dataset(val_df, config, is_training=False)
        test_dataset = create_dataset(test_df, config, is_training=False)
        
        logger.info("?? {process_id} ??????")
        model, history = train_model(config)
        
        logger.info("?? {process_id} ??????")
        best_model = tf.keras.models.load_model(config['model_training']['checkpoint']['filepath'])
        
        # ???????
        output_manager = None
        if 'output_manager' in config.get('process_info', dict()):
            from output_manager import OutputManager
            output_manager = OutputManager()
            output_manager.session_dir = config['process_info']['output_manager']['session_dir']
            output_manager.subdirs = config['process_info']['output_manager']['subdirs']
        
        evaluate_model(best_model, history, test_dataset, label_encoder, config, output_manager, {process_id})
        
        logger.info("?? {process_id} ????")
        
    except Exception as e:
        logger.error("?? {process_id} ????: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        # ??????
        script_path = f"temp_script_process_{process_id}.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def _build_environment_variables(self, gpu_allocation: Dict, process_id: int) -> Dict[str, str]:
        """??????"""
        env_vars = {
            'PROCESS_ID': str(process_id),
            'CUDA_VISIBLE_DEVICES': str(gpu_allocation.get('gpu_index', 0)),
            'TF_CPP_MIN_LOG_LEVEL': '1',  # ??TensorFlow??
        }
        
        # ??GPU????
        memory_limit = gpu_allocation.get('memory_limit')
        if memory_limit:
            env_vars['TF_GPU_MEMORY_LIMIT'] = str(memory_limit)
        
        return env_vars
    
    def _process_status_callback(self, log_entry: Dict):
        """????????"""
        process_id = log_entry['process_id']
        message = log_entry['message']
        
        # ??????
        if 'epoch' in message.lower() and 'loss' in message.lower():
            logger.info(f"?? {process_id} ????: {message}")
        elif 'error' in message.lower() or 'failed' in message.lower():
            logger.error(f"?? {process_id} ??: {message}")
        elif 'completed' in message.lower() or 'finished' in message.lower():
            logger.info(f"?? {process_id} ??: {message}")
    
    def _monitor_execution(self, timeout: Optional[int] = None):
        """??????"""
        logger.info("??????????")
        
        try:
            # ????????
            results = self.process_monitor.wait_for_all_processes(timeout)
            
            # ????
            for process_id, return_code in results.items():
                if return_code == 0:
                    logger.info(f"?? {process_id} ????")
                else:
                    logger.error(f"?? {process_id} ??????: {return_code}")
            
            self.results = results
            
        except Exception as e:
            logger.error(f"????????: {e}")
            raise
    
    def _collect_results(self) -> Dict[str, Any]:
        """??????"""
        results = {
            'execution_summary': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration': str(self.end_time - self.start_time) if self.start_time and self.end_time else None,
                'total_processes': len(self.config_paths),
                'successful_processes': sum(1 for code in self.results.values() if code == 0),
                'failed_processes': sum(1 for code in self.results.values() if code != 0),
                'session_dir': self.session_dir
            },
            'process_results': self.results,
            'process_logs': self.process_monitor.get_all_logs(),
            'gpu_status': self.gpu_manager.get_gpu_status(),
            'session_info': self.output_manager.get_session_info()
        }
        
        # ???????????
        log_data = self.process_monitor.get_all_logs()
        log_file = self.output_manager.save_log(log_data, 'execution_log.json')
        results['log_file'] = log_file
        
        # ??????
        results_file = self.output_manager.save_result(results, 'execution_results.json')
        results['results_file'] = results_file
        
        # ????????
        summary_file = self.output_manager.create_summary_report()
        results['summary_file'] = summary_file
        
        return results
    
    def _cleanup(self):
        """????"""
        try:
            logger.info("??????")
            
            # ??????
            self.process_monitor.terminate_all_processes()
            
            # ???????????
            self._move_models_to_output()
            
            # ??????
            self._cleanup_temp_files()
            
            # ??????
            self.config_manager.cleanup_temp_configs()
            
            # ??GPU??
            self.gpu_manager.cleanup()
            
            # ???????
            self.process_monitor.cleanup()
            
            # ????????????
            self.output_manager.cleanup_temp_files()
            
            logger.info("??????")
            
        except Exception as e:
            logger.error(f"??????: {e}")
    
    def _move_models_to_output(self):
        """????????????"""
        try:
            # 1. ????????????
            for filename in os.listdir('.'):
                if filename.endswith('.keras') and 'process_' in filename:
                    # ????ID
                    parts = filename.split('_')
                    process_id = None
                    for i, part in enumerate(parts):
                        if part == 'process' and i + 1 < len(parts):
                            try:
                                process_id = int(parts[i + 1])
                                break
                            except ValueError:
                                continue
                    
                    # ???????
                    target_path = self.output_manager.save_model(filename, process_id)
                    logger.info(f"????????: {target_path}")
                    
                    # ?????
                    os.remove(filename)
            
            # 2. ??temp????????
            temp_dir = self.output_manager.get_path('temp')
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    if filename.endswith('.keras') and 'process_' in filename:
                        # ????ID
                        parts = filename.split('_')
                        process_id = None
                        for i, part in enumerate(parts):
                            if part == 'process' and i + 1 < len(parts):
                                try:
                                    process_id = int(parts[i + 1])
                                    break
                                except ValueError:
                                    continue
                        
                        # ?????
                        source_path = os.path.join(temp_dir, filename)
                        
                        # ???models??
                        target_path = self.output_manager.save_model(source_path, process_id)
                        logger.info(f"??????????: {target_path}")
                        
                        # ??????
                        os.remove(source_path)
                    
        except Exception as e:
            logger.error(f"????????: {e}")
    
    def _cleanup_temp_files(self):
        """??????"""
        try:
            # ????????
            for i in range(len(self.config_paths)):
                script_path = f"temp_script_process_{i}.py"
                if os.path.exists(script_path):
                    os.remove(script_path)
                    logger.info(f"??????: {script_path}")
        except Exception as e:
            logger.error(f"????????: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """????????"""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'process_status': self.process_monitor.get_all_process_status(),
            'gpu_status': self.gpu_manager.get_gpu_status()
        }
    
    def stop_execution(self):
        """????"""
        if self.is_running:
            logger.info("??????")
            self.process_monitor.terminate_all_processes()
            self.is_running = False
