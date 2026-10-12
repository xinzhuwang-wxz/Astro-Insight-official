#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式代码生成Agent演示
完整展示用户输入、模型处理过程和输出结果
"""

import sys
from pathlib import Path
import time

# 确保能找到项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_separator(title="", char="=", width=60):
    """打印分隔线"""
    if title:
        title_line = f" {title} "
        padding = (width - len(title_line)) // 2
        print(char * padding + title_line + char * padding)
    else:
        print(char * width)

def display_step(step_num, title, status="进行中"):
    """显示步骤信息"""
    status_emoji = {
        "进行中": "🔄",
        "成功": "✅", 
        "失败": "❌",
        "警告": "⚠️"
    }
    emoji = status_emoji.get(status, "🔄")
    print(f"\n{emoji} 步骤 {step_num}: {title}")
    print("-" * 50)

def display_user_input(user_input):
    """展示用户输入"""
    print_separator("用户输入", "=")
    print(f"📝 用户需求: {user_input}")
    print(f"🕒 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def display_dataset_info(datasets):
    """展示数据集信息"""
    print_separator("数据集发现", "=")
    if not datasets:
        print("❌ 未发现可用数据集")
        return
    
    print(f"✅ 发现 {len(datasets)} 个数据集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"\n📊 数据集 {i}:")
        print(f"   名称: {dataset['name']}")
        print(f"   路径: {dataset['path']}")
        print(f"   列数: {len(dataset['columns'])}")
        print(f"   文件存在: {'✅' if Path(dataset['path']).exists() else '❌'}")
        
        if dataset['columns']:
            print(f"   主要列: {', '.join(dataset['columns'][:5])}")
            if len(dataset['columns']) > 5:
                print(f"           ... 还有 {len(dataset['columns']) - 5} 列")

def display_complexity_analysis(complexity):
    """展示复杂度分析"""
    print_separator("复杂度分析", "=")
    complexity_info = {
        "simple": ("🟢", "简单操作", "数据展示、基本统计"),
        "moderate": ("🟡", "中等复杂度", "数据可视化、清洗分析"),
        "complex": ("🔴", "复杂分析", "机器学习、高级统计")
    }
    
    emoji, level, desc = complexity_info.get(complexity.value, ("❓", "未知", ""))
    print(f"{emoji} 复杂度级别: {level}")
    print(f"📝 描述: {desc}")

def display_code_generation(code, attempt=1):
    """展示代码生成过程"""
    print_separator(f"代码生成 (第{attempt}次尝试)", "=")
    print("🤖 模型生成的代码:")
    print("```python")
    
    # 显示代码，添加行号
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        print(f"{i:3d}: {line}")
    
    print("```")
    print(f"📊 代码统计: 共 {len(lines)} 行，{len(code)} 字符")

def display_execution_result(result):
    """展示代码执行结果"""
    print_separator("代码执行结果", "=")
    
    status_info = {
        "success": ("✅", "执行成功"),
        "error": ("❌", "执行失败"),
        "timeout": ("⏰", "执行超时")
    }
    
    emoji, status_text = status_info.get(result['status'].value, ("❓", "未知状态"))
    print(f"{emoji} 执行状态: {status_text}")
    print(f"⏱️ 执行时间: {result['execution_time']:.2f} 秒")
    
    if result['status'].value == 'success':
        print("\n📋 程序输出:")
        print("=" * 40)
        output_lines = result['output'].split('\n')
        for line in output_lines:
            if line.strip():
                print(f"   {line}")
        print("=" * 40)
        
        if result['generated_files']:
            print(f"\n📁 生成的文件: {result['generated_files']}")
    else:
        print(f"\n❌ 错误信息:")
        print("=" * 40)
        error_lines = result['error'].split('\n')
        for line in error_lines[:10]:  # 只显示前10行错误
            if line.strip():
                print(f"   {line}")
        if len(error_lines) > 10:
            print(f"   ... (还有 {len(error_lines) - 10} 行错误信息)")
        print("=" * 40)

def display_final_summary(final_result):
    """展示最终总结"""
    print_separator("执行总结", "=")
    
    if final_result['success']:
        print("🎉 代码生成和执行成功!")
        print(f"📊 使用数据集: {final_result['dataset_used']}")
        print(f"🎯 复杂度: {final_result['complexity']}")
        print(f"⏱️ 总执行时间: {final_result['execution_time']:.2f} 秒")
        print(f"🔄 重试次数: {final_result['retry_count']}")
        
        if final_result.get('generated_files'):
            print(f"📁 生成文件: {len(final_result['generated_files'])} 个")
    else:
        print("❌ 代码生成或执行失败")
        print(f"🚫 错误类型: {final_result['error_type']}")
        print(f"📝 错误详情: {final_result['error']}")
        print(f"🔄 重试次数: {final_result['retry_count']}")

def run_detailed_demo(user_input):
    """运行详细的演示流程"""
    print_separator("代码生成Agent详细演示", "=")
    
    # 显示用户输入
    display_user_input(user_input)
    
    try:
        from src.coder.workflow import CodeGenerationWorkflow
        
        # 创建工作流
        display_step(1, "初始化代码生成工作流")
        workflow = CodeGenerationWorkflow()
        print("✅ 工作流创建成功")
        
        # 获取数据集信息
        display_step(2, "数据集发现和分析")
        datasets = workflow.agent.dataset_selector.get_available_datasets()
        display_dataset_info(datasets)
        
        # 开始代码生成流程
        display_step(3, "启动完整代码生成流程")
        print("🚀 开始处理用户请求...")
        
        # 运行工作流（这里会包含所有步骤）
        result = workflow.run(user_input)
        
        # 显示最终结果
        display_step(4, "生成结果展示", "成功" if result['success'] else "失败")
        display_final_summary(result)
        
        return result
        
    except Exception as e:
        display_step(4, "处理过程", "失败")
        print(f"❌ 发生异常: {str(e)}")
        import traceback
        print("\n🔍 详细错误信息:")
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def run_step_by_step_demo(user_input):
    """运行分步演示，展示每个环节"""
    print_separator("分步代码生成演示", "=")
    
    display_user_input(user_input)
    
    try:
        from src.coder.agent import CodeGeneratorAgent
        
        # 创建agent
        display_step(1, "创建代码生成Agent")
        agent = CodeGeneratorAgent()
        print("✅ Agent初始化成功")
        
        # 创建初始状态
        display_step(2, "创建初始状态")
        state = agent.create_initial_state(user_input)
        print(f"✅ 会话ID: {state['session_id']}")
        print(f"📝 用户输入: {state['user_input']}")
        
        # 数据集选择
        display_step(3, "数据集选择")
        state = agent._select_dataset(state)
        if state.get("error_info"):
            print(f"❌ 数据集选择失败: {state['error_info']['message']}")
            return
        
        selected_dataset = state['selected_dataset']
        print(f"✅ 选择数据集: {selected_dataset['name']}")
        display_dataset_info([selected_dataset])
        
        # 复杂度分析
        display_step(4, "需求复杂度分析")
        state = agent._analyze_complexity(state)
        if state.get("error_info"):
            print(f"❌ 复杂度分析失败: {state['error_info']['message']}")
            return
        
        complexity = state['generation_request']['complexity']
        display_complexity_analysis(complexity)
        
        # 代码生成
        display_step(5, "代码生成")
        state = agent._generate_code(state)
        if state.get("error_info"):
            print(f"❌ 代码生成失败: {state['error_info']['message']}")
            return
        
        generated_code = state['generated_code']
        display_code_generation(generated_code)
        
        # 代码执行
        display_step(6, "代码执行")
        state = agent._execute_code(state)
        execution_result = state['execution_result']
        display_execution_result(execution_result)
        
        # 最终结果
        final_result = agent.get_final_result(state)
        display_final_summary(final_result)
        
        return final_result
        
    except Exception as e:
        print(f"❌ 分步演示失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def interactive_mode():
    """交互模式"""
    print_separator("交互式代码生成Agent", "=")
    print("🤖 欢迎使用代码生成Agent!")
    print("💡 你可以输入任何数据分析需求，我会为你生成并执行代码")
    print("📝 例如：'展示前10行数据'、'创建类别分布图'、'进行机器学习分类'")
    print("🚪 输入 'quit' 或 'exit' 退出程序")
    
    while True:
        try:
            print("\n" + "=" * 60)
            user_input = input("🎯 请输入你的需求: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！感谢使用代码生成Agent!")
                break
            
            if not user_input:
                print("⚠️ 请输入有效的需求")
                continue
            
            print(f"\n🔄 正在处理: {user_input}")
            
            # 询问用户选择演示模式
            print("\n选择演示模式:")
            print("1. 完整流程 (推荐) - 直接看最终结果")
            print("2. 分步演示 - 查看每个步骤的详细过程")
            
            mode_choice = input("请选择 (1/2，默认1): ").strip()
            
            if mode_choice == "2":
                result = run_step_by_step_demo(user_input)
            else:
                result = run_detailed_demo(user_input)
            
            # 询问是否继续
            continue_choice = input("\n🔄 是否继续测试其他需求? (y/n，默认y): ").strip().lower()
            if continue_choice in ['n', 'no', '否']:
                print("👋 再见！")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")

def main():
    """主函数"""
    print("🚀 代码生成Agent完整演示系统")
    
    # 预设的演示需求
    demo_requests = [
        "展示前五行数据",
        "创建类别分布饼图",
        "计算各波段的基本统计信息",
        "制作redshift分布直方图"
    ]
    
    print("\n选择运行模式:")
    print("1. 交互模式 - 自定义输入需求")
    print("2. 演示模式 - 运行预设示例")
    
    choice = input("请选择 (1/2，默认1): ").strip()
    
    if choice == "2":
        print_separator("预设演示模式", "=")
        for i, request in enumerate(demo_requests, 1):
            print(f"\n🎯 演示 {i}/{len(demo_requests)}: {request}")
            result = run_detailed_demo(request)
            
            if i < len(demo_requests):
                input("\n按回车键继续下一个演示...")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
