# Database Schema Draft

Date: 2026-04-26

## 1. Design goals

The database should support not only data storage, but also the full exploratory visualization workflow:
- data ingestion and versioning
- cleaning and feature extraction
- dimensionality reduction and comparison
- chart recommendation and configuration
- user sessions and interaction tracking
- result explanation and caching

The schema is designed for a task-driven astronomy visualization platform, not a single-purpose catalog.

### Normalization requirement
The schema is intended to satisfy **Third Normal Form (3NF)**:
- each table represents one entity or one relationship
- non-key attributes depend on the key, the whole key, and nothing but the key
- derived or repeated values are not duplicated across tables unless they are explicitly versioned cache outputs

This means the design favors:
- separate lookup tables for stable dimensions
- separate fact/result tables for analysis outputs
- JSON payloads only for truly variable, source-specific, or export-oriented details

### API-field uncertainty handling
The Exoplanet Archive API contains many tables and evolving column sets, so the schema is **not tied to one fixed remote field list**.
Instead, it is built around normalized internal entities such as:
- source table metadata
- imported record payloads
- mapped core attributes
- feature extraction outputs
- analysis run outputs

This allows the platform to remain stable even if the remote archive changes table names, columns, or preferred access methods (API vs TAP).

### PSCompPars as the primary source table
For this project, `PSCompPars` is the primary source table. The implementation strategy is:
1. use TAP or API only to ingest source rows
2. map stable source attributes into normalized internal tables
3. keep raw source payloads for traceability
4. avoid designing business tables directly around every remote column

In other words, remote columns are treated as ingestion inputs, not as the database's final normalized structure.

---

## 2. Core entity groups

### A. Data assets
These tables store the astronomy data itself and its derived versions.

#### `source_datasets`
Stores metadata about each remote or local data source.

Suggested fields:
- `id` PK
- `source_name`
- `source_type`  // api, tap, file, manual
- `source_url`
- `source_table_name`
- `source_version`
- `retrieval_method`
- `schema_snapshot` JSON
- `last_synced_at`
- `status`

Purpose:
- keep source metadata normalized
- support multiple archive tables and versions
- isolate remote schema changes from business logic

#### `raw_astronomy_records`
Stores raw imported records from the registered source datasets.

Suggested fields:
- `id` PK
- `source_dataset_id` FK -> `source_datasets.id`
- `source_record_id`
- `dataset_name`
- `raw_payload` JSON
- `ingested_at`
- `ingestion_batch_id`
- `record_hash`
- `status`

Purpose:
- preserve original source fidelity
- support re-import and traceability
- allow multiple external sources later

#### `cleaning_pipelines`
Stores reusable preprocessing pipeline definitions.

Suggested fields:
- `id` PK
- `pipeline_name`
- `pipeline_version`
- `description`
- `parameters` JSON
- `created_at`
- `status`

Purpose:
- keep cleaning logic reusable and versioned
- avoid repeating pipeline definitions per record

#### `cleaned_astronomy_records`
Stores cleaned, normalized records after preprocessing.

Suggested fields:
- `id` PK
- `raw_record_id` FK -> `raw_astronomy_records.id`
- `cleaning_pipeline_id` FK -> `cleaning_pipelines.id`
- `clean_version`
- `clean_payload` JSON
- `missing_mask` JSON
- `outlier_flags` JSON
- `normalized_flags` JSON
- `cleaned_at`

Purpose:
- support preprocessing comparisons
- preserve cleaning provenance
- allow multiple cleaning strategies

#### `feature_sets`
Stores reusable definitions of feature groups.

Suggested fields:
- `id` PK
- `feature_set_name`
- `feature_set_version`
- `description`
- `feature_schema` JSON
- `created_at`
- `status`

Purpose:
- separate the feature definition from generated feature values
- support multiple comparable feature sets

#### `astronomy_features`
Stores feature vectors used in analysis.

Suggested fields:
- `id` PK
- `clean_record_id` FK -> `cleaned_astronomy_records.id`
- `feature_set_id` FK -> `feature_sets.id`
- `scaling_method`
- `feature_payload` JSON
- `feature_metadata` JSON
- `created_at`

Purpose:
- support PCA/SVD and clustering
- allow different feature sets for comparison
- keep analysis inputs reproducible

---

### B. Analysis workflow
These tables store tasks, runs, and computed outputs.

#### `viz_tasks`
Represents one analysis or visualization task initiated by the system or user.

Suggested fields:
- `id` PK
- `session_id` FK -> `user_sessions.session_id`
- `dataset_source_id` FK -> `source_datasets.id`
- `task_type`  // overview, eda, structure, comparison, explanation
- `task_name`
- `filters` JSON
- `target_variables` JSON
- `analysis_method`
- `status`
- `created_at`
- `updated_at`

Purpose:
- unify all task types under one workflow model
- support task history and replay

#### `analysis_runs`
Stores one execution of a method for a given task.

Suggested fields:
- `id` PK
- `task_id` FK -> `viz_tasks.id`
- `run_type`  // pca, tsne, umap, correlation, clustering, anomaly
- `parameters` JSON
- `input_snapshot` JSON
- `metric_summary` JSON
- `runtime_ms`
- `created_at`

Purpose:
- compare methods and parameter settings
- support caching of expensive computations
- provide explainable computation traces

#### `analysis_results`
Stores structured outputs from analysis runs.

Suggested fields:
- `id` PK
- `run_id` FK -> `analysis_runs.id`
- `result_type`  // embedding, cluster, correlation, distribution, anomaly
- `result_payload` JSON
- `summary_text`
- `created_at`

Purpose:
- store visualizable result objects
- separate computation from presentation
- make outputs reusable across views

#### `analysis_result_items`
Stores row-level result records when the analysis output needs to be joined back to samples.

Suggested fields:
- `id` PK
- `analysis_result_id` FK -> `analysis_results.id`
- `record_id`
- `item_role`  // center, outlier, cluster_member, exemplar
- `item_score`
- `item_metadata` JSON
- `created_at`

Purpose:
- support sample highlighting in linked views
- avoid duplicating result summaries inside the main result table

#### `dimensionality_reduction_results`
Stores low-dimensional coordinates.

Suggested fields:
- `id` PK
- `run_id` FK -> `analysis_runs.id`
- `method_name`  // PCA, t-SNE, UMAP
- `dimensions`
- `explained_variance` JSON
- `perplexity`
- `neighbors`
- `random_state`
- `created_at`

Purpose:
- power the structure page
- support method comparison
- preserve parameter settings

#### `dimensionality_coordinates`
Stores one row per embedded sample in a normalized form.

Suggested fields:
- `id` PK
- `reduction_result_id` FK -> `dimensionality_reduction_results.id`
- `record_id`
- `dim_1`
- `dim_2`
- `dim_3` nullable
- `cluster_label` nullable
- `point_metadata` JSON
- `created_at`

Purpose:
- keep coordinates queryable in 3NF-friendly row form
- support linked brushing and per-point highlighting

---

### C. Visualization layer
These tables store chart configuration and generated chart metadata.

#### `chart_types`
Lookup table for reusable chart categories.

Suggested fields:
- `id` PK
- `chart_type_name`
- `description`
- `created_at`

Purpose:
- avoid repeating chart labels across configs
- keep chart vocabulary normalized

#### `chart_configs`
Stores chart definitions and display options.

Suggested fields:
- `id` PK
- `task_id` FK -> `viz_tasks.id`
- `chart_type_id` FK -> `chart_types.id`
- `encoding_spec` JSON
- `color_theme`
- `axis_mapping` JSON
- `aggregation_spec` JSON
- `layout_spec` JSON
- `created_at`
- `updated_at`

Purpose:
- support chart switching
- persist visualization choices
- enable reproducible chart generation

#### `chart_generation_logs`
Records chart render events and generation decisions.

Suggested fields:
- `id` PK
- `chart_config_id` FK -> `chart_configs.id`
- `run_id` FK -> `analysis_runs.id`
- `generated_by`
- `generation_reason`
- `render_status`
- `render_time_ms`
- `created_at`

Purpose:
- explain why a chart was selected
- debug chart generation issues
- support recommendation transparency

#### `chart_view_instances`
Stores one concrete rendered view instance for a user session.

Suggested fields:
- `id` PK
- `chart_config_id` FK -> `chart_configs.id`
- `session_id` FK -> `user_sessions.session_id`
- `view_state` JSON
- `snapshot_at`
- `created_at`

Purpose:
- separate reusable chart config from session-specific rendered state
- keep the model normalized

#### `chart_recommendations`
Stores suggested chart types for tasks or data profiles.

Suggested fields:
- `id` PK
- `task_id` FK -> `viz_tasks.id`
- `recommended_chart_type`
- `reasoning`
- `confidence_score`
- `alternatives` JSON
- `created_at`

Purpose:
- power chart recommendation UI
- explain why a chart is suitable for a task

---

### D. User and behavior layer
These tables store session state and behavior traces.

#### `user_sessions`
Stores a user analysis session.

Suggested fields:
- `session_id` PK
- `user_id`
- `started_at`
- `ended_at`
- `current_page`
- `active_views` JSON
- `selected_dataset`
- `selected_task`
- `total_actions`
- `metadata` JSON

Purpose:
- support stateful exploration
- persist cross-page context
- enable replay of analysis paths

#### `interaction_events`
Stores fine-grained user actions.

Suggested fields:
- `id` PK
- `session_id` FK -> `user_sessions.session_id`
- `task_id` FK -> `viz_tasks.id` nullable
- `event_type`  // click, hover, brush, zoom, filter, sort, switch_chart, adjust_param, reset
- `target_view`
- `target_element`
- `event_payload` JSON
- `created_at`

Purpose:
- support behavior analysis
- build interaction timelines
- identify common exploration patterns

#### `query_history`
Stores query or request history.

Suggested fields:
- `id` PK
- `session_id` FK -> `user_sessions.session_id`
- `query_text`
- `query_type`
- `query_params` JSON
- `results_count`
- `execution_time_ms`
- `success`
- `cache_hit`
- `created_at`

Purpose:
- track analytical intent
- connect user questions with resulting views

---

## 3. Supporting entities

#### `data_sources`
Stores information about imported sources.

Suggested fields:
- `id` PK
- `source_name`
- `source_type`
- `source_url`
- `version`
- `refresh_policy`
- `last_synced_at`
- `metadata` JSON

#### `cache_entries`
Stores reusable cached outputs.

Suggested fields:
- `id` PK
- `cache_key`
- `cache_type`
- `payload` JSON
- `expires_at`
- `created_at`
- `hit_count`

#### `error_logs`
Stores analysis/runtime failures.

Suggested fields:
- `id` PK
- `session_id`
- `task_id`
- `error_type`
- `error_message`
- `stack_trace`
- `context` JSON
- `created_at`

#### `performance_metrics`
Stores system-level performance summaries.

Suggested fields:
- `id` PK
- `metric_name`
- `metric_value`
- `metric_unit`
- `window_start`
- `window_end`
- `metadata` JSON
- `created_at`

---

## 4. Relationship summary

### Main flow
`raw_astronomy_records` -> `cleaned_astronomy_records` -> `astronomy_features` -> `viz_tasks` -> `analysis_runs` -> `analysis_results` / `dimensionality_reduction_results` -> `chart_configs` / `chart_generation_logs`

### Behavior flow
`user_sessions` -> `interaction_events` -> `query_history`

### Cross-links
- `viz_tasks.session_id` links workflow to session context
- `analysis_runs.task_id` links computation to task intent
- `chart_configs.task_id` links view design to task requirements
- `interaction_events.task_id` links actions to specific analytical tasks

---

## 5. Versioning rules

To keep the platform explainable and reproducible:
- every cleaning pipeline should create a new clean version
- every feature extraction pipeline should create a feature version
- every dimensionality reduction run should persist parameters
- every chart config should store encoding and layout specs
- every user session should preserve active filters and current page

---

## 6. Recommended MVP subset

For the first implementation phase, the minimum useful schema is:
- `raw_astronomy_records`
- `cleaned_astronomy_records`
- `astronomy_features`
- `viz_tasks`
- `analysis_runs`
- `dimensionality_reduction_results`
- `chart_configs`
- `user_sessions`
- `interaction_events`
- `chart_recommendations`

This subset already supports:
- overview
- EDA
- structure view
- comparison
- explanation
- interaction replay

---

## 7. PSCompPars field discovery and mapping plan

Because `PSCompPars` is the primary source table, the next step is to inspect its actual column set and map columns into normalized internal entities.

### 7.1 Field classification buckets
Each incoming column should be classified into one of these buckets:

1. **Identifier fields**
   - example: system name, planet name, host star name, archive IDs
   - usually become stable keys or natural-key candidates

2. **Numerical observation fields**
   - example: mass, radius, period, temperature, semi-major axis, eccentricity, flux-related values
   - usually become features or cleaned value columns if stable enough

3. **Categorical fields**
   - example: discovery method, disposition, host properties, orbital class labels
   - usually become lookup-linked dimensions or categorical attributes

4. **Temporal fields**
   - example: discovery date, updated date, vetting date
   - usually become date columns in a normalized source/metadata table

5. **Spatial fields**
   - example: coordinates, sky position, derived angles
   - should be separated into dedicated coordinate-related tables when reused

6. **Source/provenance fields**
   - example: reference, dataset version, publication source, table name
   - should be stored in `source_datasets`, `raw_astronomy_records`, or metadata tables

7. **Derived / computed fields**
   - example: normalized values, logs, scores, embeddings, cluster labels
   - should never overwrite raw values and should instead live in feature/result tables

### 7.2 Mapping rule to preserve 3NF
For each field:
- if it is an identifying attribute of the entity, map it to the core entity table
- if it describes the source table itself, map it to `source_datasets`
- if it changes by cleaning pipeline, map it to `cleaned_astronomy_records` or a related transformation table
- if it is generated for analysis, map it to `astronomy_features`, `analysis_runs`, or `analysis_results`
- if it is repeated across many records as a category, move it to a lookup table instead of duplicating text values

### 7.3 Immediate extraction workflow
1. query the column list for `PSCompPars`
2. mark each column as stable / unstable / derived / lookup candidate
3. decide whether the column belongs to raw payload, cleaned payload, feature payload, or lookup table
4. document the mapping in the data dictionary
5. only then finalize the physical schema

### 7.4 Practical schema implication
This means the normalized internal database should **not** mirror `PSCompPars` one-to-one.
Instead, it should store a canonical astronomy object/entity record plus transformation and analysis tables.

## 8. Implementation note

The current repository already has a simpler SQLite schema for celestial objects, classification results, and execution history. That schema can be retained as a lightweight compatibility layer, but the new platform should progressively migrate toward this task-centric schema.
