# 天体物理学TAP查询系统

这是一个基于MCP (Model Context Protocol) 和LangGraph的天体物理学数据查询系统，支持通过自然语言查询Simbad天文数据库。

## 系统架构

- **MCP Server** (`server.py`): 提供天体物理学查询工具的MCP服务器
- **TAP Client** (`tap_client.py`): Simbad TAP服务的客户端，处理ADQL查询
- **Query Tools** (`tools.py`): 封装的查询工具函数
- **LangGraph Client** (`client.py`): 使用豆包API和LangGraph的智能查询客户端

## 功能特性

### 支持的查询类型

1. **天体基础信息查询**
   - 根据天体标识符获取坐标、视差、径向速度等基本参数
   - 示例："Give me basic info about M13"

2. **参考文献查询**
   - 获取与特定天体相关的研究论文和参考文献
   - 示例："Find references for Vega"

3. **坐标搜索**
   - 根据天球坐标搜索附近的天体对象
   - 示例："Search objects near RA=250.4, DEC=36.5"

### 技术特性

- 🤖 **智能查询**: 使用豆包API理解自然语言输入
- 🔄 **异步处理**: 支持异步查询和并发处理
- 🛠️ **MCP协议**: 标准化的工具调用接口
- 📊 **结构化数据**: VOTable格式数据解析
- 🔍 **ADQL查询**: 支持天文数据查询语言

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的豆包API密钥：
```env
DOUBAO_API_KEY=your_actual_api_key_here
```

### 3. 获取豆包API密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/ark)
2. 注册账号并申请API密钥
3. 将密钥填入 `.env` 文件

## 使用方法

### 运行LangGraph客户端（推荐）

```bash
python client.py
```

这将启动交互式查询界面，支持自然语言输入。系统会自动：
1. 分析您的查询意图
2. 选择合适的工具
3. 执行TAP查询
4. 生成自然语言回答

### 测试单个组件

测试TAP客户端：
```bash
python tap_client.py
```

测试查询工具：
```bash
python tools.py
```

## 查询示例

### 基础信息查询
```
🔍 请输入您的查询: Give me basic info about M13
```

### 文献查询
```
🔍 请输入您的查询: Find references for Vega
```

### 坐标搜索
```
🔍 请输入您的查询: Search objects near RA=250.4, DEC=36.5 with radius 0.1 degrees
```

## 项目结构

```
mcp/
├── client.py              # LangGraph客户端（主要入口）
├── server.py              # MCP服务器
├── tap_client.py          # Simbad TAP客户端
├── tools.py               # 查询工具函数
├── requirements.txt       # Python依赖
├── .env                  # 环境变量配置
└── README.md             # 项目说明
```

## 技术栈

- **Python 3.10+**: 主要编程语言
- **MCP Python SDK**: Model Context Protocol支持
- **LangGraph**: 工作流编排
- **LangChain**: LLM集成框架
- **豆包API**: 大语言模型服务
- **httpx**: HTTP客户端
- **xmltodict**: XML数据解析

## 开发和调试

### 启用调试模式

在 `.env` 文件中设置：
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### 测试连接

```python
from tap_client import test_connection
if test_connection():
    print("✅ Simbad TAP服务连接正常")
else:
    print("❌ Simbad TAP服务连接失败")
```

## 常见问题

### Q: 豆包API调用失败
A: 请检查：
1. API密钥是否正确设置
2. 网络连接是否正常
3. API配额是否充足

### Q: MCP工具连接失败
A: 系统会自动降级到模拟工具模式，仍可进行基本测试。

### Q: Simbad查询超时
A: 可以在 `.env` 文件中调整 `QUERY_TIMEOUT` 值。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License