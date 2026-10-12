# Project Planning Record

Date: 2026-04-26

## What was done exactly

### 1. Project positioning was clarified
I rewrote the project as an **astronomy data visualization platform** focused on exploratory analysis, not just data display.

Core framing now emphasizes:
- understanding high-dimensional astronomical data structure
- comparing how different visualization strategies affect interpretation
- presenting the analysis process, not only the final result
- supporting course-aligned EDA, PCA/SVD, multi-view linkage, and result explanation

### 2. The narrative was sharpened
I defined the story as:

> Different visualization choices can lead to different cognitive conclusions about astronomical data.

This makes the project about:
- pattern discovery
- insight preservation
- computational exploration
- explanation of why views differ

### 3. The data strategy was extended
I incorporated the planned NASA Exoplanet Archive data source and organized the data strategy into layers:
- raw astronomical data
- cleaned data
- feature tables
- dimensionality reduction outputs
- analysis/task results
- chart configs
- session / interaction history

### 4. The database direction was structured
I outlined the database objects needed to support analysis workflows, including:
- raw data table
- cleaned data table
- feature table
- visualization task table
- chart configuration table
- user/session table
- optional algorithm result and chart generation log tables
- optional user interaction/event tables for behavior analysis

### 5. The page architecture was defined
I specified a working-studio style frontend with the following main pages:
- home page
- data overview page
- EDA page
- structure / dimensionality reduction page
- comparison page
- explanation / conclusion page

### 6. The visualization strategy was organized
I grouped the visuals into four categories:
- overview charts
- structure charts
- comparison charts
- explanation charts

I also emphasized:
- multi-view linking
- chart switching
- clicking/highlighting
- filtering
- parameter tuning
- explanation text alongside charts

### 7. The backend responsibilities were clarified
The backend was framed as responsible for:
- data reading and cleaning
- EDA and analysis computation
- unified API delivery to the frontend

### 8. The project roadmap was drafted
I broke the work into phases:
- definition and convergence
- data and backend setup
- frontend studio buildout
- method comparison and explanation
- polishing and presentation

### 9. The existing repository was inspected
I checked the current repository structure and confirmed the project already contains reusable pieces such as:
- `README.md`
- `server.py`
- `src/database/local_storage.py`
- `src/database/api.py`
- `src/api/router.py`
- existing documentation files in `docs/`

This showed the project is not starting from zero and can be extended from the current astro-research assistant base.

### 10. I recorded the planning content in `docs/visual_plan.md`
I wrote the main planning content into `docs/visual_plan.md`, including:
- project定位
- dataset strategy
- database model direction
- frontend page architecture
- backend API goals
- visualization principles
- phased roadmap
- risks and mitigation

### 11. I updated the idea notes
I preserved and reorganized the visual design notes from `idea.md`, including:
- theme selection
- chart preference selection
- filtering as information-density control
- grayscale plus accent color strategy
- animation and temporal storytelling
- periodic vs timeline-based time visualization
- multimodal expansion ideas
- explanation and credibility of conclusions

## Result of this planning step
The project now has a clear direction:

> Build an interactive astronomy data exploration platform that helps users understand high-dimensional astronomical data, compare visualization choices, and explain how insight is formed.

## Next recommended step
Proceed with:
1. current codebase audit
2. database schema draft
3. API specification draft

## Current codebase audit summary

I reviewed the current repository and confirmed the project already has a usable skeleton for the new platform:

### Frontend baseline
The existing UI already includes:
- theme switching
- section navigation
- analysis task input
- system status display
- data overview cards
- explanation panels
- chart rendering hooks
- tabular data display

This means the frontend is already a working-studio shell, but it still needs to be reoriented toward high-dimensional astronomy exploration.

### Backend baseline
The existing Flask backend already exposes routes for:
- health checks
- system status
- analysis execution
- object listing
- classification listing
- execution history
- statistics

This means the backend is functional, but its API design is still centered on the earlier astronomy assistant workflow rather than the new visualization-workbench workflow.

### Database baseline
The current SQLite layer already stores:
- celestial objects
- classification results
- execution history
- basic statistics
- sample seed records

This is a good starting point, but it does not yet capture the full analysis lifecycle needed for the new platform, such as:
- raw data import records
- cleaned data versions
- feature tables
- dimensionality reduction results
- visualization tasks
- chart configs
- user sessions
- interaction events

### Main gap identified
The main gap is not infrastructure. The main gap is the data model and workflow model.

The project must be upgraded from:
- object-centric analysis

to:
- task-centric exploratory visualization analysis

## Decision for the next phase
The next work should focus on:
1. database ER design
2. API contract design
3. page interaction blueprint
4. MVP scope selection

## Database schema draft recorded
A new database schema draft was created in `docs/database_schema_draft.md`.

Key design layers:
- data assets
- analysis workflow
- visualization layer
- user and behavior layer
- supporting entities

The schema is explicitly designed to support:
- EDA
- PCA / t-SNE / UMAP
- comparison of methods
- chart recommendation
- multi-view linking
- session replay
- behavior analysis

## Database design process agreed
The database work will now follow this sequence:

1. **Conceptual design**
   - define entities and relationships
   - decide what exists in the system
   - decide which objects are core, derived, or behavioral

2. **Logical design**
   - split entities into normalized tables
   - ensure the design satisfies 3NF
   - separate lookup data, raw records, analysis outputs, and interaction logs

3. **Physical design**
   - write concrete SQL tables, keys, constraints, and indexes
   - implement the chosen schema in the actual database engine

This order is now the official database planning method for the project.

## Data source strategy decision
The database concept and logical design will now consider multiple data sources from the beginning, while physical implementation will be phased.

### Source categories
- primary structured astronomy source: `PSCompPars`
- auxiliary reference source: SIMBAD
- comparative / extension source: Kaggle SDSS Galaxy Classification DR18
- evidence / explanation source: paper or literature API

### Strategy
- **Conceptual design**: include all major source categories from the start
- **Logical design**: use a unified normalized backbone for all sources
- **Physical design**: implement the primary source first, then add SIMBAD, Kaggle, and literature support incrementally

This keeps the schema extensible without losing normalization.

## Conceptual design recorded
A new conceptual design draft was created in `docs/conceptual_design.md`.

It defines the main conceptual groups as:
- data source concepts
- astronomy record concepts
- transformation concepts
- analysis concepts
- visualization concepts
- user and interaction concepts
- evidence and explanation concepts

It also records the key cross-source flow:
- `PSCompPars` and Kaggle SDSS19 Stellar Classification Star/Galaxy/QSO as co-primary analytical sources
- SIMBAD as enrichment
- literature / paper APIs as evidence sources

## Logical design recorded
A new logical design draft was created in `docs/logical_design.md`.

It maps the conceptual model into normalized relational entities including:
- source metadata tables
- source dataset snapshots
- dataset column metadata
- canonical astronomy object table
- object identifier table
- raw record table
- record attribute table
- cleaning pipeline and step tables
- cleaned record and attribute tables
- feature set and feature value tables
- analysis task / method / run / result tables
- reduction result and coordinate tables
- chart type / config / instance / recommendation tables
- session / interaction / query history tables
- evidence / claim / support link tables

The logical design explicitly states that the model should satisfy 3NF and that JSON should only be used for variable payloads, parameter bags, and render state where appropriate.

## Minimal logical design recorded
A new minimal logical design draft was created in `docs/logical_design_minimal.md`.

This compressed version keeps the MVP-focused core tables and adds light normalization where it helps clarity:
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

This version is intended for implementation discussion and is the clearest bridge between the conceptual design and physical design.

## Minimal logical diagram recorded
A new diagram-style explanation was created in `docs/logical_design_diagram.md`.

It provides:
- a one-line relationship map
- a text ER-style diagram
- a plain-language explanation of what each table does in the project story

## Normalization notes recorded
A new note file was created in `docs/normalization_notes.md`.

It records:
- why the earlier minimal schema was only close to 2NF
- which fields felt implementation-friendly but less normalized
- the recommendation to split lookup / definition tables before physical design

## Physical design draft recorded
A new physical design draft was created in `docs/physical_design.md`.

It defines the MVP-level physical tables and columns for:
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

It also defines the recommended migration path from the existing compatibility schema to the new normalized workflow schema.

## MVP table priority recorded
A new priority plan was created in `docs/mvp_table_priority.md`.

It splits the physical tables into:
- Tier 1: must implement first
- Tier 2: can be deferred

It also groups the MVP into three lanes:
- data lane
- analysis lane
- UX / explanation lane

## MVP schema blueprint recorded
A new implementation blueprint was created in `docs/mvp_schema_blueprint.md`.

It contains:
- the build order for the MVP tables
- field drafts for each table
- foreign key suggestions
- index suggestions
- which fields can remain JSON/TEXT in the MVP
- the final recommended order for creating the tables

## Storage and format rules recorded
A new rule file was created in `docs/storage_and_format_rules.md`.

It formalizes the boundary between:
- CSV as import/export and tabular exchange
- JSON as flexible payload/config/result storage
- database tables as the source of truth for workflow state and relationships

This rule is now the default project convention for future implementation work.

## MVP physical implementation started
A new schema module was added at `src/database/mvp_schema.py`.

It creates the MVP tables and indexes for:
- data sources and datasets
- raw and cleaned records
- feature sets and definitions
- analysis task/method/run/result tables
- chart types and configs
- user sessions and interaction events
- interpretation claims

The existing database API now initializes this MVP schema at startup.
