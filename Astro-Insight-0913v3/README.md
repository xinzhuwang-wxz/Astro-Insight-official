# 🌟 Astro-Insight 天文科研Agent系统

一个基于 LangGraph 的天文科研助手与数据智能分析系统，支持爱好者问答与专业用户的数据检索、文献综述与代码生成。

## 🚀 项目概述

- 智能问答、天体分类、网络检索与文献综述
- 代码生成 Agent：将自然语言转为可执行 Python，支持安全执行与可视化

## ✨ 核心功能

- 🤖 **智能问答**: 基于LLM的天文知识问答
- 🔍 **天体分类**: 专业的SIMBAD数据库集成分类
- 📊 **数据检索**: 支持多种天文数据源
- 🌐 **网络搜索**: Tavily搜索API集成
- 📝 **文献综述**: 自动文献检索和分析
- 🧪 **代码生成 Agent（新增）**：
  - 自然语言到代码与图表
  - 智能数据集选择（内置 SDSS/Star Types）
  - 安全沙箱执行与错误自动修复

### 支持的数据集
1. SDSS Galaxy Classification DR18（约10万条，43特征）
2. Star Type Prediction Dataset（240条，6类）

## 快速开始

### 🚀 5分钟快速部署

**步骤1：克隆项目**
```bash
git clone https://github.com/xinzhuwang-wxz/Astro-Insight.git
cd Astro-Insight
```

**步骤2：安装依赖**
```bash
pip install -r requirements.txt
```

**步骤3：配置API密钥**
```bash
# 复制环境变量模板
copy env.template .env   # Windows
# cp env.template .env   # Linux/Mac

# 编辑 .env 文件，设置Tavily API密钥
# TAVILY_API_KEY=tvly-dev-your_actual_api_key_here
```

**步骤4：启动Ollama**
```bash
ollama serve
ollama pull qwen2.5:7b
```

**步骤5：运行系统**
```bash
python main.py
```

### 环境要求

- **Python 3.8+**
- **Ollama** (本地LLM服务)
- **Tavily API Key** (网络搜索)

### 配置API密钥

#### ⚠️ 重要说明
系统**完全依赖环境变量**管理API密钥，配置文件中的API密钥已被清空。您**必须**在 `.env` 文件中设置真实的API密钥，否则系统无法正常工作。

#### 配置步骤

**步骤1：复制环境变量模板**
```bash
# Windows
copy env.template .env

# Linux/Mac
cp env.template .env
```

**步骤2：编辑 `.env` 文件**
打开 `.env` 文件，填入您的真实API密钥：

```bash
# ===========================================
# 必需配置 - 系统运行必需
# ===========================================

# Tavily搜索API (必需)
# 获取地址: https://tavily.com
# 注册后获取API密钥
TAVILY_API_KEY=tvly-dev-your_actual_api_key_here

# ===========================================
# 可选配置 - 根据需要设置
# ===========================================

# OpenAI API (可选，如果使用OpenAI服务)
# 获取地址: https://platform.openai.com
OPENAI_API_KEY=sk-your_openai_api_key_here

# DeepSeek API (可选，如果使用DeepSeek服务)
# 获取地址: https://platform.deepseek.com
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here

# ===========================================
# LLM 配置 (可选，使用默认值即可)
# ===========================================

# 本地部署 (推荐，免费)
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1

# 云端服务 (需要API密钥)
# OpenAI: LLM_PROVIDER=openai, LLM_MODEL=gpt-4o
# DeepSeek: LLM_PROVIDER=deepseek, LLM_MODEL=deepseek-chat
# 豆包: LLM_PROVIDER=doubao, LLM_MODEL=doubao-pro-32k
# Claude: LLM_PROVIDER=claude, LLM_MODEL=claude-3-5-sonnet-20241022
# Gemini: LLM_PROVIDER=gemini, LLM_MODEL=gemini-1.5-pro
```

#### 配置验证

启动系统时会自动验证配置：
```bash
python main.py --status
```

**正常输出示例**：
```
✅ 环境变量配置正常
🚀 正在初始化天文科研Agent系统...
✅ 系统初始化完成
```

**错误输出示例**：
```
⚠️  警告: 部分必需的环境变量未设置，某些功能可能不可用
🔧 环境变量配置状态:
  .env文件: ✅ 已加载
  Tavily搜索: ❌ 未配置
  LLM服务: ✅ 已配置
```

#### 获取API密钥

**Tavily搜索API**：
1. 访问 [https://tavily.com](https://tavily.com)
2. 注册账号并登录
3. 在控制台中创建API密钥
4. 复制密钥到 `.env` 文件

**OpenAI API**（可选）：
1. 访问 [https://platform.openai.com](https://platform.openai.com)
2. 注册账号并登录
3. 在API Keys页面创建新密钥
4. 复制密钥到 `.env` 文件

**DeepSeek API**（可选）：
1. 访问 [https://platform.deepseek.com](https://platform.deepseek.com)
2. 注册账号并登录
3. 在API管理页面创建密钥
4. 复制密钥到 `.env` 文件

**豆包 API**（可选）：
1. 访问 [https://www.volcengine.com/product/doubao](https://www.volcengine.com/product/doubao)
2. 注册字节跳动账号并登录
3. 在控制台创建API密钥
4. 复制密钥到 `.env` 文件

**Claude API**（可选）：
1. 访问 [https://console.anthropic.com](https://console.anthropic.com)
2. 注册Anthropic账号并登录
3. 在API Keys页面创建密钥
4. 复制密钥到 `.env` 文件

**Gemini API**（可选）：
1. 访问 [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. 使用Google账号登录
3. 创建API密钥
4. 复制密钥到 `.env` 文件

### 启动Ollama服务

```bash
# 安装并启动Ollama
ollama serve

# 拉取模型
ollama pull qwen2.5:7b
```

### 运行系统

```bash
# 交互模式
python main.py

# 单次查询
python main.py -q "分类这个天体：M87"

# 查看系统状态
python main.py --status
```

### 代码生成 Agent 快速上手
```python
from src.coder.workflow import CodeGenerationWorkflow

workflow = CodeGenerationWorkflow()
result = workflow.run("使用星类型数据集训练一个分类模型并可视化结果")
```

常用指令示例：
```python
# 数据探索
workflow.run("展示6_class_csv数据集的前5行和基本统计信息")
workflow.run("分析星类型数据集中各类别的分布情况")

# 可视化
workflow.run("绘制温度-光度散点图，按星类型着色")

# 机器学习
workflow.run("使用星类型数据训练随机森林分类器并评估性能")
```

## 环境变量管理

### 配置优先级
1. **环境变量** (`.env` 文件) - 最高优先级
2. **系统环境变量** - 次优先级  
3. **配置文件** (`conf.yaml`) - 最低优先级（仅用于非敏感配置）

### 必需配置
| 变量名 | 描述 | 获取地址 | 示例 |
|--------|------|----------|------|
| `TAVILY_API_KEY` | Tavily搜索API密钥 | [https://tavily.com](https://tavily.com) | `tvly-dev-xxx` |

### 可选配置
| 变量名 | 描述 | 获取地址 | 默认值 |
|--------|------|----------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | [https://platform.openai.com](https://platform.openai.com) | 未设置 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | [https://platform.deepseek.com](https://platform.deepseek.com) | 未设置 |
| `LLM_PROVIDER` | LLM提供商 | - | `ollama` |
| `LLM_MODEL` | LLM模型 | - | `qwen2.5:7b` |
| `LLM_BASE_URL` | LLM服务地址 | - | `http://localhost:11434/v1` |

### LLM提供商配置
| 提供商 | 模型示例 | API密钥格式 | 服务地址 |
|--------|----------|-------------|----------|
| **Ollama** (本地) | `qwen2.5:7b`, `llama3.1:8b` | `ollama` | `http://localhost:11434/v1` |
| **OpenAI** | `gpt-4o`, `gpt-3.5-turbo` | `sk-xxx` | `https://api.openai.com/v1` |
| **DeepSeek** | `deepseek-chat`, `deepseek-coder` | `sk-xxx` | `https://api.deepseek.com/v1` |
| **豆包** | `doubao-pro-32k`, `doubao-lite-4k` | `xxx` | `https://ark.cn-beijing.volces.com/api/v3` |
| **Claude** | `claude-3-5-sonnet-20241022` | `sk-ant-xxx` | `https://api.anthropic.com/v1` |
| **Gemini** | `gemini-1.5-pro`, `gemini-1.5-flash` | `xxx` | `https://generativelanguage.googleapis.com/v1beta` |

### 配置验证

系统启动时会自动验证环境变量配置：

**正常状态**：
```
✅ 环境变量配置正常
🚀 正在初始化天文科研Agent系统...
✅ 系统初始化完成
```

**配置缺失**：
```
⚠️  警告: 部分必需的环境变量未设置，某些功能可能不可用
🔧 环境变量配置状态:
  .env文件: ✅ 已加载
  Tavily搜索: ❌ 未配置
  LLM服务: ✅ 已配置
```

### 故障排除

**问题1：Tavily搜索失败**
```
Tavily 搜索错误: Unauthorized: missing or invalid API key.
```
**解决方案**：检查 `.env` 文件中的 `TAVILY_API_KEY` 是否正确设置

**问题2：环境变量未加载**
```
🔧 环境变量配置状态:
  .env文件: ❌ 未找到
```
**解决方案**：确保 `.env` 文件存在于项目根目录

**问题3：API密钥格式错误**
```
警告: 未设置 TAVILY_API_KEY，将返回空结果
```
**解决方案**：检查API密钥格式，确保以 `tvly-dev-` 开头

## 使用示例

### 爱好者问答
```
🔭 请输入您的身份与问题: 什么是黑洞？
```

### 专业分类
```
🔭 请输入您的身份与问题: 分类这个天体：M87
```

### 数据检索
```
🔭 请输入您的身份与问题: 分析M87的射电星系特征
```
## 项目结构

```
Astro-Insight/
├── src/
│   ├── coder/                 # 代码生成 Agent 核心
│   │   ├── agent.py
│   │   ├── workflow.py
│   │   ├── dataset_selector.py
│   │   ├── executor.py
│   │   ├── prompts.py
│   │   └── types.py
│   ├── config/         # 配置管理
│   │   └── env_manager.py  # 环境变量管理器
│   ├── graph/          # LangGraph工作流
│   ├── llms/           # LLM客户端
│   ├── tools/          # 工具模块
│   └── ...
├── dataset/
│   ├── dataset/
│   └── full_description/
├── output/
├── conf.yaml           # 主配置文件
├── env.template        # 环境变量模板
├── main.py            # 主程序入口
└── requirements.txt   # 依赖列表
```

## 开发说明

### 添加新的API服务

1. 在 `env.template` 中添加环境变量
2. 在 `src/config/env_manager.py` 中添加配置获取方法
3. 在相应的模块中使用 `get_api_key()` 获取密钥

### 自定义LLM模型

#### 切换到云端LLM服务

**OpenAI配置**：
```bash
# 在 .env 文件中设置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=sk-your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
```

**豆包配置**：
```bash
# 在 .env 文件中设置
LLM_PROVIDER=doubao
LLM_MODEL=doubao-pro-32k
LLM_API_KEY=your_doubao_api_key_here
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

**DeepSeek配置**：
```bash
# 在 .env 文件中设置
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-your_deepseek_api_key_here
LLM_BASE_URL=https://api.deepseek.com/v1
```

**Claude配置**：
```bash
# 在 .env 文件中设置
LLM_PROVIDER=claude
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=sk-ant-your_claude_api_key_here
LLM_BASE_URL=https://api.anthropic.com/v1
```

**Gemini配置**：
```bash
# 在 .env 文件中设置
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-pro
LLM_API_KEY=your_gemini_api_key_here
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

#### 本地LLM配置

**Ollama配置**（推荐）：
```bash
# 在 .env 文件中设置
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
```

**支持的Ollama模型**：
- `qwen2.5:7b` - 通义千问2.5 7B（推荐）
- `llama3.1:8b` - Llama 3.1 8B
- `llama3.1:70b` - Llama 3.1 70B（需要更多内存）
- `gemma2:9b` - Google Gemma 2 9B
- `mistral:7b` - Mistral 7B

## 安全说明

### 🔒 敏感信息保护
- **`.env` 文件包含敏感信息**，已加入 `.gitignore`
- **请勿将包含真实API密钥的文件提交到版本控制**
- **生产环境建议使用系统环境变量而非文件**

### 🛡️ 最佳实践
1. **定期轮换API密钥**：建议每3-6个月更换一次API密钥
2. **限制API权限**：在服务提供商处设置适当的API使用限制
3. **监控API使用**：定期检查API使用情况，发现异常及时处理
4. **备份配置**：将 `.env` 文件备份到安全位置，但不要提交到代码仓库

### ⚠️ 安全警告
- **不要在代码中硬编码API密钥**
- **不要在公开的聊天、邮件或文档中分享API密钥**
- **不要在截图或录屏中暴露API密钥**
- **如果API密钥泄露，立即在服务提供商处撤销并重新生成**

### 🔍 配置检查清单
- [ ] `.env` 文件已创建并包含真实API密钥
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 配置文件 `conf.yaml` 中的API密钥已清空
- [ ] 系统启动时显示"环境变量配置正常"
- [ ] Tavily搜索功能正常工作

## 故障排除

- Tavily 未授权：检查 `.env` 中 `TAVILY_API_KEY`
- .env 未加载：确保根目录存在 `.env`
- API 密钥格式错误：确认提供商要求的格式

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

**注意**: 请确保不要将包含真实API密钥的 `.env` 文件提交到版本控制系统。
