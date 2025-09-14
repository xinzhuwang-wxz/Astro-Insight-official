# 🐍 虚拟环境配置和预装库说明

## 📋 目录
- [当前环境概述](#当前环境概述)
- [预装库清单](#预装库清单)
- [环境配置方式](#环境配置方式)
- [库的来源和安装](#库的来源和安装)
- [沙箱执行机制](#沙箱执行机制)
- [环境问题排查](#环境问题排查)

## 🌟 当前环境概述

### 基本信息
- **环境类型**: Anaconda base环境
- **Python版本**: 3.11+ (Anaconda默认)
- **操作系统**: Windows 10/11
- **包管理器**: conda (主) + pip (辅)
- **环境位置**: `C:\Users\32830\anaconda3\`

### 环境特点
- ✅ **即开即用**: 无需额外虚拟环境配置
- ✅ **库丰富**: Anaconda预装大量科学计算库
- ✅ **稳定性高**: 经过Anaconda团队测试的库版本组合
- ⚠️ **依赖宿主**: 代码执行依赖当前Python环境
- ⚠️ **安全性相对较低**: 直接使用宿主环境

## 📦 预装库清单

### 核心数据科学库
```python
# 数据处理和分析
pandas              # 数据框架和分析 ✅
numpy               # 数值计算基础 ✅
scipy               # 科学计算扩展 ✅

# 机器学习
scikit-learn        # 经典机器学习算法 ✅
xgboost            # 梯度提升算法 (可能需要单独安装)
lightgbm           # 轻量级梯度提升 (可能需要单独安装)

# 数据可视化
matplotlib          # 基础绘图库 ✅
seaborn            # 统计可视化 ✅
plotly             # 交互式可视化 ✅

# 天文数据处理
astropy            # 天文数据处理 ✅
astroquery         # 天文数据查询 ❌ (需要安装)
```

### Python标准库
```python
# 系统和文件操作
os                 # 操作系统接口 ✅
sys                # 系统参数和函数 ✅
pathlib            # 面向对象路径操作 ✅

# 数据格式
json               # JSON数据处理 ✅
csv                # CSV文件处理 ✅
re                 # 正则表达式 ✅

# 数学和统计
math               # 数学函数 ✅
statistics         # 统计函数 ✅
datetime           # 日期时间处理 ✅

# 工具库
collections        # 特殊容器类型 ✅
itertools          # 迭代器工具 ✅
functools          # 函数工具 ✅
operator           # 操作符函数 ✅
warnings           # 警告控制 ✅
```

### 可选/缺失库状态
```python
# 自然语言处理 (用于翻译功能)
langdetect         # 语言检测 ❌
deep_translator    # 深度翻译 ❌
google-trans-new   # 谷歌翻译 ❌
translators        # 翻译服务 ❌

# 云服务SDK (用于翻译)
azure-cognitiveservices-language-translator  # 微软翻译 ❌
tencentcloud-sdk-python                      # 腾讯云 ❌
alibabacloud-translate20181012               # 阿里云 ❌

# 深度学习 (按需安装)
tensorflow         # TensorFlow ❓
torch              # PyTorch ❓
```

## 🔧 环境配置方式

### 1. 当前配置 (推荐用于开发测试)
```bash
# 直接使用Anaconda base环境
conda activate base

# 检查已安装库
conda list

# 安装缺失的库
pip install astroquery langdetect deep_translator
```

### 2. 独立虚拟环境 (推荐用于生产)
```bash
# 创建专用环境
conda create -n astro-coder python=3.11

# 激活环境
conda activate astro-coder

# 安装基础库
conda install pandas numpy scipy scikit-learn matplotlib seaborn plotly astropy

# 安装额外库
pip install astroquery langdetect deep_translator xgboost lightgbm
```

### 3. Docker容器 (推荐用于部署)
```dockerfile
FROM continuumio/anaconda3:latest

# 设置工作目录
WORKDIR /app

# 复制requirements文件
COPY requirements.txt .

# 安装依赖
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "server.py"]
```

## 📥 库的来源和安装

### Anaconda预装库
```python
# 这些库随Anaconda自动安装，无需手动操作
pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, astropy
```

### 手动安装库
```bash
# 使用pip安装的库 (在项目开发过程中添加)
pip install langchain-core langchain-openai langgraph langchain-community

# 天文数据相关
pip install astroquery

# 可选的机器学习库
pip install xgboost lightgbm

# 翻译功能相关 (可选)
pip install langdetect deep_translator google-trans-new
```

### 安装历史记录
根据终端输出，我们在开发过程中安装了：
1. `langchain-core` - LangChain核心库
2. `langchain-openai` - OpenAI集成
3. `langgraph` - 图工作流库
4. `langchain-community` - 社区扩展

## ⚡ 沙箱执行机制

### 执行方式
```python
# 代码执行器使用Python内置exec()函数
def _execute_in_sandbox(self, code, context):
    # 创建受限的全局命名空间
    globals_dict = {
        '__builtins__': {
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            # ... 其他安全的内置函数
        },
        '__import__': __import__,  # 允许导入
    }
    
    # 执行代码
    exec(code, globals_dict)
```

### 安全限制
```python
# 1. 库导入白名单
allowed_imports = {
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'sklearn', 
    'scipy', 'astropy', 'plotly', 'warnings', 'os', 'sys'
}

# 2. 危险操作黑名单
forbidden_patterns = [
    'import subprocess',    # 系统命令执行
    'import os.system',     # 系统调用
    'exec(',               # 动态代码执行
    'eval(',               # 表达式求值
    'open(',               # 文件操作 (受限)
    'input(',              # 用户输入
]
```

### 环境隔离程度
- **进程级隔离**: ❌ (同一Python进程)
- **命名空间隔离**: ✅ (受限的globals和locals)
- **文件系统隔离**: ⚠️ (部分限制，允许读写output目录)
- **网络隔离**: ❌ (可访问网络)
- **资源限制**: ⚠️ (时间限制，内存监控基础)

## 🔍 环境问题排查

### 常见问题和解决方案

#### 1. ImportError: No module named 'xxx'
```bash
# 问题: 缺少必要的库
# 解决: 安装缺失的库
pip install xxx

# 检查已安装库
pip list | grep xxx
conda list | grep xxx
```

#### 2. 版本冲突问题
```bash
# 问题: 库版本不兼容
# 解决: 创建独立环境
conda create -n clean-env python=3.11
conda activate clean-env
pip install -r requirements.txt
```

#### 3. 路径问题
```python
# 问题: Windows路径反斜杠
data_path = 'C:\data\file.csv'  # ❌

# 解决: 使用正斜杠或raw字符串
data_path = 'C:/data/file.csv'   # ✅
data_path = r'C:\data\file.csv'  # ✅
```

#### 4. 编码问题
```python
# 问题: 中文路径或文件名
# 解决: 确保使用UTF-8编码
pd.read_csv(file_path, encoding='utf-8')
```

### 环境健康检查脚本
```python
# check_environment.py
import sys
import importlib

required_packages = [
    'pandas', 'numpy', 'matplotlib', 'seaborn', 
    'sklearn', 'scipy', 'astropy'
]

print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")

for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - 需要安装")
```

## 📊 环境性能基准

### 库加载时间
```python
# 典型库导入时间 (首次)
pandas:      ~2.0s
numpy:       ~0.3s
matplotlib:  ~1.5s
sklearn:     ~3.0s
seaborn:     ~2.5s
```

### 内存使用
```python
# 基础Python进程: ~50MB
# 加载pandas+numpy: ~150MB
# 加载完整数据科学栈: ~300MB
# 执行机器学习任务: ~500MB+
```

### 推荐的环境优化
1. **预加载常用库** - 减少重复导入时间
2. **内存监控** - 防止内存泄漏
3. **定期清理** - 清理临时文件和缓存
4. **版本锁定** - 使用requirements.txt固定版本

---

## 🔗 相关资源

- [Anaconda官方文档](https://docs.anaconda.com/)
- [Python虚拟环境指南](https://docs.python.org/3/tutorial/venv.html)
- [pip用户指南](https://pip.pypa.io/en/stable/user_guide/)
- [conda用户指南](https://conda.io/projects/conda/en/latest/user-guide/index.html)

---

**最后更新**: 2025-01-09  
**环境版本**: Anaconda 2024.02 + Python 3.11  
**测试平台**: Windows 10/11
