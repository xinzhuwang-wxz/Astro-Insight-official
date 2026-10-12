# MVP Schema Blueprint

Date: 2026-04-26

## 1. Purpose

This document turns the MVP table-priority plan into a concrete build order and field draft that is close enough to SQL implementation.

The aim is to keep the first schema:
- compact
- normalized enough for the platform story
- realistic to implement in the current codebase
- expandable later without a full redesign

---

## 2. Build order

### Phase 1 — Core data ingestion lane
Build these first because everything else depends on them.
1. `data_sources`
2. `source_datasets`
3. `dataset_records`
4. `cleaned_records`

### Phase 2 — Feature engineering lane
Build these after the core data lane is in place.
5. `feature_sets`
6. `feature_definitions`
7. `feature_values`

### Phase 3 — Analysis lane
Build these once the feature lane is available.
8. `analysis_task_types`
9. `analysis_tasks`
10. `analysis_methods`
11. `analysis_runs`
12. `analysis_results`

### Phase 4 — Visualization and UX lane
Build these to support the visual workbench.
13. `chart_types`
14. `chart_configs`
15. `user_sessions`
16. `interaction_events`
17. `interpretation_claims`

---

## 3. Field drafts by table

## 3.1 `data_sources`
Source registry.

Recommended fields:
- `source_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `source_name` TEXT NOT NULL
- `source_type` TEXT NOT NULL
- `access_method` TEXT
- `base_url` TEXT
- `description` TEXT
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

Notes:
- keep `source_type` as TEXT in MVP
- later it can become a lookup table if needed

---

## 3.2 `source_datasets`
Imported dataset snapshot registry.

Recommended fields:
- `dataset_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `source_id` INTEGER NOT NULL
- `dataset_name` TEXT NOT NULL
- `dataset_version` TEXT
- `snapshot_time` TEXT
- `row_count` INTEGER
- `column_count` INTEGER
- `query_signature` TEXT
- `created_at` TEXT NOT NULL

Foreign key:
- `source_id` -> `data_sources.source_id`

Recommended index:
- `source_id`

---

## 3.3 `dataset_records`
Raw imported records.

Recommended fields:
- `record_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `dataset_id` INTEGER NOT NULL
- `source_row_key` TEXT
- `object_name` TEXT
- `object_family` TEXT
- `raw_payload` TEXT NOT NULL
- `ingested_at` TEXT NOT NULL

Foreign key:
- `dataset_id` -> `source_datasets.dataset_id`

Notes:
- `raw_payload` stores JSON text
- `object_name` and `object_family` are useful for display and filtering, but not all source rows will populate them equally

Recommended index:
- `dataset_id`

---

## 3.4 `cleaned_records`
Cleaned versions of raw records.

Recommended fields:
- `cleaned_record_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `record_id` INTEGER NOT NULL
- `clean_version` TEXT
- `clean_payload` TEXT NOT NULL
- `cleaning_flags` TEXT
- `cleaned_at` TEXT NOT NULL

Foreign key:
- `record_id` -> `dataset_records.record_id`

Recommended index:
- `record_id`

---

## 3.5 `feature_sets`
Feature recipe registry.

Recommended fields:
- `feature_set_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `feature_set_name` TEXT NOT NULL
- `feature_version` TEXT
- `scaling_method` TEXT
- `description` TEXT
- `created_at` TEXT NOT NULL

Notes:
- keep this table small and reusable
- feature recipes should be versioned if the feature logic changes

---

## 3.6 `feature_definitions`
Feature definition registry.

Recommended fields:
- `feature_definition_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `feature_set_id` INTEGER NOT NULL
- `feature_name` TEXT NOT NULL
- `source_column_name` TEXT
- `transformation_type` TEXT
- `transformation_parameters` TEXT
- `feature_order` INTEGER
- `created_at` TEXT NOT NULL

Foreign key:
- `feature_set_id` -> `feature_sets.feature_set_id`

Notes:
- `source_column_name` is enough for MVP
- a later version can replace it with a `dataset_columns` FK

Recommended index:
- `feature_set_id`

---

## 3.7 `feature_values`
Feature values per cleaned record.

Recommended fields:
- `feature_value_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `cleaned_record_id` INTEGER NOT NULL
- `feature_definition_id` INTEGER NOT NULL
- `feature_value_num` REAL
- `feature_value_text` TEXT
- `created_at` TEXT NOT NULL

Foreign keys:
- `cleaned_record_id` -> `cleaned_records.cleaned_record_id`
- `feature_definition_id` -> `feature_definitions.feature_definition_id`

Recommended indexes:
- `cleaned_record_id`
- `feature_definition_id`

Notes:
- keep one value row per record-feature pair
- numeric values should go into `feature_value_num` whenever possible

---

## 3.8 `analysis_task_types`
Task category lookup.

Recommended fields:
- `task_type_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_type_name` TEXT NOT NULL
- `description` TEXT

Suggested seed values:
- overview
- eda
- structure
- comparison
- explanation

---

## 3.9 `analysis_tasks`
Task registry.

Recommended fields:
- `task_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_type_id` INTEGER NOT NULL
- `source_scope` TEXT
- `filters` TEXT
- `target_variables` TEXT
- `task_name` TEXT
- `task_status` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

Foreign key:
- `task_type_id` -> `analysis_task_types.task_type_id`

Recommended index:
- `task_type_id`

Notes:
- `source_scope`, `filters`, and `target_variables` can be JSON text in MVP
- these fields are intentionally flexible because task filters will evolve during design

---

## 3.10 `analysis_methods`
Method lookup.

Recommended fields:
- `method_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `method_name` TEXT NOT NULL
- `method_family` TEXT
- `description` TEXT

Suggested seed values:
- PCA
- t-SNE
- UMAP
- correlation
- clustering
- anomaly detection

---

## 3.11 `analysis_runs`
Run registry.

Recommended fields:
- `run_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL
- `method_id` INTEGER NOT NULL
- `parameters` TEXT
- `input_snapshot_hash` TEXT
- `runtime_ms` INTEGER
- `run_status` TEXT NOT NULL
- `created_at` TEXT NOT NULL

Foreign keys:
- `task_id` -> `analysis_tasks.task_id`
- `method_id` -> `analysis_methods.method_id`

Recommended indexes:
- `task_id`
- `method_id`

---

## 3.12 `analysis_results`
Run output registry.

Recommended fields:
- `result_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `run_id` INTEGER NOT NULL
- `result_type` TEXT NOT NULL
- `result_payload` TEXT NOT NULL
- `summary_text` TEXT
- `created_at` TEXT NOT NULL

Foreign key:
- `run_id` -> `analysis_runs.run_id`

Recommended index:
- `run_id`

Notes:
- `result_payload` is JSON text in MVP
- a later version can split reduction results into separate tables if needed

---

## 3.13 `chart_types`
Chart category lookup.

Recommended fields:
- `chart_type_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `chart_type_name` TEXT NOT NULL
- `description` TEXT

Suggested seed values:
- histogram
- scatter
- heatmap
- boxplot
- parallel_coordinates
- embedding
- comparison_matrix

---

## 3.14 `chart_configs`
Visualization config registry.

Recommended fields:
- `chart_config_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL
- `chart_type_id` INTEGER NOT NULL
- `encoding_spec` TEXT
- `color_theme` TEXT
- `axis_mapping` TEXT
- `layout_spec` TEXT
- `created_at` TEXT NOT NULL

Foreign keys:
- `task_id` -> `analysis_tasks.task_id`
- `chart_type_id` -> `chart_types.chart_type_id`

Recommended indexes:
- `task_id`
- `chart_type_id`

---

## 3.15 `user_sessions`
Session registry.

Recommended fields:
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

Recommended indexes:
- `active_dataset_id`
- `active_task_id`

Notes:
- `session_id` stays as TEXT because it is easy to generate and pass around in the app

---

## 3.16 `interaction_events`
Interaction log.

Recommended fields:
- `event_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `session_id` TEXT NOT NULL
- `task_id` INTEGER
- `event_type` TEXT NOT NULL
- `target_view` TEXT
- `event_payload` TEXT
- `created_at` TEXT NOT NULL

Foreign keys:
- `session_id` -> `user_sessions.session_id`
- `task_id` -> `analysis_tasks.task_id`

Recommended indexes:
- `session_id`
- `task_id`
- `event_type`

Notes:
- event payload can contain filters, clicked item IDs, view names, and parameter changes

---

## 3.17 `interpretation_claims`
Conclusion registry.

Recommended fields:
- `claim_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL
- `claim_text` TEXT NOT NULL
- `confidence_level` REAL
- `created_at` TEXT NOT NULL

Foreign key:
- `task_id` -> `analysis_tasks.task_id`

Recommended index:
- `task_id`

---

## 4. What should stay TEXT/JSON in MVP

To keep the first implementation fast, the following can remain JSON-text fields for now:
- `raw_payload`
- `clean_payload`
- `cleaning_flags`
- `source_scope`
- `filters`
- `target_variables`
- `parameters`
- `result_payload`
- `encoding_spec`
- `axis_mapping`
- `layout_spec`
- `metadata`
- `event_payload`

These are acceptable in MVP because they are mainly variable payloads, not core repeating facts.

---

## 5. What should be indexed first

If implementing in SQLite, prioritize these indexes:
- `source_datasets.source_id`
- `dataset_records.dataset_id`
- `cleaned_records.record_id`
- `feature_definitions.feature_set_id`
- `feature_values.cleaned_record_id`
- `feature_values.feature_definition_id`
- `analysis_tasks.task_type_id`
- `analysis_runs.task_id`
- `analysis_runs.method_id`
- `analysis_results.run_id`
- `chart_configs.task_id`
- `chart_configs.chart_type_id`
- `interaction_events.session_id`
- `interaction_events.task_id`
- `interaction_events.event_type`
- `interpretation_claims.task_id`

---

## 6. Implementation note

If you want the simplest practical first release, the tables can be created in exactly this order:
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

That is the most practical build order for the current project.
