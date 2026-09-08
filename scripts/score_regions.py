from pathlib import Path

import pandas as pd

from src.energy_agent.scoring import DEFAULT_WEIGHTS, score_regions


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
    / "scored_regional_results.csv"
)


def main() -> None:
    regional_data = pd.read_csv(INPUT_PATH)

    scored_data = score_regions(regional_data)

    display_columns = [
        "rank",
        "region",
        "cost_score",
        "carbon_score",
        "price_risk_score",
        "overall_score",
    ]

    print("\nRegional Scoring Model")
    print("----------------------")

    print("\nWeights:")
    for category, weight in DEFAULT_WEIGHTS.items():
        print(f"- {category}: {weight:.0%}")

    print("\nResults:")
    print(
        scored_data[display_columns].to_string(
            index=False,
            float_format=lambda value: f"{value:,.2f}",
        )
    )

    scored_data.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved results to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()