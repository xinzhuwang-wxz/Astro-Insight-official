#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强配置模块测试
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.enhanced_config import (
    AstroConfig, DatabaseConfig, LLMConfig, SecurityConfig,
    LoggingConfig, CacheConfig, ServerConfig, ConfigManager,
    get_config, get_config_manager
)


class TestDatabaseConfig:
    """测试DatabaseConfig类"""
    
    def test_database_config_defaults(self):
        """测试数据库配置默认值"""
        config = DatabaseConfig()
        
        assert config.type == "sqlite"
        assert config.name == "astro_insight.db"
        assert config.connection_pool_size == 10
        assert config.max_overflow == 20


class TestLLMConfig:
    """测试LLMConfig类"""
    
    def test_llm_config_defaults(self):
        """测试LLM配置默认值"""
        config = LLMConfig()
        
        assert config.provider == "openai"
        assert config.model == "gpt-3.5-turbo"
        assert config.max_tokens == 4000
        assert config.temperature == 0.7
        assert config.max_retries == 3


class TestSecurityConfig:
    """测试SecurityConfig类"""
    
    def test_security_config_defaults(self):
        """测试安全配置默认值"""
        config = SecurityConfig()
        
        assert config.jwt_expiry == 3600
        assert config.password_min_length == 8
        assert config.max_login_attempts == 5
        assert config.lockout_duration == 300


class TestAstroConfig:
    """测试AstroConfig类"""
    
    def test_astro_config_creation(self):
        """测试AstroConfig创建"""
        config = AstroConfig()
        
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.cache, CacheConfig)
        assert isinstance(config.server, ServerConfig)
    
    @patch.dict(os.environ, {
        'DB_TYPE': 'postgresql',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'LLM_PROVIDER': 'openai',
        'LLM_API_KEY': 'test_key',
        'SECRET_KEY': 'test_secret'
    })
    def test_load_from_env(self):
        """测试从环境变量加载配置"""
        config = AstroConfig()
        
        assert config.database.type == "postgresql"
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.database.name == "test_db"
        assert config.llm.provider == "openai"
        assert config.llm.api_key == "test_key"
        assert config.security.secret_key == "test_secret"
    
    def test_validate_config_valid(self):
        """测试有效配置验证"""
        config = AstroConfig()
        config.llm.api_key = "test_key"
        config.security.secret_key = "test_secret"
        
        # 应该不抛出异常
        config._validate_config()
    
    def test_validate_config_invalid(self):
        """测试无效配置验证"""
        config = AstroConfig()
        # 不设置必需的API key和secret key
        
        with pytest.raises(ValueError) as exc_info:
            config._validate_config()
        
        assert "LLM API key is required" in str(exc_info.value)
        assert "Secret key is required" in str(exc_info.value)
    
    def test_encrypt_decrypt_value(self):
        """测试值加密和解密"""
        config = AstroConfig()
        config.security.secret_key = "test_secret"
        config._setup_encryption()
        
        original_value = "sensitive_data"
        encrypted_value = config.encrypt_value(original_value)
        decrypted_value = config.decrypt_value(encrypted_value)
        
        assert encrypted_value != original_value
        assert decrypted_value == original_value


class TestConfigManager:
    """测试ConfigManager类"""
    
    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
    
    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_creation(self):
        """测试ConfigManager创建"""
        manager = ConfigManager(self.config_file)
        
        assert manager.config_path == self.config_file
        assert manager.config is None
    
    def test_load_config_from_yaml(self):
        """测试从YAML文件加载配置"""
        yaml_content = """
database:
  type: postgresql
  host: localhost
  port: 5432
  name: test_db

llm:
  provider: openai
  model: gpt-4
  api_key: test_key

security:
  secret_key: test_secret
"""
        
        with open(self.config_file, 'w') as f:
            f.write(yaml_content)
        
        manager = ConfigManager(self.config_file)
        config = manager.load_config()
        
        assert config.database.type == "postgresql"
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.database.name == "test_db"
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"
        assert config.llm.api_key == "test_key"
        assert config.security.secret_key == "test_secret"
    
    def test_load_config_missing_file(self):
        """测试加载不存在的配置文件"""
        manager = ConfigManager("nonexistent.yaml")
        config = manager.load_config()
        
        # 应该使用默认配置
        assert config.database.type == "sqlite"
        assert config.llm.provider == "openai"
    
    def test_save_config(self):
        """测试保存配置"""
        manager = ConfigManager(self.config_file)
        config = manager.load_config()
        
        # 修改配置
        config.database.type = "postgresql"
        config.llm.model = "gpt-4"
        
        # 保存配置
        manager.save_config(config)
        
        # 重新加载配置验证
        new_manager = ConfigManager(self.config_file)
        new_config = new_manager.load_config()
        
        assert new_config.database.type == "postgresql"
        assert new_config.llm.model == "gpt-4"
    
    def test_reload_config(self):
        """测试重新加载配置"""
        manager = ConfigManager(self.config_file)
        config1 = manager.load_config()
        
        # 修改配置文件
        yaml_content = """
database:
  type: postgresql
  host: localhost
  port: 5432
  name: test_db

llm:
  provider: openai
  model: gpt-4
  api_key: test_key

security:
  secret_key: test_secret
"""
        
        with open(self.config_file, 'w') as f:
            f.write(yaml_content)
        
        config2 = manager.reload_config()
        
        assert config2.database.type == "postgresql"
        assert config2.llm.model == "gpt-4"


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_get_config_manager(self):
        """测试get_config_manager便捷函数"""
        manager = get_config_manager("test_config.yaml")
        
        assert isinstance(manager, ConfigManager)
        assert manager.config_path == "test_config.yaml"
    
    def test_get_config(self):
        """测试get_config便捷函数"""
        with patch.dict(os.environ, {
            'LLM_API_KEY': 'test_key',
            'SECRET_KEY': 'test_secret'
        }):
            config = get_config()
            
            assert isinstance(config, AstroConfig)
            assert config.llm.api_key == "test_key"
            assert config.security.secret_key == "test_secret"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
