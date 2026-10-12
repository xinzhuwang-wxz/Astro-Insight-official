# Normalization Notes

Date: 2026-04-26

## What was discussed

The minimal logical design is close to 2NF, but it is not yet the cleanest possible version.

## Why it was considered only "near 2NF"

The main reason is that some implementation-friendly fields are still stored directly in core tables, such as:
- `feature_name` inside `feature_values`
- `task_type` inside `analysis_tasks`
- `chart_type` inside `chart_configs`
- some repeated descriptive labels that could become lookup-table values

These do not automatically break 2NF in a single-primary-key design, but they make the schema less normalized and less future-proof.

## Recommended fix

Before physical design, introduce a few lookup / definition tables so the minimal schema is cleaner and closer to 2NF:
- `analysis_task_types`
- `analysis_methods`
- `chart_types`
- `feature_definitions`

## Resulting rule of thumb

- core fact tables should store only instance-specific values
- repeated labels should be moved into lookup tables
- reusable feature naming should be moved into feature definition tables
- the MVP schema should remain compact, but not sloppy
