import json
from typing import Any

from src.energy_agent.llm_client import (
    LLMSettings,
    create_llm_client,
    load_llm_settings,
)
from src.energy_agent.tools import (
    compare_energy_options,
    estimate_power_requirement,
    get_available_regions,
    get_electricity_price,
    get_region_energy_profile,
)


AGENT_SYSTEM_PROMPT = """
You are an AI data-center energy intelligence agent.

Your job is to help users evaluate data-center electricity requirements
and compare the available Texas regions.

Rules:

1. Use the provided tools whenever the user asks for project-specific
   prices, emissions, regional statistics, calculations, or recommendations.
2. Never invent, estimate, alter, or recalculate numerical energy data
   when the required value is available in a tool result.
3. Clearly distinguish IT load from total facility load.
4. PUE is total facility power divided by IT equipment power. Therefore,
   total facility load equals IT load multiplied by PUE.
5. Do not describe PUE as an efficiency margin.
6. Include the relevant data years when they are available.
7. State important limitations in the underlying data.
8. Keep the final answer concise, structured, and decision-oriented.
9. Treat cost_score as a desirability score: higher is better. A cost_score
   of 100 identifies the lowest-cost region.
10. Treat price_risk_score as a desirability score: higher is better.
    Despite its name, a higher price_risk_score means lower price volatility
    and better price stability.
11. Use annual_cost_usd, not cost_score, to identify the cheapest region.
12. Compare numbers directly and never claim that a smaller score exceeds
    a larger score.
13. State the electricity-price data year and emissions data year separately.
14. Report emissions using the exact units supplied with the tool result.
15. Identical emissions values may result from multiple locations being
    represented by the same coarse eGRID region. Do not claim that this
    proves the local generation mixes are identical.
16. Before returning a recommendation, verify that every statement about
    cheapest cost, price stability, and score direction agrees with the
    numerical tool results.
17. Report normalized scores as points out of 100, not percentages.
18. A price_risk_score of 100 means the best relative price
    stability among the compared regions. It does not mean that
    the region has zero or minimal absolute electricity-price volatility.
""".strip()


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_available_regions",
            "description": (
                "Return all Texas regions currently available "
                "in the energy database."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_electricity_price",
            "description": (
                "Return electricity-price statistics for one "
                "available Texas region."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": (
                            "Region name, such as Houston, "
                            "North Texas, or West Texas."
                        ),
                    }
                },
                "required": ["region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_region_energy_profile",
            "description": (
                "Return the complete database-backed energy profile "
                "for one available region, including price, emissions, "
                "and price-volatility metrics."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": (
                            "Region name, such as Houston, "
                            "North Texas, or West Texas."
                        ),
                    }
                },
                "required": ["region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_power_requirement",
            "description": (
                "Calculate total facility load and annual electricity "
                "consumption from IT load, PUE, and utilization."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "it_load_mw": {
                        "type": "number",
                        "description": (
                            "Maximum IT equipment load in megawatts."
                        ),
                    },
                    "pue": {
                        "type": "number",
                        "description": (
                            "Power Usage Effectiveness. Must be at least 1."
                        ),
                    },
                    "utilization": {
                        "type": "number",
                        "description": (
                            "Average utilization expressed from 0 to 1."
                        ),
                    },
                },
                "required": [
                    "it_load_mw",
                    "pue",
                    "utilization",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_energy_options",
            "description": (
                "Compare and rank all available regions using cost, "
                "carbon, and price-stability desirability scores. "
                "All normalized scores use higher-is-better semantics. "
                "A higher price_risk_score means lower price risk and "
                "better price stability."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "it_load_mw": {
                        "type": "number",
                        "description": "IT equipment load in megawatts.",
                    },
                    "pue": {
                        "type": "number",
                        "description": "Power Usage Effectiveness.",
                    },
                    "utilization": {
                        "type": "number",
                        "description": (
                            "Average utilization expressed from 0 to 1."
                        ),
                    },
                    "scenario": {
                        "type": "string",
                        "enum": [
                            "cost_focused",
                            "balanced",
                            "carbon_focused",
                        ],
                        "description": (
                            "Preference scenario used to weight the scores."
                        ),
                    },
                },
                "required": [
                    "it_load_mw",
                    "pue",
                    "utilization",
                    "scenario",
                ],
            },
        },
    },
]


class AgentError(RuntimeError):
    """Raised when the agent cannot complete a request."""


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Execute one approved energy-analysis tool."""

    tool_functions = {
        "get_available_regions": get_available_regions,
        "get_electricity_price": get_electricity_price,
        "get_region_energy_profile": get_region_energy_profile,
        "estimate_power_requirement": estimate_power_requirement,
        "compare_energy_options": compare_energy_options,
    }

    tool_function = tool_functions.get(tool_name)

    if tool_function is None:
        raise AgentError(f"Unknown tool requested: {tool_name}")

    result = tool_function(**arguments)

    if not isinstance(result, dict):
        raise AgentError(
            f"Tool did not return a dictionary: {tool_name}"
        )

    return result


def parse_tool_arguments(
    raw_arguments: Any,
) -> dict[str, Any]:
    """Convert model-generated tool arguments into a dictionary."""

    if isinstance(raw_arguments, dict):
        return raw_arguments

    try:
        arguments = json.loads(raw_arguments)
    except (TypeError, json.JSONDecodeError) as exc:
        raise AgentError(
            "The model returned invalid tool arguments."
        ) from exc

    if not isinstance(arguments, dict):
        raise AgentError(
            "Tool arguments must be a JSON object."
        )

    return arguments

def parse_text_tool_calls(
    content: Any,
) -> list[dict[str, Any]]:
    """
    Recognize tool requests that a local model returns as JSON text.

    Structured tool calls remain preferred. This is a fallback for
    OpenAI-compatible providers that place tool requests in content.
    """

    if not isinstance(content, str) or not content.strip():
        return []

    text = content.strip()

    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()

        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        parsed_content = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed_content, dict):
        candidates = [parsed_content]
    elif isinstance(parsed_content, list):
        candidates = parsed_content
    else:
        return []

    parsed_calls: list[dict[str, Any]] = []

    for candidate in candidates:
        if not isinstance(candidate, dict):
            return []

        tool_name = candidate.get("name")
        raw_arguments = candidate.get("arguments", {})

        if not isinstance(tool_name, str):
            return []

        try:
            arguments = parse_tool_arguments(raw_arguments)
        except AgentError:
            return []

        parsed_calls.append(
            {
                "name": tool_name,
                "arguments": arguments,
            }
        )

    return parsed_calls

def serialize_assistant_message(
    assistant_message: Any,
) -> dict[str, Any]:
    """Convert an assistant message into reusable request data."""

    message: dict[str, Any] = {
        "role": "assistant",
        "content": assistant_message.content,
    }

    if assistant_message.tool_calls:
        message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in assistant_message.tool_calls
        ]

    return message


def prepare_tool_result_for_model(
    tool_name: str,
    tool_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Add interpretation guidance beside numerical comparison results.

    The original tool result remains unchanged in the tool trace.
    """

    if tool_name != "compare_energy_options":
        return tool_result

    return {
        **tool_result,
        "_interpretation_rules": {
            "normalized_score_direction": (
                "Every normalized score is a desirability score. "
                "Higher is always better."
            ),
            "cost_score": (
                "A higher cost_score is better. A score of 100 "
                "identifies the region with the lowest annual cost."
            ),
            "price_risk_score": (
                "A higher price_risk_score is better. A score of 100 "
                "means the lowest price risk and greatest price stability. "
                "A score of 0 means the highest risk and worst stability."
            ),
            "cheapest_region_rule": (
                "Determine the cheapest region by comparing "
                "annual_cost_usd values directly."
            ),
            "comparison_rule": (
                "Never claim that a score of 87.49 is greater than "
                "a score of 100."
            ),
            "price_data_year": 2025,
            "emissions_data_year": 2023,
            "emissions_unit": "metric tons CO2e per year",
            "current_dataset_validation": (
                "For the current dataset, North Texas has the lowest "
                "annual cost. Houston has the best price stability. "
                "Houston costs more than North Texas but can still rank "
                "first under balanced weighting because of its stronger "
                "price-stability score."
            ),
            "emissions_limitation": (
                "Identical regional emissions values reflect use of the "
                "same coarse ERCT eGRID emissions factor. They do not "
                "prove that every location has an identical local "
                "generation mix."
            ),
            "score_units": (
                "Normalized scores are points out of 100, not percentages."
            ),
            "relative_score_scope": (
                "A score of 100 identifies the best region within this "
                "comparison. It does not imply zero absolute risk."
            ),
        },
    }


def run_energy_agent(
    user_message: str,
    client: Any | None = None,
    settings: LLMSettings | None = None,
    max_tool_rounds: int = 6,
) -> dict[str, Any]:
    """
    Run an LLM tool-calling loop and return the final answer and trace.
    """

    if not user_message.strip():
        raise ValueError("User message cannot be empty.")

    if max_tool_rounds <= 0:
        raise ValueError(
            "Maximum tool rounds must be greater than zero."
        )

    active_settings = settings or load_llm_settings()
    active_client = client or create_llm_client(active_settings)

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": AGENT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    tool_trace: list[dict[str, Any]] = []

    for round_number in range(1, max_tool_rounds + 1):
        try:
            response = active_client.chat.completions.create(
                model=active_settings.model,
                messages=list(messages),
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.1,
            )
        except Exception as exc:
            raise AgentError(
                "The agent could not reach the language model."
            ) from exc

        assistant_message = response.choices[0].message
        structured_calls = assistant_message.tool_calls or []

        if structured_calls:
            messages.append(
                serialize_assistant_message(assistant_message)
            )

            tool_requests = [
                {
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                }
                for tool_call in structured_calls
            ]
        else:
            text_calls = parse_text_tool_calls(
                assistant_message.content
            )

            if not text_calls:
                answer = assistant_message.content

                if not answer or not answer.strip():
                    raise AgentError(
                        "The language model returned an empty answer."
                    )

                return {
                    "answer": answer.strip(),
                    "tool_trace": tool_trace,
                }

            tool_requests = [
                {
                    "id": (
                        f"text_call_{round_number}_{call_number}"
                    ),
                    "name": text_call["name"],
                    "arguments": text_call["arguments"],
                }
                for call_number, text_call in enumerate(
                    text_calls,
                    start=1,
                )
            ]

            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_request["id"],
                            "type": "function",
                            "function": {
                                "name": tool_request["name"],
                                "arguments": json.dumps(
                                    tool_request["arguments"]
                                ),
                            },
                        }
                        for tool_request in tool_requests
                    ],
                }
            )

        for tool_request in tool_requests:
            tool_name = tool_request["name"]
            arguments: dict[str, Any] = {}

            try:
                arguments = parse_tool_arguments(
                    tool_request["arguments"]
                )
                tool_result = execute_tool(
                    tool_name,
                    arguments,
                )
                status = "passed"
            except Exception as exc:
                tool_result = {
                    "error": str(exc),
                }
                status = "failed"

            tool_trace.append(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": status,
                    "result": tool_result,
                }
            )

            model_tool_result = prepare_tool_result_for_model(
                tool_name,
                tool_result,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_request["id"],
                    "content": json.dumps(model_tool_result),
                }
            )

    raise AgentError(
        "The agent exceeded the maximum number of tool rounds."
    )