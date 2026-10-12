# Minimal Logical Design Draft

Date: 2026-04-26

## 1. Why this minimal version exists

The full logical design was intentionally large. For implementation and communication, this document compresses the schema into a small set of core tables that still support the project goal:
- compare astronomy datasets
- perform EDA and dimensionality reduction
- recommend and explain visualizations
- track user sessions and interactions

This version is the one to use for MVP discussion.

---

## 2. Core table set

### 1) `data_sources`
Stores the source itself.
Examples:
- `PSCompPars`
- Kaggle SDSS19 Stellar Classification Star/Galaxy/QSO
- SIMBAD
- literature API

Main fields:
- `source_id` PK
- `source_name`
- `source_type`
- `access_method`
- `base_url`
- `description`

Purpose:
- keep source metadata in one place

### 2) `source_datasets`
Stores one imported snapshot or query result from a source.
Main fields:
- `dataset_id` PK
- `source_id` FK -> `data_sources.source_id`
- `dataset_name`
- `dataset_version`
- `snapshot_time`
- `row_count`
- `column_count`
- `query_signature`

Purpose:
- separate source from imported dataset instances

### 3) `dataset_records`
Stores raw imported records.
Main fields:
- `record_id` PK
- `dataset_id` FK -> `source_datasets.dataset_id`
- `source_row_key`
- `object_name`
- `object_family`
- `raw_payload` JSON
- `ingested_at`

Purpose:
- keep source fidelity
- support traceability

### 4) `cleaned_records`
Stores cleaned and normalized records.
Main fields:
- `cleaned_record_id` PK
- `record_id` FK -> `dataset_records.record_id`
- `clean_version`
- `clean_payload` JSON
- `cleaning_flags` JSON
- `cleaned_at`

Purpose:
- preserve preprocessing history
- allow multiple cleaning versions

### 5) `feature_sets`
Defines a feature configuration.
Main fields:
- `feature_set_id` PK
- `feature_set_name`
- `feature_version`
- `scaling_method`
- `description`

Purpose:
- make feature construction explicit

### 6) `feature_definitions`
Defines feature names and how they are derived.
Main fields:
- `feature_definition_id` PK
- `feature_set_id` FK -> `feature_sets.feature_set_id`
- `feature_name`
- `source_column_name` nullable
- `transformation_type`
- `transformation_parameters` JSON
- `feature_order`

Purpose:
- separate reusable feature definitions from per-record values
- reduce repetition of feature names inside value rows

### 7) `feature_values`
Stores feature values per cleaned record.
Main fields:
- `feature_value_id` PK
- `cleaned_record_id` FK -> `cleaned_records.cleaned_record_id`
- `feature_definition_id` FK -> `feature_definitions.feature_definition_id`
- `feature_value_num` nullable
- `feature_value_text` nullable

Purpose:
- support EDA, PCA, clustering, and comparisons

### 8) `analysis_task_types`
Lookup table for task categories.
Main fields:
- `task_type_id` PK
- `task_type_name`
- `description`

Purpose:
- normalize repeated task category labels

### 9) `analysis_tasks`
Stores one analysis intent.
Main fields:
- `task_id` PK
- `task_type_id` FK -> `analysis_task_types.task_type_id`
- `source_scope` JSON
- `filters` JSON
- `target_variables` JSON
- `task_name`
- `created_at`
- `task_status`

Purpose:
- represent what the user wants to do

### 10) `analysis_methods`
Lookup table for analysis methods.
Main fields:
- `method_id` PK
- `method_name`
- `method_family`
- `description`

Purpose:
- normalize repeated method labels

### 11) `analysis_runs`
Stores one execution of an analysis method.
Main fields:
- `run_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `method_id` FK -> `analysis_methods.method_id`
- `parameters` JSON
- `input_snapshot_hash`
- `runtime_ms`
- `run_status`
- `created_at`

Purpose:
- record computation and make it reproducible

### 12) `analysis_results`
Stores the outputs of a run.
Main fields:
- `result_id` PK
- `run_id` FK -> `analysis_runs.run_id`
- `result_type`
- `result_payload` JSON
- `summary_text`
- `created_at`

Purpose:
- store results for charts and interpretation

### 13) `chart_types`
Lookup table for chart categories.
Main fields:
- `chart_type_id` PK
- `chart_type_name`
- `description`

Purpose:
- normalize chart labels

### 14) `chart_configs`
Stores visualization settings.
Main fields:
- `chart_config_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `chart_type_id` FK -> `chart_types.chart_type_id`
- `encoding_spec` JSON
- `color_theme`
- `axis_mapping` JSON
- `layout_spec` JSON
- `created_at`

Purpose:
- support chart switching and recommendation

### 15) `user_sessions`
Stores one exploration session.
Main fields:
- `session_id` PK
- `user_id` nullable
- `started_at`
- `ended_at` nullable
- `current_page`
- `active_dataset_id` FK -> `source_datasets.dataset_id` nullable
- `active_task_id` FK -> `analysis_tasks.task_id` nullable

Purpose:
- keep the analysis context across pages

### 16) `interaction_events`
Stores user actions in a session.
Main fields:
- `event_id` PK
- `session_id` FK -> `user_sessions.session_id`
- `task_id` FK -> `analysis_tasks.task_id` nullable
- `event_type`
- `target_view`
- `event_payload` JSON
- `created_at`

Purpose:
- support behavior analysis and session replay

### 17) `interpretation_claims`
Stores final explanatory conclusions.
Main fields:
- `claim_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `claim_text`
- `confidence_level`
- `created_at`

Purpose:
- keep result explanations explicit and reviewable

---

## 3. Why this version is more normalized

Compared with the earlier minimal version, this revision reduces repetition by splitting out:
- task categories into `analysis_task_types`
- analysis methods into `analysis_methods`
- chart categories into `chart_types`
- feature naming and definition logic into `feature_definitions`

This makes the design cleaner and closer to 2NF / 3NF practice while still remaining compact enough for MVP implementation.

---

## 4. Optional tables for later

These are not required for MVP but can be added later if needed:
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

## 5. Why this version is enough for the project

This minimal set can already support the full main workflow:
1. import data from multiple sources
2. store raw records
3. clean and normalize data
4. build features
5. run analysis tasks
6. store analysis results
7. configure and compare charts
8. track user sessions and interactions
9. generate explanatory conclusions

That is enough for the project story:

> Different visualization choices can lead to different cognitive conclusions about astronomical data.

---

## 6. Recommended MVP implementation order

1. `data_sources`
2. `source_datasets`
3. `dataset_records`
4. `cleaned_records`
5. `feature_sets`
6. `feature_definitions`
7. `feature_values`
8. `analysis_task_types`
9. `analysis_tasks`
10. `analysis_methods`
11. `analysis_runs`
12. `analysis_results`
13. `chart_types`
14. `chart_configs`
15. `user_sessions`
16. `interaction_events`
17. `interpretation_claims`
