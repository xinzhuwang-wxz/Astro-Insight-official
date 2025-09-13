# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image

from ..config.loader import load_yaml_config
from .types import VLMRequest, VLMResponse


class VLMClient:
    """Vision Language Model 客户端"""
    
    def __init__(self):
        self.config = load_yaml_config()
        self.vlm_config = self.config.get("Explain_MODEL", {})
        
        self.base_url = self.vlm_config.get("base_url")
        self.model = self.vlm_config.get("model") 
        self.api_key = self.vlm_config.get("api_key")
        self.max_retries = self.vlm_config.get("max_retries", 3)
        self.verify_ssl = self.vlm_config.get("verify_ssl", True)
        
        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })
    
    def analyze_image(self, image_path: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> VLMResponse:
        """分析单张图片"""
        start_time = time.time()
        
        try:
            # 检查图片文件
            if not Path(image_path).exists():
                return VLMResponse(
                    success=False,
                    content="",
                    error=f"图片文件不存在: {image_path}",
                    processing_time=time.time() - start_time,
                    model_used=self.model
                )
            
            # 编码图片
            encoded_image = self._encode_image(image_path)
            if not encoded_image:
                return VLMResponse(
                    success=False,
                    content="",
                    error=f"图片编码失败: {image_path}",
                    processing_time=time.time() - start_time,
                    model_used=self.model
                )
            
            # 构建请求
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            },
                            {
                                "type": "text", 
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # 添加上下文信息到prompt中
            if context:
                enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
                request_data["messages"][0]["content"][1]["text"] = enhanced_prompt
            
            # 发送请求
            response = self._make_request(request_data)
            
            if response["success"]:
                return VLMResponse(
                    success=True,
                    content=response["content"],
                    error=None,
                    processing_time=time.time() - start_time,
                    model_used=self.model
                )
            else:
                return VLMResponse(
                    success=False,
                    content="",
                    error=response["error"],
                    processing_time=time.time() - start_time,
                    model_used=self.model
                )
                
        except Exception as e:
            return VLMResponse(
                success=False,
                content="",
                error=f"VLM调用异常: {str(e)}",
                processing_time=time.time() - start_time,
                model_used=self.model
            )
    
    def analyze_multiple_images(self, image_paths: List[str], prompt: str, context: Optional[Dict[str, Any]] = None) -> List[VLMResponse]:
        """批量分析多张图片"""
        results = []
        
        for image_path in image_paths:
            # 为每张图片调整prompt
            image_specific_prompt = self._customize_prompt_for_image(prompt, image_path, context)
            result = self.analyze_image(image_path, image_specific_prompt, context)
            results.append(result)
            
            # 避免请求过快
            time.sleep(0.5)
        
        return results
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """将图片编码为base64字符串"""
        try:
            # 检查和转换图片格式
            img_path = Path(image_path)
            
            # 使用PIL确保图片格式正确
            with Image.open(img_path) as img:
                # 转换为RGB（去除透明通道）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 压缩大图片
                max_size = (1024, 1024)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存为临时JPEG
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                    img.save(tmp_file.name, 'JPEG', quality=85)
                    tmp_path = tmp_file.name
            
            # 读取并编码
            with open(tmp_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 清理临时文件
            Path(tmp_path).unlink(missing_ok=True)
            
            return encoded
            
        except Exception as e:
            print(f"图片编码错误 {image_path}: {e}")
            return None
    
    def _enhance_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """用上下文信息增强prompt"""
        enhanced_prompt = prompt
        
        # 添加数据集信息
        if context.get("dataset_used"):
            enhanced_prompt += f"\n\n数据集信息: {context['dataset_used']}"
        
        # 添加用户需求
        if context.get("user_input"):
            enhanced_prompt += f"\n用户需求: {context['user_input']}"
        
        # 添加代码上下文
        if context.get("generated_code"):
            # 提取关键信息，避免prompt过长
            code_summary = self._summarize_code(context["generated_code"])
            enhanced_prompt += f"\n生成代码概要: {code_summary}"
        
        # 添加数据集描述
        if context.get("dataset_description"):
            enhanced_prompt += f"\n数据集描述: {context['dataset_description']}"
        
        return enhanced_prompt
    
    def _customize_prompt_for_image(self, prompt: str, image_path: str, context: Optional[Dict[str, Any]]) -> str:
        """为特定图片定制prompt"""
        image_name = Path(image_path).stem
        
        # 根据图片名称推断图片类型
        image_type = self._infer_image_type(image_name)
        
        customized_prompt = prompt + f"\n\n当前分析的图片: {image_name}"
        
        if image_type:
            customized_prompt += f"\n图片类型: {image_type}"
        
        return customized_prompt
    
    def _infer_image_type(self, image_name: str) -> str:
        """根据文件名推断图片类型"""
        name_lower = image_name.lower()
        
        if any(word in name_lower for word in ['histogram', 'hist', 'distribution']):
            return "直方图/分布图"
        elif any(word in name_lower for word in ['scatter', 'plot']):
            return "散点图"
        elif any(word in name_lower for word in ['pie', 'chart']):
            return "饼图"
        elif any(word in name_lower for word in ['heatmap', 'heat', 'correlation']):
            return "热力图/相关性图"
        elif any(word in name_lower for word in ['box', 'boxplot']):
            return "箱线图"
        elif any(word in name_lower for word in ['confusion', 'matrix']):
            return "混淆矩阵"
        else:
            return "数据可视化图表"
    
    def _summarize_code(self, code: str) -> str:
        """总结代码的关键信息"""
        lines = code.split('\n')
        key_operations = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ['plt.', 'sns.', 'plot', 'hist', 'scatter', 'savefig']):
                key_operations.append(line)
        
        return "; ".join(key_operations[:3])  # 只取前3个关键操作
    
    def _make_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送HTTP请求到VLM API"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=request_data,
                    verify=self.verify_ssl,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return {"success": True, "content": content, "error": None}
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    return {"success": False, "content": "", "error": error_msg}
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "content": "", "error": str(e)}
        
        return {"success": False, "content": "", "error": "最大重试次数已达到"}
