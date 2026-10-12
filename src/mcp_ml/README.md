# MCP ML模块

基于MCP (Model Context Protocol) 的机器学习模块，提供天文图像分类和深度学习功能。

## 系统架构

- **MCP Server** (`server.py`): 提供机器学习工具的MCP服务器
- **MCP Client** (`client.py`): 与MCP ML服务器通信的客户端
- **ML Modules**: 数据加载、预处理、模型定义、训练、结果分析

## 功能特性

### 支持的ML任务

1. **图像分类**
   - 星系形态分类
   - 天体类型识别
   - 图像质量评估

2. **模型训练**
   - CNN模型构建
   - 数据增强
   - 模型评估

3. **结果分析**
   - 训练历史可视化
   - 混淆矩阵生成
   - 性能指标计算

### 技术特性

- 🤖 **深度学习**: 基于TensorFlow/Keras的CNN模型
- 🔄 **数据增强**: 支持多种图像增强技术
- 🛠️ **MCP协议**: 标准化的工具调用接口
- 📊 **可视化**: 训练过程和结果的可视化
- 🔍 **多格式支持**: JPG, PNG, TIFF等图像格式

## 安装和配置

### 1. 虚拟环境

模块包含独立的虚拟环境：
```bash
# 激活虚拟环境
.venv/Scripts/activate  # Windows
.venv/bin/activate      # Linux/Mac
```

### 2. 依赖管理

使用uv进行依赖管理：
```bash
# 安装依赖
uv sync

# 或使用pip
pip install -r requirements.txt
```

## 使用方法

### 运行MCP服务器

```bash
# 直接运行
python server.py

# 或通过MCP Inspector调试
npx @modelcontextprotocol/inspector python server.py
```

### 通过客户端调用

```python
from src.mcp_ml.client import get_ml_client

# 获取客户端
client = get_ml_client()

# 运行ML训练流程
result = client.run_pipeline()
```

### 集成到工作流

```python
# 在multimark节点中自动调用
# 用户说"训练模型"或"图像分类"时会自动启动
```

## 项目结构

```
src/mcp_ml/
├── client.py              # MCP客户端
├── server.py              # MCP服务器
├── data_loading.py        # 数据加载
├── data_preprocessing.py  # 数据预处理
├── model_definition.py    # 模型定义
├── model_training.py      # 模型训练
├── result_analysis.py     # 结果分析
├── config/
│   └── config.yaml        # 配置文件
├── sample_data/           # 样本数据
│   └── images/
├── .venv/                 # 虚拟环境
├── requirements.txt       # Python依赖
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁定
├── .python-version       # Python版本
└── README.md             # 项目说明
```

## 配置说明

### config.yaml

```yaml
data_preprocessing:
  image_size: [128, 128]
  batch_size: 32
  
model_training:
  epochs: 10
  optimizer: 'adam'
  
result_analysis:
  plot_history: true
  confusion_matrix: true
```

## 技术栈

- **Python 3.12**: 主要编程语言
- **TensorFlow/Keras**: 深度学习框架
- **MCP Python SDK**: Model Context Protocol支持
- **uv**: 包管理工具
- **scikit-learn**: 机器学习工具
- **matplotlib/seaborn**: 数据可视化

## 开发和调试

### 启用调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试连接

```python
from src.mcp_ml.client import test_ml_client
import asyncio

# 测试MCP ML客户端
asyncio.run(test_ml_client())
```

## 常见问题

### Q: 虚拟环境启动失败
A: 确保Python 3.12已安装，并检查.venv目录完整性

### Q: TensorFlow导入错误
A: 激活虚拟环境后重新安装：`pip install tensorflow`

### Q: MCP连接失败
A: 检查MCP相关依赖是否正确安装

## 贡献

欢迎提交Issue和Pull Request来改进这个模块！

## 许可证

MIT License
