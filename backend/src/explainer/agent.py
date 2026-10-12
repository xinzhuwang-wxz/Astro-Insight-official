# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from .types import (
    ExplainerState, ExplainerRequest, ExplainerResult, CoderOutput,
    ExplanationStatus, ExplanationComplexity, ImageInfo, VLMResponse
)
from .vlm_client import VLMClient
from .prompts import ExplanationPrompts
from .dialogue_manager import DialogueManager


class ExplainerAgent:
    """数据可视化解释器Agent"""
    
    def __init__(self, output_dir: str = "output"):
        self.vlm_client = VLMClient()
        self.prompts = ExplanationPrompts()
        self.dialogue_manager = DialogueManager(output_dir)
        self.output_dir = Path(output_dir)
        
        # 配置参数
        self.max_retries = 3
        self.default_complexity = ExplanationComplexity.DETAILED
    
    def create_initial_state(self, coder_output: CoderOutput, 
                           explanation_type: ExplanationComplexity = None,
                           focus_aspects: Optional[List[str]] = None,
                           session_id: str = None) -> ExplainerState:
        """创建初始状态"""
        
        if session_id is None:
            session_id = self.dialogue_manager.create_session_id()
        
        # 构建解释请求
        request = ExplainerRequest(
            coder_output=coder_output,
            explanation_type=explanation_type or self.default_complexity,
            focus_aspects=focus_aspects,
            target_audience="研究人员",
            dataset_description=None,  # 稍后从数据集文件中获取
            additional_context=None
        )
        
        # 处理图片信息
        image_files = coder_output.get("generated_files", [])
        processed_images = []
        pending_images = []
        
        # 为会话创建独立目录，并复制图片
        session_media_dir = self.dialogue_manager.dialogue_dir / session_id / "images"
        session_media_dir.mkdir(parents=True, exist_ok=True)
        
        for image_path in image_files:
            if Path(image_path).exists():
                # 复制到会话目录
                target_path = session_media_dir / Path(image_path).name
                try:
                    import shutil
                    shutil.copy2(image_path, target_path)
                    session_image_path = str(target_path)
                except Exception:
                    session_image_path = image_path  # 复制失败则退回原路径
                
                image_info = self._create_image_info(session_image_path)
                processed_images.append(image_info)
                pending_images.append(session_image_path)
        
        return ExplainerState(
            session_id=session_id,
            request=request,
            current_step="initialization",
            processed_images=processed_images,
            pending_images=pending_images,
            analysis_context={},
            vlm_responses=[],
            analysis_results=[],
            explanation_result=None,
            error_info=None,
            retry_count=0,
            max_retries=self.max_retries,
            dialogue_record=None,
            output_file_path=None,
            timestamp=time.time()
        )
    
    def process_explanation_request(self, state: ExplainerState) -> ExplainerState:
        """处理解释请求的主流程"""
        try:
            # 1. 准备上下文信息
            state["current_step"] = "context_preparation"
            state = self._prepare_context(state)
            
            if state.get("error_info"):
                return state
            
            # 2. 分析图片
            state["current_step"] = "image_analysis"
            state = self._analyze_images(state)
            
            if state.get("error_info"):
                return state
            
            # 3. 生成解释
            state["current_step"] = "explanation_generation"
            state = self._generate_explanations(state)
            
            if state.get("error_info"):
                return state
            
            # 4. 创建最终结果
            state["current_step"] = "result_creation"
            state = self._create_final_result(state)
            
            # 5. 保存对话记录
            state["current_step"] = "dialogue_saving"
            state = self._save_dialogue(state)
            
            state["current_step"] = "completed"
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "processing_error",
                "message": f"处理过程中发生错误: {str(e)}",
                "step": state.get("current_step", "unknown")
            }
            state["current_step"] = "error"
            return state
    
    def _prepare_context(self, state: ExplainerState) -> ExplainerState:
        """准备上下文信息"""
        try:
            request = state["request"]
            coder_output = request["coder_output"]
            
            # 获取数据集描述
            dataset_used = coder_output.get("dataset_used")
            if dataset_used:
                dataset_description = self._get_dataset_description(dataset_used)
                request["dataset_description"] = dataset_description
            
            # 准备分析上下文
            context = {
                "user_input": coder_output.get("user_input", ""),
                "dataset_used": dataset_used,
                "dataset_description": request.get("dataset_description", ""),
                "generated_code": coder_output.get("code", ""),
                "code_summary": self._summarize_code(coder_output.get("code", "")),
                "complexity": coder_output.get("complexity", ""),
                "execution_output": coder_output.get("output", ""),
                "generated_texts": coder_output.get("generated_texts", []),
                "focus_aspects": request.get("focus_aspects", [])
            }
            
            state["analysis_context"] = context
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "context_preparation_error",
                "message": f"准备上下文信息失败: {str(e)}"
            }
            return state
    
    def _analyze_images(self, state: ExplainerState) -> ExplainerState:
        """分析所有图片"""
        try:
            pending_images = state["pending_images"]
            analysis_context = state["analysis_context"]
            explanation_type = state["request"]["explanation_type"]
            
            vlm_responses = []
            
            for image_path in pending_images:
                print(f"🔍 正在分析图片: {Path(image_path).name}")
                
                # 为这张图片准备特定的上下文
                image_context = analysis_context.copy()
                image_context["image_name"] = Path(image_path).name
                image_context["image_path"] = image_path
                
                # 获取适当的prompt
                prompt = self.prompts.get_explanation_prompt(
                    explanation_type.value, 
                    image_context
                )
                
                # 调用VLM分析
                vlm_response = self.vlm_client.analyze_image(
                    image_path, 
                    prompt, 
                    image_context
                )
                
                vlm_responses.append({
                    "image_path": image_path,
                    "image_name": Path(image_path).name,
                    "response": vlm_response,
                    "context": image_context
                })
                
                if not vlm_response["success"]:
                    print(f"⚠️ 图片分析失败: {vlm_response['error']}")
                else:
                    print(f"✅ 图片分析完成: {Path(image_path).name}")
            
            state["vlm_responses"] = vlm_responses
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "image_analysis_error",
                "message": f"图片分析失败: {str(e)}"
            }
            return state

    def _generate_text_only_explanations(self, state: ExplainerState) -> ExplainerState:
        """无图模式：基于执行输出与文本工件生成解释/总结/洞察"""
        try:
            analysis_context = state["analysis_context"]
            text_artifacts = analysis_context.get("generated_texts", [])
            stdout_text = analysis_context.get("execution_output", "")

            # 组装可供LLM的文本上下文
            combined_texts = []
            if stdout_text:
                combined_texts.append(f"[STDOUT]\n{stdout_text}")
            for p in text_artifacts:
                try:
                    content = Path(p).read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    try:
                        content = Path(p).read_text(errors='ignore')
                    except Exception:
                        content = ""
                if content:
                    combined_texts.append(f"[FILE] {Path(p).name}\n{content}")

            # 利用 prompts 现有结构：构造一个“文本解释”的 prompt
            from .prompts import ExplanationPrompts
            prompts = self.prompts if hasattr(self, 'prompts') else ExplanationPrompts()

            # 复用 detailed prompt 的结构，但在背景信息中仅使用文本来源
            context_for_prompt = analysis_context.copy()
            context_for_prompt["image_name"] = "无图片（文本模式）"

            base_prompt = prompts.get_explanation_prompt(
                state["request"]["explanation_type"].value,
                context_for_prompt
            )

            text_block = "\n\n## 文本材料\n" + "\n\n".join(combined_texts[:3])  # 控长度
            full_prompt = base_prompt + text_block + "\n\n请基于上述文本材料进行解释与总结。"

            # 通过 VLMClient 走同一请求通道，但不传图片：使用一个内部方法实现 text-only
            explanation_text = self._call_text_model(full_prompt)

            explanations = [{
                "image_path": None,
                "image_name": "文本模式",
                "explanation": explanation_text,
                "processing_time": 0,
                "key_findings": self._extract_key_findings(explanation_text)
            }]

            # 总结与洞察
            summary_text = self._call_text_model(self.prompts.get_summary_prompt([explanation_text], analysis_context))
            insights = self._parse_insights(self._call_text_model(self.prompts.get_insight_extraction_prompt([explanation_text])))

            state["analysis_results"] = {
                "explanations": explanations,
                "summary": summary_text or "",
                "insights": insights or [],
                "successful_count": 1 if explanation_text else 0,
                "total_count": 0
            }
            return state
        except Exception as e:
            state["error_info"] = {
                "type": "text_only_explanation_error",
                "message": f"文本模式解释失败: {str(e)}"
            }
            return state

    def _call_text_model(self, prompt: str) -> str:
        """调用纯文本LLM（借用 VLMClient 的 HTTP 通道，如果不支持则返回空字符串）"""
        try:
            # 如果 Explain API 仅支持含 image 的消息，这里降级使用第一原则：发送纯 text 请求
            payload = {
                "model": getattr(self.vlm_client, "model", None),
                "messages": [{"role": "user", "content": prompt}]
            }
            resp = self.vlm_client._make_request(payload)  # 复用其请求方法
            return resp.get("content", "") if resp.get("success") else ""
        except Exception:
            return ""
    
    def _generate_explanations(self, state: ExplainerState) -> ExplainerState:
        """生成最终解释"""
        try:
            vlm_responses = state["vlm_responses"]
            analysis_context = state["analysis_context"]
            
            # 无图模式：如果没有任何图片待分析，则改走文本模式
            if not vlm_responses and not state.get("processed_images"):
                return self._generate_text_only_explanations(state)

            # 处理每个图片的解释
            explanations = []
            successful_explanations = []
            
            for vlm_data in vlm_responses:
                vlm_response = vlm_data["response"]
                
                if vlm_response["success"]:
                    explanation = {
                        "image_path": vlm_data["image_path"],
                        "image_name": vlm_data["image_name"],
                        "explanation": vlm_response["content"],
                        "processing_time": vlm_response["processing_time"],
                        "key_findings": self._extract_key_findings(vlm_response["content"])
                    }
                    explanations.append(explanation)
                    successful_explanations.append(vlm_response["content"])
                else:
                    explanation = {
                        "image_path": vlm_data["image_path"],
                        "image_name": vlm_data["image_name"],
                        "explanation": f"分析失败: {vlm_response['error']}",
                        "processing_time": 0,
                        "key_findings": []
                    }
                    explanations.append(explanation)
            
            # 生成整体总结
            if successful_explanations:
                summary_prompt = self.prompts.get_summary_prompt(
                    successful_explanations, 
                    analysis_context
                )
                summary_response = self.vlm_client.analyze_image(
                    vlm_responses[0]["image_path"],  # 使用第一张图片作为参考
                    summary_prompt,
                    analysis_context
                )
                
                if summary_response["success"]:
                    summary = summary_response["content"]
                else:
                    summary = "无法生成整体总结"
                
                # 提取关键洞察
                insights_prompt = self.prompts.get_insight_extraction_prompt(successful_explanations)
                insights_response = self.vlm_client.analyze_image(
                    vlm_responses[0]["image_path"],
                    insights_prompt,
                    analysis_context
                )
                
                if insights_response["success"]:
                    insights = self._parse_insights(insights_response["content"])
                else:
                    insights = ["无法提取关键洞察"]
            else:
                summary = "所有图片分析均失败"
                insights = []
            
            state["analysis_results"] = {
                "explanations": explanations,
                "summary": summary,
                "insights": insights,
                "successful_count": len(successful_explanations),
                "total_count": len(vlm_responses)
            }
            
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "explanation_generation_error",
                "message": f"生成解释失败: {str(e)}"
            }
            return state
    
    def _create_final_result(self, state: ExplainerState) -> ExplainerState:
        """创建最终结果"""
        try:
            analysis_results = state["analysis_results"]
            vlm_responses = state["vlm_responses"]
            start_time = state["timestamp"]
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 计算VLM调用次数
            vlm_calls = len(vlm_responses) + 2  # 图片分析 + 总结 + 洞察提取
            
            # 收集警告信息
            warnings = []
            failed_images = []
            
            for vlm_data in vlm_responses:
                if not vlm_data["response"]["success"]:
                    failed_images.append(vlm_data["image_name"])
            
            if failed_images:
                warnings.append(f"以下图片分析失败: {', '.join(failed_images)}")
            
            # 创建最终结果
            result = ExplainerResult(
                status=ExplanationStatus.SUCCESS if analysis_results["successful_count"] > 0 else ExplanationStatus.ERROR,
                explanations=analysis_results["explanations"],
                summary=analysis_results["summary"],
                insights=analysis_results["insights"],
                images_analyzed=state["processed_images"],
                processing_time=processing_time,
                vlm_calls=vlm_calls,
                error=None if analysis_results["successful_count"] > 0 else "所有图片分析均失败",
                warnings=warnings
            )
            
            state["explanation_result"] = result
            return state
            
        except Exception as e:
            state["error_info"] = {
                "type": "result_creation_error",
                "message": f"创建最终结果失败: {str(e)}"
            }
            return state
    
    def _save_dialogue(self, state: ExplainerState) -> ExplainerState:
        """保存对话记录"""
        try:
            if not state.get("explanation_result"):
                return state
            
            session_id = state["session_id"]
            coder_output = state["request"]["coder_output"]
            explainer_result = state["explanation_result"]
            user_request = coder_output.get("user_input", "")
            
            # 保存对话记录
            dialogue_file = self.dialogue_manager.save_dialogue_record(
                session_id, user_request, coder_output, explainer_result
            )
            
            # 生成解释报告
            report_file = self.dialogue_manager.generate_explanation_report(
                session_id, explainer_result, coder_output
            )
            
            state["output_file_path"] = report_file
            
            print(f"💾 对话记录已保存: {dialogue_file}")
            print(f"📄 解释报告已生成: {report_file}")
            
            # 标记完成
            state["current_step"] = "completed"
            
            return state
            
        except Exception as e:
            print(f"⚠️ 保存对话记录失败: {str(e)}")
            return state
    
    def get_final_result(self, state: ExplainerState) -> Dict[str, Any]:
        """获取最终结果"""
        # 以 explanation_result 是否存在作为成功判定，更稳健
        if state.get("explanation_result"):
            result = state["explanation_result"]
            return {
                "success": True,
                "session_id": state.get("session_id"),
                "explanations": result.get("explanations", []),
                "summary": result.get("summary", ""),
                "insights": result.get("insights", []),
                "images_count": len(result.get("images_analyzed", [])),
                "processing_time": result.get("processing_time", 0.0),
                "vlm_calls": result.get("vlm_calls", 0),
                "warnings": result.get("warnings", []),
                "output_file": state.get("output_file_path"),
                "dialogue_saved": bool(state.get("output_file_path"))
            }
        else:
            error_info = state.get("error_info") or {}
            return {
                "success": False,
                "session_id": state.get("session_id"),
                "error": error_info.get("message", "未知错误"),
                "error_type": error_info.get("type", "unknown"),
                "step": state.get("current_step", "unknown"),
                "retry_count": state.get("retry_count", 0)
            }
    
    # 辅助方法
    def _create_image_info(self, image_path: str) -> ImageInfo:
        """创建图片信息"""
        path = Path(image_path)
        return ImageInfo(
            file_path=str(path),
            file_name=path.name,
            file_size=path.stat().st_size if path.exists() else 0,
            created_time=path.stat().st_mtime if path.exists() else 0,
            image_type=path.suffix.lower()
        )
    
    def _get_dataset_description(self, dataset_name: str) -> str:
        """获取数据集描述"""
        # 尝试从数据集描述文件中读取
        desc_dir = Path("dataset/full_description")
        if desc_dir.exists():
            for desc_file in desc_dir.glob("*.txt"):
                if dataset_name.lower() in desc_file.name.lower():
                    try:
                        return desc_file.read_text(encoding='utf-8')
                    except Exception:
                        pass
        return f"数据集: {dataset_name}"
    
    def _summarize_code(self, code: str) -> str:
        """总结代码的关键操作"""
        if not code:
            return "无代码信息"
        
        lines = code.split('\n')
        key_operations = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in [
                'plt.', 'sns.', 'plot', 'hist', 'scatter', 'savefig',
                'DataFrame', 'groupby', 'agg', 'merge'
            ]):
                key_operations.append(line)
        
        return "; ".join(key_operations[:5])  # 只取前5个关键操作
    
    def _extract_key_findings(self, explanation: str) -> List[str]:
        """从解释中提取关键发现"""
        findings = []
        lines = explanation.split('\n')
        
        in_findings_section = False
        for line in lines:
            line = line.strip()
            
            # 查找关键发现相关的章节
            if any(keyword in line.lower() for keyword in [
                '关键发现', 'key findings', '主要发现', '重要观察'
            ]):
                in_findings_section = True
                continue
            
            # 如果在发现章节中，收集列表项
            if in_findings_section:
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    findings.append(line[1:].strip())
                elif line.startswith('#') or not line:
                    # 遇到新章节或空行，停止收集
                    break
        
        # 如果没有找到明确的发现章节，尝试提取前几个要点
        if not findings:
            for line in lines:
                line = line.strip()
                if (line.startswith('-') or line.startswith('•') or line.startswith('*')) and len(line) > 10:
                    findings.append(line[1:].strip())
                    if len(findings) >= 3:
                        break
        
        return findings[:5]  # 最多返回5个关键发现
    
    def _parse_insights(self, insights_text: str) -> List[str]:
        """解析洞察文本为列表"""
        insights = []
        lines = insights_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                insight = line[1:].strip()
                if insight and len(insight) > 5:
                    insights.append(insight)
        
        return insights
