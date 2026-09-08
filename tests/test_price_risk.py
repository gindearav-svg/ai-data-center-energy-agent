import pandas as pd
import pytest

from src.energy_agent.price_risk import (
    calculate_price_risk_metrics,
)


def create_example_prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Settlement Point": [
                "LZ_TEST",
                "LZ_TEST",
                "LZ_TEST",
                "LZ_TEST",
                "LZ_TEST",
                "LZ_OTHER",
            ],
            "Settlement Point Price": [
                -10.0,
                20.0,
                100.0,
                150.0,
                600.0,
                50.0,
            ],
        }
    )


def test_price_risk_metrics_count_observations():
    results = calculate_price_risk_metrics(
        create_example_prices(),
        ["LZ_TEST"],
    )

    assert results.iloc[0]["price_observations"] == 5


def test_price_risk_metrics_count_special_hours():
    results = calculate_price_risk_metrics(
        create_example_prices(),
        ["LZ_TEST"],
    )

    row = results.iloc[0]

    assert row["negative_price_hours"] == 1
    assert row["high_price_hours_above_100"] == 2
    assert row["extreme_price_hours_above_500"] == 1


def test_price_risk_metrics_calculate_distribution():
    results = calculate_price_risk_metrics(
        create_example_prices(),
        ["LZ_TEST"],
    )

    row = results.iloc[0]

    assert row["average_price_usd_per_mwh"] == pytest.approx(172.0)
    assert row["price_standard_deviation_usd_per_mwh"] > 0
    assert row["p99_price_usd_per_mwh"] > row["p95_price_usd_per_mwh"]


def test_unrequested_settlement_points_are_excluded():
    results = calculate_price_risk_metrics(
        create_example_prices(),
        ["LZ_TEST"],
    )

    assert len(results) == 1
    assert results.iloc[0]["ercot_settlement_point"] == "LZ_TEST"


def test_missing_columns_raise_error():
    incomplete_data = pd.DataFrame(
        {
            "wrong_column": [1, 2, 3],
        }
    )

    with pytest.raises(ValueError):
        calculate_price_risk_metrics(
            incomplete_data,
            ["LZ_TEST"],
        )


def test_unknown_settlement_point_raises_error():
    with pytest.raises(ValueError):
        calculate_price_risk_metrics(
            create_example_prices(),
            ["DOES_NOT_EXIST"],
        )