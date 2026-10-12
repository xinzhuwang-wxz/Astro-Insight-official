# Diary

Date: 2026-04-26

## Full summary of today

### 1. Project direction was clarified
We reframed the project as an astronomy data visualization and exploratory analysis platform, not just a data display or classification tool.

The main narrative became:
> Different visualization choices can lead to different cognitive conclusions about astronomical data.

That means the system is about:
- pattern discovery
- comparing views and methods
- preserving insight through analysis
- explaining why different charts lead to different interpretations

### 2. Existing codebase was inspected
We reviewed the current repository and confirmed that it already has useful reusable pieces:
- a Flask backend
- a SQLite-based local storage layer
- an existing front-end workbench style UI
- routes for status, analysis, data summary, and history

This showed the project was not starting from zero.

### 3. The planning record was updated repeatedly
We kept a project planning record in `docs/project_planning_record.md` and updated it as the direction evolved.

It now includes:
- the revised project positioning
- the narrative focus
- the existing-codebase audit
- the database design process
- the multiple data source strategy
- the concept/logic/physical design sequence
- the MVP table strategy
- the storage rules for CSV / JSON / database usage

### 4. The database design process was agreed
We decided the database work should follow:
1. conceptual design
2. logical design
3. physical design

This avoids jumping too early into SQL and makes the schema easier to reason about.

### 5. Multiple data sources were incorporated from the start
We agreed that the project should not be designed around only one dataset.
The source strategy now includes:
- `PSCompPars` as a primary source
- Kaggle `SDSS19 Stellar Classification Star/Galaxy/QSO` as a co-primary analytical source
- SIMBAD as an enrichment source
- literature / paper APIs as evidence sources

This makes the platform more general and better aligned with the astronomy comparison story.

### 6. Conceptual design was written
We created `docs/conceptual_design.md`.

It defines the main conceptual groups:
- data sources
- astronomy records
- transformation / cleaning
- analysis tasks and runs
- visualization configuration
- user sessions and interaction traces
- evidence and explanation concepts

### 7. Logical design was written
We created `docs/logical_design.md`.

It maps the conceptual entities into normalized relational entities and explains the 3NF-oriented structure.

It includes tables for:
- source metadata
- imported datasets
- raw records
- record attributes
- cleaning pipelines
- feature sets and feature values
- analysis tasks, methods, runs, and results
- chart configs
- user sessions and interaction logs
- evidence and claims

### 8. A smaller MVP-oriented logical design was created
We then compressed the schema into `docs/logical_design_minimal.md` so it would be easier to implement.

The minimal design keeps the core tables needed for the project story and avoids over-fragmenting the schema.

### 9. Normalization concerns were reviewed
We explicitly revisited 2NF / 3NF concerns and tightened the schema.

To make the design cleaner, we added lookup / definition tables such as:
- `analysis_task_types`
- `analysis_methods`
- `chart_types`
- `feature_definitions`

We also recorded the reasoning in `docs/normalization_notes.md`.

### 10. A diagram-style explanation was created
We added `docs/logical_design_diagram.md`.

This was meant to make the table relationships easier to understand at a glance.
It shows the main relationship chain from source to dataset to record to cleaned record to features to analysis to results to charts to interpretation.

### 11. The storage-format rule was established
We agreed on a storage rule and recorded it in `docs/storage_and_format_rules.md`.

The rule is:
- database tables are the source of truth for workflow state and relationships
- CSV is for import/export and tabular exchange
- JSON is for flexible payloads, configs, and result structures

This was important because we discussed whether everything should be stored as CSV, and concluded that mixed storage is fine as long as the boundaries are clear.

### 12. Physical design was drafted
We created `docs/physical_design.md`.

This contains the first concrete SQLite-oriented table definitions for the MVP.

The MVP physical schema includes:
- `data_sources`
- `source_datasets`
- `dataset_records`
- `cleaned_records`
- `feature_sets`
- `feature_definitions`
- `feature_values`
- `analysis_task_types`
- `analysis_tasks`
- `analysis_methods`
- `analysis_runs`
- `analysis_results`
- `chart_types`
- `chart_configs`
- `user_sessions`
- `interaction_events`
- `interpretation_claims`

### 13. MVP scope was compressed further
We then prioritized the 17 physical tables into a practical MVP implementation plan in `docs/mvp_table_priority.md`.

This split the work into:
- Tier 1: must implement first
- Tier 2: can be deferred

It also grouped the MVP into three lanes:
- data lane
- analysis lane
- UX / explanation lane

### 14. A concrete schema blueprint was produced
We then created `docs/mvp_schema_blueprint.md`.

This turned the MVP table priority plan into a more concrete build order and field draft.

It includes:
- the table creation order
- field suggestions for each table
- foreign-key suggestions
- index suggestions
- which fields can remain TEXT or JSON in the MVP

### 15. The MVP schema implementation started
We added a new module:
- `src/database/mvp_schema.py`

This module creates the MVP SQLite schema and indexes automatically.

The database API initialization was updated so the schema is created at startup.

### 16. We clarified how the database is implemented technically
We discussed and clarified that the system uses:
- Python for backend and database operations
- SQL for the schema and queries
- SQLite as the current database engine
- a database file in the project, likely under `data/astro_insight.db`

### 17. We agreed on the next implementation step
The next practical work is:
- connect the backend API to the new MVP schema
- add the first CSV import pipeline
- load a small sample of data from the primary datasets
- verify that tasks, runs, results, and charts can all be stored and queried

## Result of today
By the end of the day, the project had moved from planning into real implementation.

The key deliverables created today were:
- conceptual design document
- logical design document
- minimal logical design document
- logical relationship diagram
- normalization notes
- storage format rules
- physical design draft
- MVP priority plan
- MVP schema blueprint
- MVP SQLite schema module
- updated planning record

## Next step
Continue by wiring the backend to the new schema and adding the first data import pipeline.

接下来最该做的是两步：

## 1. 先把数据库和后端真正连起来
现在表已经有了，下一步要让后端接口开始读写这套 MVP schema。  
也就是把现在旧的：

- `celestial_objects`
- `classification_results`
- `execution_history`

逐步过渡到新的：

- `data_sources`
- `source_datasets`
- `dataset_records`
- `cleaned_records`
- `analysis_tasks`
- `analysis_runs`
- `analysis_results`
- `chart_configs`
- `user_sessions`
- `interaction_events`
- `interpretation_claims`

这一步最关键，因为它决定系统是不是已经从“文档设计”变成“可运行平台”。

---

## 2. 做数据导入第一版
先挑一个最小闭环数据源开始：

- `PSCompPars`
- Kaggle `SDSS19 Stellar Classification Star/Galaxy/QSO`

先做一个最基础的导入流程：
- 读取 CSV
- 存入 `source_datasets`
- 原始行存入 `dataset_records`
- 清洗后存入 `cleaned_records`
- 抽几个核心特征写入 `feature_values`

---

# 我建议的执行顺序
最稳的是：

1. **后端 API 接入新 schema**
2. **做 CSV 导入脚本**
3. **导一小批样本数据**
4. **验证查询和页面显示**
5. **再做分析任务和图表配置**

---

# 如果要我继续，我建议下一步直接做这个
**把后端 API 改成支持新 MVP 数据表。**
