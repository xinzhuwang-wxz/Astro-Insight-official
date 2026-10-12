# Logical Design Draft

Date: 2026-04-26

## 1. Goal of the logical design

The conceptual model is now converted into a normalized relational structure that can satisfy **3NF** while still supporting:
- multiple astronomy data sources
- preprocessing history
- feature engineering
- exploratory analysis
- dimensionality reduction
- visualization recommendations
- user session and behavior tracking
- evidence-backed explanations

The design does **not** mirror any external source table one-to-one. Instead, it stores a normalized internal schema and keeps source-specific variability in dedicated source and raw-data tables.

---

## 2. Normalization principles used

### 2.1 First Normal Form
- each field is atomic from the database point of view
- repeating groups are separated into child tables
- multi-valued source-specific payloads are not flattened into one wide table unless they are genuinely atomic in the business model

### 2.2 Second Normal Form
- non-key attributes depend on the full key
- many-to-many relationships are split into bridge tables
- derived labels and lookup values are separated from core facts

### 2.3 Third Normal Form
- no transitive dependency between non-key attributes
- descriptive metadata about a source, chart type, pipeline, or method lives in its own lookup/entity table
- analysis results and user interactions do not duplicate source descriptions

---

## 3. Logical entity groups and table mapping

## A. Data source layer

### 3.1 `source_types`
Lookup table for source categories.

Suggested attributes:
- `source_type_id` PK
- `source_type_name`
- `description`

Examples:
- archive
- catalog
- kaggle dataset
- literature API
- enrichment service

Purpose:
- normalize source classification
- avoid repeating category text in every source row

### 3.2 `data_sources`
Represents a concrete external source or service.

Suggested attributes:
- `source_id` PK
- `source_type_id` FK -> `source_types.source_type_id`
- `source_name`
- `access_method`
- `base_url`
- `license_name`
- `reliability_notes`
- `status`

Purpose:
- store stable source metadata once
- support multiple source families uniformly

### 3.3 `source_datasets`
Represents a specific import snapshot or query result from a source.

Suggested attributes:
- `dataset_id` PK
- `source_id` FK -> `data_sources.source_id`
- `dataset_name`
- `dataset_version`
- `query_signature`
- `snapshot_time`
- `row_count`
- `column_count`
- `coverage_notes`

Purpose:
- separate the source from each imported dataset instance
- support versioning and reproducibility

### 3.4 `dataset_columns`
Stores metadata for columns discovered in each imported dataset snapshot.

Suggested attributes:
- `column_id` PK
- `dataset_id` FK -> `source_datasets.dataset_id`
- `column_name`
- `data_type`
- `semantic_role`
- `unit_name` nullable
- `is_nullable`
- `is_key_candidate`
- `description`

Purpose:
- normalize schema discovery
- keep column metadata separate from record data

---

## B. Astronomy record layer

### 3.5 `astronomy_objects`
Canonical object entity table.

Suggested attributes:
- `object_id` PK
- `canonical_name`
- `object_family`  // exoplanet_system, star, galaxy, qso, etc.
- `object_status`
- `created_at`
- `updated_at`

Purpose:
- represent the logical object being analyzed
- avoid mixing source-specific observations into the core object row

### 3.6 `object_identifiers`
Stores alternate names and source-specific identifiers.

Suggested attributes:
- `identifier_id` PK
- `object_id` FK -> `astronomy_objects.object_id`
- `source_id` FK -> `data_sources.source_id`
- `identifier_type`
- `identifier_value`

Purpose:
- keep alternate names normalized
- support SIMBAD cross-reference and source aliasing

### 3.7 `raw_records`
Stores one imported record from one dataset.

Suggested attributes:
- `raw_record_id` PK
- `dataset_id` FK -> `source_datasets.dataset_id`
- `object_id` FK -> `astronomy_objects.object_id` nullable
- `source_row_key`
- `raw_payload` JSON
- `ingested_at`
- `record_hash`

Purpose:
- preserve source fidelity
- support traceability to the exact imported row

### 3.8 `record_attributes`
Stores normalized atomic observations from raw records.

Suggested attributes:
- `attribute_id` PK
- `raw_record_id` FK -> `raw_records.raw_record_id`
- `column_id` FK -> `dataset_columns.column_id`
- `attribute_value_text` nullable
- `attribute_value_num` nullable
- `attribute_value_date` nullable
- `attribute_value_bool` nullable
- `value_unit` nullable

Purpose:
- provide 3NF-friendly storage for source fields
- avoid storing repeated wide raw fields in the main record table

Note:
- only one value type should be populated per row
- the value type used depends on the semantic type of the original column

---

## C. Transformation layer

### 3.9 `cleaning_pipelines`
Defines preprocessing workflows.

Suggested attributes:
- `pipeline_id` PK
- `pipeline_name`
- `pipeline_version`
- `description`
- `status`

### 3.10 `pipeline_steps`
Defines ordered steps inside a pipeline.

Suggested attributes:
- `step_id` PK
- `pipeline_id` FK -> `cleaning_pipelines.pipeline_id`
- `step_order`
- `step_name`
- `step_type`
- `step_parameters` JSON

Purpose:
- separate pipeline definition from pipeline execution
- support reusable and versioned cleaning logic

### 3.11 `cleaned_records`
Represents a cleaned version of a raw record.

Suggested attributes:
- `cleaned_record_id` PK
- `raw_record_id` FK -> `raw_records.raw_record_id`
- `pipeline_id` FK -> `cleaning_pipelines.pipeline_id`
- `clean_version`
- `cleaned_at`

### 3.12 `cleaned_attributes`
Stores cleaned observations after preprocessing.

Suggested attributes:
- `cleaned_attribute_id` PK
- `cleaned_record_id` FK -> `cleaned_records.cleaned_record_id`
- `column_id` FK -> `dataset_columns.column_id`
- `cleaned_value_text` nullable
- `cleaned_value_num` nullable
- `cleaned_value_date` nullable
- `cleaned_value_bool` nullable
- `cleaning_flags` JSON nullable

Purpose:
- store transformed field values in normalized form
- keep cleaning output separate from raw input

---

## D. Feature layer

### 3.13 `feature_sets`
Defines a feature configuration.

Suggested attributes:
- `feature_set_id` PK
- `feature_set_name`
- `feature_version`
- `scaling_method`
- `description`

### 3.14 `feature_definitions`
Defines which columns or transformed metrics belong to a feature set.

Suggested attributes:
- `feature_definition_id` PK
- `feature_set_id` FK -> `feature_sets.feature_set_id`
- `feature_name`
- `source_column_id` FK -> `dataset_columns.column_id` nullable
- `transformation_type`
- `transformation_parameters` JSON
- `feature_order`

Purpose:
- keep feature construction rules explicit
- support multiple comparable feature sets

### 3.15 `feature_values`
Stores feature values per cleaned record.

Suggested attributes:
- `feature_value_id` PK
- `cleaned_record_id` FK -> `cleaned_records.cleaned_record_id`
- `feature_definition_id` FK -> `feature_definitions.feature_definition_id`
- `feature_value_num` nullable
- `feature_value_text` nullable
- `feature_value_date` nullable

Purpose:
- keep derived features normalized
- support PCA, clustering, and EDA

---

## E. Analysis layer

### 3.16 `analysis_task_types`
Lookup table for task categories.

Suggested attributes:
- `task_type_id` PK
- `task_type_name`
- `description`

Examples:
- overview
- eda
- structure
- comparison
- explanation

### 3.17 `analysis_tasks`
Represents a user or system task.

Suggested attributes:
- `task_id` PK
- `task_type_id` FK -> `analysis_task_types.task_type_id`
- `session_id` FK -> `user_sessions.session_id`
- `dataset_scope_id` FK -> `source_datasets.dataset_id` nullable
- `task_name`
- `task_status`
- `filters` JSON
- `created_at`
- `updated_at`

### 3.18 `analysis_methods`
Lookup table for analysis methods.

Suggested attributes:
- `method_id` PK
- `method_name`
- `method_family`
- `description`

Examples:
- PCA
- t-SNE
- UMAP
- correlation
- clustering
- anomaly detection

### 3.19 `analysis_runs`
Represents one execution of a method for a task.

Suggested attributes:
- `run_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `method_id` FK -> `analysis_methods.method_id`
- `run_status`
- `input_snapshot_hash`
- `parameters` JSON
- `runtime_ms`
- `created_at`

### 3.20 `analysis_results`
Stores generic outputs of an analysis run.

Suggested attributes:
- `result_id` PK
- `run_id` FK -> `analysis_runs.run_id`
- `result_type`
- `summary_text`
- `created_at`

### 3.21 `result_payload_items`
Stores normalized pieces of a result payload when the result is not naturally a single scalar.

Suggested attributes:
- `payload_item_id` PK
- `result_id` FK -> `analysis_results.result_id`
- `payload_key`
- `payload_value_text` nullable
- `payload_value_num` nullable
- `payload_value_json` nullable

Purpose:
- preserve 3NF when result payloads contain repeated structured elements
- avoid denormalized blobs for reusable result parts

### 3.22 `reduction_results`
Specialized result table for PCA / t-SNE / UMAP-like outputs.

Suggested attributes:
- `reduction_result_id` PK
- `run_id` FK -> `analysis_runs.run_id`
- `dimensions`
- `explained_variance_json` nullable
- `quality_metrics_json` nullable

### 3.23 `reduction_coordinates`
Stores one row per embedded object/record.

Suggested attributes:
- `coordinate_id` PK
- `reduction_result_id` FK -> `reduction_results.reduction_result_id`
- `cleaned_record_id` FK -> `cleaned_records.cleaned_record_id`
- `dim_1`
- `dim_2`
- `dim_3` nullable
- `cluster_label` nullable
- `point_metadata` JSON nullable

Purpose:
- support linked brushing and point selection
- keep coordinates queryable in row form

---

## F. Visualization layer

### 3.24 `chart_types`
Lookup table for chart categories.

Suggested attributes:
- `chart_type_id` PK
- `chart_type_name`
- `description`

### 3.25 `chart_configs`
Stores a reusable chart specification.

Suggested attributes:
- `chart_config_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `chart_type_id` FK -> `chart_types.chart_type_id`
- `encoding_spec` JSON
- `color_theme`
- `axis_mapping` JSON
- `layout_spec` JSON
- `created_at`
- `updated_at`

### 3.26 `chart_instances`
Stores a rendered chart in a session.

Suggested attributes:
- `chart_instance_id` PK
- `chart_config_id` FK -> `chart_configs.chart_config_id`
- `session_id` FK -> `user_sessions.session_id`
- `render_state` JSON
- `rendered_at`

### 3.27 `chart_recommendations`
Stores recommended chart choices.

Suggested attributes:
- `recommendation_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `recommended_chart_type_id` FK -> `chart_types.chart_type_id`
- `reasoning`
- `confidence_score`
- `created_at`

---

## G. User and behavior layer

### 3.28 `user_sessions`
Stores one exploration session.

Suggested attributes:
- `session_id` PK
- `user_id` nullable
- `started_at`
- `ended_at` nullable
- `current_page`
- `active_dataset_id` FK -> `source_datasets.dataset_id` nullable
- `active_task_id` FK -> `analysis_tasks.task_id` nullable
- `metadata` JSON nullable

### 3.29 `interaction_event_types`
Lookup table for event categories.

Suggested attributes:
- `event_type_id` PK
- `event_type_name`
- `description`

### 3.30 `interaction_events`
Stores user actions during a session.

Suggested attributes:
- `event_id` PK
- `session_id` FK -> `user_sessions.session_id`
- `task_id` FK -> `analysis_tasks.task_id` nullable
- `event_type_id` FK -> `interaction_event_types.event_type_id`
- `target_view`
- `target_element`
- `event_payload` JSON
- `created_at`

### 3.31 `query_history`
Stores user queries or prompts.

Suggested attributes:
- `query_id` PK
- `session_id` FK -> `user_sessions.session_id`
- `task_id` FK -> `analysis_tasks.task_id` nullable
- `query_text`
- `query_type`
- `execution_time_ms`
- `success`
- `created_at`

---

## H. Evidence and explanation layer

### 3.32 `evidence_sources`
Lookup table for evidence categories.

Suggested attributes:
- `evidence_source_id` PK
- `source_name`
- `source_type`
- `access_url`

### 3.33 `evidence_items`
Stores literature or citation entries.

Suggested attributes:
- `evidence_item_id` PK
- `evidence_source_id` FK -> `evidence_sources.evidence_source_id`
- `title`
- `authors`
- `year`
- `reference_text`
- `metadata` JSON

### 3.34 `interpretation_claims`
Stores analytical conclusions.

Suggested attributes:
- `claim_id` PK
- `task_id` FK -> `analysis_tasks.task_id`
- `claim_text`
- `confidence_level`
- `created_at`

### 3.35 `claim_support_links`
Links a claim to the evidence or result items that support it.

Suggested attributes:
- `link_id` PK
- `claim_id` FK -> `interpretation_claims.claim_id`
- `evidence_item_id` FK -> `evidence_items.evidence_item_id` nullable
- `result_id` FK -> `analysis_results.result_id` nullable
- `chart_instance_id` FK -> `chart_instances.chart_instance_id` nullable
- `support_note`

Purpose:
- keep explanations auditable and traceable
- avoid ungrounded summary text

---

## 4. Important relationship rules

### 4.1 One source can produce many datasets
A single `data_sources` row may correspond to many `source_datasets` snapshots.

### 4.2 One dataset can produce many raw records
A dataset snapshot contains many `raw_records`.

### 4.3 One raw record can produce many cleaned versions only if the pipeline differs
If the same raw record is processed through multiple cleaning pipelines, each pipeline creates its own `cleaned_records` row.

### 4.4 One cleaned record can produce many features
Different feature sets may derive from the same cleaned record.

### 4.5 One task can have many runs
A task may run multiple methods or parameter settings.

### 4.6 One run can have multiple result representations
A run may have a generic result, a reduction result, and coordinate rows.

### 4.7 One session can contain many charts and interactions
A session is the top-level behavior container.

---

## 5. Source-specific modeling implications

### PSCompPars
Use it as a source dataset that maps into:
- source metadata
- astronomical objects
- object identifiers
- raw records
- cleaned records
- features
- reduction outputs

### Kaggle SDSS19 Stellar Classification Star/Galaxy/QSO
Use it as a second primary analytical source with a similar pipeline but a different object family and feature space.

### SIMBAD
Use it primarily for:
- `object_identifiers`
- enrichment metadata
- cross-references

### Literature API
Use it for:
- `evidence_items`
- interpretation support
- comparison claims

---

## 6. Tables that are likely lookup tables
These should remain small and highly reusable:
- `source_types`
- `analysis_task_types`
- `analysis_methods`
- `chart_types`
- `interaction_event_types`
- `evidence_sources`

These lookup tables are important for 3NF because they prevent repeated descriptive text across the database.

---

## 7. Tables that are likely fact / event tables
These capture time-based or instance-based data:
- `source_datasets`
- `raw_records`
- `record_attributes`
- `cleaned_records`
- `cleaned_attributes`
- `feature_values`
- `analysis_tasks`
- `analysis_runs`
- `analysis_results`
- `reduction_results`
- `reduction_coordinates`
- `chart_configs`
- `chart_instances`
- `interaction_events`
- `query_history`
- `interpretation_claims`
- `claim_support_links`

---

## 8. Logical design decision on JSON usage
JSON is allowed only where it does not break the logical separation of entities:
- source-specific raw payloads
- parameter bags
- render state
- evidence metadata
- result metadata

But if a field becomes important for filtering, joining, or comparison, it should be promoted into a normalized column or child table.

---

## 9. Recommended next step

The next step is **physical design**, which means:
- choosing the concrete SQL tables for MVP
- defining primary keys and foreign keys
- deciding which tables to implement first
- mapping the existing SQLite schema to the new normalized schema
