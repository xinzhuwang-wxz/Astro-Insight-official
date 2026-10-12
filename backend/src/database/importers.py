"""CSV import helpers for MVP datasets."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

from .api import DatabaseAPI


class CSVImporter:
    def __init__(self, db_api: DatabaseAPI):
        self.db_api = db_api

    def import_dataset(
        self,
        csv_path: str | Path,
        source_name: str,
        source_type: str,
        dataset_name: str,
        dataset_version: str | None = None,
        access_method: str | None = "csv",
        base_url: str | None = None,
        description: str | None = None,
        object_family_field: str | None = None,
        object_name_field: str | None = None,
        feature_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        csv_path = Path(csv_path)
        rows: list[dict[str, Any]] = []
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        source_id = self.db_api.create_data_source(
            {
                "source_name": source_name,
                "source_type": source_type,
                "access_method": access_method,
                "base_url": base_url,
                "description": description,
            }
        )
        dataset_id = self.db_api.create_source_dataset(
            {
                "source_id": source_id,
                "dataset_name": dataset_name,
                "dataset_version": dataset_version,
                "row_count": len(rows),
                "column_count": len(rows[0]) if rows else 0,
                "query_signature": f"csv:{csv_path.name}",
            }
        )

        record_ids: list[int] = []
        cleaned_ids: list[int] = []
        feature_set_id = self.db_api.create_feature_set(
            {
                "feature_set_name": f"{dataset_name} default features",
                "feature_version": dataset_version or "v1",
                "scaling_method": "none",
                "description": f"Auto-generated feature set for {dataset_name}",
            }
        )

        field_names = feature_fields or (list(rows[0].keys()) if rows else [])
        for order, field in enumerate(field_names):
            self.db_api.create_feature_definition(
                {
                    "feature_set_id": feature_set_id,
                    "feature_name": field,
                    "source_column_name": field,
                    "transformation_type": "identity",
                    "transformation_parameters": {},
                    "feature_order": order,
                }
            )

        for row in rows:
            object_name = row.get(object_name_field) if object_name_field else row.get("name") or row.get("object_name") or row.get("id")
            object_family = row.get(object_family_field) if object_family_field else row.get("class") or row.get("object_family") or row.get("object_type")
            record_id = self.db_api.create_dataset_record(
                {
                    "dataset_id": dataset_id,
                    "source_row_key": row.get("id") or row.get("objid") or object_name,
                    "object_name": object_name,
                    "object_family": object_family,
                    "raw_payload": row,
                }
            )
            record_ids.append(record_id)

            cleaned_id = self.db_api.create_cleaned_record(
                {
                    "record_id": record_id,
                    "clean_version": dataset_version or "v1",
                    "clean_payload": row,
                    "cleaning_flags": {"imported_from": str(csv_path.name)},
                }
            )
            cleaned_ids.append(cleaned_id)

            for field in field_names:
                value = row.get(field)
                if value is None or value == "":
                    continue
                num_value = None
                try:
                    num_value = float(value)
                except (TypeError, ValueError):
                    num_value = None
                self.db_api.create_feature_value(
                    {
                        "cleaned_record_id": cleaned_id,
                        "feature_definition_id": self._feature_definition_id(feature_set_id, field),
                        "feature_value_num": num_value,
                        "feature_value_text": value if num_value is None else None,
                    }
                )

        return {
            "source_id": source_id,
            "dataset_id": dataset_id,
            "feature_set_id": feature_set_id,
            "record_count": len(record_ids),
            "cleaned_count": len(cleaned_ids),
        }

    def _feature_definition_id(self, feature_set_id: int, feature_name: str) -> int:
        # Lightweight lookup for MVP: query by exact match.
        import sqlite3

        with sqlite3.connect(self.db_api.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT feature_definition_id
                FROM feature_definitions
                WHERE feature_set_id = ? AND feature_name = ?
                ORDER BY feature_order ASC, feature_definition_id ASC
                LIMIT 1
                """,
                (feature_set_id, feature_name),
            )
            result = cursor.fetchone()

        if result:
            return result[0]
        
        # 不存在则创建
        cursor.execute(
            "INSERT INTO feature_definitions (feature_set_id, field_name) VALUES (?, ?)",
            (feature_set_id, feature_name)
        )
        conn.commit()
        new_id = cursor.lastrowid
        # 执行完立即关闭连接，解决锁死
        cursor.close()
        return new_id