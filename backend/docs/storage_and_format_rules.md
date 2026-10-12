# Storage and Format Rules

Date: 2026-04-26

## Purpose

Define a clear boundary between CSV files, JSON payloads, and relational database tables so the codebase stays maintainable.

---

## 1. Core rule

- **Database tables** are the source of truth for application state, workflow state, and relationships.
- **CSV files** are used for import/export and tabular data exchange.
- **JSON** is used for flexible payloads, configuration, and result structures that are not yet stable enough to become columns.

---

## 2. CSV usage rules

Use CSV when the data is:
- tabular
- flat
- easy to inspect in spreadsheet tools
- meant for ingestion or export
- useful as a reproducible data artifact

Examples:
- imported source snapshots
- cleaned intermediate tables
- exported feature matrices
- exported embedding coordinates

CSV should **not** be treated as the authoritative source for workflow state.

---

## 3. JSON usage rules

Use JSON when the data is:
- nested
- variable
- schema-light
- configuration-like
- result-like and not yet stable as fixed columns

Examples:
- chart encoding specification
- filter conditions
- run parameters
- event payloads
- flexible analysis outputs

JSON should remain a controlled escape hatch, not a replacement for the relational model.

---

## 4. Database usage rules

Use relational tables when the data must support:
- joins
- filtering
- aggregation
- session tracking
- interaction history
- reproducibility
- comparison across tasks or methods

Examples:
- data sources
- imported dataset versions
- raw records
- cleaned records
- feature sets and feature values
- tasks and runs
- chart configs
- user sessions
- interaction events
- interpretation claims

---

## 5. Practical boundary rule

If a field is often queried, grouped, filtered, or joined, it should eventually become a relational column or a lookup table value.

If a field is only a payload blob or a temporary parameter, JSON is acceptable.

If a dataset is only meant for transfer or archival, CSV is acceptable.

---

## 6. Maintenance rule

Do not keep duplicate authoritative copies of the same business fact across CSV, JSON, and database tables.

Choose one authoritative place:
- database for application truth
- CSV for file-based transfer
- JSON for flexible payloads

---

## 7. Project-specific recommendation

For Astro-Insight:
- keep platform state in the database
- keep source snapshots and exports in CSV
- keep chart and analysis payloads in JSON until they stabilize

This keeps the project easier to reason about while preserving flexibility.
