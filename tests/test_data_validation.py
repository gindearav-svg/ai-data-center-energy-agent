import pandas as pd
import pytest

from src.energy_agent.data_validation import (
    build_data_quality_summary,
    validate_regional_metrics,
)


def create_valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": [
                "North Texas",
                "Houston",
                "West Texas",
            ],
            "ercot_settlement_point": [
                "LZ_NORTH",
                "LZ_HOUSTON",
                "LZ_WEST",
            ],
            "price_year": [2025, 2025, 2025],
            "annual_average_dam_price_usd_per_mwh": [
                33.401,
                34.566,
                42.716,
            ],
            "price_observations": [8760, 8760, 8760],
            "emissions_year": [2023, 2023, 2023],
            "grid_emissions_kg_co2e_per_mwh": [
                334.129,
                334.129,
                334.129,
            ],
            "price_standard_deviation_usd_per_mwh": [
                28.900,
                25.932,
                34.466,
            ],
            "p95_price_usd_per_mwh": [
                73.354,
                70.520,
                91.421,
            ],
            "p99_price_usd_per_mwh": [
                120.320,
                111.830,
                142.312,
            ],
            "negative_price_hours": [1, 2, 220],
            "high_price_hours_above_100": [177, 134, 306],
            "extreme_price_hours_above_500": [6, 4, 6],
        }
    )


def test_valid_regional_data_passes():
    validate_regional_metrics(create_valid_data())


def test_missing_column_fails():
    data = create_valid_data().drop(
        columns=["grid_emissions_kg_co2e_per_mwh"]
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_regional_metrics(data)


def test_duplicate_region_fails():
    data = create_valid_data()
    data.loc[1, "region"] = "North Texas"

    with pytest.raises(ValueError, match="Region names must be unique"):
        validate_regional_metrics(data)


def test_incorrect_observation_count_fails():
    data = create_valid_data()
    data.loc[0, "price_observations"] = 8759

    with pytest.raises(ValueError, match="8,760"):
        validate_regional_metrics(data)


def test_invalid_percentile_order_fails():
    data = create_valid_data()
    data.loc[0, "p99_price_usd_per_mwh"] = 50
    data.loc[0, "p95_price_usd_per_mwh"] = 60

    with pytest.raises(ValueError, match="99th-percentile"):
        validate_regional_metrics(data)


def test_impossible_event_count_fails():
    data = create_valid_data()
    data.loc[0, "negative_price_hours"] = 9000

    with pytest.raises(ValueError, match="cannot exceed"):
        validate_regional_metrics(data)


def test_quality_summary_contains_expected_values():
    summary = build_data_quality_summary(create_valid_data())

    assert summary["status"] == "passed"
    assert summary["regional_rows"] == 3
    assert summary["total_price_observations"] == 26_280
    assert summary["missing_required_values"] == 0
    assert summary["price_years"] == [2025]
    assert summary["emissions_years"] == [2023]