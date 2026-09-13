from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.energy_agent import api as api_module
from src.energy_agent.database import initialize_database
from src.energy_agent.agent import AgentError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

REGIONAL_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "api_test.db"
    regional_data = pd.read_csv(REGIONAL_DATA_PATH)

    initialize_database(
        database_path=database_path,
        schema_path=SCHEMA_PATH,
        regional_data=regional_data,
    )

    monkeypatch.setattr(
        api_module,
        "DATABASE_PATH",
        database_path,
    )

    return TestClient(api_module.app)


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["version"] == "0.3.0"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_regions_endpoint(client):
    response = client.get("/regions")

    assert response.status_code == 200
    assert response.json()["count"] == 3


def test_region_price_endpoint(client):
    response = client.get("/regions/Houston/price")

    assert response.status_code == 200
    assert (
        response.json()["average_price_usd_per_mwh"]
        == pytest.approx(34.566)
    )


def test_region_profile_endpoint(client):
    response = client.get("/regions/North%20Texas")

    assert response.status_code == 200
    assert response.json()["region"] == "North Texas"


def test_unknown_region_returns_404(client):
    response = client.get("/regions/California")

    assert response.status_code == 404
    assert "not available" in response.json()["detail"]


def test_recommendation_endpoint(client):
    response = client.post(
        "/recommendations",
        json={
            "it_load_mw": 200,
            "pue": 1.25,
            "utilization": 0.95,
            "scenario": "balanced",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["recommendation"]["region"] == "Houston"
    assert len(result["regional_results"]) == 3


def test_invalid_utilization_returns_422(client):
    response = client.post(
        "/recommendations",
        json={
            "it_load_mw": 200,
            "pue": 1.25,
            "utilization": 95,
            "scenario": "balanced",
        },
    )

    assert response.status_code == 422


def test_invalid_scenario_returns_422(client):
    response = client.post(
        "/recommendations",
        json={
            "it_load_mw": 200,
            "pue": 1.25,
            "utilization": 0.95,
            "scenario": "cheapest_possible",
        },
    )

    assert response.status_code == 422

def test_agent_query_endpoint(client, monkeypatch):
    def fake_grounded_agent(message):
        assert "200 MW" in message

        return {
            "answer": (
                "Houston is recommended for the balanced scenario."
            ),
            "answer_source": "llm",
            "grounded": True,
            "grounding_checks": {
                "recommended_region_present": True,
                "annual_energy_present": True,
                "recommended_cost_present": True,
                "emissions_present": True,
            },
            "grounded_summary": {
                "recommended_region": "Houston",
                "annual_energy_mwh": 2080500.0,
            },
            "tool_trace": [
                {
                    "tool": "compare_energy_options",
                    "arguments": {
                        "it_load_mw": 200,
                        "pue": 1.25,
                        "utilization": 0.95,
                        "scenario": "balanced",
                    },
                    "status": "passed",
                    "result": {},
                }
            ],
        }

    monkeypatch.setattr(
        api_module,
        "run_grounded_comparison_agent",
        fake_grounded_agent,
    )

    response = client.post(
        "/agent/query",
        json={
            "message": (
                "Compare Texas regions for a 200 MW "
                "AI data center."
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["grounded"] is True
    assert result["answer_source"] == "llm"
    assert result["grounded_summary"][
        "recommended_region"
    ] == "Houston"
    assert result["tool_trace"][0]["status"] == "passed"


def test_blank_agent_query_returns_422(
    client,
    monkeypatch,
):
    def agent_should_not_run(message):
        raise AssertionError(
            "Agent should not run for a blank message."
        )

    monkeypatch.setattr(
        api_module,
        "run_grounded_comparison_agent",
        agent_should_not_run,
    )

    response = client.post(
        "/agent/query",
        json={
            "message": "   ",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Message cannot be blank."
    )


def test_agent_failure_returns_503(
    client,
    monkeypatch,
):
    def unavailable_agent(message):
        raise AgentError(
            "The language model is unavailable."
        )

    monkeypatch.setattr(
        api_module,
        "run_grounded_comparison_agent",
        unavailable_agent,
    )

    response = client.post(
        "/agent/query",
        json={
            "message": "Compare the available regions.",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The language model is unavailable."
    )