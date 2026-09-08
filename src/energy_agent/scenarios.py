import pandas as pd

from src.energy_agent.scoring import score_regions


SCORING_SCENARIOS = {
    "cost_focused": {
        "cost": 0.85,
        "carbon": 0.05,
        "price_risk": 0.10,
    },
    "balanced": {
        "cost": 0.50,
        "carbon": 0.20,
        "price_risk": 0.30,
    },
    "carbon_focused": {
        "cost": 0.30,
        "carbon": 0.60,
        "price_risk": 0.10,
    },
}


def compare_scenarios(
    regional_data: pd.DataFrame,
    scenarios: dict[str, dict[str, float]] | None = None,
) -> pd.DataFrame:
    """
    Score all regions under multiple preference scenarios.

    Returns one row for every region-scenario combination.
    """
    if scenarios is None:
        scenarios = SCORING_SCENARIOS

    scenario_results = []

    for scenario_name, weights in scenarios.items():
        scored_data = score_regions(
            regional_data=regional_data,
            weights=weights,
        )

        scored_data.insert(0, "scenario", scenario_name)
        scored_data["cost_weight"] = weights["cost"]
        scored_data["carbon_weight"] = weights["carbon"]
        scored_data["price_risk_weight"] = weights["price_risk"]

        scenario_results.append(scored_data)

    return pd.concat(
        scenario_results,
        ignore_index=True,
    )