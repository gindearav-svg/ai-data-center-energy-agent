import subprocess
import sys
from collections.abc import Callable


def build_pipeline_commands(
    it_load_mw: float = 200.0,
    pue: float = 1.25,
    utilization: float = 0.95,
    scenario: str = "balanced",
) -> list[tuple[str, list[str]]]:
    """Build the ordered commands required for the full pipeline."""
    return [
        (
            "Calculate hourly price-risk metrics",
            [
                sys.executable,
                "-m",
                "scripts.calculate_price_risk_metrics",
            ],
        ),
        (
            "Enrich regional metrics",
            [
                sys.executable,
                "-m",
                "scripts.enrich_regional_metrics",
            ],
        ),
        (
            "Validate regional data",
            [
                sys.executable,
                "-m",
                "scripts.validate_data",
            ],
        ),
        (
            "Calculate baseline results",
            [
                sys.executable,
                "-m",
                "scripts.calculate_baseline_results",
            ],
        ),
        (
            "Score candidate regions",
            [
                sys.executable,
                "-m",
                "scripts.score_regions",
            ],
        ),
        (
            "Compare preference scenarios",
            [
                sys.executable,
                "-m",
                "scripts.compare_scenarios",
            ],
        ),
        (
            "Generate custom recommendation",
            [
                sys.executable,
                "-m",
                "scripts.recommend_sites",
                "--it-load-mw",
                str(it_load_mw),
                "--pue",
                str(pue),
                "--utilization",
                str(utilization),
                "--scenario",
                scenario,
            ],
        ),
    ]


def run_pipeline(
    commands: list[tuple[str, list[str]]],
    runner: Callable = subprocess.run,
) -> list[dict[str, str]]:
    """
    Execute pipeline commands in order.

    A failing command stops the pipeline immediately.
    """
    completed_steps = []

    for step_number, (step_name, command) in enumerate(
        commands,
        start=1,
    ):
        print(f"\n[{step_number}/{len(commands)}] {step_name}")
        print("-" * (len(step_name) + 6))

        runner(command, check=True)

        completed_steps.append(
            {
                "step": step_name,
                "status": "passed",
            }
        )

    return completed_steps