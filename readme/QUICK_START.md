# 🚀 Astro-Insight 快速入门

## 📋 项目主体文件

### 🎯 **核心文件** (必须了解)
1. **`complete_simple_system.py`** - 主系统文件 ⭐⭐⭐
2. **`main.py`** - 命令行入口 ⭐⭐
3. **`conf.yaml`** - 配置文件 ⭐⭐

### 🔧 **重要模块**
1. **`src/core/interfaces.py`** - 接口定义
2. **`src/tools/supabase_client.py`** - 数据库工具
3. **`src/llms/llm.py`** - LLM管理

---

## 🏃‍♂️ 快速开始

### 1. **运行项目**
```bash
# 安装依赖
pip install -r requirements.txt

# 启动系统
python main.py
```

### 2. **理解核心流程**
```
用户输入 → 身份识别 → 任务分类 → 功能处理 → 结果输出
```

### 3. **主要功能节点**
- **问答查询** (`qa`) - 智能天文问答
- **天体分类** (`classification`) - Simbad数据查询
- **数据分析** (`data_analysis`) - Supabase + 代码生成
- **文献综述** (`literature_review`) - 学术文献搜索

---

## 🔨 快速修改指南

### **添加新功能**
1. 在 `interfaces.py` 添加任务类型
2. 在 `complete_simple_system.py` 添加处理函数
3. 更新任务分类逻辑

### **修改现有功能**
- **问答**: 修改 `_handle_qa_query_with_context()`
- **分类**: 修改 `_handle_classification_query()`
- **数据分析**: 修改 `_handle_data_analysis_query()`

### **配置修改**
- **LLM**: 修改 `conf.yaml`
- **数据库**: 修改 `supabase_config.py`

---

## 📖 详细文档

查看 [PROJECT_GUIDE.md](PROJECT_GUIDE.md) 获取完整的开发指南。

---

**💡 提示**: 从 `complete_simple_system.py` 开始阅读，这是整个系统的核心！
