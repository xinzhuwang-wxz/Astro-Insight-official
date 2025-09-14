#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量管理模块
统一管理所有环境变量和API密钥
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EnvManager:
    """环境变量管理器"""
    
    def __init__(self, env_file_path: Optional[str] = None):
        """
        初始化环境变量管理器
        
        Args:
            env_file_path: .env文件路径，默认为项目根目录的.env
        """
        self.env_file_path = env_file_path or self._find_env_file()
        self._load_env_file()
    
    def _find_env_file(self) -> Optional[str]:
        """查找.env文件"""
        current_dir = Path(__file__).parent.parent.parent
        env_file = current_dir / ".env"
        return str(env_file) if env_file.exists() else None
    
    def _load_env_file(self):
        """加载.env文件"""
        if self.env_file_path and os.path.exists(self.env_file_path):
            try:
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                logger.info(f"已加载环境变量文件: {self.env_file_path}")
            except Exception as e:
                logger.warning(f"加载环境变量文件失败: {e}")
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        获取环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            required: 是否必需，如果为True且不存在则抛出异常
            
        Returns:
            环境变量值
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(f"必需的环境变量 {key} 未设置")
        
        return value
    
    def get_api_key(self, service: str) -> str:
        """
        获取API密钥
        
        Args:
            service: 服务名称 (tavily, openai, deepseek等)
            
        Returns:
            API密钥
        """
        key_map = {
            'tavily': 'TAVILY_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'ollama': 'OLLAMA_API_KEY',
        }
        
        env_key = key_map.get(service.lower())
        if not env_key:
            raise ValueError(f"不支持的服务: {service}")
        
        return self.get(env_key, required=True)
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            'type': self.get('DB_TYPE', 'sqlite'),
            'host': self.get('DB_HOST', 'localhost'),
            'port': self.get('DB_PORT', '5432'),
            'name': self.get('DB_NAME', 'astro_insight.db'),
            'user': self.get('DB_USER', ''),
            'password': self.get('DB_PASSWORD', ''),
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return {
            'provider': self.get('LLM_PROVIDER', 'ollama'),
            'model': self.get('LLM_MODEL', 'qwen2.5:7b'),
            'api_key': self.get('LLM_API_KEY', 'ollama'),
            'base_url': self.get('LLM_BASE_URL', 'http://localhost:11434/v1'),
        }
    
    def get_search_config(self) -> Dict[str, Any]:
        """获取搜索配置"""
        # 解析允许的域名列表
        allowed_domains = self.get('SEARCH_ALLOWED_DOMAINS', '')
        allowed_domains_list = [d.strip() for d in allowed_domains.split(',') if d.strip()] if allowed_domains else []
        
        # 解析禁止的域名列表
        blocked_domains = self.get('SEARCH_BLOCKED_DOMAINS', '')
        blocked_domains_list = [d.strip() for d in blocked_domains.split(',') if d.strip()] if blocked_domains else []
        
        return {
            'provider': self.get('SEARCH_PROVIDER', 'tavily'),
            'api_key': self.get('TAVILY_API_KEY'),
            'base_url': self.get('SEARCH_BASE_URL', 'https://api.tavily.com'),
            'max_results': int(self.get('SEARCH_MAX_RESULTS', '5')),
            'allowed_domains': allowed_domains_list,
            'blocked_domains': blocked_domains_list,
            'safe_content': self.get('SEARCH_SAFE_CONTENT', 'true').lower() == 'true',
        }
    
    
    def validate_required_keys(self) -> bool:
        """验证必需的环境变量"""
        required_keys = [
            'TAVILY_API_KEY',  # 搜索功能必需
        ]
        
        missing_keys = []
        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            logger.warning(f"缺少必需的环境变量: {', '.join(missing_keys)}")
            return False
        
        return True
    
    def print_config_status(self):
        """打印配置状态"""
        print("\n🔧 环境变量配置状态:")
        print(f"  .env文件: {'✅ 已加载' if self.env_file_path else '❌ 未找到'}")
        
        # 检查关键配置
        configs = {
            'Tavily搜索': self.get('TAVILY_API_KEY'),
            'LLM服务': self.get('LLM_PROVIDER', 'ollama'),
        }
        
        for name, value in configs.items():
            status = "✅ 已配置" if value else "❌ 未配置"
            print(f"  {name}: {status}")


# 全局环境变量管理器实例
env_manager = EnvManager()


def get_env(key: str, default: Any = None, required: bool = False) -> Any:
    """便捷函数：获取环境变量"""
    return env_manager.get(key, default, required)


def get_api_key(service: str) -> str:
    """便捷函数：获取API密钥"""
    return env_manager.get_api_key(service)


def validate_environment() -> bool:
    """便捷函数：验证环境配置"""
    return env_manager.validate_required_keys()


