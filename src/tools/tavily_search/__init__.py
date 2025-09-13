#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tavily 搜索模块
提供天文相关的网络搜索功能
"""

from .tavily_search_api_wrapper import tavily_search, tavily_search_with_images

__all__ = ['tavily_search', 'tavily_search_with_images']
