# Planner模块

Planner模块是Astro-Insight系统的需求规划和任务分解组件，负责通过多轮对话收集和澄清用户需求，并将其分解为具体的可执行任务。

## 🎯 主要功能

1. **多轮需求对话** - 与用户进行交互式对话，逐步明确和细化需求
2. **智能任务分解** - 将用户需求分解为详细的、可执行的编程任务
3. **数据集智能选择** - 根据用户需求自动推荐最合适的数据集
4. **完整Pipeline集成** - 无缝集成Coder和Explainer模块

## 📁 模块结构

```
src/planner/
├── __init__.py              # 模块初始化
├── types.py                # 类型定义和数据结构
├── dataset_manager.py      # 数据集管理器
├── dialogue_manager.py     # 对话状态管理
├── task_decomposer.py      # 任务分解器
├── prompts.py              # Prompt模板
├── agent.py               # Planner核心Agent
├── workflow.py            # 工作流集成
├── test_planner.py        # 测试文件
├── example_usage.py       # 使用示例
└── README.md              # 说明文档
```

## 🚀 快速开始

### 1. 基本使用

```python
from src.planner import PlannerWorkflow

# 创建Planner工作流
planner = PlannerWorkflow()

# 运行完整Pipeline
user_request = "分析星系数据，生成散点图"
result = planner.run_complete_pipeline(user_request)

if result["success"]:
    print("✅ 分析完成！")
    print(f"生成文件: {result['generated_files']}")
    print(f"解释结果: {result['explanations']}")
```

### 2. 交互式会话

```python
# 开始交互式会话
session = planner.run_interactive_session("我想分析星系数据")

# 继续对话
session_id = session["session_id"]
result = planner.continue_interactive_session(session_id, "使用SDSS数据集")

# 处理确认
if result.get("needs_confirmation"):
    confirmation_result = planner.handle_confirmation(
        session_id, "确认，开始执行"
    )
```

### 3. 直接使用Agent

```python
from src.planner import PlannerAgent

agent = PlannerAgent()

# 开始规划会话
state = agent.start_planning_session("分析恒星数据")

# 处理用户输入
state = agent.process_user_input(state, "生成恒星类型分布图")

# 获取最终结果
result = agent.get_final_result(state)
```

## 📋 核心概念

### 对话状态

- `INITIAL` - 初始状态
- `COLLECTING` - 需求收集中
- `CLARIFYING` - 需求澄清中
- `CONFIRMING` - 需求确认中
- `COMPLETED` - 对话完成

### 任务步骤

每个任务步骤包含：
- `step_id` - 步骤唯一标识
- `description` - 步骤描述
- `action_type` - 操作类型（load, clean, analyze, visualize, export）
- `details` - 详细说明
- `dependencies` - 依赖关系
- `priority` - 优先级

### 数据集管理

Planner会自动：
- 扫描可用数据集
- 分析数据集特征
- 根据用户需求推荐最合适的数据集
- 提供数据集详细信息

## 🔧 配置选项

### 对话设置

- `max_turns` - 最大对话轮次（默认10轮）
- `max_retries` - 最大重试次数（默认3次）

### 数据集设置

- `dataset_dir` - 数据集目录（默认"dataset"）
- `output_dir` - 输出目录（默认"output"）

## 📊 工作流程

```
用户输入 → 需求分析 → 多轮对话 → 任务分解 → 确认 → 执行
    ↓           ↓         ↓         ↓       ↓      ↓
  初始需求    澄清问题   细化需求   具体步骤  用户确认  Coder执行
```

### 详细流程

1. **需求收集** - 分析用户初始需求
2. **数据集选择** - 推荐最合适的数据集
3. **多轮对话** - 澄清和细化需求细节
4. **任务分解** - 将需求分解为具体步骤
5. **需求确认** - 用户确认最终计划
6. **代码生成** - 调用Coder模块执行
7. **结果解释** - 调用Explainer模块解释

## 🧪 测试

运行测试：

```bash
python src/planner/test_planner.py
```

运行示例：

```bash
python src/planner/example_usage.py
```

## 📝 示例场景

### 场景1：星系数据分析

```
用户: "我想分析星系数据"
助手: "我理解您想要分析星系数据。我发现了几个可用的数据集，包括SDSS星系数据集。请问您想要分析星系的哪个方面？比如分类、分布、还是其他特征？"

用户: "我想看看星系的分类情况"
助手: "好的，星系分类分析。我推荐使用SDSS星系数据集，它包含丰富的星系形态学特征。您希望生成什么类型的图表来展示分类结果？比如散点图、直方图，还是热力图？"

用户: "生成散点图展示星系的大小和亮度关系"
助手: "明白了。我将为您创建一个分析计划：1. 加载SDSS星系数据集 2. 数据清洗和预处理 3. 生成散点图展示星系大小与亮度的关系 4. 保存结果。请确认是否开始执行？"

用户: "确认，开始执行"
```

### 场景2：恒星类型分析

```
用户: "分析恒星的类型分布"
助手: "我理解您想要分析恒星的类型分布。我发现了恒星分类数据集。请问您希望如何展示分布结果？比如饼图、柱状图，还是统计表格？"

用户: "生成饼图"
助手: "好的，我将为您创建分析计划：1. 加载恒星分类数据集 2. 统计各类型恒星的数量 3. 生成饼图展示分布 4. 添加标签和说明。请确认是否开始执行？"
```

## 🔍 故障排除

### 常见问题

1. **数据集未找到**
   - 检查`dataset`目录是否存在
   - 确认数据集文件格式为CSV

2. **LLM调用失败**
   - 检查LLM配置
   - 确认网络连接

3. **任务分解失败**
   - 检查用户需求是否明确
   - 确认数据集信息完整

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 运行测试
python src/planner/test_planner.py
```

## 🤝 贡献

欢迎贡献代码和改进建议！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License - 详见LICENSE文件
