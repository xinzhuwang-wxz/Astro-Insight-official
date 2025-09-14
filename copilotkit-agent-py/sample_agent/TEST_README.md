# OpenRouter Agent 测试文档

## 📋 概述

本文档描述了 CopilotKit Agent 从 Anthropic Claude 迁移到 OpenRouter 后的综合测试验证流程。

## 🎯 测试目标

验证以下功能正常工作：
- ✅ OpenRouter API 基础调用
- ✅ OpenRouter 多轮对话功能
- ✅ Agent 模块正确导入
- ✅ LangChain LLM 集成
- ✅ LangGraph 图状态管理
- ✅ 工具集成（搜索功能）
- ✅ 环境配置正确性

## 🚀 快速开始

### 环境准备

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   
   在项目根目录创建 `.env` 文件：
   ```env
   # OpenRouter 配置
   OPENROUTER_API_KEY=sk-or-your-api-key-here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=google/gemini-2.5-flash
   
   # 备用配置（可选）
   OPENAI_API_KEY=your-openai-compatible-key
   ```

### 运行测试

#### 🌟 推荐：综合测试（包含所有测试项目）
```bash
cd sample_agent
python test_comprehensive.py
```

#### 🎯 专门测试：Agent.py LangGraph 直接测试
```bash
cd sample_agent
python test_agent_direct.py
```

#### 其他测试方式
```bash
# 仅测试 Agent 模块
python test_agent.py

# 使用 unittest 模块运行
python -m unittest test_comprehensive -v
```

## 📊 测试项目详情

### 🔌 OpenRouter API 测试组

#### 🔍 API 测试 1：基本对话
- **目的**：验证 OpenRouter API 基础连接和单轮对话
- **测试消息**：`"用一句话介绍一下 OpenRouter。"`
- **验证项目**：
  - API 响应成功
  - 响应内容不为空
  - 响应格式正确
- **预期结果**：获得关于 OpenRouter 的简介

#### 💭 API 测试 2：多轮对话
- **目的**：验证 OpenRouter 上下文理解和多轮交互能力
- **测试场景**：编程任务的多轮对话
- **验证项目**：
  - 多轮消息正确处理
  - 上下文保持完整
  - 代码生成质量
- **预期结果**：生成符合要求的 Python 函数

### 🤖 Agent 模块测试组

#### 🔍 Agent 测试 1：模块导入验证
- **目的**：确保 agent 模块及其核心组件可以正常导入
- **验证项目**：
  - State 类
  - chatbot 函数
  - graph 对象
  - llm 实例
  - search_tool 工具
- **预期结果**：所有组件导入成功，LLM 类型为 `ChatOpenAI`

#### 💬 Agent 测试 2：LLM 基本调用
- **目的**：验证通过 LangChain 的 OpenRouter 连接
- **测试消息**：`"你好，请用一句话介绍自己。"`
- **验证项目**：
  - LangChain 封装正确
  - API 响应成功
  - 消息类型正确
- **预期结果**：获得有意义的 AI 自我介绍

#### 🕸️ Agent 测试 3：LangGraph 图调用
- **目的**：验证复杂的图状态管理和工作流
- **测试消息**：`"什么是 AI？用一句话回答。"`
- **验证项目**：
  - 图正确处理输入
  - 状态管理正常
  - 返回正确数据结构
- **预期结果**：通过图获得智能回复

#### 🔍 Agent 测试 附加：搜索工具
- **目的**：验证集成工具的正常工作
- **测试查询**：`"人工智能"`
- **验证项目**：
  - 工具调用成功
  - 返回模拟搜索结果
  - 结果格式正确
- **预期结果**：获得包含查询词的搜索结果

### 🎯 专门测试：Agent.py LangGraph 直接测试

#### 🚀 完整工作流测试
- **文件**：`test_agent_direct.py`
- **目的**：直接测试 `agent.py` 中的完整 LangGraph 功能
- **测试场景**：
  1. 基本自我介绍
  2. 搜索请求（触发工具调用）
  3. 知识问答
  4. 专家协助请求（触发 RequestAssistance）
- **验证项目**：
  - LangGraph 图的完整调用流程
  - OpenRouter LLM 集成
  - 工具调用机制
  - 状态管理功能
  - 人工协助请求机制
- **特点**：
  - ✅ 直接调用 `agent.py` 的所有组件
  - ✅ 详细的调试输出和状态跟踪
  - ✅ 多场景覆盖测试
  - ✅ 独立运行，不依赖 unittest

## 📈 测试输出示例

```
================================================================================
🤖 OpenRouter Agent 综合测试套件
================================================================================
📁 测试目录: E:\work\work24\copilotkit-agent-py\sample_agent
🐍 Python 路径: E:\work\work24\copilotkit-agent-py\sample_agent
📄 agent.py 文件: ✅ 存在
--------------------------------------------------------------------------------

================================================================================
🚀 开始运行综合测试...
================================================================================

🔌 [API 测试 1/2] OpenRouter 基本对话测试
----------------------------------------
📤 发送消息: '用一句话介绍一下 OpenRouter。'
📥 API 响应:
   📝 OpenRouter是一个AI模型路由平台，让开发者通过统一API访问多种大语言模型。
   📊 响应长度: 42 字符
   🎯 使用模型: google/gemini-2.5-flash
🎉 API 基本对话测试通过

💭 [API 测试 2/2] OpenRouter 多轮对话测试
----------------------------------------
📤 发送多轮对话...
   👤 用户: 你能用 Python 写一个支持加减乘除的函数吗？
   🤖 助手: 当然，可以，请说明入参与返回值。
   👤 用户: 入参 a,b 与 op，返回计算结果。
📥 API 响应:
   📝 def calculate(a, b, op):
       if op == '+': return a + b
       elif op == '-': return a - b
       elif op == '*': return a * b
       elif op == '/': return a / b if b != 0 else "除零错误"
   📊 响应长度: 156 字符
🎉 API 多轮对话测试通过

🔍 [Agent 测试 1/3] Agent 模块导入测试
----------------------------------------
✅ Agent 模块导入成功
🤖 LLM 类型: ChatOpenAI
🎯 使用模型: google/gemini-2.5-flash
✅ State
✅ chatbot
✅ graph
✅ llm
✅ search_tool
🎉 模块导入测试通过

💬 [Agent 测试 2/3] LLM 基本调用测试
----------------------------------------
📤 发送消息: '你好，请用一句话介绍自己。'
📥 LLM 响应:
   📝 你好，我是一个大型语言模型，由 Google 训练。
   📊 响应长度: 20 字符
   📋 消息类型: AIMessage
🎉 LLM 调用测试通过

🕸️ [Agent 测试 3/3] LangGraph 图调用测试
----------------------------------------
📤 发送消息: '什么是 AI？用一句话回答。'
🔧 使用配置: thread_id = test_thread_123
📊 返回类型: AddableValuesDict
📥 图响应:
   📝 AI是人工智能的简称，指的是通过计算机程序模拟、延伸和扩展人类智能的技术。
   📊 响应长度: 39 字符
   📋 消息类型: AIMessage
🎉 图调用测试通过

🔍 [Agent 测试 附加] 搜索工具测试
----------------------------------------
📤 测试搜索工具: '人工智能'
📥 搜索结果:
   📝 关于 '人工智能' 的搜索结果：这是一个模拟的搜索结果。在实际应用中，这里会连接到真实的搜索API。
   📊 结果长度: 54 字符
🎉 搜索工具测试通过

================================================================================
✨ 所有测试通过！
================================================================================
```

## 🔧 故障排除

### 常见问题

1. **模块导入失败**
   ```
   ModuleNotFoundError: No module named 'agent'
   ```
   **解决方案**：确保在 `sample_agent` 目录下运行测试

2. **API 密钥错误**
   ```
   请在 .env 中设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY
   ```
   **解决方案**：检查 `.env` 文件配置和密钥有效性

3. **网络连接问题**
   ```
   Connection timeout
   ```
   **解决方案**：检查网络连接和 OpenRouter 服务状态

4. **配额不足**
   ```
   Error code: 402 - This request requires more credits
   ```
   **解决方案**：充值 OpenRouter 账户或降低 `max_tokens` 参数

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查环境变量**
   ```python
   import os
   print("API Key:", os.getenv("OPENROUTER_API_KEY")[:10] + "...")
   print("Base URL:", os.getenv("OPENROUTER_BASE_URL"))
   ```

## 📝 技术说明

### 架构变更
- **原架构**：LangChain + Anthropic Claude
- **新架构**：LangChain + OpenRouter (Google Gemini)
- **工具变更**：Tavily Search → 模拟搜索工具

### 关键组件
- **LLM 提供商**：OpenRouter API
- **模型**：google/gemini-2.5-flash
- **图框架**：LangGraph
- **状态管理**：MemorySaver + CopilotKitState

## 📚 相关资源

- [OpenRouter API 文档](https://openrouter.ai/docs)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [CopilotKit 文档](https://docs.copilotkit.ai/)

## 🤝 贡献指南

如需添加新的测试用例或改进现有测试：

1. 在 `TestAgent` 类中添加新的测试方法
2. 遵循命名约定：`test_<功能名称>`
3. 添加详细的打印输出和断言
4. 更新本文档

---

*最后更新：2024年12月*