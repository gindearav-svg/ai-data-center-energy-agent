import argparse
from pathlib import Path

import pandas as pd

from src.energy_agent.recommendation import (
    build_regional_recommendation,
)
from src.energy_agent.scenarios import SCORING_SCENARIOS


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "custom_recommendation_results.csv"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare Texas regions for an AI data center."
    )

    parser.add_argument(
        "--it-load-mw",
        type=float,
        required=True,
        help="Data-center IT equipment load in megawatts.",
    )

    parser.add_argument(
        "--pue",
        type=float,
        required=True,
        help="Power Usage Effectiveness, such as 1.25.",
    )

    parser.add_argument(
        "--utilization",
        type=float,
        required=True,
        help="Average utilization as a decimal, such as 0.95.",
    )

    parser.add_argument(
        "--scenario",
        choices=SCORING_SCENARIOS.keys(),
        default="balanced",
        help="Preference scenario used for scoring.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    regional_metrics = pd.read_csv(INPUT_PATH)
    weights = SCORING_SCENARIOS[arguments.scenario]

    results = build_regional_recommendation(
        regional_metrics=regional_metrics,
        it_load_mw=arguments.it_load_mw,
        pue=arguments.pue,
        utilization=arguments.utilization,
        weights=weights,
    )

    winner = results.iloc[0]

    print("\nAI Data Center Regional Recommendation")
    print("--------------------------------------")
    print(f"IT load: {arguments.it_load_mw:,.1f} MW")
    print(f"PUE: {arguments.pue:.2f}")
    print(f"Utilization: {arguments.utilization:.1%}")
    print(f"Scenario: {arguments.scenario}")

    print("\nRegional comparison:")

    display_columns = [
        "rank",
        "region",
        "estimated_annual_wholesale_cost_usd",
        "estimated_annual_emissions_metric_tons_co2e",
        "overall_score",
    ]

    print(
        results[display_columns].to_string(
            index=False,
            float_format=lambda value: f"{value:,.2f}",
        )
    )

    print(
        f"\nRecommended region: {winner['region']}"
        f"\nOverall score: {winner['overall_score']:.2f}"
    )

    results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved results to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()