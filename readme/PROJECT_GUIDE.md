# 🌌 Astro-Insight 项目开发指南

## 📋 项目概述

**Astro-Insight** 是一个基于大语言模型的交互式天文研究助手系统，集成了多种AI技术为天文爱好者和专业研究人员提供智能化的天文数据分析服务。

### 🎯 核心功能
- **智能问答** - 基于Ollama+Qwen的天文知识问答
- **天体分类** - 使用Simbad API进行真实天体数据查询
- **数据分析** - 整合Supabase数据检索、代码生成和执行
- **文献综述** - 基于Tavily API的学术文献搜索
- **多用户支持** - 区分业余爱好者和专业用户

---

## 🏗️ 项目架构

### 📁 核心文件结构

```
Astro-Insight/
├── 📄 主体文件
│   ├── complete_simple_system.py    # 🎯 主系统文件（核心）
│   ├── complete_astro_system.py     # 🔄 完整系统（备用）
│   ├── main.py                      # 🚀 命令行入口
│   └── server.py                    # 🌐 Web服务入口
│
├── 📁 核心模块 (src/)
│   ├── core/                        # 🏛️ 核心架构
│   │   ├── interfaces.py            # 📋 接口定义
│   │   ├── container.py             # 🏗️ 依赖注入容器
│   │   └── implementations.py       # ⚙️ 具体实现
│   │
│   ├── tools/                       # 🛠️ 工具集
│   │   ├── simbad_client.py         # 🌟 Simbad API客户端
│   │   ├── supabase_client.py       # 🗄️ Supabase数据库客户端
│   │   ├── python_repl.py           # 🐍 Python代码执行
│   │   └── language_processor.py    # 🌍 多语言处理
│   │
│   ├── llms/                        # 🤖 大语言模型
│   │   ├── llm.py                   # 🔧 LLM工厂和配置
│   │   └── providers/               # 🔌 模型提供商
│   │
│   ├── database/                    # 💾 数据存储
│   │   ├── local_storage.py         # 💿 本地SQLite存储
│   │   └── enhanced_schema.py       # 📊 增强数据库架构
│   │
│   └── prompts/                     # 📝 提示词工程
│       ├── my_prompts.md            # 📋 提示词模板
│       └── template.py              # 🎨 模板引擎
│
├── 📁 配置文件
│   ├── conf.yaml                    # ⚙️ 主配置文件
│   ├── supabase_config.py           # 🗄️ Supabase配置
│   └── requirements.txt             # 📦 依赖包列表
│
└── 📁 测试和文档
    ├── tests/                       # 🧪 测试文件
    ├── docs/                        # 📚 文档
    └── PROJECT_GUIDE.md             # 📖 本指南
```

---

## 🎯 主体文件详解

### 1. **complete_simple_system.py** - 主系统文件 ⭐

**作用**: 系统的核心实现，包含所有主要功能逻辑

**关键类**:
```python
class CompleteSimpleAstroSystem:
    """完整功能的天文科研系统 - 简化版"""
```

**主要方法**:
- `process_query()` - 主查询处理入口
- `_identify_user_type()` - 用户类型识别
- `_classify_task()` - 任务分类
- `_handle_*_query()` - 各功能节点处理
- `_handle_data_analysis_query()` - 数据分析（新增）

**如何修改**:
1. **添加新功能**: 在相应的 `_handle_*_query()` 方法中添加逻辑
2. **修改任务分类**: 更新 `_classify_task()` 方法中的关键词
3. **调整用户识别**: 修改 `_identify_user_type()` 中的专业关键词列表

### 2. **main.py** - 命令行入口

**作用**: 提供命令行交互界面

**主要功能**:
- 交互式问答模式
- 单次查询模式
- 系统状态查看
- 会话管理

**如何修改**:
- 添加新的命令行参数
- 修改交互界面显示
- 扩展会话管理功能

### 3. **server.py** - Web服务入口

**作用**: 提供Web API服务

**主要功能**:
- RESTful API接口
- WebSocket支持
- 静态文件服务

---

## 🔧 核心模块详解

### 1. **src/core/interfaces.py** - 接口定义

**作用**: 定义系统的核心接口，实现依赖倒置原则

**关键枚举**:
```python
class UserType(Enum):
    AMATEUR = "amateur"      # 业余爱好者
    PROFESSIONAL = "professional"  # 专业用户

class TaskType(Enum):
    QA = "qa"                        # 问答查询
    CLASSIFICATION = "classification" # 天体分类
    DATA_ANALYSIS = "data_analysis"   # 数据分析（整合）
    LITERATURE_REVIEW = "literature_review"  # 文献综述
```

**如何修改**:
- 添加新的用户类型
- 定义新的任务类型
- 扩展接口方法

### 2. **src/tools/** - 工具集

#### **simbad_client.py** - Simbad API客户端
```python
class SimbadClient:
    def search_object(self, name: str) -> Dict[str, Any]
    def get_object_info(self, name: str) -> Dict[str, Any]
```

#### **supabase_client.py** - Supabase数据库客户端
```python
class SupabaseClient:
    def query_data(self, table_name: str, filters: Dict, limit: int) -> Dict
    def save_query_result(self, data: List[Dict], filename: str) -> Dict
```

**如何修改**:
- 添加新的API客户端
- 扩展数据库查询功能
- 修改数据格式处理

### 3. **src/llms/llm.py** - LLM管理

**作用**: 管理不同的大语言模型提供商

**支持的模型**:
- Ollama (本地)
- OpenAI
- DeepSeek
- 阿里云DashScope

**如何修改**:
- 添加新的模型提供商
- 修改模型配置
- 调整提示词处理

---

## 🚀 如何阅读项目

### 1. **从入口开始**
```bash
# 命令行模式
python main.py

# Web服务模式  
python server.py
```

### 2. **理解数据流**
```
用户输入 → 身份识别 → 任务分类 → 功能处理 → 结果输出
    ↓         ↓         ↓         ↓         ↓
  文本     业余/专业   任务类型   具体服务   格式化回答
```

### 3. **关键处理流程**
```python
# 在 complete_simple_system.py 中
def process_query(self, session_id: str, user_input: str):
    # 1. 身份识别
    user_type = self._identify_user_type(user_input)
    
    # 2. 任务分类
    task_type = self._classify_task_with_context(user_input, user_type, session_id)
    
    # 3. 功能处理
    if task_type == "qa":
        result = self._handle_qa_query_with_context(...)
    elif task_type == "data_analysis":
        result = self._handle_data_analysis_query(...)
    # ... 其他功能
```

---

## 🔨 如何修改项目

### 1. **添加新功能节点**

**步骤1**: 在 `interfaces.py` 中添加新的任务类型
```python
class TaskType(Enum):
    NEW_FEATURE = "new_feature"  # 新功能
```

**步骤2**: 在 `complete_simple_system.py` 中添加处理函数
```python
def _handle_new_feature_query(self, user_input: str, user_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """处理新功能查询"""
    # 实现新功能逻辑
    pass
```

**步骤3**: 在主处理逻辑中添加分支
```python
elif task_type == "new_feature":
    result = self._handle_new_feature_query(user_input, user_type, state)
```

**步骤4**: 更新任务分类逻辑
```python
new_feature_keywords = ["关键词1", "关键词2"]
if any(keyword in user_input for keyword in new_feature_keywords):
    return "new_feature"
```

### 2. **修改现有功能**

**修改问答功能**:
- 文件: `complete_simple_system.py`
- 方法: `_handle_qa_query_with_context()`
- 修改: 调整LLM提示词或处理逻辑

**修改分类功能**:
- 文件: `complete_simple_system.py`
- 方法: `_handle_classification_query()`
- 修改: 调整Simbad查询或分类规则

**修改数据分析功能**:
- 文件: `complete_simple_system.py`
- 方法: `_handle_data_analysis_query()`
- 修改: 调整Supabase查询或代码生成逻辑

### 3. **添加新的工具**

**步骤1**: 在 `src/tools/` 中创建新工具文件
```python
# src/tools/new_tool.py
class NewTool:
    def __init__(self):
        pass
    
    def process(self, data):
        # 工具逻辑
        pass
```

**步骤2**: 在主系统中导入和使用
```python
from tools.new_tool import NewTool

# 在相应的方法中使用
tool = NewTool()
result = tool.process(data)
```

### 4. **修改配置**

**LLM配置**: 修改 `conf.yaml`
```yaml
BASIC_MODEL:
  base_url: http://localhost:11434/v1
  model: "qwen2.5:7b"
  api_key: "ollama"
```

**数据库配置**: 修改 `supabase_config.py`
```python
SUPABASE_CONFIG = {
    "url": "your_supabase_url",
    "anon_key": "your_api_key"
}
```

---

## 🧪 测试和调试

### 1. **运行测试**
```bash
# 运行所有测试
python run_tests.py

# 测试特定功能
python test_supabase.py
python test_galaxy_table.py
```

### 2. **调试模式**
```python
# 在代码中添加调试信息
print(f"Debug: {variable}")
import logging
logging.debug("Debug message")
```

### 3. **交互式测试**
```bash
# 启动交互式测试
python interactive_test.py
```

---

## 📚 开发最佳实践

### 1. **代码组织**
- 保持单一职责原则
- 使用清晰的命名
- 添加适当的注释
- 遵循现有的代码风格

### 2. **错误处理**
- 使用try-catch包装外部调用
- 提供有意义的错误信息
- 实现降级处理机制

### 3. **配置管理**
- 将配置与代码分离
- 使用环境变量存储敏感信息
- 提供默认配置

### 4. **测试**
- 为新功能编写测试
- 测试边界情况
- 保持测试的独立性

---

## 🚀 部署指南

### 1. **本地部署**
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件

# 启动服务
python main.py
```

### 2. **Docker部署**
```dockerfile
# 创建 Dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### 3. **云部署**
- 配置Supabase数据库
- 设置环境变量
- 部署到云平台

---

## 📞 支持和贡献

### 1. **问题报告**
- 使用GitHub Issues
- 提供详细的错误信息
- 包含复现步骤

### 2. **功能请求**
- 描述功能需求
- 说明使用场景
- 提供实现建议

### 3. **代码贡献**
- Fork项目
- 创建功能分支
- 提交Pull Request

---

## 📖 相关文档

- [README.md](README.md) - 项目介绍
- [src/database/README.md](src/database/README.md) - 数据库模块说明
- [PHASE1_IMPROVEMENTS.md](PHASE1_IMPROVEMENTS.md) - 第一阶段改进
- [PHASE2_ARCHITECTURE_ANALYSIS.md](PHASE2_ARCHITECTURE_ANALYSIS.md) - 架构分析

---

**🎯 总结**: 这个项目采用模块化设计，核心逻辑集中在 `complete_simple_system.py` 中，通过清晰的接口和工具集实现功能扩展。修改时请遵循现有的架构模式，保持代码的一致性和可维护性。
