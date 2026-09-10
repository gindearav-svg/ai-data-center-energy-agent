import argparse
import json
from pathlib import Path

from src.energy_agent.pipeline import (
    build_pipeline_commands,
    run_pipeline,
)
from src.energy_agent.scenarios import SCORING_SCENARIOS


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "pipeline_run_report.json"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete AI data-center regional "
            "recommendation pipeline."
        )
    )

    parser.add_argument(
        "--it-load-mw",
        type=float,
        default=200.0,
    )

    parser.add_argument(
        "--pue",
        type=float,
        default=1.25,
    )

    parser.add_argument(
        "--utilization",
        type=float,
        default=0.95,
    )

    parser.add_argument(
        "--scenario",
        choices=SCORING_SCENARIOS.keys(),
        default="balanced",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    commands = build_pipeline_commands(
        it_load_mw=arguments.it_load_mw,
        pue=arguments.pue,
        utilization=arguments.utilization,
        scenario=arguments.scenario,
    )

    completed_steps = run_pipeline(commands)

    report = {
        "status": "passed",
        "it_load_mw": arguments.it_load_mw,
        "pue": arguments.pue,
        "utilization": arguments.utilization,
        "scenario": arguments.scenario,
        "completed_steps": completed_steps,
    }

    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nFull pipeline completed successfully.")
    print(f"Completed steps: {len(completed_steps)}")
    print(f"Pipeline report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()