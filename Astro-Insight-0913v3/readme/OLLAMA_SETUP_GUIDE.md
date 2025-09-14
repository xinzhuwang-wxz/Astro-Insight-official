# Ollama + Qwen 2.5:7b 配置指导

## 已完成的配置

✅ **conf.yaml 已更新为Ollama配置**
- 模型: qwen2.5:7b
- 服务地址: http://localhost:11434/v1
- SSL验证: 已禁用（本地服务）
- 重试次数: 3次

## 安装和启动Ollama

### 1. 安装Ollama

**Windows用户:**
```bash
# 下载并安装Ollama
# 访问 https://ollama.ai/download 下载Windows版本
# 或者使用PowerShell:
winget install Ollama.Ollama
```

**Linux/macOS用户:**
```bash
# 使用官方安装脚本
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. 启动Ollama服务

```bash
# 启动Ollama服务（后台运行）
ollama serve
```

### 3. 下载Qwen 2.5:7b模型

```bash
# 下载模型（约4.4GB）
ollama pull qwen2.5:7b

# 验证模型是否下载成功
ollama list
```

## 验证配置

### 1. 测试Ollama连接

```bash
# 测试Ollama是否运行
curl http://localhost:11434/api/tags

# 测试模型是否可用
ollama run qwen2.5:7b "你好，请介绍一下你自己"
```

### 2. 测试项目配置

运行我们创建的测试脚本：

```bash
python test_fix.py
```

### 3. 完整功能测试

```bash
# 运行主程序
python main.py
```

## 常见问题解决

### Q: Ollama服务启动失败
A: 检查端口11434是否被占用：
```bash
# Windows
netstat -ano | findstr :11434

# Linux/macOS
lsof -i :11434
```

### Q: 模型下载失败
A: 检查网络连接，或尝试使用代理：
```bash
# 设置代理（如果需要）
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
ollama pull qwen2.5:7b
```

### Q: 内存不足
A: Qwen 2.5:7b需要约8GB内存，如果内存不足：
- 关闭其他程序释放内存
- 或使用更小的模型：`ollama pull qwen2.5:1.5b`

### Q: 模型响应慢
A: 这是正常的，本地模型比云端API慢：
- 首次运行会较慢（需要加载模型）
- 后续运行会快一些
- 可以调整模型参数优化性能

## 性能优化建议

### 1. 调整Ollama参数

创建 `~/.ollama/config.json`：
```json
{
  "num_ctx": 2048,
  "num_gpu": 1,
  "num_thread": 4
}
```

### 2. 使用GPU加速（如果有NVIDIA GPU）

```bash
# 安装CUDA版本的Ollama
# 确保已安装NVIDIA驱动和CUDA
ollama run qwen2.5:7b --gpu
```

## 测试运行

配置完成后，运行以下命令测试：

```bash
# 1. 测试Ollama连接
python -c "
from src.llms.llm import get_llm_by_type
llm = get_llm_by_type('basic')
print('Ollama连接成功！')
"

# 2. 测试完整工作流
python -c "
from src.workflow import execute_astro_workflow
result = execute_astro_workflow('test_1', '我是专业人士 想查询m31天体最近的两个天体')
print('测试结果:', result.get('final_answer', '无结果'))
"
```

## 下一步

1. 按照上述步骤安装和配置Ollama
2. 下载Qwen 2.5:7b模型
3. 运行测试验证配置
4. 如果一切正常，就可以使用完整的天文科研助手功能了！

## 注意事项

- Ollama服务需要一直运行才能使用
- 首次使用某个模型时会自动下载
- 模型文件较大，确保有足够的磁盘空间
- 本地模型响应速度取决于您的硬件配置
