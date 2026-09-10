import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from src.energy_agent.database import initialize_database
from src.energy_agent.queries import (
    compare_all_regions,
    get_region_metrics,
    list_regions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

REGIONAL_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)


def build_test_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "query_test.db"
    regional_data = pd.read_csv(REGIONAL_DATA_PATH)

    initialize_database(
        database_path=database_path,
        schema_path=SCHEMA_PATH,
        regional_data=regional_data,
    )

    return database_path


def test_list_regions_returns_alphabetical_names(tmp_path):
    database_path = build_test_database(tmp_path)

    regions = list_regions(database_path)

    assert regions == [
        "Houston",
        "North Texas",
        "West Texas",
    ]


def test_get_houston_metrics(tmp_path):
    database_path = build_test_database(tmp_path)

    result = get_region_metrics(
        database_path,
        "Houston",
    )

    assert result["region"] == "Houston"
    assert (
        result["ercot_settlement_point"]
        == "LZ_HOUSTON"
    )
    assert (
        result["annual_average_dam_price_usd_per_mwh"]
        == pytest.approx(34.566)
    )
    assert result["price_observations"] == 8760


def test_unknown_region_raises_error(tmp_path):
    database_path = build_test_database(tmp_path)

    with pytest.raises(
        ValueError,
        match="Region is not available",
    ):
        get_region_metrics(
            database_path,
            "Unknown Region",
        )


def test_compare_all_regions_returns_three_rows(tmp_path):
    database_path = build_test_database(tmp_path)

    results = compare_all_regions(database_path)

    assert len(results) == 3
    assert results.iloc[0]["region"] == "North Texas"
    assert results.iloc[1]["region"] == "Houston"
    assert results.iloc[2]["region"] == "West Texas"


def test_parameterized_query_prevents_sql_injection(tmp_path):
    database_path = build_test_database(tmp_path)

    malicious_input = "Houston'; DROP TABLE regions; --"

    with pytest.raises(ValueError):
        get_region_metrics(
            database_path,
            malicious_input,
        )

    # The regions table must still exist afterward.
    regions = list_regions(database_path)

    assert regions == [
        "Houston",
        "North Texas",
        "West Texas",
    ]


def test_missing_database_raises_error(tmp_path):
    nonexistent_path = tmp_path / "does_not_exist.db"

    with pytest.raises(FileNotFoundError):
        list_regions(nonexistent_path)

    assert not nonexistent_path.exists()


def test_comparison_query_returns_expected_columns(tmp_path):
    database_path = build_test_database(tmp_path)

    results = compare_all_regions(database_path)

    expected_columns = {
        "region",
        "annual_average_dam_price_usd_per_mwh",
        "grid_emissions_kg_co2e_per_mwh",
        "price_standard_deviation_usd_per_mwh",
        "p95_price_usd_per_mwh",
    }

    assert expected_columns.issubset(results.columns)