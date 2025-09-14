import os
import unittest
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


class TestOpenRouter(unittest.TestCase):
    def setUp(self):
        # 加载 .env（从仓库根目录）
        load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

        # 优先使用 OPENROUTER_API_KEY；没有则回落到 OPENAI_API_KEY（OpenRouter 也接受 sk-or-*）
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 中设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY")

        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

        # 初始化 OpenAI 客户端（指向 OpenRouter）
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def test_basic_conversation(self):
        """测试基本的对话功能"""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": "用一句话介绍一下 OpenRouter。"}],
            max_tokens=1000,
        )

        # 验证响应
        self.assertTrue(hasattr(completion, "choices"))
        content = completion.choices[0].message.content
        print(f"基本对话响应: {content}")
        self.assertIsInstance(content, (str, type(None)))
        self.assertTrue((content is not None) and (len(content) > 0))

    def test_complex_conversation(self):
        """测试多轮对话功能"""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": "你能用 Python 写一个支持加减乘除的函数吗？"},
                {"role": "assistant", "content": "当然，可以，请说明入参与返回值。"},
                {"role": "user", "content": "入参 a,b 与 op，返回计算结果。"},
            ],
            max_tokens=200,
        )

        # 验证响应
        self.assertTrue(hasattr(completion, "choices"))
        content = completion.choices[0].message.content
        print(f"复杂对话响应: {content}")
        self.assertIsInstance(content, (str, type(None)))
        self.assertTrue((content is not None) and (len(content) > 0))


if __name__ == "__main__":
    unittest.main()
