# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path
from typing import List

from .workflow import ExplainerWorkflow
from .types import ExplanationComplexity


def explain_existing_images(image_paths: List[str], user_input: str = "解释这些图像", complexity: ExplanationComplexity = ExplanationComplexity.DETAILED):
    """直接解释已有图片文件（用于调试）"""
    # 构造一个伪造的Coder结果，最小字段满足Explainer需求
    coder_result = {
        "success": True,
        "code": "# N/A",
        "output": "",
        "execution_time": 0.0,
        "generated_files": image_paths,
        "dataset_used": "custom",
        "complexity": "MODERATE",
        "retry_count": 0
    }

    wf = ExplainerWorkflow()
    result = wf.explain_from_coder_workflow(
        coder_result=coder_result,
        user_input=user_input,
        explanation_type=complexity,
        focus_aspects=["数据分布", "趋势", "异常"]
    )

    print(result)


def explain_from_coder(user_input: str):
    """先运行Coder，再解释Coder输出"""
    wf = ExplainerWorkflow()
    result = wf.run_combined_workflow(
        user_input=user_input,
        explanation_type=ExplanationComplexity.DETAILED,
        focus_aspects=["科学意义", "数据质量", "关键发现"]
    )
    print(result)


if __name__ == "__main__":
    # 用法:
    # 1) 解释已有图片: python -m src.explainer.example_usage images output/feature_importance.png output/correlation_heatmap.png
    # 2) 从Coder运行:  python -m src.explainer.example_usage coder "创建star、galaxy、qso类别分布的饼图并进行解释"

    if len(sys.argv) < 2:
        print("用法: python -m src.explainer.example_usage [images|coder] <args...>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "images":
        if len(sys.argv) < 3:
            print("请提供至少一张图片路径")
            sys.exit(1)
        image_paths = sys.argv[2:]
        explain_existing_images(image_paths)
    elif mode == "coder":
        if len(sys.argv) < 3:
            print("请提供用户需求字符串")
            sys.exit(1)
        user_input = sys.argv[2]
        explain_from_coder(user_input)
    else:
        print("未知模式，应为 images 或 coder")
        sys.exit(1)
