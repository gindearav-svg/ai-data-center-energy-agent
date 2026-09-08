from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

REGIONAL_METRICS_PATH = PROCESSED_DATA_DIR / "regional_metrics.csv"
BASELINE_RESULTS_PATH = (
    PROCESSED_DATA_DIR / "baseline_regional_results.csv"
)


def test_processed_files_exist():
    assert REGIONAL_METRICS_PATH.exists()
    assert BASELINE_RESULTS_PATH.exists()


def test_regional_metrics_contains_expected_regions():
    data = pd.read_csv(REGIONAL_METRICS_PATH)

    expected_regions = {
        "North Texas",
        "Houston",
        "West Texas",
    }

    assert set(data["region"]) == expected_regions
    assert len(data) == 3


def test_regional_metrics_have_valid_values():
    data = pd.read_csv(REGIONAL_METRICS_PATH)

    assert (data["price_observations"] == 8760).all()
    assert data["annual_average_dam_price_usd_per_mwh"].notna().all()
    assert (data["grid_emissions_kg_co2e_per_mwh"] > 0).all()


def test_baseline_energy_calculation():
    data = pd.read_csv(BASELINE_RESULTS_PATH)

    assert (data["facility_load_mw"] == 250.0).all()
    assert (data["annual_energy_mwh"] == 2_080_500.0).all()


def test_baseline_cost_calculation():
    data = pd.read_csv(BASELINE_RESULTS_PATH)

    for _, row in data.iterrows():
        expected_cost = (
            row["annual_energy_mwh"]
            * row["annual_average_dam_price_usd_per_mwh"]
        )

        assert row["estimated_annual_wholesale_cost_usd"] == pytest.approx(
            expected_cost
        )


def test_baseline_emissions_calculation():
    data = pd.read_csv(BASELINE_RESULTS_PATH)

    for _, row in data.iterrows():
        expected_emissions = (
            row["annual_energy_mwh"]
            * row["grid_emissions_kg_co2e_per_mwh"]
            / 1000
        )

        assert (
            row["estimated_annual_emissions_metric_tons_co2e"]
            == pytest.approx(expected_emissions)
        )