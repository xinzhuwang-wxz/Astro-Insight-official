# Explainer 模块说明（数据可视化解读）

`src/explainer` 提供对 `@coder` 生成的数据可视化图片的自动化解读能力：综合图片、用户需求、数据集背景与生成代码上下文，生成结构化的中文解释报告，并将对话与产物以“会话”维度进行隔离存储。

## 功能特性
- 图片理解：调用视觉大模型（VLM）对单图/多图进行分析与解读。
- 上下文增强：结合用户需求、数据集描述与生成代码关键信息，产生专业、可读的说明。
- 结构化输出：生成逐图解释、整体总结、关键洞察列表。
- 持久化：保存完整对话记录（JSON）与解释报告（Markdown），支持检索与审阅。
- 会话隔离：每次对话独立的会话目录，图片与报告不混淆。

## 目录结构
```
src/explainer/
├─ __init__.py
├─ agent.py               # ExplainerAgent：核心业务逻辑
├─ workflow.py            # LangGraph 工作流封装
├─ vlm_client.py          # 视觉大模型客户端（调用火山引擎Doubao Vision）
├─ prompts.py             # 解释Prompt模板（basic/detailed/professional）
├─ dialogue_manager.py    # 对话与报告的存储管理
├─ types.py               # 类型定义（状态/请求/结果）
├─ example_usage.py       # 使用示例（images / coder / 组合）
└─ README.md              # 当前文档
```

## 配置
使用 `conf.yaml` 的 `Explain_MODEL` 段落：
```yaml
Explain_MODEL:
  base_url: https://ark.cn-beijing.volces.com/api/v3
  model: "doubao-seed-1-6-vision-250815"
  api_key: "<YOUR_API_KEY>"
  max_retries: 3
  verify_ssl: true
```
Explainer 通过 `src/config/loader.py` 加载该配置。

## 会话与输出规范
- 全局输出目录：`output/`
- 会话ID：`session_YYYYMMDD_HHMMSS_<8位uuid>`
- 会话内产物：
  - 图片副本：`output/dialogues/<session>/images/*.png`
  - 对话记录：`output/dialogues/<session>/<session>_dialogue.json`
  - 解释报告：`output/explanation_reports/<session>/<session>_explanation_report.md`
- 汇总副本：
  - `output/dialogues/<session>_dialogue.json`
  - `output/explanation_reports/<session>_explanation_report.md`
- 仅使用本次对话新生成图片：`@coder` 执行器基于“执行前后差集+修改时间窗口”筛选，避免历史图片混入。

## 使用方法
### 1）端到端（Coder→Explainer）
```bash
python -m src.explainer.example_usage coder "创建一个显示star、galaxy、qso类别分布的饼图，并进行解释"
```
输出包含：
- `generated_files`: 本次生成图片（1..n）
- `explainer_result`: 逐图解释、总结、洞察
- 会话目录内的对话与报告文件

### 2）仅解释已有图片（跳过 Coder）
```bash
python -m src.explainer.example_usage images output/feature_importance.png output/correlation_heatmap.png
```

## 编程接口
### ExplainerWorkflow
```python
from src.explainer.workflow import ExplainerWorkflow
from src.explainer.types import ExplanationComplexity

wf = ExplainerWorkflow()

# 场景A：直接解释Coder工作流返回
def explain_from_coder(coder_result, user_input: str):
    return wf.explain_from_coder_workflow(
        coder_result=coder_result,
        user_input=user_input,
        explanation_type=ExplanationComplexity.DETAILED,
        focus_aspects=["科学意义", "数据质量", "关键发现"],
        session_id=None,
    )

# 场景B：端到端执行（内部先跑Coder，再跑Explainer）
def run_all(user_input: str):
    return wf.run_combined_workflow(
        user_input=user_input,
        explanation_type=ExplanationComplexity.DETAILED,
        focus_aspects=["数据分布", "趋势", "异常"],
        session_id=None,
    )
```

### ExplainerAgent（核心字段）
- 输入（简化）：
  - `coder_output`: 包含 `generated_files`, `code`, `dataset_used`, `output`, `complexity`, `user_input` 等
  - `explanation_type`: basic/detailed/professional
  - `focus_aspects`: 关注重点（可选）
- 过程：
  - `context_preparation` → `image_analysis` → `explanation_generation` → `result_creation` → `dialogue_saving`
- 输出：
  - `explanations`: 每图解释
  - `summary`: 总结
  - `insights`: 关键洞察
  - `images_analyzed`: 图片元信息
  - `processing_time`, `vlm_calls`, `warnings`
  - `output_file`: 解释报告路径

## Prompt 等级
- `basic`: 简明扼要；
- `detailed`: 结构化的专业说明（默认）；
- `professional`: 更深入的学术化分析（含方法、局限与研究建议）。

## 视觉大模型调用
- 客户端：`vlm_client.py`
- 封装了图片 base64 内嵌、上下文增强（用户需求、代码摘要、数据集描述）、错误重试与异常信息。

## 故障排查
- 无图片被解释：
  - 检查 `coder_result.generated_files` 是否为空；
  - 确认 `@coder` 的执行器未被历史图片干扰（本仓库已用差集+时间窗口修复）。
- VLM 请求失败：
  - 确认 `conf.yaml` 的 `Explain_MODEL.api_key/base_url/model` 正确；
  - 网络/SSL问题可设置 `verify_ssl=false` 测试。
- NoneType/状态异常：
  - 工作流已做健壮性处理；若仍遇到，请查看返回中的 `traceback` 或 `debug` 字段并附带日志。

## 设计要点与注意
- 会话隔离：所有图片在进入解释流程前复制到会话目录，确保文件与报告一一对应。
- 只读外部图片：解释过程不修改原始图片。
- 代码摘要：自动从生成代码中提取关键绘图/保存语句，避免上下文过长。
- 报告模板：Markdown，包含“基本信息 / 整体总结 / 图表解释 / 关键洞察 / 技术信息 / 生成代码 / 执行输出 / 注意事项”。

## 示例产物
- `output/dialogues/<session>/<session>_dialogue.json`
- `output/explanation_reports/<session>/<session>_explanation_report.md`
- `output/dialogues/<session>/images/*.png`

---
如需集成到你的 API/UI，请复用 `ExplainerWorkflow` 并以会话ID为主键，将用户请求、Coder 输出与 Explainer 结果串联，前端可直链报告与会话内图片。


