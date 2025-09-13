#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的配置管理模块
提供环境变量配置、配置验证和多环境支持
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
import base64


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "sqlite"
    host: Optional[str] = None
    port: Optional[int] = None
    name: str = "astro_insight.db"
    user: Optional[str] = None
    password: Optional[str] = None
    connection_pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    api_key: str = ""
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    max_retries: int = 3
    timeout: int = 30
    verify_ssl: bool = True


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = ""
    encryption_key: Optional[str] = None
    jwt_secret: str = ""
    jwt_expiry: int = 3600
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration: int = 300


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class CacheConfig:
    """缓存配置"""
    type: str = "memory"  # memory, redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    default_ttl: int = 3600
    max_memory: str = "100mb"


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    max_connections: int = 1000
    keep_alive_timeout: int = 5
    max_request_size: int = 16777216  # 16MB


@dataclass
class AstroConfig:
    """Astro-Insight主配置"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    
    # 环境相关
    environment: str = "development"
    debug: bool = False
    
    def __post_init__(self):
        """配置后处理"""
        self._load_from_env()
        self._validate_config()
        self._setup_encryption()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 数据库配置
        self.database.type = os.getenv("DB_TYPE", self.database.type)
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", self.database.port or 0)) or None
        self.database.name = os.getenv("DB_NAME", self.database.name)
        self.database.user = os.getenv("DB_USER", self.database.user)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)
        
        # LLM配置
        self.llm.provider = os.getenv("LLM_PROVIDER", self.llm.provider)
        self.llm.model = os.getenv("LLM_MODEL", self.llm.model)
        self.llm.api_key = os.getenv("LLM_API_KEY", self.llm.api_key)
        self.llm.base_url = os.getenv("LLM_BASE_URL", self.llm.base_url)
        
        # 安全配置
        self.security.secret_key = os.getenv("SECRET_KEY", self.security.secret_key)
        self.security.encryption_key = os.getenv("ENCRYPTION_KEY", self.security.encryption_key)
        self.security.jwt_secret = os.getenv("JWT_SECRET", self.security.jwt_secret)
        
        # 服务器配置
        self.server.host = os.getenv("SERVER_HOST", self.server.host)
        self.server.port = int(os.getenv("SERVER_PORT", self.server.port))
        self.server.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # 环境配置
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def _validate_config(self):
        """验证配置"""
        errors = []
        
        # 验证必需字段
        if not self.llm.api_key:
            errors.append("LLM API key is required")
        
        if not self.security.secret_key:
            errors.append("Secret key is required")
        
        # 验证数据库配置
        if self.database.type == "postgresql":
            if not self.database.host or not self.database.user:
                errors.append("PostgreSQL requires host and user")
        
        # 验证端口范围
        if not (1 <= self.server.port <= 65535):
            errors.append("Server port must be between 1 and 65535")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _setup_encryption(self):
        """设置加密"""
        if not self.security.encryption_key:
            # 生成新的加密密钥
            self.security.encryption_key = Fernet.generate_key().decode()
            self._save_encryption_key()
    
    def _save_encryption_key(self):
        """保存加密密钥到环境变量文件"""
        env_file = Path(".env")
        if not env_file.exists():
            env_file.write_text(f"ENCRYPTION_KEY={self.security.encryption_key}\n")
    
    def encrypt_value(self, value: str) -> str:
        """加密值"""
        if not self.security.encryption_key:
            return value
        
        fernet = Fernet(self.security.encryption_key.encode())
        return fernet.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """解密值"""
        if not self.security.encryption_key:
            return encrypted_value
        
        try:
            fernet = Fernet(self.security.encryption_key.encode())
            return fernet.decrypt(encrypted_value.encode()).decode()
        except Exception:
            return encrypted_value


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "conf.yaml"
        self.config: Optional[AstroConfig] = None
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> AstroConfig:
        """加载配置"""
        if self.config is not None:
            return self.config
        
        # 从YAML文件加载
        yaml_config = self._load_yaml_config()
        
        # 创建配置对象
        self.config = AstroConfig()
        
        # 应用YAML配置
        if yaml_config:
            self._apply_yaml_config(yaml_config)
        
        # 验证配置
        self.config._validate_config()
        
        self.logger.info(f"Configuration loaded from {self.config_path}")
        return self.config
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            self.logger.warning(f"Configuration file {self.config_path} not found, using defaults")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.logger.error(f"Failed to load configuration file: {e}")
            return {}
    
    def _apply_yaml_config(self, yaml_config: Dict[str, Any]):
        """应用YAML配置到配置对象"""
        # 数据库配置
        if "database" in yaml_config:
            db_config = yaml_config["database"]
            self.config.database = DatabaseConfig(**db_config)
        
        # LLM配置
        if "llm" in yaml_config:
            llm_config = yaml_config["llm"]
            self.config.llm = LLMConfig(**llm_config)
        
        # 安全配置
        if "security" in yaml_config:
            security_config = yaml_config["security"]
            self.config.security = SecurityConfig(**security_config)
        
        # 日志配置
        if "logging" in yaml_config:
            logging_config = yaml_config["logging"]
            self.config.logging = LoggingConfig(**logging_config)
        
        # 缓存配置
        if "cache" in yaml_config:
            cache_config = yaml_config["cache"]
            self.config.cache = CacheConfig(**cache_config)
        
        # 服务器配置
        if "server" in yaml_config:
            server_config = yaml_config["server"]
            self.config.server = ServerConfig(**server_config)
    
    def save_config(self, config: AstroConfig, path: Optional[str] = None):
        """保存配置到文件"""
        save_path = path or self.config_path
        
        config_dict = {
            "database": {
                "type": config.database.type,
                "host": config.database.host,
                "port": config.database.port,
                "name": config.database.name,
                "user": config.database.user,
                "connection_pool_size": config.database.connection_pool_size,
                "max_overflow": config.database.max_overflow,
                "pool_timeout": config.database.pool_timeout,
                "pool_recycle": config.database.pool_recycle,
            },
            "llm": {
                "provider": config.llm.provider,
                "model": config.llm.model,
                "base_url": config.llm.base_url,
                "max_tokens": config.llm.max_tokens,
                "temperature": config.llm.temperature,
                "max_retries": config.llm.max_retries,
                "timeout": config.llm.timeout,
                "verify_ssl": config.llm.verify_ssl,
            },
            "security": {
                "jwt_expiry": config.security.jwt_expiry,
                "password_min_length": config.security.password_min_length,
                "max_login_attempts": config.security.max_login_attempts,
                "lockout_duration": config.security.lockout_duration,
            },
            "logging": {
                "level": config.logging.level,
                "format": config.logging.format,
                "file_path": config.logging.file_path,
                "max_file_size": config.logging.max_file_size,
                "backup_count": config.logging.backup_count,
                "console_output": config.logging.console_output,
            },
            "cache": {
                "type": config.cache.type,
                "redis_host": config.cache.redis_host,
                "redis_port": config.cache.redis_port,
                "redis_db": config.cache.redis_db,
                "default_ttl": config.cache.default_ttl,
                "max_memory": config.cache.max_memory,
            },
            "server": {
                "host": config.server.host,
                "port": config.server.port,
                "debug": config.server.debug,
                "workers": config.server.workers,
                "max_connections": config.server.max_connections,
                "keep_alive_timeout": config.server.keep_alive_timeout,
                "max_request_size": config.server.max_request_size,
            },
            "environment": config.environment,
            "debug": config.debug,
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_config(self) -> AstroConfig:
        """获取配置"""
        if self.config is None:
            return self.load_config()
        return self.config
    
    def reload_config(self) -> AstroConfig:
        """重新加载配置"""
        self.config = None
        return self.load_config()


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(config_path: Optional[str] = None) -> AstroConfig:
    """获取配置"""
    manager = get_config_manager(config_path)
    return manager.get_config()


def reload_config(config_path: Optional[str] = None) -> AstroConfig:
    """重新加载配置"""
    manager = get_config_manager(config_path)
    return manager.reload_config()


if __name__ == "__main__":
    # 测试配置管理
    config = get_config()
    print("配置加载成功:")
    print(f"环境: {config.environment}")
    print(f"调试模式: {config.debug}")
    print(f"服务器端口: {config.server.port}")
    print(f"LLM提供商: {config.llm.provider}")
    print(f"数据库类型: {config.database.type}")
