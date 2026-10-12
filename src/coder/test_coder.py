#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码生成Agent测试和示例
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.coder.workflow import CodeGenerationWorkflow
from src.coder.agent import CodeGeneratorAgent
from src.coder.dataset_selector import DatasetSelector


def test_dataset_selector():
    """测试数据集选择器"""
    print("=== 测试数据集选择器 ===")
    
    selector = DatasetSelector()
    datasets = selector.get_available_datasets()
    
    print(f"发现 {len(datasets)} 个数据集:")
    for i, dataset in enumerate(datasets):
        print(f"{i+1}. {dataset['name']}")
        print(f"   路径: {dataset['path']}")
        print(f"   列数: {len(dataset['columns'])}")
        print()
    
    summary = selector.get_dataset_summary()
    print("数据集摘要:")
    print(summary)


def test_simple_request():
    """测试简单请求"""
    print("=== 测试简单请求：展示前5行数据 ===")
    
    workflow = CodeGenerationWorkflow()
    result = workflow.run("展示前五行数据")
    
    print("执行结果:")
    print(f"成功: {result['success']}")
    
    if result['success']:
        print(f"使用数据集: {result['dataset_used']}")
        print(f"复杂度: {result['complexity']}")
        print(f"执行时间: {result['execution_time']:.2f}秒")
        print(f"重试次数: {result['retry_count']}")
        print("\n生成的代码:")
        print("```python")
        print(result['code'])
        print("```")
        print("\n执行输出:")
        print(result['output'])
        
        if result['generated_files']:
            print(f"\n生成的文件: {result['generated_files']}")
    else:
        print(f"错误: {result['error']}")
        print(f"错误类型: {result['error_type']}")
        if result.get('code'):
            print("\n生成的代码:")
            print("```python")
            print(result['code'])
            print("```")


def test_visualization_request():
    """测试可视化请求"""
    print("=== 测试可视化请求：创建数据分布图 ===")
    
    workflow = CodeGenerationWorkflow()
    result = workflow.run("创建一个显示star、galaxy、qso类别分布的饼图")
    
    print("执行结果:")
    print(f"成功: {result['success']}")
    
    if result['success']:
        print(f"使用数据集: {result['dataset_used']}")
        print(f"复杂度: {result['complexity']}")
        print(f"执行时间: {result['execution_time']:.2f}秒")
        print("\n生成的代码:")
        print("```python")
        print(result['code'])
        print("```")
        print("\n执行输出:")
        print(result['output'])
        
        if result['generated_files']:
            print(f"\n生成的文件: {result['generated_files']}")
    else:
        print(f"错误: {result['error']}")
        print(f"错误类型: {result['error_type']}")


def test_complex_analysis():
    """测试复杂分析请求"""
    print("=== 测试复杂分析：机器学习分类 ===")
    
    workflow = CodeGenerationWorkflow()
    result = workflow.run("使用随机森林算法对star、galaxy、qso进行分类，并显示分类报告和混淆矩阵")
    
    print("执行结果:")
    print(f"成功: {result['success']}")
    
    if result['success']:
        print(f"使用数据集: {result['dataset_used']}")
        print(f"复杂度: {result['complexity']}")
        print(f"执行时间: {result['execution_time']:.2f}秒")
        print("\n生成的代码:")
        print("```python")
        print(result['code'])
        print("```")
        print("\n执行输出:")
        print(result['output'][:500] + "..." if len(result['output']) > 500 else result['output'])
        
        if result['generated_files']:
            print(f"\n生成的文件: {result['generated_files']}")
    else:
        print(f"错误: {result['error']}")
        print(f"错误类型: {result['error_type']}")


def test_single_step():
    """测试单步执行"""
    print("=== 测试单步执行 ===")
    
    workflow = CodeGenerationWorkflow()
    
    # 测试数据集选择
    print("1. 数据集选择:")
    result = workflow.run_single_step("展示前五行数据", "dataset_selection")
    print(f"成功: {result['success']}")
    if result['success']:
        selected = result['state']['selected_dataset']
        print(f"选择的数据集: {selected['name']}")
    
    # 测试复杂度分析
    print("\n2. 复杂度分析:")
    result = workflow.run_single_step("创建可视化图表", "complexity_analysis")
    print(f"成功: {result['success']}")
    if result['success']:
        request = result['state']['generation_request']
        print(f"分析的复杂度: {request['complexity'].value}")


if __name__ == "__main__":
    print("开始测试代码生成Agent...")
    print("=" * 50)
    
    # 测试数据集选择器
    test_dataset_selector()
    
    print("\n" + "=" * 50)
    
    # 测试简单请求
    test_simple_request()
    
    print("\n" + "=" * 50)
    
    # 测试可视化请求
    test_visualization_request()
    
    print("\n" + "=" * 50)
    
    # 测试复杂分析
    test_complex_analysis()
    
    print("\n" + "=" * 50)
    
    # 测试单步执行
    test_single_step()
    
    print("\n测试完成！")
