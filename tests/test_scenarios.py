import pandas as pd

from src.energy_agent.scenarios import (
    SCORING_SCENARIOS,
    compare_scenarios,
)


def create_example_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": [
                "Low Cost Region",
                "Low Risk Region",
                "Expensive Region",
            ],
            "estimated_annual_wholesale_cost_usd": [
                50_000_000,
                60_000_000,
                80_000_000,
            ],
            "estimated_annual_emissions_metric_tons_co2e": [
                500_000,
                500_000,
                500_000,
            ],
            "maximum_dam_price_usd_per_mwh": [
                900,
                400,
                1_000,
            ],
        }
    )


def test_compare_scenarios_returns_every_combination():
    data = create_example_data()

    results = compare_scenarios(data)

    expected_rows = len(data) * len(SCORING_SCENARIOS)

    assert len(results) == expected_rows
    assert set(results["scenario"]) == set(SCORING_SCENARIOS)


def test_each_scenario_ranks_every_region():
    data = create_example_data()

    results = compare_scenarios(data)

    for scenario_name in SCORING_SCENARIOS:
        scenario_results = results[
            results["scenario"] == scenario_name
        ]

        assert set(scenario_results["rank"]) == {1, 2, 3}


def test_scenario_weights_are_saved():
    data = create_example_data()

    results = compare_scenarios(data)

    balanced_results = results[
        results["scenario"] == "balanced"
    ]

    assert (balanced_results["cost_weight"] == 0.50).all()
    assert (balanced_results["carbon_weight"] == 0.20).all()
    assert (balanced_results["price_risk_weight"] == 0.30).all()


def test_cost_focused_scenario_prefers_low_cost_region():
    data = create_example_data()

    results = compare_scenarios(data)

    cost_results = results[
        results["scenario"] == "cost_focused"
    ]

    winner = cost_results.loc[
        cost_results["rank"] == 1,
        "region",
    ].iloc[0]

    assert winner == "Low Cost Region"