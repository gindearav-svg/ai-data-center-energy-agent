from src.energy_agent.grounding import (
    answer_contains_number,
    build_deterministic_answer,
    build_grounded_summary,
    validate_llm_answer,
)


def make_tool_trace():
    return [
        {
            "tool": "estimate_power_requirement",
            "arguments": {
                "it_load_mw": 200,
                "pue": 1.25,
                "utilization": 0.95,
            },
            "status": "passed",
            "result": {
                "it_load_mw": 200,
                "pue": 1.25,
                "utilization": 0.95,
                "facility_load_mw": 250.0,
                "annual_energy_mwh": 2080500.0,
            },
        },
        {
            "tool": "compare_energy_options",
            "arguments": {
                "it_load_mw": 200,
                "pue": 1.25,
                "utilization": 0.95,
                "scenario": "balanced",
            },
            "status": "passed",
            "result": {
                "requirements": {
                    "it_load_mw": 200,
                    "pue": 1.25,
                    "utilization": 0.95,
                },
                "scenario": "balanced",
                "weights": {
                    "cost": 0.5,
                    "carbon": 0.2,
                    "price_risk": 0.3,
                },
                "recommendation": {
                    "region": "Houston",
                    "overall_score": 83.75,
                },
                "regional_results": [
                    {
                        "rank": 1,
                        "region": "Houston",
                        "estimated_annual_wholesale_cost_usd": (
                            71914563.0
                        ),
                        "estimated_annual_emissions_metric_tons_co2e": (
                            695155.3845
                        ),
                        "cost_score": 87.4932903918,
                        "carbon_score": 50.0,
                        "price_risk_score": 100.0,
                        "overall_score": 83.75,
                    },
                    {
                        "rank": 2,
                        "region": "North Texas",
                        "estimated_annual_wholesale_cost_usd": (
                            69490780.5
                        ),
                        "estimated_annual_emissions_metric_tons_co2e": (
                            695155.3845
                        ),
                        "cost_score": 100.0,
                        "carbon_score": 50.0,
                        "price_risk_score": 68.08,
                        "overall_score": 80.42,
                    },
                    {
                        "rank": 3,
                        "region": "West Texas",
                        "estimated_annual_wholesale_cost_usd": (
                            88870638.0
                        ),
                        "estimated_annual_emissions_metric_tons_co2e": (
                            695155.3845
                        ),
                        "cost_score": 0.0,
                        "carbon_score": 50.0,
                        "price_risk_score": 0.0,
                        "overall_score": 10.0,
                    },
                ],
            },
        },
    ]


def test_build_grounded_summary():
    summary = build_grounded_summary(make_tool_trace())

    assert summary["recommended_region"] == "Houston"
    assert summary["cheapest_region"] == "North Texas"
    assert summary["annual_energy_mwh"] == 2080500.0
    assert summary["recommended_annual_cost_usd"] == 71914563.0
    assert summary["recommended_cost_premium_usd"] == 2423782.5


def test_answer_contains_rounded_millions():
    assert answer_contains_number(
        "The annual cost is $71.9 million.",
        71914563.0,
        allow_millions=True,
    )


def test_valid_answer_passes_grounding_checks():
    summary = build_grounded_summary(make_tool_trace())

    answer = (
        "Houston is recommended. Annual electricity use is "
        "2,080,500 MWh, estimated cost is $71.9 million, and "
        "emissions are 695,155 metric tons CO2e."
    )

    checks = validate_llm_answer(answer, summary)

    assert all(checks.values())


def test_hallucinated_answer_fails_grounding_checks():
    summary = build_grounded_summary(make_tool_trace())

    answer = (
       
 
 "New York is recommended with annual electricity use of "
        "2,082,000 MWh, a cost of $120 million, and emissions "
        "of 15,000 metric tons CO2e."
    )

    checks = validate_llm_answer(answer, summary)

    assert not all(checks.values())
    assert checks["recommended_region_present"] is False
    assert checks["annual_energy_present"] is False


def test_deterministic_answer_uses_tool_values():
    summary = build_grounded_summary(make_tool_trace())

    answer = build_deterministic_answer(summary)

    assert "Houston" in answer
    assert "2,080,500 MWh" in answer
    assert "$71,914,563" in answer
    assert "695,155 metric tons" in answer
    assert "$2,423,782 cheaper" in answer