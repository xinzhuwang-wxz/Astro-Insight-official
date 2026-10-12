from langchain_community.chat_models import ChatTongyi
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Any, Dict, Optional

class ChatDashscope(ChatTongyi):
    """豆包/通义千问聊天模型包装类"""
    
    def __init__(
        self,
        model: str = "qwen-plus",
        dashscope_api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any
    ):
        """初始化豆包聊天模型
        
        Args:
            model: 模型名称
            dashscope_api_key: API密钥
            base_url: API基础URL
            **kwargs: 其他参数
        """
        # 设置API密钥
        if dashscope_api_key:
            kwargs['dashscope_api_key'] = dashscope_api_key
        
        # 设置模型名称
        kwargs['model'] = model
        
        # 调用父类初始化
        super().__init__(**kwargs)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ChatDashscope":
        """从配置创建实例
        
        Args:
            config: 配置字典
            
        Returns:
            ChatDashscope实例
        """
        return cls(
            model=config.get('model', 'qwen-plus'),
            dashscope_api_key=config.get('api_key'),
            base_url=config.get('base_url'),
            **{k: v for k, v in config.items() if k not in ['model', 'api_key', 'base_url']}
        )