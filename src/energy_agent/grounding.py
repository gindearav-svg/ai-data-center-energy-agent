from typing import Any

from src.energy_agent.tools import (
    estimate_power_requirement,
)


PRICE_DATA_YEAR = 2025
EMISSIONS_DATA_YEAR = 2023


class GroundingError(RuntimeError):
    """Raised when authoritative tool data cannot be validated."""


def get_passed_tool_result(
    tool_trace: list[dict[str, Any]],
    tool_name: str,
) -> dict[str, Any] | None:
    """Return the most recent successful result for one tool."""

    for tool_call in reversed(tool_trace):
        if (
            tool_call.get("tool") == tool_name
            and tool_call.get("status") == "passed"
        ):
            result = tool_call.get("result")

            if isinstance(result, dict):
                return result

    return None


def build_grounded_summary(
    tool_trace: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build an authoritative decision summary from tool results."""

    comparison = get_passed_tool_result(
        tool_trace,
        "compare_energy_options",
    )

    if comparison is None:
        raise GroundingError(
            "A successful comparison tool result is required."
        )

    requirements = comparison.get("requirements")
    recommendation = comparison.get("recommendation")
    regional_results = comparison.get("regional_results")
    weights = comparison.get("weights")

    if not isinstance(requirements, dict):
        raise GroundingError(
            "Comparison result is missing requirements."
        )

    if not isinstance(recommendation, dict):
        raise GroundingError(
            "Comparison result is missing its recommendation."
        )

    if not isinstance(regional_results, list) or not regional_results:
        raise GroundingError(
            "Comparison result is missing regional results."
        )

    recommended_region = recommendation.get("region")

    if not isinstance(recommended_region, str):
        raise GroundingError(
            "Comparison result has an invalid recommended region."
        )

    recommended_result = next(
        (
            result
            for result in regional_results
            if result.get("region") == recommended_region
        ),
        None,
    )

    if recommended_result is None:
        raise GroundingError(
            "Recommended region is absent from regional results."
        )

    cheapest_result = min(
        regional_results,
        key=lambda result: result[
            "estimated_annual_wholesale_cost_usd"
        ],
    )

    power_result = get_passed_tool_result(
        tool_trace,
        "estimate_power_requirement",
    )

    if power_result is None:
        power_result = estimate_power_requirement(
            it_load_mw=requirements["it_load_mw"],
            pue=requirements["pue"],
            utilization=requirements["utilization"],
        )

    recommended_cost = float(
        recommended_result[
            "estimated_annual_wholesale_cost_usd"
        ]
    )
    cheapest_cost = float(
        cheapest_result[
            "estimated_annual_wholesale_cost_usd"
        ]
    )

    return {
        "scenario": comparison.get("scenario"),
        "weights": weights,
        "it_load_mw": float(power_result["it_load_mw"]),
        "pue": float(power_result["pue"]),
        "utilization": float(
            power_result["utilization"]
        ),
        "facility_load_mw": float(
            power_result["facility_load_mw"]
        ),
        "annual_energy_mwh": float(
            power_result["annual_energy_mwh"]
        ),
        "recommended_region": recommended_region,
        "recommended_overall_score": float(
            recommendation["overall_score"]
        ),
        "recommended_annual_cost_usd": recommended_cost,
        "recommended_annual_emissions_metric_tons_co2e": float(
            recommended_result[
                "estimated_annual_emissions_metric_tons_co2e"
            ]
        ),
        "recommended_cost_score": float(
            recommended_result["cost_score"]
        ),
        "recommended_price_stability_score": float(
            recommended_result["price_risk_score"]
        ),
        "cheapest_region": cheapest_result["region"],
        "cheapest_annual_cost_usd": cheapest_cost,
        "recommended_cost_premium_usd": (
            recommended_cost - cheapest_cost
        ),
        "price_data_year": PRICE_DATA_YEAR,
        "emissions_data_year": EMISSIONS_DATA_YEAR,
        "regional_results": regional_results,
        "limitations": [
            (
                "The cost estimate represents wholesale electricity "
                "cost and does not include construction, transmission, "
                "taxes, or retail electricity charges."
            ),
            (
                "The shared ERCT eGRID emissions factor is too coarse "
                "to prove that local generation mixes are identical."
            ),
        ],
    }


def answer_contains_number(
    answer: str,
    value: float,
    allow_millions: bool = False,
) -> bool:
    """Check for an exact or appropriately rounded number."""

    normalized_answer = (
        answer.lower()
        .replace(",", "")
        .replace("$", "")
    )

    rounded_integer = str(int(round(value)))

    if rounded_integer in normalized_answer:
        return True

    if allow_millions:
        millions = value / 1_000_000
        rounded_millions = f"{millions:.1f}"

        if (
            f"{rounded_millions}m" in normalized_answer
            or f"{rounded_millions} million"
            in normalized_answer
        ):
            return True

    return False


def validate_llm_answer(
    answer: str,
    summary: dict[str, Any],
) -> dict[str, bool]:
    """Check important LLM claims against authoritative values."""

    normalized_answer = answer.lower()

    return {
        "recommended_region_present": (
            summary["recommended_region"].lower()
            in normalized_answer
        ),
        "annual_energy_present": answer_contains_number(
            answer,
            summary["annual_energy_mwh"],
        ),
        "recommended_cost_present": answer_contains_number(
            answer,
            summary["recommended_annual_cost_usd"],
            allow_millions=True,
        ),
        "emissions_present": answer_contains_number(
            answer,
            summary[
                "recommended_annual_emissions_metric_tons_co2e"
            ],
        ),
    }


def build_deterministic_answer(
    summary: dict[str, Any],
) -> str:
    """Build a guaranteed-grounded decision explanation."""

    recommended_region = summary["recommended_region"]
    cheapest_region = summary["cheapest_region"]
    cost_premium = summary["recommended_cost_premium_usd"]

    if cost_premium > 0:
        tradeoff = (
            f"{cheapest_region} is approximately "
            f"${cost_premium:,.0f} cheaper annually, but "
            f"{recommended_region}'s stronger price stability "
            "offsets that cost disadvantage under the selected "
            "scenario weights."
        )
    else:
        tradeoff = (
            f"{recommended_region} is also the lowest-cost option "
            "in the current comparison."
        )

    return (
        f"**Recommended region:** {recommended_region}\n\n"
        f"- **Facility load:** "
        f"{summary['facility_load_mw']:,.1f} MW\n"
        f"- **Annual electricity use:** "
        f"{summary['annual_energy_mwh']:,.0f} MWh\n"
        f"- **Estimated annual wholesale cost:** "
        f"${summary['recommended_annual_cost_usd']:,.0f}\n"
        f"- **Estimated annual emissions:** "
        f"{summary['recommended_annual_emissions_metric_tons_co2e']:,.0f} "
        "metric tons CO2e\n"
        f"- **Overall score:** "
        f"{summary['recommended_overall_score']:,.2f}\n\n"
        f"**Main tradeoff:** {tradeoff}\n\n"
        f"Electricity prices use {summary['price_data_year']} data, "
        f"while emissions use {summary['emissions_data_year']} data. "
        "Identical emissions estimates reflect the shared coarse ERCT "
        "eGRID factor and do not prove identical local generation mixes."
    )