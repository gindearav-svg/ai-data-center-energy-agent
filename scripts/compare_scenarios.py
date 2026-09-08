from pathlib import Path

import pandas as pd

from src.energy_agent.scenarios import (
    SCORING_SCENARIOS,
    compare_scenarios,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "baseline_regional_results.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "scenario_comparison_results.csv"
)


def main() -> None:
    regional_data = pd.read_csv(INPUT_PATH)

    results = compare_scenarios(regional_data)

    print("\nRegional Scenario Comparison")
    print("----------------------------")

    for scenario_name, weights in SCORING_SCENARIOS.items():
        print(f"\nScenario: {scenario_name}")

        print(
            "Weights: "
            f"cost={weights['cost']:.0%}, "
            f"carbon={weights['carbon']:.0%}, "
            f"price risk={weights['price_risk']:.0%}"
        )

        scenario_results = results[
            results["scenario"] == scenario_name
        ]

        display_columns = [
            "rank",
            "region",
            "cost_score",
            "carbon_score",
            "price_risk_score",
            "overall_score",
        ]

        print(
            scenario_results[display_columns].to_string(
                index=False,
                float_format=lambda value: f"{value:,.2f}",
            )
        )

    results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved results to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()