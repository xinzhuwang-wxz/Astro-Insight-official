"""MVP relational schema for Astro-Insight.

This module contains the first-pass normalized schema used to build the
new astronomy analysis workbench database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA_STATEMENTS: list[str] = [
    """
    CREATE TABLE IF NOT EXISTS data_sources (
        source_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT NOT NULL,
        source_type TEXT NOT NULL,
        access_method TEXT,
        base_url TEXT,
        description TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS source_datasets (
        dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        dataset_name TEXT NOT NULL,
        dataset_version TEXT,
        snapshot_time TEXT,
        row_count INTEGER,
        column_count INTEGER,
        query_signature TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (source_id) REFERENCES data_sources (source_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dataset_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        source_row_key TEXT,
        object_name TEXT,
        object_family TEXT,
        raw_payload TEXT NOT NULL,
        ingested_at TEXT NOT NULL,
        FOREIGN KEY (dataset_id) REFERENCES source_datasets (dataset_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cleaned_records (
        cleaned_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER NOT NULL,
        clean_version TEXT,
        clean_payload TEXT NOT NULL,
        cleaning_flags TEXT,
        cleaned_at TEXT NOT NULL,
        FOREIGN KEY (record_id) REFERENCES dataset_records (record_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS feature_sets (
        feature_set_id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature_set_name TEXT NOT NULL,
        feature_version TEXT,
        scaling_method TEXT,
        description TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS feature_definitions (
        feature_definition_id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature_set_id INTEGER NOT NULL,
        feature_name TEXT NOT NULL,
        source_column_name TEXT,
        transformation_type TEXT,
        transformation_parameters TEXT,
        feature_order INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (feature_set_id) REFERENCES feature_sets (feature_set_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS feature_values (
        feature_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cleaned_record_id INTEGER NOT NULL,
        feature_definition_id INTEGER NOT NULL,
        feature_value_num REAL,
        feature_value_text TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (cleaned_record_id) REFERENCES cleaned_records (cleaned_record_id),
        FOREIGN KEY (feature_definition_id) REFERENCES feature_definitions (feature_definition_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analysis_task_types (
        task_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type_name TEXT NOT NULL,
        description TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analysis_tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type_id INTEGER NOT NULL,
        source_scope TEXT,
        filters TEXT,
        target_variables TEXT,
        task_name TEXT,
        task_status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (task_type_id) REFERENCES analysis_task_types (task_type_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analysis_methods (
        method_id INTEGER PRIMARY KEY AUTOINCREMENT,
        method_name TEXT NOT NULL,
        method_family TEXT,
        description TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analysis_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        method_id INTEGER NOT NULL,
        parameters TEXT,
        input_snapshot_hash TEXT,
        runtime_ms INTEGER,
        run_status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES analysis_tasks (task_id),
        FOREIGN KEY (method_id) REFERENCES analysis_methods (method_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analysis_results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        result_type TEXT NOT NULL,
        result_payload TEXT NOT NULL,
        summary_text TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (run_id) REFERENCES analysis_runs (run_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chart_types (
        chart_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        chart_type_name TEXT NOT NULL,
        description TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chart_configs (
        chart_config_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        chart_type_id INTEGER NOT NULL,
        encoding_spec TEXT,
        color_theme TEXT,
        axis_mapping TEXT,
        layout_spec TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES analysis_tasks (task_id),
        FOREIGN KEY (chart_type_id) REFERENCES chart_types (chart_type_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        current_page TEXT,
        active_dataset_id INTEGER,
        active_task_id INTEGER,
        metadata TEXT,
        FOREIGN KEY (active_dataset_id) REFERENCES source_datasets (dataset_id),
        FOREIGN KEY (active_task_id) REFERENCES analysis_tasks (task_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS interaction_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        task_id INTEGER,
        event_type TEXT NOT NULL,
        target_view TEXT,
        event_payload TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES user_sessions (session_id),
        FOREIGN KEY (task_id) REFERENCES analysis_tasks (task_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS interpretation_claims (
        claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        claim_text TEXT NOT NULL,
        confidence_level REAL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES analysis_tasks (task_id)
    )
    """,
]

INDEX_STATEMENTS: list[str] = [
    "CREATE INDEX IF NOT EXISTS idx_source_datasets_source_id ON source_datasets(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_dataset_records_dataset_id ON dataset_records(dataset_id)",
    "CREATE INDEX IF NOT EXISTS idx_cleaned_records_record_id ON cleaned_records(record_id)",
    "CREATE INDEX IF NOT EXISTS idx_feature_definitions_feature_set_id ON feature_definitions(feature_set_id)",
    "CREATE INDEX IF NOT EXISTS idx_feature_values_cleaned_record_id ON feature_values(cleaned_record_id)",
    "CREATE INDEX IF NOT EXISTS idx_feature_values_feature_definition_id ON feature_values(feature_definition_id)",
    "CREATE INDEX IF NOT EXISTS idx_analysis_tasks_task_type_id ON analysis_tasks(task_type_id)",
    "CREATE INDEX IF NOT EXISTS idx_analysis_runs_task_id ON analysis_runs(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_analysis_runs_method_id ON analysis_runs(method_id)",
    "CREATE INDEX IF NOT EXISTS idx_analysis_results_run_id ON analysis_results(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_chart_configs_task_id ON chart_configs(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_chart_configs_chart_type_id ON chart_configs(chart_type_id)",
    "CREATE INDEX IF NOT EXISTS idx_interaction_events_session_id ON interaction_events(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_interaction_events_task_id ON interaction_events(task_id)",
    "CREATE INDEX IF NOT EXISTS idx_interaction_events_event_type ON interaction_events(event_type)",
    "CREATE INDEX IF NOT EXISTS idx_interpretation_claims_task_id ON interpretation_claims(task_id)",
]


def initialize_mvp_schema(db_path: str | Path) -> None:
    """Create MVP tables and indexes in a SQLite database."""

    db_path = Path(db_path)
    if db_path.parent:
        db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        for statement in INDEX_STATEMENTS:
            cursor.execute(statement)
        conn.commit()
