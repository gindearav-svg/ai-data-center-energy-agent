import sqlite3
from pathlib import Path

import pandas as pd

from src.energy_agent.database import initialize_database


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
REGIONAL_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)


def build_test_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "test_energy.db"
    regional_data = pd.read_csv(REGIONAL_DATA_PATH)

    initialize_database(
        database_path=database_path,
        schema_path=SCHEMA_PATH,
        regional_data=regional_data,
    )

    return database_path


def test_database_tables_are_created(tmp_path):
    database_path = build_test_database(tmp_path)

    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

    table_names = {row[0] for row in tables}

    assert "regions" in table_names
    assert "regional_metrics" in table_names


def test_database_contains_three_regions(tmp_path):
    database_path = build_test_database(tmp_path)

    with sqlite3.connect(database_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM regions"
        ).fetchone()[0]

    assert count == 3


def test_database_contains_three_metric_records(tmp_path):
    database_path = build_test_database(tmp_path)

    with sqlite3.connect(database_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM regional_metrics"
        ).fetchone()[0]

    assert count == 3


def test_database_can_join_regions_and_metrics(tmp_path):
    database_path = build_test_database(tmp_path)

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                r.region_name,
                m.annual_average_dam_price_usd_per_mwh
            FROM regions AS r
            JOIN regional_metrics AS m
                ON r.region_id = m.region_id
            WHERE r.region_name = 'Houston'
            """
        ).fetchone()

    assert row[0] == "Houston"
    assert row[1] == 34.566


def test_rerunning_loader_does_not_create_duplicates(
    tmp_path,
):
    database_path = build_test_database(tmp_path)
    regional_data = pd.read_csv(REGIONAL_DATA_PATH)

    initialize_database(
        database_path=database_path,
        schema_path=SCHEMA_PATH,
        regional_data=regional_data,
    )

    with sqlite3.connect(database_path) as connection:
        region_count = connection.execute(
            "SELECT COUNT(*) FROM regions"
        ).fetchone()[0]

        metric_count = connection.execute(
            "SELECT COUNT(*) FROM regional_metrics"
        ).fetchone()[0]

    assert region_count == 3
    assert metric_count == 3