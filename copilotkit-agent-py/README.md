# copilotkit-agent-py

一个最小的 LangGraph + FastAPI 示例，封装为可通过 Poetry 安装与运行的包。

## 运行环境
- Python 3.10–3.12（推荐 3.12）
- Poetry 1.6+（或 2.x）

## 安装依赖
```cmd
poetry install
```

如仅想管理依赖、暂不安装当前项目，可使用：
```cmd
poetry install --no-root
```

或在 `pyproject.toml` 设置：
```toml
[tool.poetry]
package-mode = false
```

## 启动示例服务
- 方式一（安装当前包后使用脚本入口）：
```cmd
poetry run demo
```
- 方式二（直接运行模块）：
```cmd
poetry run uvicorn sample_agent.demo:app --host 0.0.0.0 --port 8000 --reload
```

访问接口：
- http://localhost:8000/
- http://localhost:8000/docs

## 环境变量
在仓库根创建 `.env`：
```ini
OPENAI_API_KEY=你的key
# 可选
PORT=8000
```

## 目录结构
- `sample_agent/agent.py` 定义工作流图
- `sample_agent/demo.py` 提供 FastAPI 入口（并注册脚本 `demo`）
