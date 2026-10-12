#!/usr/bin/env python3
"""Import small CSV samples for PSCompPars and Kaggle SDSS19 into MVP schema."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database.api import DatabaseAPI
from src.database.importers import CSVImporter


def main() -> None:
    db_api = DatabaseAPI(str(ROOT / "data" / "astro_insight.db"))
    importer = CSVImporter(db_api)

    pscomp_path = ROOT / "dataset" / "raw" / "pscomppars_sample.csv"
    kaggle_path = ROOT / "dataset" / "raw" / "sdss19_imbalanced.csv"

    ps_feature_fields = [
        "disc_year",
        "pl_orbper",
        "pl_rade",
        "pl_bmasse",
        "st_teff",
        "st_rad",
        "sy_dist",
    ]

    kaggle_feature_fields = [
        "alpha",
        "delta",
        "u",
        "g",
        "r",
        "i",
        "z",
        "redshift",
    ]

    ps_result = importer.import_dataset(
        csv_path=pscomp_path,
        source_name="NASA Exoplanet Archive PSCompPars",
        source_type="archive",
        dataset_name="PSCompPars Sample",
        dataset_version="sample-v1",
        access_method="csv",
        base_url="https://exoplanetarchive.ipac.caltech.edu/",
        description="Small local sample derived from PSCompPars-like fields",
        object_family_field="discoverymethod",
        object_name_field="pl_name",
        feature_fields=ps_feature_fields,
    )
    print("PSComp样本导入完成！")

    
    kaggle_result = importer.import_dataset(
        csv_path=kaggle_path,
        source_name="Kaggle SDSS19 Stellar Classification",
        source_type="kaggle",
        dataset_name="SDSS19 Stellar Classification Sample",
        dataset_version="sample-v1",
        access_method="csv",
        base_url="https://www.kaggle.com/datasets/diegovillagranc/sdss19-stellar-classification-star-galaxy-qso",
        description="Small imported sample from local sdss19_imbalanced.csv",
        object_family_field="class",
        object_name_field="obj_ID",
        feature_fields=kaggle_feature_fields,
    )
    print("Kaggle样本导入完成！")
    
    
    print("PSCompPars sample import:", ps_result)
    print("Kaggle sample import:", kaggle_result)
    print("MVP table statistics:", db_api.get_mvp_statistics())


if __name__ == "__main__":
    main()
