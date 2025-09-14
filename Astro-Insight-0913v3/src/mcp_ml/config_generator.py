"""
配置生成器模块
使用LLM通过自然语言描述生成ML训练配置文件
"""
import os
import sys
import yaml
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from src.llms.llm import get_llm_by_type

logger = logging.getLogger(__name__)

class ConfigGenerator:
    """ML训练配置生成器"""
    
    def __init__(self):
        """初始化配置生成器"""
        self.llm = None
        self._init_llm()
        
    def _init_llm(self):
        """初始化LLM"""
        try:
            self.llm = get_llm_by_type("basic")
            logger.info("LLM初始化成功")
        except Exception as e:
            logger.error(f"LLM初始化失败: {e}")
            self.llm = None
    
    
    def generate_config(self, description: str, config_name: str = None) -> str:
        """
        根据自然语言描述生成ML训练配置
        
        Args:
            description: 自然语言描述，描述想要的ML训练配置
            config_name: 配置名称，用于生成文件名
            
        Returns:
            str: 生成的配置文本
        """
        if not self.llm:
            raise RuntimeError("LLM未初始化，无法生成配置")
        
        try:
            # 构建prompt
            prompt = self._build_generation_prompt(description)
            
            # 调用LLM生成配置
            response = self.llm.invoke(prompt)
            config_text = response.content.strip()
            
            # 清理文本，移除可能的markdown标记
            config_text = config_text.strip()
            if config_text.startswith('```yaml'):
                config_text = config_text[7:]
            if config_text.startswith('```'):
                config_text = config_text[3:]
            if config_text.endswith('```'):
                config_text = config_text[:-3]
            
            logger.info(f"成功生成配置: {config_name or 'unnamed'}")
            return config_text
            
        except Exception as e:
            logger.error(f"生成配置失败: {e}")
            raise
    
    def _build_generation_prompt(self, description: str) -> str:
        """构建配置生成prompt"""
        # 读取原始配置文件作为格式参考
        original_config_path = "config/config.yaml"
        try:
            with open(original_config_path, 'r', encoding='utf-8') as f:
                original_config_text = f.read()
        except:
            original_config_text = "# 无法读取原始配置文件"
        
        prompt = f"""你是一个专业的机器学习配置生成助手。请根据用户的自然语言描述，生成一个完整的ML训练配置文件。

## 用户需求描述：
{description}

## 原始配置格式（必须严格遵循此格式）：
```yaml
{original_config_text}
```

## 生成要求：
1. 根据用户描述，修改基础配置模板中的相关参数
2. 严禁修改其他任何文字，包括顺序、格式，你要做的只是替换数字或者参数
3. 严禁改换config文件中的顺序，你只可以替换极少的参数 其他的不做任何改动
4. **重要：严禁修改数据路径 image_dir，必须保持为 'sample_data/images'**
5. **严禁修改任何文件路径相关的配置**


请生成完整的YAML配置："""
        
        return prompt
    
    
    
    def save_config(self, config_text: str, filepath: str) -> str:
        """
        保存配置到文件，直接使用LLM生成的原始文本
        
        Args:
            config_text: 配置文本
            filepath: 保存路径
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 直接保存LLM生成的文本
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(config_text)
            
            logger.info(f"配置已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise
    
    
    def generate_multiple_configs(self, descriptions: List[str], output_dir: str = "config") -> List[str]:
        """
        生成多个配置文件
        
        Args:
            descriptions: 配置描述列表
            output_dir: 输出目录
            
        Returns:
            List[str]: 生成的配置文件路径列表
        """
        config_paths = []
        
        for i, description in enumerate(descriptions):
            try:
                # 生成配置
                config_text = self.generate_config(description, f"config_{i+1}")
                
                # 保存配置
                config_name = f"generated_config_{i+1}.yaml"
                config_path = os.path.join(output_dir, config_name)
                saved_path = self.save_config(config_text, config_path)
                
                config_paths.append(saved_path)
                
            except Exception as e:
                logger.error(f"生成第{i+1}个配置失败: {e}")
                continue
        
        return config_paths


def main():
    """测试配置生成器"""
    print("🚀 测试配置生成器")
    
    try:
        generator = ConfigGenerator()
        
        # 测试单个配置生成
        description = "我想要一个简单的CNN模型，使用较小的batch_size(16)，训练5个epochs，使用RMSprop优化器"
        print(f"\n📝 生成配置: {description}")
        
        config_text = generator.generate_config(description, "test_config")
        print("✅ 配置生成成功")
        
        # 保存配置
        config_path = generator.save_config(config_text, "config/test_generated.yaml")
        print(f"💾 配置已保存到: {config_path}")
        
        # 测试多个配置生成
        descriptions = [
            "简单的CNN模型，batch_size=32，epochs=3",
            "复杂的深度CNN模型，batch_size=16，epochs=10，使用RMSprop优化器",
            "轻量级模型，batch_size=64，epochs=1，快速训练"
        ]
        
        print(f"\n📝 生成多个配置...")
        config_paths = generator.generate_multiple_configs(descriptions, "config")
        print(f"✅ 生成了 {len(config_paths)} 个配置文件")
        
        for path in config_paths:
            print(f"   📄 {path}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
