# 代码生成Agent设置指南

## 🎯 现在可以运行了！

我已经为你的代码生成Agent完成了所有必要的配置。

### ✅ 已完成的配置

1. **LLM配置**: 在`Astro-Insight/conf.yaml`中添加了`CODE_MODEL`配置
2. **模块导出**: 修复了`src/coder/__init__.py`的导出问题
3. **Agent配置**: 在`src/config/agents.py`中添加了coder agent的LLM映射

### 🚀 快速开始

#### 1. 最简单的测试
```bash
cd C:\Users\32830\Desktop\heckathon
python simple_coder_test.py
```

这个脚本会：
- 测试基本的模块导入
- 验证配置是否正确
- 运行最简单的"展示前五行数据"请求

#### 2. 配置验证测试
```bash
python test_coder_config.py
```

这个脚本会全面测试：
- 配置文件加载
- LLM实例创建
- Agent创建
- 工作流测试

#### 3. 完整演示
```bash
python quick_coder_demo.py
```

### 📋 配置说明

#### conf.yaml中的新配置
```yaml
# 代码生成专用模型配置
CODE_MODEL:
  base_url: http://localhost:11434/v1
  model: "qwen2.5:7b"  # 可以使用相同模型，或者专门的代码模型如 "codellama" 
  api_key: "ollama"
  max_retries: 3
  verify_ssl: false
```

### 🔧 使用方式

#### 基本使用
```python
from src.coder.workflow import CodeGenerationWorkflow

workflow = CodeGenerationWorkflow()
result = workflow.run("展示前五行数据")

if result['success']:
    print("代码:")
    print(result['code'])
    print("\n结果:")
    print(result['output'])
```

#### 支持的请求类型

**简单操作 (SIMPLE)**
- `"展示前五行数据"`
- `"显示数据集基本信息"`
- `"计算基本统计信息"`

**数据可视化 (MODERATE)**
- `"创建类别分布饼图"`
- `"画redshift分布直方图"`
- `"制作波段相关性热力图"`

**复杂分析 (COMPLEX)**
- `"使用随机森林进行分类"`
- `"进行聚类分析"`
- `"训练神经网络模型"`

### 🛠️ 前置要求

1. **Ollama运行**: 确保Ollama在`http://localhost:11434`运行
2. **模型下载**: 确保已下载`qwen2.5:7b`模型
3. **数据集**: 确保SDSS数据集在正确位置

### 🔍 故障排除

#### 常见问题

1. **模块导入失败**
   - 确保在正确的项目目录下运行
   - 检查Python路径配置

2. **LLM连接失败**
   - 检查Ollama是否运行: `curl http://localhost:11434/api/tags`
   - 确认模型已下载: `ollama list`

3. **数据集未找到**
   - 检查`dataset/full_description/`目录
   - 确认数据文件存在

#### 调试命令

```bash
# 检查Ollama状态
curl http://localhost:11434/api/tags

# 检查模型列表
ollama list

# 如果需要下载模型
ollama pull qwen2.5:7b

# 或者使用代码专用模型
ollama pull codellama
```

### 🎯 推荐的测试顺序

1. 运行`simple_coder_test.py` - 验证基本功能
2. 运行`test_coder_config.py` - 验证完整配置
3. 运行`quick_coder_demo.py` - 体验完整功能
4. 使用`src/coder/example_usage.py` - 交互式探索

### 🔮 下一步

如果基本测试通过，你可以：

1. **集成到现有图形系统**: 将coder节点添加到主要的LangGraph工作流中
2. **扩展数据集**: 添加更多数据集描述文件
3. **优化模型**: 尝试使用专门的代码生成模型如CodeLlama
4. **自定义Prompt**: 根据具体需求调整代码生成的Prompt

现在运行 `python simple_coder_test.py` 开始测试吧！🚀
