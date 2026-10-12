# MVP Table Priority Plan

Date: 2026-04-26

## Goal

Compress the 17-table physical design into the smallest practical schema that can still deliver the core project story:
- ingest astronomy data from multiple sources
- clean and normalize it
- build features
- run analysis tasks
- generate chart configs
- track sessions and interactions
- produce explanatory claims

This is the implementation-first version.

---

## 1. Tier 1 — Must implement first
These tables are required for the MVP to function end-to-end.

### 1) `data_sources`
Why it is essential:
- every dataset must come from somewhere
- source metadata is needed for PSCompPars, Kaggle, SIMBAD, and literature API

### 2) `source_datasets`
Why it is essential:
- represents one import snapshot or query result
- allows versioning and reproducibility

### 3) `dataset_records`
Why it is essential:
- stores raw imported records
- keeps the source fidelity needed for traceability

### 4) `cleaned_records`
Why it is essential:
- stores cleaned/normalized versions of raw records
- preserves preprocessing history

### 5) `feature_sets`
Why it is essential:
- defines which feature recipe is being used
- lets the platform compare different analytical views

### 6) `feature_definitions`
Why it is essential:
- removes repeated feature-name logic from per-record value rows
- keeps feature engineering explicit and reusable

### 7) `feature_values`
Why it is essential:
- provides analysis-ready numeric/text values
- powers EDA, PCA, clustering, and comparison

### 8) `analysis_task_types`
Why it is essential:
- normalizes the task categories
- keeps the task schema clean

### 9) `analysis_tasks`
Why it is essential:
- stores what the user wants to analyze
- acts as the anchor for the whole workflow

### 10) `analysis_methods`
Why it is essential:
- normalizes method names such as PCA, t-SNE, UMAP
- avoids repeated method labels in run rows

### 11) `analysis_runs`
Why it is essential:
- stores each computation run
- preserves parameters and runtime for comparison

### 12) `analysis_results`
Why it is essential:
- stores run outputs
- feeds the explanation page and chart rendering

### 13) `chart_types`
Why it is essential:
- normalizes chart categories
- supports recommendation and comparison

### 14) `chart_configs`
Why it is essential:
- stores chart encodings and layout choices
- captures the core visualization strategy being studied

### 15) `user_sessions`
Why it is essential:
- keeps the user’s analytical journey together
- connects pages, filters, and tasks

### 16) `interaction_events`
Why it is essential:
- records clicks, filters, brush actions, parameter changes
- supports linked-view and behavior analysis

### 17) `interpretation_claims`
Why it is essential:
- stores the final explanation or conclusion
- makes the platform result-oriented rather than chart-only

---

## 2. Tier 2 — Can be deferred until after MVP
These tables are useful, but they are not required for the first working version.

### Deferred helpers / provenance / explanation extras
- `data_source_types`
- `dataset_columns`
- `record_attributes`
- `reduction_results`
- `reduction_coordinates`
- `interaction_event_types`
- `evidence_sources`
- `evidence_items`
- `claim_support_links`

Why they can wait:
- they improve normalization and provenance
- but they are not needed to prove the core platform concept
- the MVP can use JSON payloads and simple text fields first

---

## 3. Recommended MVP schema shape

The smallest useful implementation should be treated as **three connected lanes**:

### Lane A — Data lane
- `data_sources`
- `source_datasets`
- `dataset_records`
- `cleaned_records`
- `feature_sets`
- `feature_definitions`
- `feature_values`

### Lane B — Analysis lane
- `analysis_task_types`
- `analysis_tasks`
- `analysis_methods`
- `analysis_runs`
- `analysis_results`

### Lane C — UX / explanation lane
- `chart_types`
- `chart_configs`
- `user_sessions`
- `interaction_events`
- `interpretation_claims`

This is the practical minimum that still supports the full narrative.

---

## 4. Why this is the best compression

If we compress further than this, we start losing one of the core project goals:
- no source tracking
- no cleaning history
- no feature engineering clarity
- no method comparison
- no chart strategy records
- no session replay
- no explanation traceability

So this 17-table version is already the smallest schema that still feels like a real analytical platform.

---

## 5. Even smaller emergency fallback
If time becomes extremely limited, the absolute emergency fallback would be:
- `data_sources`
- `source_datasets`
- `dataset_records`
- `cleaned_records`
- `feature_values`
- `analysis_tasks`
- `analysis_runs`
- `chart_configs`
- `user_sessions`
- `interaction_events`
- `interpretation_claims`

But this fallback sacrifices feature-definition clarity and method normalization, so it should only be used if the schedule becomes very tight.
