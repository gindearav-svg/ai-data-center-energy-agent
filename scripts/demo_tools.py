import json

from src.energy_agent.tools import (
    compare_energy_options,
    estimate_power_requirement,
    get_available_regions,
    get_electricity_price,
)


def display_tool_result(
    tool_name: str,
    result: dict,
) -> None:
    print(f"\nTool: {tool_name}")
    print("-" * (len(tool_name) + 6))
    print(json.dumps(result, indent=2))


def main() -> None:
    display_tool_result(
        "get_available_regions",
        get_available_regions(),
    )

    display_tool_result(
        "get_electricity_price",
        get_electricity_price("Houston"),
    )

    display_tool_result(
        "estimate_power_requirement",
        estimate_power_requirement(
            it_load_mw=200,
            pue=1.25,
            utilization=0.95,
        ),
    )

    display_tool_result(
        "compare_energy_options",
        compare_energy_options(
            it_load_mw=200,
            pue=1.25,
            utilization=0.95,
            scenario="balanced",
        ),
    )


if __name__ == "__main__":
    main()