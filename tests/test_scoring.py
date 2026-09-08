import pandas as pd
import pytest

from src.energy_agent.scoring import (
    normalize_lower_is_better,
    score_regions,
    validate_weights,
)


def test_lower_value_receives_higher_score():
    values = pd.Series([10.0, 20.0, 30.0])

    scores = normalize_lower_is_better(values)

    assert scores.iloc[0] == pytest.approx(100.0)
    assert scores.iloc[1] == pytest.approx(50.0)
    assert scores.iloc[2] == pytest.approx(0.0)


def test_identical_values_receive_neutral_score():
    values = pd.Series([25.0, 25.0, 25.0])

    scores = normalize_lower_is_better(values)

    assert (scores == 50.0).all()


def test_weights_must_total_one():
    invalid_weights = {
        "cost": 0.70,
        "carbon": 0.20,
        "price_risk": 0.20,
    }

    with pytest.raises(ValueError):
        validate_weights(invalid_weights)


def test_score_regions_ranks_best_region_first():
    example_data = pd.DataFrame(
        {
            "region": ["Region A", "Region B", "Region C"],
            "estimated_annual_wholesale_cost_usd": [
                50_000_000,
                60_000_000,
                70_000_000,
            ],
            "estimated_annual_emissions_metric_tons_co2e": [
                400_000,
                500_000,
                600_000,
            ],
            "maximum_dam_price_usd_per_mwh": [
                500,
                700,
                900,
            ],
        }
    )

    results = score_regions(example_data)

    assert results.iloc[0]["region"] == "Region A"
    assert results.iloc[0]["rank"] == 1
    assert results.iloc[0]["overall_score"] == pytest.approx(100.0)


def test_missing_column_raises_error():
    incomplete_data = pd.DataFrame(
        {
            "region": ["Region A"],
            "estimated_annual_wholesale_cost_usd": [50_000_000],
        }
    )

    with pytest.raises(ValueError):
        score_regions(incomplete_data)