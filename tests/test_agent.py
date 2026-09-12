import json
from types import SimpleNamespace
from copy import deepcopy

import pytest

from src.energy_agent.agent import (
    AgentError,
    TOOL_DEFINITIONS,
    execute_tool,
    parse_tool_arguments,
    run_energy_agent,
)


def make_tool_call(
    name: str,
    arguments: dict,
    call_id: str = "call_1",
):
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(
            name=name,
            arguments=json.dumps(arguments),
        ),
    )


def make_response(
    content: str | None,
    tool_calls: list | None = None,
):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=content,
                    tool_calls=tool_calls or [],
                )
            )
        ]
    )


class FakeCompletions:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(deepcopy(kwargs))
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.completions = FakeCompletions(responses)
        self.chat = SimpleNamespace(
            completions=self.completions,
        )


def test_five_tools_are_available():
    tool_names = {
        tool["function"]["name"]
        for tool in TOOL_DEFINITIONS
    }

    assert tool_names == {
        "get_available_regions",
        "get_electricity_price",
        "get_region_energy_profile",
        "estimate_power_requirement",
        "compare_energy_options",
    }


def test_parse_tool_arguments():
    result = parse_tool_arguments(
        '{"region": "Houston"}'
    )

    assert result == {
        "region": "Houston",
    }


def test_invalid_tool_arguments_raise_error():
    with pytest.raises(
        AgentError,
        match="invalid tool arguments",
    ):
        parse_tool_arguments(
            "not valid JSON"
        )


def test_execute_power_requirement_tool():
    result = execute_tool(
        "estimate_power_requirement",
        {
            "it_load_mw": 200,
            "pue": 1.25,
            "utilization": 0.95,
        },
    )

    assert result["facility_load_mw"] == 250.0
    assert result["annual_energy_mwh"] == 2080500.0


def test_unknown_tool_raises_error():
    with pytest.raises(
        AgentError,
        match="Unknown tool requested",
    ):
        execute_tool(
            "delete_database",
            {},
        )


def test_agent_executes_tool_and_returns_final_answer():
    tool_call = make_tool_call(
        "estimate_power_requirement",
        {
            "it_load_mw": 200,
            "pue": 1.25,
            "utilization": 0.95,
        },
    )

    client = FakeClient(
        [
            make_response(
                content=None,
                tool_calls=[tool_call],
            ),
            make_response(
                content=(
                    "The facility requires 250 MW and "
                    "2,080,500 MWh annually."
                )
            ),
        ]
    )

    result = run_energy_agent(
        (
            "Estimate the power requirement for a "
            "200 MW data center."
        ),
        client=client,
    )

    assert result["answer"] == (
        "The facility requires 250 MW and "
        "2,080,500 MWh annually."
    )
    assert len(result["tool_trace"]) == 1
    assert result["tool_trace"][0]["tool"] == (
        "estimate_power_requirement"
    )
    assert result["tool_trace"][0]["status"] == "passed"


def test_tool_result_is_returned_to_model():
    tool_call = make_tool_call(
        "estimate_power_requirement",
        {
            "it_load_mw": 200,
            "pue": 1.25,
            "utilization": 0.95,
        },
    )

    client = FakeClient(
        [
            make_response(
                content=None,
                tool_calls=[tool_call],
            ),
            make_response(
                content="Calculation completed."
            ),
        ]
    )

    run_energy_agent(
        "Calculate the data-center demand.",
        client=client,
    )

    second_request = client.completions.requests[1]
    tool_message = second_request["messages"][-1]
    tool_result = json.loads(
        tool_message["content"]
    )

    assert tool_message["role"] == "tool"
    assert tool_result["facility_load_mw"] == 250.0
    assert tool_result["annual_energy_mwh"] == 2080500.0


def test_agent_can_answer_without_calling_tool():
    client = FakeClient(
        [
            make_response(
                content=(
                    "PUE compares total facility power "
                    "with IT equipment power."
                )
            )
        ]
    )

    result = run_energy_agent(
        "What does PUE mean?",
        client=client,
    )

    assert result["tool_trace"] == []
    assert "facility power" in result["answer"]


def test_empty_user_message_raises_error():
    with pytest.raises(
        ValueError,
        match="User message cannot be empty",
    ):
        run_energy_agent(
            "   ",
            client=FakeClient([]),
        )