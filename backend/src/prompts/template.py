# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
from datetime import datetime
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.graph import MessagesState as AgentState
from langchain_core.prompts import ChatPromptTemplate

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def get_prompt(prompt_name: str, **kwargs) -> str:
    """
    Get a formatted prompt by loading template and applying variables.
    
    Args:
        prompt_name: Name of the prompt template file (without .md extension)
        **kwargs: Variables to substitute in the template
    
    Returns:
        Formatted prompt string
    """
    # Add current time as a default variable
    template_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **kwargs
    }
    
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render(**template_vars)
    except Exception as e:
        raise ValueError(f"Error rendering template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str, state: AgentState, configurable: Optional[Dict[str, Any]] = None
) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    # Add configurable variables
    if configurable:
        state_vars.update(configurable) 

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)  # render means substitute the variables in the template
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")