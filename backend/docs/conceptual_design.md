# Conceptual Design Draft

Date: 2026-04-26

## 1. Design objective

The platform is not a simple astronomy catalog. It is an exploratory visualization workbench for understanding high-dimensional astronomical data and comparing how different visualization choices shape interpretation.

The conceptual model therefore needs to support:
- multiple astronomy data sources
- preprocessing and transformation history
- analytical tasks and computation runs
- chart recommendation and visualization configuration
- user sessions and interaction traces
- interpretation and evidence generation

---

## 2. Core concept groups

### A. Data source concepts
These represent where data come from and how they are ingested.

#### 1) `DataSource`
A logical source of astronomy or related evidence data.
Examples:
- NASA Exoplanet Archive `PSCompPars`
- SIMBAD
- Kaggle SDSS Galaxy Classification DR18
- literature / paper API results

Attributes at the conceptual level:
- source name
- source type
- access method
- version / snapshot
- update policy
- reliability notes

#### 2) `SourceDataset`
A dataset instance imported from a source.
Examples:
- a specific `PSCompPars` snapshot
- a specific Kaggle dataset import
- a SIMBAD query result set

Attributes at the conceptual level:
- dataset title
- source link
- import time
- snapshot version
- coverage notes

---

### B. Astronomy record concepts
These represent the actual subject entities being analyzed.

#### 1) `AstronomyObject`
A canonical astronomical entity under study.
This could represent:
- a planet system
- a host star
- a galaxy
- another astronomical object depending on source context

The concept is intentionally abstract so the platform can support multiple sources.

Attributes at the conceptual level:
- canonical object identifier
- object name
- object category
- source-specific identifiers
- summary attributes

#### 2) `ObjectObservation`
A record of observed or cataloged properties for an astronomy object.
Examples:
- orbital parameters
- stellar properties
- photometric values
- spectral properties
- spatial coordinates

Attributes at the conceptual level:
- observed attribute name
- observed value
- unit
- provenance
- timestamp or snapshot context

This is conceptually separate from the object itself so that different sources can contribute different observations.

---

### C. Transformation concepts
These represent how raw data becomes analysis-ready data.

#### 1) `CleaningPipeline`
A reusable preprocessing procedure.
Examples:
- missing value handling
- outlier treatment
- unit normalization
- encoding conversion
- feature scaling

Attributes at the conceptual level:
- pipeline name
- version
- steps
- parameters
- status

#### 2) `CleanedRecord`
A cleaned version of an imported record.
Attributes at the conceptual level:
- raw record reference
- pipeline reference
- cleaned attribute values
- flags for missing/outlier/normalized fields

#### 3) `FeatureSet`
A derived set of analysis features built from cleaned records.
Examples:
- standardized numeric features
- log-transformed features
- selected feature subset

Attributes at the conceptual level:
- feature set name
- feature definition
- scaling method
- version

---

### D. Analysis concepts
These represent the user’s analytic intent and the computational results.

#### 1) `AnalysisTask`
A task requested by a user or triggered by the system.
Examples:
- data overview
- EDA
- structure discovery
- method comparison
- explanation generation

Attributes at the conceptual level:
- task type
- intent
- filters
- target variables
- dataset scope
- status

#### 2) `AnalysisRun`
One execution instance of an analysis task.
Examples:
- one PCA run
- one t-SNE run with a specific perplexity
- one UMAP run with a specific neighbor count
- one correlation analysis run

Attributes at the conceptual level:
- method name
- parameters
- input snapshot
- runtime
- status

#### 3) `AnalysisResult`
The output of an analysis run.
Examples:
- embeddings
- correlation matrix
- cluster labels
- anomaly scores
- summary text

Attributes at the conceptual level:
- result type
- payload
- summary
- interpretation note

#### 4) `ReductionResult`
A specialized analysis result for PCA/t-SNE/UMAP-like methods.
Attributes at the conceptual level:
- method
- dimensions
- coordinate set
- variance / quality metadata
- parameter context

---

### E. Visualization concepts
These represent how analysis results are turned into charts and linked views.

#### 1) `ChartType`
A reusable chart category.
Examples:
- histogram
- scatter plot
- heatmap
- box plot
- parallel coordinates
- embedding plot
- comparison matrix

#### 2) `ChartConfig`
A visualization specification for a task or result.
Attributes at the conceptual level:
- chart type
- encoding choices
- axes
- color theme
- filters
- linked views
- layout

#### 3) `ChartInstance`
A rendered chart in a particular user session.
This is distinct from `ChartConfig` because the same config can appear in multiple sessions with different filters or states.

Attributes at the conceptual level:
- config reference
- session reference
- current state
- rendered time

#### 4) `ChartRecommendation`
A system-generated suggestion about what chart best fits a task.
Attributes at the conceptual level:
- task reference
- recommended chart type
- reasoning
- confidence
- alternatives

---

### F. User and interaction concepts
These represent how people explore the system.

#### 1) `UserSession`
A single exploration session.
Attributes at the conceptual level:
- session id
- start / end time
- current page
- active dataset
- active task
- active filters

#### 2) `InteractionEvent`
A single user action.
Examples:
- click
- hover
- brush
- zoom
- filter change
- parameter adjustment
- chart switch

Attributes at the conceptual level:
- event type
- target view
- payload
- timestamp

#### 3) `QueryHistory`
A record of user questions or requests.
Attributes at the conceptual level:
- query text
- query type
- context
- execution time
- success / failure

---

### G. Evidence and explanation concepts
These are important because the project is not only about charts but also about interpretation.

#### 1) `EvidenceSource`
A literature or external evidence item.
Examples:
- paper abstract
- bibliographic record
- API-provided citation context

#### 2) `InterpretationClaim`
A conclusion generated from the analysis.
Examples:
- which visualization is more suitable for a task
- why a method reveals a cluster more clearly
- why a result should be trusted

#### 3) `SupportLink`
A conceptual link between a claim and the data / analysis / chart that supports it.
This helps the result page remain explainable.

---

## 3. Key relationships

### Data flow
`DataSource` -> `SourceDataset` -> `RawRecord` -> `CleanedRecord` -> `FeatureSet` -> `AnalysisTask` -> `AnalysisRun` -> `AnalysisResult` -> `ChartConfig` -> `ChartInstance`

### Behavior flow
`UserSession` -> `InteractionEvent` -> `QueryHistory`

### Explanation flow
`EvidenceSource` -> `InterpretationClaim` -> `SupportLink` -> analysis outputs / charts

---

## 4. How multiple data sources fit together

### Primary sources
- `PSCompPars`
- Kaggle SDSS19 Stellar Classification Star/Galaxy/QSO

These should be treated as **co-primary analytical sources** rather than one main source plus a secondary dataset.

Why:
- `PSCompPars` represents exoplanetary systems and their host-star context.
- Kaggle SDSS19 Stellar Classification Star/Galaxy/QSO represents stellar / extragalactic classification across multiple object classes.
- Together they support a broader astronomy-structure comparison story: different celestial object families, different feature spaces, and different visualization behavior.

This makes the project stronger because the platform is not tied to one object family only.

### Auxiliary enrichment source
- SIMBAD
This is used to enrich object identity, host metadata, and cross-reference naming / physical context.

### Evidence source
- paper / literature API
This is used to support interpretation, comparison, and explanation.

The conceptual model keeps these sources separate at the source level, but lets them flow into the same analytic pipeline when appropriate.

---

## 5. 3NF-oriented conceptual rule

To preserve normalization, the conceptual model follows these rules:
- one concept per entity
- source metadata separated from imported records
- raw values separated from cleaned values
- cleaned values separated from features
- analysis runs separated from results
- chart configs separated from rendered instances
- user sessions separated from individual actions
- evidence separated from claims

This prevents overloading any one table with mixed responsibilities.

---

## 6. Recommended next step after conceptual design

After the conceptual layer is accepted, move to logical design:
- map each concept to a table
- define keys and relationships
- decide lookup tables vs fact tables
- decide which source-specific fields stay in raw payload versus normalized fields
