import json

from src.energy_agent.agent import AgentError
from src.energy_agent.service import (
    run_grounded_comparison_agent,
)


def main() -> None:
    """Run a real tool-calling agent demonstration."""

    request = (
        "I need a data center with a 200 MW IT load, "
        "a PUE of 1.25, and 95% utilization. "
        "Use the balanced scenario to compare all available "
        "Texas regions and recommend the best option. "
        "Include annual electricity use, estimated wholesale "
        "cost, emissions, and the main tradeoff."
    )

    print("AI Data Center Energy Agent")
    print("---------------------------")
    print(f"\nUser request:\n{request}")

    try:
        result = run_grounded_comparison_agent(request)
    except AgentError as exc:
        print(f"\nAgent error:\n{exc}")
        raise SystemExit(1) from exc

    print("\nTools used:")
    print("-----------")

    if not result["tool_trace"]:
        print("- No tools were used.")
    else:
        for tool_number, tool_call in enumerate(
            result["tool_trace"],
            start=1,
        ):
            print(
                f"{tool_number}. "
                f"{tool_call['tool']} "
                f"({tool_call['status']})"
            )
            print(
                json.dumps(
                    tool_call["arguments"],
                    indent=2,
                )
            )
            print("Result:")
            print(
                json.dumps(
                    tool_call["result"],
                    indent=2,
                )
            )
    

    print("\nGrounding validation:")
    print("---------------------")
    print(f"Grounded: {result['grounded']}")
    print(f"Answer source: {result['answer_source']}")

    for check_name, passed in result["grounding_checks"].items():
        print(f"- {check_name}: {passed}")

    print("\nFinal answer:")
    print("-------------")
    print(result["answer"])


if __name__ == "__main__":
    main()