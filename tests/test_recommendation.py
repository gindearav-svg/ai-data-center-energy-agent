import pandas as pd
import pytest

from src.energy_agent.recommendation import (
    build_regional_recommendation,
)


BALANCED_WEIGHTS = {
    "cost": 0.50,
    "carbon": 0.20,
    "price_risk": 0.30,
}


def create_example_regional_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["Region A", "Region B"],
            "annual_average_dam_price_usd_per_mwh": [
                30.0,
                40.0,
            ],
            "maximum_dam_price_usd_per_mwh": [
                500.0,
                700.0,
            ],
            "grid_emissions_kg_co2e_per_mwh": [
                300.0,
                400.0,
            ],
            "price_standard_deviation_usd_per_mwh": [
                10.0,
                20.0,
            ],
            "p95_price_usd_per_mwh": [
                50.0,
                70.0,
            ],
            "high_price_hours_above_100": [
                25,
                50,
            ],
            "extreme_price_hours_above_500": [
                1,
                5,
            ],
        }
    )


def test_recommendation_uses_user_requirements():
    data = create_example_regional_data()

    results = build_regional_recommendation(
        regional_metrics=data,
        it_load_mw=100,
        pue=1.20,
        utilization=0.90,
        weights=BALANCED_WEIGHTS,
    )

    expected_facility_load = 120.0
    expected_annual_energy = 946_080.0

    assert (results["facility_load_mw"] == expected_facility_load).all()
    assert (
        results["annual_energy_mwh"] == expected_annual_energy
    ).all()


def test_recommendation_calculates_cost():
    data = create_example_regional_data()

    results = build_regional_recommendation(
        regional_metrics=data,
        it_load_mw=100,
        pue=1.20,
        utilization=0.90,
        weights=BALANCED_WEIGHTS,
    )

    region_a = results[results["region"] == "Region A"].iloc[0]

    expected_cost = 946_080.0 * 30.0

    assert region_a[
        "estimated_annual_wholesale_cost_usd"
    ] == pytest.approx(expected_cost)


def test_recommendation_calculates_emissions():
    data = create_example_regional_data()

    results = build_regional_recommendation(
        regional_metrics=data,
        it_load_mw=100,
        pue=1.20,
        utilization=0.90,
        weights=BALANCED_WEIGHTS,
    )

    region_a = results[results["region"] == "Region A"].iloc[0]

    expected_emissions = 946_080.0 * 300.0 / 1000

    assert region_a[
        "estimated_annual_emissions_metric_tons_co2e"
    ] == pytest.approx(expected_emissions)


def test_recommendation_ranks_best_region_first():
    data = create_example_regional_data()

    results = build_regional_recommendation(
        regional_metrics=data,
        it_load_mw=100,
        pue=1.20,
        utilization=0.90,
        weights=BALANCED_WEIGHTS,
    )

    assert results.iloc[0]["region"] == "Region A"
    assert results.iloc[0]["rank"] == 1


def test_missing_regional_column_raises_error():
    incomplete_data = pd.DataFrame(
        {
            "region": ["Region A"],
            "annual_average_dam_price_usd_per_mwh": [30.0],
        }
    )

    with pytest.raises(ValueError):
        build_regional_recommendation(
            regional_metrics=incomplete_data,
            it_load_mw=100,
            pue=1.20,
            utilization=0.90,
            weights=BALANCED_WEIGHTS,
        )