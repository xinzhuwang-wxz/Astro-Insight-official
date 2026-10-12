# Minimal Logical Design Diagram

Date: 2026-04-26

## 1. One-line relationship map

`data_sources` -> `source_datasets` -> `dataset_records` -> `cleaned_records` -> `feature_values` -> `analysis_runs` -> `analysis_results` -> `chart_configs` -> `interpretation_claims`

In parallel:
- `user_sessions` anchors the user context
- `interaction_events` records behavior under the session
- `analysis_tasks` connects the analytical intent to the computation chain
- `feature_sets` defines the feature construction rule set used by `feature_values`

---

## 2. Simple ER-style explanation

### Source and data flow
- One `data_sources` row can have many `source_datasets`
- One `source_datasets` row can have many `dataset_records`
- One `dataset_records` row can have many `cleaned_records` if the data are processed by different cleaning versions

### Feature flow
- One `cleaned_records` row can have many `feature_values`
- One `feature_sets` row can be used by many `feature_values`

### Analysis flow
- One `analysis_tasks` row can spawn many `analysis_runs`
- One `analysis_runs` row can produce many `analysis_results`
- One `analysis_tasks` row can also generate one or more `chart_configs`
- One `analysis_tasks` row can end with one or more `interpretation_claims`

### Session and behavior flow
- One `user_sessions` row can have many `interaction_events`
- One `user_sessions` row can point to the currently active dataset and task

---

## 3. Text diagram

```text
[data_sources]
      |
      v
[source_datasets]
      |
      v
[dataset_records] -----> [cleaned_records] -----> [feature_values] -----> [analysis_runs] -----> [analysis_results]
                                  ^                     ^                       ^                        |
                                  |                     |                       |                        v
                             (cleaning)           [feature_sets]           [analysis_tasks]      [chart_configs]
                                                                                 |
                                                                                 v
                                                                       [interpretation_claims]

[user_sessions] -----> [interaction_events]
      |
      +---- active_dataset_id ----> [source_datasets]
      +---- active_task_id --------> [analysis_tasks]
```

---

## 4. What each table does in the story

- `data_sources`: identifies where the data came from
- `source_datasets`: stores imported snapshots or query results
- `dataset_records`: keeps raw source records
- `cleaned_records`: preserves preprocessing history
- `feature_sets`: defines feature engineering recipes
- `feature_values`: stores analysis-ready feature values
- `analysis_tasks`: stores what the user wants to investigate
- `analysis_runs`: stores the method execution itself
- `analysis_results`: stores outputs for charts and comparisons
- `chart_configs`: stores visualization choices
- `user_sessions`: keeps one analytical journey together
- `interaction_events`: records clicks, filters, brushes, and parameter changes
- `interpretation_claims`: stores the final explanation or conclusion
