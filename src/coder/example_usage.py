#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码生成Agent使用示例
演示如何使用CodeGeneratorAgent进行各种数据分析任务
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.coder.workflow import CodeGenerationWorkflow


def simple_example():
    """简单使用示例"""
    print("=== 简单使用示例 ===")
    
    # 创建工作流
    workflow = CodeGenerationWorkflow()
    
    # 运行代码生成
    user_request = "展示前五行数据"
    result = workflow.run(user_request)
    
    # 处理结果
    if result['success']:
        print("✅ 代码生成和执行成功！")
        print(f"📊 使用数据集: {result['dataset_used']}")
        print(f"⚡ 执行时间: {result['execution_time']:.2f}秒")
        print(f"🔄 重试次数: {result['retry_count']}")
        
        print("\n📝 生成的代码:")
        print("```python")
        print(result['code'])
        print("```")
        
        print("\n📋 执行结果:")
        print(result['output'])
        
        if result['generated_files']:
            print(f"\n📁 生成的文件: {result['generated_files']}")
    else:
        print("❌ 代码生成或执行失败")
        print(f"错误: {result['error']}")
        print(f"错误类型: {result['error_type']}")


def visualization_example():
    """数据可视化示例"""
    print("\n=== 数据可视化示例 ===")
    
    workflow = CodeGenerationWorkflow()
    
    # 各种可视化请求示例
    requests = [
        "创建一个显示star、galaxy、qso类别分布的饼图",
        "画出redshift的分布直方图",
        "创建u、g、r、i、z波段的散点图矩阵",
        "制作class和redshift的关系散点图"
    ]
    
    for i, request in enumerate(requests, 1):
        print(f"\n{i}. 请求: {request}")
        result = workflow.run(request)
        
        if result['success']:
            print("✅ 执行成功")
            print(f"⚡ 执行时间: {result['execution_time']:.2f}秒")
            if result['generated_files']:
                print(f"📁 生成文件: {[Path(f).name for f in result['generated_files']]}")
        else:
            print(f"❌ 执行失败: {result['error']}")


def analysis_example():
    """数据分析示例"""
    print("\n=== 数据分析示例 ===")
    
    workflow = CodeGenerationWorkflow()
    
    analysis_requests = [
        "计算各个类别的基本统计信息",
        "分析不同类别的redshift分布差异",
        "找出异常值和离群点",
        "计算各波段之间的相关性"
    ]
    
    for i, request in enumerate(analysis_requests, 1):
        print(f"\n{i}. 分析: {request}")
        result = workflow.run(request)
        
        if result['success']:
            print("✅ 分析完成")
            print(f"⚡ 执行时间: {result['execution_time']:.2f}秒")
            # 只显示输出的前200个字符
            output_preview = result['output'][:200] + "..." if len(result['output']) > 200 else result['output']
            print(f"📊 结果预览: {output_preview}")
        else:
            print(f"❌ 分析失败: {result['error']}")


def machine_learning_example():
    """机器学习示例"""
    print("\n=== 机器学习示例 ===")
    
    workflow = CodeGenerationWorkflow()
    
    ml_requests = [
        "使用随机森林对star、galaxy、qso进行分类",
        "使用支持向量机进行三分类，并显示分类报告",
        "用逻辑回归预测天体类别，画出混淆矩阵",
        "比较不同机器学习算法的性能"
    ]
    
    for i, request in enumerate(ml_requests, 1):
        print(f"\n{i}. 机器学习任务: {request}")
        result = workflow.run(request)
        
        if result['success']:
            print("✅ 模型训练完成")
            print(f"⚡ 执行时间: {result['execution_time']:.2f}秒")
            print(f"🎯 复杂度: {result['complexity']}")
            if result['generated_files']:
                print(f"📁 生成文件: {[Path(f).name for f in result['generated_files']]}")
        else:
            print(f"❌ 训练失败: {result['error']}")


def custom_example():
    """自定义示例 - 允许用户输入"""
    print("\n=== 自定义示例 ===")
    print("请输入你的数据分析需求（输入'quit'退出）:")
    
    workflow = CodeGenerationWorkflow()
    
    while True:
        try:
            user_input = input("\n🤖 你的需求: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            print("🔄 正在处理...")
            result = workflow.run(user_input)
            
            if result['success']:
                print("✅ 执行成功！")
                print(f"📊 数据集: {result['dataset_used']}")
                print(f"⚡ 时间: {result['execution_time']:.2f}秒")
                print(f"🎯 复杂度: {result['complexity']}")
                
                print("\n📝 生成的代码:")
                print("```python")
                print(result['code'])
                print("```")
                
                print("\n📋 执行结果:")
                print(result['output'])
                
                if result['generated_files']:
                    print(f"\n📁 生成文件: {[Path(f).name for f in result['generated_files']]}")
            else:
                print(f"❌ 执行失败: {result['error']}")
                if result.get('code'):
                    print("\n🔍 生成的代码:")
                    print("```python")
                    print(result['code'])
                    print("```")
        
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    print("🚀 代码生成Agent使用示例")
    print("=" * 60)
    
    # 简单示例
    simple_example()
    
    # 可视化示例
    visualization_example()
    
    # 数据分析示例
    analysis_example()
    
    # 机器学习示例
    machine_learning_example()
    
    # 自定义示例
    custom_example()
