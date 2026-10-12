#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
运行所有单元测试并生成报告
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(test_path: str = "tests", verbose: bool = True, coverage: bool = False):
    """
    运行测试
    
    Args:
        test_path: 测试路径
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
    """
    # 添加src目录到Python路径
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    cmd.append(test_path)
    
    print(f"运行测试命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败，退出码: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ 未找到pytest，请先安装: pip install pytest")
        return False


def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        "pytest",
        "pytest-cov",
        "cryptography",
        "pyyaml"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行Astro-Insight测试")
    parser.add_argument(
        "--test-path", 
        default="tests",
        help="测试路径 (默认: tests)"
    )
    parser.add_argument(
        "--no-verbose", 
        action="store_true",
        help="不显示详细输出"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="仅检查依赖"
    )
    
    args = parser.parse_args()
    
    print("Astro-Insight 测试运行器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_deps:
        print("✅ 依赖检查完成")
        return
    
    # 运行测试
    success = run_tests(
        test_path=args.test_path,
        verbose=not args.no_verbose,
        coverage=args.coverage
    )
    
    if success:
        print("\n🎉 测试完成！")
        if args.coverage:
            print("📊 覆盖率报告已生成: htmlcov/index.html")
    else:
        print("\n💥 测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
