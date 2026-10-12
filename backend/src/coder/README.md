# 代码生成Agent (CodeGeneratorAgent)

专门负责天文数据分析代码生成和执行的智能Agent。

## 🎯 核心功能

### 1. **智能数据集选择**
- 自动发现`dataset/full_description/`目录下的数据集描述文件
- 根据用户需求智能选择最合适的数据集
- 支持多数据集环境

### 2. **代码复杂度分析**
- **SIMPLE**: 简单操作（展示前5行、基本统计）
- **MODERATE**: 中等复杂度（数据可视化、清洗）
- **COMPLEX**: 复杂分析（机器学习、高级统计）

### 3. **智能代码生成**
- 基于数据集描述和用户需求生成完整Python代码
- 支持pandas、numpy、matplotlib、sklearn等常用库
- 自动处理文件路径和输出目录

### 4. **安全代码执行**
- 沙箱环境执行，确保系统安全
- 自动处理异常和错误
- 生成的图片自动保存到`output/`目录

### 5. **智能错误恢复**
- 自动检测语法错误和运行时错误
- 基于错误信息重新生成修复后的代码
- 支持多次重试机制

## 🏗️ 架构设计

```
src/coder/
├── __init__.py              # 模块导出
├── types.py                 # 数据类型定义
├── agent.py                 # 核心Agent类
├── dataset_selector.py      # 数据集选择器
├── prompts.py              # Prompt管理器
├── executor.py             # 代码执行器
├── workflow.py             # LangGraph工作流
├── test_coder.py           # 测试文件
├── example_usage.py        # 使用示例
└── README.md               # 说明文档
```

## 🚀 快速开始

### 基本使用

```python
from src.coder.workflow import CodeGenerationWorkflow

# 创建工作流
workflow = CodeGenerationWorkflow()

# 简单请求
result = workflow.run("展示前五行数据")

if result['success']:
    print("生成的代码:")
    print(result['code'])
    print("\n执行结果:")
    print(result['output'])
else:
    print(f"错误: {result['error']}")
```

### 数据可视化

```python
# 创建可视化
result = workflow.run("创建一个显示star、galaxy、qso类别分布的饼图")

if result['success']:
    print(f"生成的图片: {result['generated_files']}")
```

### 机器学习分析

```python
# 复杂分析
result = workflow.run("使用随机森林对star、galaxy、qso进行分类，并显示分类报告")

if result['success']:
    print(f"执行时间: {result['execution_time']:.2f}秒")
    print(f"模型性能: {result['output']}")
```

## 📊 支持的分析类型

### 简单数据操作 (SIMPLE)
- 数据展示：`"展示前10行数据"`
- 基本统计：`"计算基本统计信息"`
- 数据结构：`"显示数据集的结构和列信息"`

### 数据可视化 (MODERATE)
- 分布图：`"创建redshift的分布直方图"`
- 散点图：`"画出u和g波段的散点图"`
- 饼图：`"显示各类别的分布饼图"`
- 相关性：`"创建波段间的相关性热力图"`

### 机器学习 (COMPLEX)
- 分类：`"使用随机森林进行三分类"`
- 聚类：`"使用K-means聚类分析"`
- 降维：`"使用PCA进行降维可视化"`
- 模型比较：`"比较不同算法的分类性能"`

## 🔧 配置说明

### 数据集配置
1. 将数据集描述文件放在`dataset/full_description/`目录
2. 数据文件放在`dataset/dataset/`目录
3. 描述文件应包含数据集路径和列信息

### 执行环境配置
- 默认超时：60秒
- 输出目录：`output/`
- 最大重试次数：3次

## 🛡️ 安全特性

### 代码安全检查
- 禁止危险操作（`exec`, `eval`, `subprocess`等）
- 限制导入模块白名单
- 沙箱环境执行

### 错误处理
- 语法错误自动修复
- 运行时异常捕获
- 详细错误报告

## 📝 使用示例

### 1. 运行测试
```bash
python src/coder/test_coder.py
```

### 2. 交互式使用
```bash
python src/coder/example_usage.py
```

### 3. 集成到现有系统
```python
from src.coder.agent import CodeGeneratorAgent

agent = CodeGeneratorAgent()
state = agent.create_initial_state("你的需求")
result_state = agent.process_request(state)
final_result = agent.get_final_result(result_state)
```

## 🔄 工作流程

1. **数据集选择** → 根据需求选择合适的数据集
2. **复杂度分析** → 分析请求复杂度等级
3. **代码生成** → 基于模板和描述生成代码
4. **代码执行** → 在安全环境中执行代码
5. **错误恢复** → 如有错误，自动修复并重试

## 🎛️ API参考

### CodeGenerationWorkflow

主要的工作流类，提供完整的代码生成功能。

```python
class CodeGenerationWorkflow:
    def run(self, user_input: str, session_id: str = None) -> Dict[str, Any]
    def run_single_step(self, user_input: str, step: str = "full") -> Dict[str, Any]
```

### 返回结果格式

```python
{
    "success": bool,                    # 是否成功
    "code": str,                       # 生成的代码
    "output": str,                     # 执行输出
    "execution_time": float,           # 执行时间
    "generated_files": List[str],      # 生成的文件
    "dataset_used": str,               # 使用的数据集
    "complexity": str,                 # 复杂度等级
    "retry_count": int,                # 重试次数
    "error": str,                      # 错误信息（如果失败）
    "error_type": str                  # 错误类型（如果失败）
}
```

## 🚨 注意事项

1. **数据集路径**: 确保数据集文件存在且路径正确
2. **依赖库**: 确保安装了pandas、numpy、matplotlib等必要库
3. **输出目录**: `output/`目录会自动创建
4. **安全限制**: 某些操作可能被安全机制阻止
5. **执行时间**: 复杂分析可能需要较长时间

## 🔮 未来扩展

- [ ] 支持更多数据格式（JSON、Parquet等）
- [ ] 增加深度学习模型支持
- [ ] 交互式图表生成
- [ ] 代码版本管理
- [ ] 性能优化和缓存
