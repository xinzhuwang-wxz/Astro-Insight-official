# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision", "code"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "identity_check": "basic",
    "qa_agent": "basic",
    "task_selector": "basic",
    "classification_config": "basic",
    "data_retrieval": "basic",
    "literature_review": "basic",
    "code_generator": "basic",
    "code_executor": "basic",
    "review_loop": "basic",
    "error_recovery": "basic",
    "coder": "code",  # 新增：代码生成Agent使用代码专用LLM
}