import json
from pathlib import Path

import pandas as pd

from src.energy_agent.data_validation import (
    build_data_quality_summary,
)


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
    / "data_quality_report.json"
)


def main() -> None:
    regional_data = pd.read_csv(INPUT_PATH)

    summary = build_data_quality_summary(regional_data)

    OUTPUT_PATH.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nRegional Data Quality Report")
    print("----------------------------")
    print(json.dumps(summary, indent=2))
    print(f"\nSaved report to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()