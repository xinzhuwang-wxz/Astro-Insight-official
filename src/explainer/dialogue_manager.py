# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

from .types import DialogueRecord, CoderOutput, ExplainerResult


class DialogueManager:
    """对话和文件管理器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建对话子目录
        self.dialogue_dir = self.output_dir / "dialogues"
        self.dialogue_dir.mkdir(exist_ok=True)
        
        # 创建解释报告子目录  
        self.reports_dir = self.output_dir / "explanation_reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def create_session_id(self) -> str:
        """创建会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"session_{timestamp}_{unique_id}"
    
    def save_dialogue_record(self, session_id: str, user_request: str, 
                           coder_output: CoderOutput, explainer_result: ExplainerResult) -> str:
        """保存完整的对话记录"""
        
        # 创建对话记录
        dialogue_record = DialogueRecord(
            session_id=session_id,
            timestamp=time.time(),
            user_request=user_request,
            coder_output=coder_output,
            explainer_result=explainer_result,
            conversation_context={
                "datetime": datetime.now().isoformat(),
                "dataset_used": coder_output.get("dataset_used"),
                "images_count": len(coder_output.get("generated_files", [])),
                "processing_time": {
                    "coder": coder_output.get("execution_time", 0),
                    "explainer": explainer_result.get("processing_time", 0)
                }
            }
        )
        
        # 保存到JSON文件（会话目录与总目录各存一份）
        session_dir = self.dialogue_dir / session_id
        session_dir.mkdir(exist_ok=True)
        dialogue_file_session = session_dir / f"{session_id}_dialogue.json"
        dialogue_file_total = self.dialogue_dir / f"{session_id}_dialogue.json"
        
        try:
            for path in [dialogue_file_session, dialogue_file_total]:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(dialogue_record, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"📝 对话记录已保存: {dialogue_file_session}")
            return str(dialogue_file_session)
            
        except Exception as e:
            print(f"❌ 保存对话记录失败: {e}")
            return ""
    
    def generate_explanation_report(self, session_id: str, explainer_result: ExplainerResult, 
                                  coder_output: CoderOutput) -> str:
        """生成格式化的解释报告"""
        
        # 创建报告内容
        report_content = self._build_report_content(explainer_result, coder_output)
        
        # 保存报告文件（会话目录与总目录各存一份）
        session_dir = self.reports_dir / session_id
        session_dir.mkdir(exist_ok=True)
        report_file_session = session_dir / f"{session_id}_explanation_report.md"
        report_file_total = self.reports_dir / f"{session_id}_explanation_report.md"
        
        try:
            for path in [report_file_session, report_file_total]:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            print(f"📊 解释报告已生成: {report_file_session}")
            return str(report_file_session)
            
        except Exception as e:
            print(f"❌ 生成解释报告失败: {e}")
            return ""
    
    def _build_report_content(self, explainer_result: ExplainerResult, 
                            coder_output: CoderOutput) -> str:
        """构建报告内容"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 数据可视化解释报告

## 📋 基本信息

- **生成时间**: {timestamp}
- **数据集**: {coder_output.get('dataset_used', 'Unknown')}
- **用户需求**: {coder_output.get('user_input', 'N/A')}
- **分析图片数量**: {len(explainer_result.get('images_analyzed', []))}
- **处理时间**: {explainer_result.get('processing_time', 0):.2f}秒

## 🎯 整体总结

{explainer_result.get('summary', '暂无总结')}

## 📊 图片详细解释

"""
        
        # 添加每张图片的解释
        explanations = explainer_result.get('explanations', [])
        for i, explanation in enumerate(explanations, 1):
            report += f"""### 图片 {i}: {explanation.get('image_name', f'Image_{i}')}

**图片路径**: `{explanation.get('image_path', 'N/A')}`

**解释内容**:
{explanation.get('explanation', '暂无解释')}

**关键发现**:
"""
            # 添加关键发现
            findings = explanation.get('key_findings', [])
            for finding in findings:
                report += f"- {finding}\n"
            
            report += "\n---\n\n"
        
        # 添加整体洞察
        insights = explainer_result.get('insights', [])
        if insights:
            report += "## 💡 关键洞察\n\n"
            for insight in insights:
                report += f"- {insight}\n"
            report += "\n"
        
        # 添加技术信息
        report += f"""## 🔧 技术信息

- **VLM调用次数**: {explainer_result.get('vlm_calls', 0)}
- **解释状态**: {explainer_result.get('status', 'unknown')}
- **代码复杂度**: {coder_output.get('complexity', 'unknown')}
- **代码执行时间**: {coder_output.get('execution_time', 0):.2f}秒

## 📝 生成代码

```python
{coder_output.get('code', '# 代码不可用')}
```

## 📈 执行输出

```
{coder_output.get('output', '无输出')}
```
"""
        
        # 添加警告信息
        warnings = explainer_result.get('warnings', [])
        if warnings:
            report += "\n## ⚠️ 注意事项\n\n"
            for warning in warnings:
                report += f"- {warning}\n"
        
        return report
    
    def get_dialogue_history(self, session_id: str) -> Optional[DialogueRecord]:
        """获取对话历史记录"""
        dialogue_file = self.dialogue_dir / f"{session_id}_dialogue.json"
        
        if not dialogue_file.exists():
            return None
        
        try:
            with open(dialogue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取对话记录失败: {e}")
            return None
    
    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        sessions = []
        
        for file_path in self.dialogue_dir.glob("*_dialogue.json"):
            session_id = file_path.stem.replace("_dialogue", "")
            sessions.append(session_id)
        
        return sorted(sessions, reverse=True)  # 最新的在前
    
    def cleanup_old_sessions(self, keep_days: int = 30) -> int:
        """清理旧的会话记录"""
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        cleaned_count = 0
        
        # 清理对话记录
        for file_path in self.dialogue_dir.glob("*_dialogue.json"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
        
        # 清理报告文件
        for file_path in self.reports_dir.glob("*_explanation_report.md"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
        
        print(f"🧹 已清理 {cleaned_count} 个旧文件")
        return cleaned_count
    
    def copy_images_to_session(self, session_id: str, image_paths: List[str]) -> List[str]:
        """将图片复制到会话目录"""
        session_dir = self.dialogue_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        copied_paths = []
        
        for image_path in image_paths:
            source_path = Path(image_path)
            if source_path.exists():
                target_path = session_dir / source_path.name
                try:
                    import shutil
                    shutil.copy2(source_path, target_path)
                    copied_paths.append(str(target_path))
                except Exception as e:
                    print(f"复制图片失败 {image_path}: {e}")
        
        return copied_paths
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要信息"""
        dialogue_record = self.get_dialogue_history(session_id)
        
        if not dialogue_record:
            return {}
        
        return {
            "session_id": session_id,
            "timestamp": dialogue_record["timestamp"],
            "user_request": dialogue_record["user_request"],
            "dataset_used": dialogue_record["coder_output"].get("dataset_used"),
            "images_count": len(dialogue_record["coder_output"].get("generated_files", [])),
            "success": dialogue_record["explainer_result"].get("status") == "success",
            "processing_time": dialogue_record["explainer_result"].get("processing_time", 0)
        }
