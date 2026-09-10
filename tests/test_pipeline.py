import subprocess

import pytest

from src.energy_agent.pipeline import (
    build_pipeline_commands,
    run_pipeline,
)


def test_pipeline_contains_eight_steps():
    commands = build_pipeline_commands()

    assert len(commands) == 8


def test_pipeline_steps_are_in_correct_order():
    commands = build_pipeline_commands()

    step_names = [step_name for step_name, _ in commands]

    assert step_names == [
        "Calculate hourly price-risk metrics",
        "Enrich regional metrics",
        "Validate regional data",
        "Build SQLite database",
        "Calculate baseline results",
        "Score candidate regions",
        "Compare preference scenarios",
        "Generate custom recommendation",
    ]


def test_custom_requirements_are_added_to_final_command():
    commands = build_pipeline_commands(
        it_load_mw=150,
        pue=1.20,
        utilization=0.90,
        scenario="cost_focused",
    )

    final_command = commands[-1][1]

    assert "--it-load-mw" in final_command
    assert "150" in final_command
    assert "1.2" in final_command
    assert "0.9" in final_command
    assert "cost_focused" in final_command


def test_pipeline_executes_every_command():
    executed_commands = []

    def fake_runner(command, check):
        assert check is True
        executed_commands.append(command)

    commands = build_pipeline_commands()

    results = run_pipeline(
        commands=commands,
        runner=fake_runner,
    )

    assert len(executed_commands) == 8
    assert len(results) == 8
    assert all(
        result["status"] == "passed"
        for result in results
    )


def test_pipeline_stops_when_a_command_fails():
    call_count = 0

    def failing_runner(command, check):
        nonlocal call_count
        call_count += 1

        if call_count == 2:
            raise subprocess.CalledProcessError(
                returncode=1,
                cmd=command,
            )

    commands = build_pipeline_commands()

    with pytest.raises(subprocess.CalledProcessError):
        run_pipeline(
            commands=commands,
            runner=failing_runner,
        )

    assert call_count == 2