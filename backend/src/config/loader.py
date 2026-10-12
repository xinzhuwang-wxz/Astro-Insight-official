import yaml
import os
from typing import Dict, Any

def load_yaml_config(config_path: str = None) -> Dict[str, Any]:
    """加载YAML配置文件
    
    Args:
        config_path: 配置文件路径，默认为项目根目录下的conf.yaml
        
    Returns:
        配置字典
    """
    if config_path is None:
        # 默认配置文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        config_path = os.path.join(project_root, 'conf.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config if config is not None else {}
    except FileNotFoundError:
        print(f"配置文件未找到: {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"YAML解析错误: {e}")
        return {}
    except Exception as e:
        print(f"加载配置文件时发生错误: {e}")
        return {}