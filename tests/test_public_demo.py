from fastapi.testclient import TestClient

from src.energy_agent import api as api_module


def test_public_mode_disables_agent_before_model_call(monkeypatch):
    monkeypatch.setenv("PUBLIC_DEMO", "1")

    def unexpected_model_call(message):
        raise AssertionError("Public mode must not call the model.")

    monkeypatch.setattr(
        api_module,
        "run_grounded_comparison_agent",
        unexpected_model_call,
    )

    client = TestClient(api_module.app)

    assert client.get("/app-config").json() == {
        "agent_enabled": False
    }

    response = client.post(
        "/agent/query",
        json={"message": "Compare Texas regions."},
    )

    assert response.status_code == 503
    assert "unavailable in the public demo" in response.json()["detail"]


def test_local_mode_keeps_agent_available(monkeypatch):
    monkeypatch.delenv("PUBLIC_DEMO", raising=False)

    client = TestClient(api_module.app)

    assert client.get("/app-config").json() == {
        "agent_enabled": True
    }