#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务测试脚本
专注于核心功能测试，便于学习
"""

import requests
import json
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self):
        """测试健康检查"""
        logger.info("🔍 测试健康检查...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ 健康检查通过: {data}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 健康检查失败: {e}")
            return False
    
    def test_status(self):
        """测试系统状态"""
        logger.info("🔍 测试系统状态...")
        
        try:
            response = self.session.get(f"{self.base_url}/status")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ 系统状态: {data['status']} - {data['message']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 系统状态检查失败: {e}")
            return False
    
    def test_query(self, query: str, user_type: str = None):
        """测试查询功能"""
        logger.info(f"🔍 测试查询: {query[:30]}...")
        
        try:
            payload = {
                "query": query,
                "user_type": user_type
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/query", json=payload)
            end_time = time.time()
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ 查询成功:")
            logger.info(f"   - 执行时间: {data['execution_time']:.2f}秒")
            logger.info(f"   - 实际时间: {end_time - start_time:.2f}秒")
            logger.info(f"   - 用户类型: {data['data'].get('user_type', 'N/A')}")
            logger.info(f"   - 任务类型: {data['data'].get('task_type', 'N/A')}")
            logger.info(f"   - 是否完成: {data['data'].get('is_complete', False)}")
            logger.info(f"   - 回答长度: {len(data['data'].get('answer', ''))} 字符")
            
            # 注意：已移除token统计功能
            
            if data['data'].get('answer'):
                answer_preview = data['data']['answer'][:100] + "..." if len(data['data']['answer']) > 100 else data['data']['answer']
                logger.info(f"   - 回答预览: {answer_preview}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
            return False
    
    def test_multiple_queries(self):
        """测试多个查询"""
        logger.info("🔍 测试多个查询...")
        
        test_cases = [
            {"query": "什么是黑洞？", "user_type": "amateur"},
            {"query": "分类这个天体：M87", "user_type": "professional"},
            {"query": "绘制天体位置图", "user_type": "professional"},
            {"query": "分析M87的射电星系特征", "user_type": "professional"}
        ]
        
        success_count = 0
        total_time = 0
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"  测试用例 {i}/{len(test_cases)}: {test_case['query'][:30]}...")
            
            try:
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/query", json=test_case)
                end_time = time.time()
                
                response.raise_for_status()
                data = response.json()
                
                if data['success']:
                    success_count += 1
                    total_time += data['execution_time']
                    logger.info(f"    ✅ 成功 ({data['execution_time']:.2f}s)")
                else:
                    logger.error(f"    ❌ 失败: {data['message']}")
                    
            except Exception as e:
                logger.error(f"    ❌ 异常: {e}")
        
        logger.info(f"📊 测试结果: {success_count}/{len(test_cases)} 成功")
        if success_count > 0:
            logger.info(f"📊 平均执行时间: {total_time/success_count:.2f}秒")
        
        return success_count == len(test_cases)
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始运行API测试")
        logger.info("=" * 50)
        
        tests = [
            ("健康检查", self.test_health),
            ("系统状态", self.test_status),
            ("单次查询", lambda: self.test_query("什么是黑洞？", "amateur")),
            ("多查询测试", self.test_multiple_queries)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 运行测试: {test_name}")
            try:
                if test_func():
                    passed += 1
                    logger.info(f"✅ {test_name} 通过")
                else:
                    logger.error(f"❌ {test_name} 失败")
            except Exception as e:
                logger.error(f"❌ {test_name} 异常: {e}")
        
        logger.info("\n" + "=" * 50)
        logger.info(f"📊 测试总结: {passed}/{total} 通过")
        
        if passed == total:
            logger.info("🎉 所有测试通过！")
        else:
            logger.warning(f"⚠️  {total - passed} 个测试失败")
        
        return passed == total

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API服务测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务地址")
    parser.add_argument("--test", help="运行特定测试: health, status, query, multiple")
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    
    if args.test:
        if args.test == "health":
            tester.test_health()
        elif args.test == "status":
            tester.test_status()
        elif args.test == "query":
            tester.test_query("什么是黑洞？", "amateur")
        elif args.test == "multiple":
            tester.test_multiple_queries()
        else:
            logger.error(f"未知测试: {args.test}")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()
