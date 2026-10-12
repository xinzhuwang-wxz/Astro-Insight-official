# Astro-Insight 运行指南

本文档说明如何在本地运行 `Astro-Insight` 项目，以及如何打开前端页面进行查看。

## 1. 项目是什么

`Astro-Insight` 是一个面向天文数据分析的项目，当前仓库包含：

- Flask 后端服务 `server.py`
- Web 前端模板 `templates/index.html`
- 前端脚本 `static/js/main.js`
- 数据分析、代码生成、工作流等后端模块位于 `src/`

当前前端已被逐步改造成“分析工作台”风格，主要用于：

- 天文数据概览
- 探索性数据分析（EDA）
- 可视化结果展示
- 图表推荐与结果解释

## 2. 运行前准备

### 2.1 Python

建议使用 Python 3.10 或更高版本。

### 2.2 创建虚拟环境

在项目根目录执行：

```bash
python -m venv .venv
```

### 2.3 激活虚拟环境

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

### 2.4 安装依赖

```bash
pip install -r requirements.txt
```

如果依赖较多、安装较慢，这是正常的。首次安装可能需要较长时间。

## 3. 启动后端服务

项目当前的 Web 服务入口是 `server.py`。

在项目根目录运行：

```bash
python server.py
```

默认会启动在：

- `http://localhost:8000`

如果启动成功，你会在终端看到类似信息：

- 数据库初始化完成
- 分析图初始化完成
- 服务启动成功

## 4. 打开前端页面

后端启动后，在浏览器访问：

```text
http://localhost:8000
```

如果当前版本的 `server.py` 只返回 API JSON，而没有把 `templates/index.html` 作为主页渲染出来，那么说明还需要把首页路由切到前端模板。

这种情况下，你仍然可以先通过以下方式检查后端 API：

- `http://localhost:8000/api/status`
- `http://localhost:8000/api/data/statistics`
- `http://localhost:8000/api/data/objects?limit=20`

## 5. 常用接口

- `GET /api/status`：系统状态
- `POST /api/analyze`：分析请求
- `GET /api/data/statistics`：统计数据
- `GET /api/data/objects`：天体对象
- `GET /api/data/classifications`：分类结果
- `GET /api/data/history`：执行历史

## 6. 运行前可能需要的配置

项目中可能依赖以下外部能力：

- 数据库连接
- LangGraph 工作流
- 代码生成模块
- MCP / LLM 相关能力
- 某些天文数据源或 API

如果启动时报错，常见原因包括：

1. 依赖没有装全
2. 数据库未初始化
3. 外部 API key 未配置
4. 后端模块导入失败

## 7. 推荐的排错顺序

### 7.1 先看后端是否能启动

```bash
python server.py
```

### 7.2 再访问健康检查

```text
http://localhost:8000/health
```

### 7.3 再访问状态接口

```text
http://localhost:8000/api/status
```

### 7.4 最后看前端页面

```text
http://localhost:8000
```

## 8. 适合本项目的开发方式

建议按以下顺序开发：

1. 先保证后端能运行
2. 再保证数据接口可用
3. 再逐步重做前端工作台
4. 再加入图表推荐、多视图联动、EDA 过程展示

## 9. 你现在最适合做什么

如果你只是想“先跑起来看看”，最短路径是：

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

然后浏览器访问 `http://localhost:8000`。

---

如果你后续要把前端真正接成分析工作台，我建议把首页路由从 JSON 改成模板渲染，再把 EDA 的核心视图逐步接进来。
