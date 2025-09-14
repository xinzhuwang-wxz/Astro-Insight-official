# 数据库模块说明

## 📋 当前状态

**数据库框架已完整实现，但当前版本暂未启用数据持久化功能**

## 🏗️ 已实现的组件

### 核心类
- `LocalDatabase` - SQLite数据库操作类
- `DataManager` - 高级数据管理接口
- `CelestialObject` - 天体对象数据结构
- `ClassificationResult` - 分类结果数据结构
- `ExecutionHistory` - 执行历史记录

### 数据库表结构
- `celestial_objects` - 天体对象表
- `classification_results` - 分类结果表
- `execution_history` - 执行历史表
- `query_history` - 查询历史表（增强版）
- `user_sessions` - 用户会话表（增强版）
- `performance_metrics` - 性能指标表（增强版）

## 🔧 预留接口

### 当前被注释的方法调用
```python
# 在 complete_simple_system.py 和 complete_astro_system.py 中
# TODO: 数据库存储功能（预留接口）
# self.db.save_celestial_object(celestial_obj)
```

### 可用的方法（已实现但未启用）
```python
# 天体对象操作
db.add_celestial_object(obj)
db.get_celestial_object(obj_id)
db.search_celestial_objects()

# 分类结果操作
db.add_classification_result(result)
db.get_classification_results(obj_id)

# 执行历史操作
db.add_execution_history(history)
db.get_execution_history(session_id)
```

## 🚀 启用数据持久化

当需要启用数据库功能时，只需：

1. 取消注释相关方法调用
2. 确保数据库文件路径正确
3. 根据需要调整数据模型

## 📁 文件结构

```
src/database/
├── __init__.py              # 模块初始化
├── local_storage.py         # 核心数据库操作
├── enhanced_schema.py       # 增强数据库架构
├── api.py                   # 数据库API接口
├── migration.py             # 数据库迁移工具
└── README.md               # 本说明文档
```

## 💡 设计理念

- **接口优先**：先定义接口，后实现功能
- **渐进式启用**：框架完整，按需启用
- **向后兼容**：保留现有功能，不影响核心逻辑
