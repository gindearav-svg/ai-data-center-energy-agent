import json
from pathlib import Path

import pandas as pd
import pytest

from src.energy_agent.database import initialize_database
from src.energy_agent.tools import (
    compare_energy_options,
    estimate_power_requirement,
    get_available_regions,
    get_electricity_price,
    get_region_energy_profile,
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
    database_path = tmp_path / "tool_test.db"
    regional_data = pd.read_csv(REGIONAL_DATA_PATH)

    initialize_database(
        database_path=database_path,
        schema_path=SCHEMA_PATH,
        regional_data=regional_data,
    )

    return database_path


def test_get_available_regions(tmp_path):
    database_path = build_test_database(tmp_path)

    result = get_available_regions(database_path)

    assert result["count"] == 3
    assert result["regions"] == [
        "Houston",
        "North Texas",
        "West Texas",
    ]


def test_get_electricity_price(tmp_path):
    database_path = build_test_database(tmp_path)

    result = get_electricity_price(
        region="Houston",
        database_path=database_path,
    )

    assert result["region"] == "Houston"
    assert result["price_year"] == 2025
    assert result[
        "average_price_usd_per_mwh"
    ] == pytest.approx(34.566)
    assert result["price_observations"] == 8760


def test_get_region_energy_profile(tmp_path):
    database_path = build_test_database(tmp_path)

    result = get_region_energy_profile(
        region="North Texas",
        database_path=database_path,
    )

    assert result["region"] == "North Texas"
    assert result["ercot_settlement_point"] == "LZ_NORTH"
    assert result[
        "grid_emissions_kg_co2e_per_mwh"
    ] == pytest.approx(334.129)


def test_estimate_power_requirement():
    result = estimate_power_requirement(
        it_load_mw=200,
        pue=1.25,
        utilization=0.95,
    )

    assert result["facility_load_mw"] == 250.0
    assert result["annual_energy_mwh"] == 2_080_500.0


def test_compare_energy_options(tmp_path):
    database_path = build_test_database(tmp_path)

    result = compare_energy_options(
        it_load_mw=200,
        pue=1.25,
        utilization=0.95,
        scenario="balanced",
        database_path=database_path,
    )

    assert result["recommendation"]["region"] == "Houston"
    assert len(result["regional_results"]) == 3
    assert result["regional_results"][0]["rank"] == 1


def test_tool_results_are_json_serializable(tmp_path):
    database_path = build_test_database(tmp_path)

    result = compare_energy_options(
        it_load_mw=200,
        pue=1.25,
        utilization=0.95,
        scenario="balanced",
        database_path=database_path,
    )

    serialized_result = json.dumps(result)

    assert isinstance(serialized_result, str)


def test_unknown_scenario_raises_error(tmp_path):
    database_path = build_test_database(tmp_path)

    with pytest.raises(ValueError, match="Unknown scenario"):
        compare_energy_options(
            it_load_mw=200,
            pue=1.25,
            utilization=0.95,
            scenario="unknown",
            database_path=database_path,
        )


def test_unknown_region_raises_error(tmp_path):
    database_path = build_test_database(tmp_path)

    with pytest.raises(ValueError):
        get_electricity_price(
            region="California",
            database_path=database_path,
        )