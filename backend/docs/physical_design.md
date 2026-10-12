# Physical Design Draft

Date: 2026-04-26

## 1. Physical design goal

Turn the revised minimal logical model into a concrete database implementation that is simple enough for the MVP, but still aligned with the 2NF-oriented structure and the broader 3NF direction.

The first physical version should prioritize:
- implementation simplicity
- stable foreign-key relationships
- query efficiency for the main workflow
- compatibility with the current SQLite-based codebase
- clear migration from the existing astronomy-assistant schema

---

## 2. MVP implementation principle

For the first build, implement only the core tables required to support:
- data source registration
- imported dataset storage
- raw records
- cleaned records
- feature definitions and feature values
- analysis task types and analysis tasks
- analysis methods and analysis runs
- analysis results
- chart types and chart configs
- user sessions and interaction logs
- interpretation conclusions

Optional evidence/provenance tables can be added later.

---

## 3. MVP physical tables

### 3.1 `data_sources`
Stores source metadata.

Suggested columns:
- `source_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `source_name` TEXT NOT NULL
- `source_type` TEXT NOT NULL
- `access_method` TEXT
- `base_url` TEXT
- `description` TEXT
- `created_at` TEXT
- `updated_at` TEXT

Notes:
- `source_type` is a plain text field for MVP
- later it can be normalized into a lookup table if needed

### 3.2 `source_datasets`
Stores dataset snapshots from each source.

Suggested columns:
- `dataset_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `source_id` INTEGER NOT NULL
- `dataset_name` TEXT NOT NULL
- `dataset_version` TEXT
- `snapshot_time` TEXT
- `row_count` INTEGER
- `column_count` INTEGER
- `query_signature` TEXT
- `created_at` TEXT

Foreign keys:
- `source_id` -> `data_sources.source_id`

Suggested index:
- `idx_source_datasets_source_id`

### 3.3 `dataset_records`
Stores raw imported records.

Suggested columns:
- `record_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `dataset_id` INTEGER NOT NULL
- `source_row_key` TEXT
- `object_name` TEXT
- `object_family` TEXT
- `raw_payload` TEXT NOT NULL
- `ingested_at` TEXT

Foreign keys:
- `dataset_id` -> `source_datasets.dataset_id`

Suggested indexes:
- `idx_dataset_records_dataset_id`
- `idx_dataset_records_object_name`

Notes:
- `raw_payload` stores JSON text
- this keeps the raw import flexible without a huge wide table

### 3.4 `cleaned_records`
Stores cleaned versions of raw records.

Suggested columns:
- `cleaned_record_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `record_id` INTEGER NOT NULL
- `clean_version` TEXT
- `clean_payload` TEXT NOT NULL
- `cleaning_flags` TEXT
- `cleaned_at` TEXT

Foreign keys:
- `record_id` -> `dataset_records.record_id`

Suggested index:
- `idx_cleaned_records_record_id`

### 3.5 `feature_sets`
Defines feature construction recipes.

Suggested columns:
- `feature_set_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `feature_set_name` TEXT NOT NULL
- `feature_version` TEXT
- `scaling_method` TEXT
- `description` TEXT
- `created_at` TEXT

Suggested unique constraint:
- `(feature_set_name, feature_version)`

### 3.6 `feature_definitions`
Defines feature names and how they are derived.

Suggested columns:
- `feature_definition_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `feature_set_id` INTEGER NOT NULL
- `feature_name` TEXT NOT NULL
- `source_column_name` TEXT
- `transformation_type` TEXT
- `transformation_parameters` TEXT
- `feature_order` INTEGER
- `created_at` TEXT

Foreign keys:
- `feature_set_id` -> `feature_sets.feature_set_id`

Suggested indexes:
- `idx_feature_definitions_feature_set_id`
- `idx_feature_definitions_feature_name`

Notes:
- `source_column_name` is acceptable for MVP
- later, it can be replaced or supplemented by a normalized source-column table if needed

### 3.7 `feature_values`
Stores feature values for each cleaned record.

Suggested columns:
- `feature_value_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `cleaned_record_id` INTEGER NOT NULL
- `feature_definition_id` INTEGER NOT NULL
- `feature_value_num` REAL
- `feature_value_text` TEXT
- `created_at` TEXT

Foreign keys:
- `cleaned_record_id` -> `cleaned_records.cleaned_record_id`
- `feature_definition_id` -> `feature_definitions.feature_definition_id`

Suggested indexes:
- `idx_feature_values_cleaned_record_id`
- `idx_feature_values_feature_definition_id`

### 3.8 `analysis_task_types`
Lookup table for task categories.

Suggested columns:
- `task_type_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_type_name` TEXT NOT NULL UNIQUE
- `description` TEXT

Suggested seed values:
- overview
- eda
- structure
- comparison
- explanation

### 3.9 `analysis_tasks`
Stores the analytical intent.

Suggested columns:
- `task_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id` TEXT NOT NULL
- `task_type_id` INTEGER NOT NULL
- `source_scope` TEXT
- `filters` TEXT
- `target_variables` TEXT
- `task_name` TEXT
- `task_status` TEXT
- `created_at` TEXT
- `updated_at` TEXT

Foreign keys:
- `session_id` -> `user_sessions.session_id`
- `task_type_id` -> `analysis_task_types.task_type_id`

Suggested indexes:
- `idx_analysis_tasks_session_id`
- `idx_analysis_tasks_task_type_id`

### 3.10 `analysis_methods`
Lookup table for analysis methods.

Suggested columns:
- `method_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `method_name` TEXT NOT NULL UNIQUE
- `method_family` TEXT
- `description` TEXT

Suggested seed values:
- PCA
- t-SNE
- UMAP
- correlation
- clustering
- anomaly detection

### 3.11 `analysis_runs`
Stores one execution of an analysis method.

Suggested columns:
- `run_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL
- `method_id` INTEGER NOT NULL
- `parameters` TEXT
- `input_snapshot_hash` TEXT
- `runtime_ms` INTEGER
- `run_status` TEXT
- `created_at` TEXT

Foreign keys:
- `task_id` -> `analysis_tasks.task_id`
- `method_id` -> `analysis_methods.method_id`

Suggested indexes:
- `idx_analysis_runs_task_id`
- `idx_analysis_runs_method_id`

### 3.12 `analysis_results`
Stores run outputs.

Suggested columns:
- `result_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `run_id` INTEGER NOT NULL
- `result_type` TEXT NOT NULL
- `result_payload` TEXT NOT NULL
- `summary_text` TEXT
- `created_at` TEXT

Foreign keys:
- `run_id` -> `analysis_runs.run_id`

Suggested index:
- `idx_analysis_results_run_id`

### 3.13 `chart_types`
Lookup table for chart categories.

Suggested columns:
- `chart_type_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `chart_type_name` TEXT NOT NULL UNIQUE
- `description` TEXT

Suggested seed values:
- histogram
- scatter
- heatmap
- boxplot
- parallel_coordinates
- embedding
- comparison_matrix

### 3.14 `chart_configs`
Stores visualization configurations.

Suggested columns:
- `chart_config_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL
- `chart_type_id` INTEGER NOT NULL
- `encoding_spec` TEXT
- `color_theme` TEXT
- `axis_mapping` TEXT
- `layout_spec` TEXT
- `created_at` TEXT

Foreign keys:
- `task_id` -> `analysis_tasks.task_id`
- `chart_type_id` -> `chart_types.chart_type_id`

Suggested indexes:
- `idx_chart_configs_task_id`
- `idx_chart_configs_chart_type_id`

### 3.15 `user_sessions`
Stores one exploration session.

Suggested columns:
- `session_id` TEXT PRIMARY KEY
- `user_id` TEXT
- `started_at` TEXT NOT NULL
- `ended_at` TEXT
- `current_page` TEXT
- `active_dataset_id` INTEGER
- `active_task_id` INTEGER
- `metadata` TEXT

Foreign keys:
- `active_dataset_id` -> `source_datasets.dataset_id`
- `active_task_id` -> `analysis_tasks.task_id`

Suggested indexes:
- `idx_user_sessions_active_dataset_id`
- `idx_user_sessions_active_task_id`

### 3.16 `interaction_events`
Stores user actions.

Suggested columns:
- `event_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id` TEXT NOT NULL
- `task_id` INTEGER
- `event_type` TEXT NOT NULL
- `target_view` TEXT
- `event_payload` TEXT
- `created_at` TEXT

Foreign keys:
- `session_id` -> `user_sessions.session_id`
- `task_id` -> `analysis_tasks.task_id`

Suggested indexes:
- `idx_interaction_events_session_id`
- `idx_interaction_events_task_id`

### 3.17 `interpretation_claims`
Stores final explanatory conclusions.

Suggested columns:
- `claim_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL
- `claim_text` TEXT NOT NULL
- `confidence_level` REAL
- `created_at` TEXT

Foreign keys:
- `task_id` -> `analysis_tasks.task_id`

Suggested index:
- `idx_interpretation_claims_task_id`

---

## 4. Optional tables for later

These are not required for the first physical build, but they can be added later if the project needs more strict provenance or deeper normalization:
- `data_source_types`
- `interaction_event_types`
- `evidence_sources`
- `evidence_items`
- `claim_support_links`
- `dataset_columns`
- `record_attributes`
- `reduction_results`
- `reduction_coordinates`

---

## 5. Suggested implementation order

### Phase 1: core data storage
1. `data_sources`
2. `source_datasets`
3. `dataset_records`
4. `cleaned_records`

### Phase 2: feature layer
5. `feature_sets`
6. `feature_definitions`
7. `feature_values`

### Phase 3: analysis layer
8. `analysis_task_types`
9. `analysis_tasks`
10. `analysis_methods`
11. `analysis_runs`
12. `analysis_results`

### Phase 4: visualization and behavior
13. `chart_types`
14. `chart_configs`
15. `user_sessions`
16. `interaction_events`
17. `interpretation_claims`

---

## 6. Migration strategy from the current codebase

The existing schema in `src/database/local_storage.py` can remain temporarily as a compatibility layer.

Recommended migration path:
1. keep old tables working so the current app does not break
2. add the new MVP tables in a new migration step
3. gradually route the frontend and APIs to the new tables
4. once stable, deprecate or map old classification-centric tables into the new workflow model

---

## 7. Indexing and query performance notes

The MVP will likely query most often by:
- source id
- dataset id
- session id
- task id
- run id
- cleaned record id
- feature definition id

Therefore, these indexes are important from day one.

---

## 8. Physical design note

The first physical schema is intentionally pragmatic:
- it keeps JSON text for flexible payloads
- it uses lookup tables only where they clearly help normalization and reuse
- it avoids over-modeling source-specific details before the source fields are fully mapped

This is the right tradeoff for the current stage of the project.
