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
    Use the agent to select tools, then build the public answer from
    authoritative tool results.

    The model's original wording is retained for inspection, but
    presence checks alone do not certify all of its claims.
    """

    agent_result = run_energy_agent(
        user_message=user_message,
        client=client,
        settings=settings,
    )

    summary = build_grounded_summary(
        agent_result["tool_trace"]
    )

    model_draft = agent_result["answer"]
    draft_checks = validate_llm_answer(
        model_draft,
        summary,
    )

    return {
        **agent_result,
        "answer": build_deterministic_answer(summary),
        "model_draft": model_draft,
        "answer_source": "tool_summary",
        "grounded": True,
        "grounding_checks": draft_checks,
        "grounded_summary": summary,
    }