from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REGIONAL_METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)

BASELINE_RESULTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "baseline_regional_results.csv"
)


@pytest.fixture
def regional_metrics() -> pd.DataFrame:
    """Load the processed regional metrics."""

    assert REGIONAL_METRICS_FILE.exists(), (
        "regional_metrics.csv does not exist. "
        "Run the ERCOT processing script."
    )

    return pd.read_csv(REGIONAL_METRICS_FILE)


@pytest.fixture
def baseline_results() -> pd.DataFrame:
    """Load the baseline regional results."""

    assert BASELINE_RESULTS_FILE.exists(), (
        "baseline_regional_results.csv does not exist. "
        "Run the baseline analysis script."
    )

    return pd.read_csv(BASELINE_RESULTS_FILE)


def test_has_expected_regions(
    regional_metrics: pd.DataFrame,
) -> None:
    expected_regions = {
        "North Texas",
        "Houston",
        "West Texas",
    }

    assert len(regional_metrics) == 3
    assert set(regional_metrics["region"]) == expected_regions


def test_required_values_are_complete(
    regional_metrics: pd.DataFrame,
) -> None:
    required_columns = [
        "region",
        "ercot_settlement_point",
        "price_year",
        "annual_average_dam_price_usd_per_mwh",
        "annual_median_dam_price_usd_per_mwh",
        "minimum_dam_price_usd_per_mwh",
        "maximum_dam_price_usd_per_mwh",
        "price_observations",
        "egrid_subregion",
        "emissions_year",
        "grid_emissions_kg_co2e_per_mwh",
        "noaa_station_id",
        "noaa_station_name",
    ]

    assert set(required_columns).issubset(
        regional_metrics.columns
    )

    assert regional_metrics[required_columns].notna().all().all()


def test_price_observation_counts(
    regional_metrics: pd.DataFrame,
) -> None:
    assert (
        regional_metrics["price_observations"] == 8760
    ).all()


def test_price_statistics_are_logically_ordered(
    regional_metrics: pd.DataFrame,
) -> None:
    minimum = regional_metrics[
        "minimum_dam_price_usd_per_mwh"
    ]

    average = regional_metrics[
        "annual_average_dam_price_usd_per_mwh"
    ]

    median = regional_metrics[
        "annual_median_dam_price_usd_per_mwh"
    ]

    maximum = regional_metrics[
        "maximum_dam_price_usd_per_mwh"
    ]

    assert (minimum <= average).all()
    assert (average <= maximum).all()
    assert (minimum <= median).all()
    assert (median <= maximum).all()


def test_expected_annual_average_prices(
    regional_metrics: pd.DataFrame,
) -> None:
    expected_prices = {
        "North Texas": 33.401,
        "Houston": 34.566,
        "West Texas": 42.716,
    }

    for region, expected_price in expected_prices.items():
        actual_price = regional_metrics.loc[
            regional_metrics["region"] == region,
            "annual_average_dam_price_usd_per_mwh",
        ].iloc[0]

        assert actual_price == pytest.approx(
            expected_price,
            abs=0.001,
        )


def test_source_metadata(
    regional_metrics: pd.DataFrame,
) -> None:
    assert set(regional_metrics["price_year"]) == {2025}
    assert set(regional_metrics["emissions_year"]) == {2023}
    assert set(regional_metrics["egrid_subregion"]) == {"ERCT"}

    assert all(
        value == pytest.approx(334.129)
        for value in regional_metrics[
            "grid_emissions_kg_co2e_per_mwh"
        ]
    )


def test_identifiers_are_unique(
    regional_metrics: pd.DataFrame,
) -> None:
    assert regional_metrics[
        "ercot_settlement_point"
    ].is_unique

    assert regional_metrics[
        "noaa_station_id"
    ].is_unique


def test_baseline_costs_recalculate_correctly(
    baseline_results: pd.DataFrame,
) -> None:
    for _, row in baseline_results.iterrows():
        expected_cost = (
            row["annual_energy_mwh"]
            * row["annual_average_dam_price_usd_per_mwh"]
        )

        assert row[
            "estimated_annual_wholesale_cost_usd"
        ] == pytest.approx(expected_cost)


def test_baseline_emissions_recalculate_correctly(
    baseline_results: pd.DataFrame,
) -> None:
    for _, row in baseline_results.iterrows():
        expected_emissions = (
            row["annual_energy_mwh"]
            * row["grid_emissions_kg_co2e_per_mwh"]
            / 1000
        )

        assert row[
            "estimated_annual_emissions_metric_tons_co2e"
        ] == pytest.approx(expected_emissions)