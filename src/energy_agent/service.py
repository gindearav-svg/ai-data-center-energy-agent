from typing import Any

from src.energy_agent.agent import run_energy_agent
from src.energy_agent.grounding import (
    build_deterministic_answer,
    build_grounded_summary,
    validate_llm_answer,
)
from src.energy_agent.llm_client import LLMSettings


def run_grounded_comparison_agent(
    user_message: str,
    client: Any | None = None,
    settings: LLMSettings | None = None,
) -> dict[str, Any]:
    """
    Run the agent and verify its final answer against tool data.

    If validation fails, replace the LLM answer with a deterministic
    explanation assembled from authoritative tool results.
    """

    agent_result = run_energy_agent(
        user_message=user_message,
        client=client,
        settings=settings,
    )

    summary = build_grounded_summary(
        agent_result["tool_trace"]
    )

    checks = validate_llm_answer(
        agent_result["answer"],
        summary,
    )

    grounded = all(checks.values())

    if grounded:
        final_answer = agent_result["answer"]
        answer_source = "llm"
    else:
        final_answer = build_deterministic_answer(summary)
        answer_source = "deterministic_fallback"

    return {
        **agent_result,
        "answer": final_answer,
        "answer_source": answer_source,
        "grounded": grounded,
        "grounding_checks": checks,
        "grounded_summary": summary,
    }