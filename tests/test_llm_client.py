from types import SimpleNamespace

import pytest

from src.energy_agent.llm_client import (
    LLMError,
    generate_llm_response,
    load_llm_settings,
)


class FakeCompletions:
    def __init__(
        self,
        content: str | None = "PUE measures data-center efficiency.",
        error: Exception | None = None,
    ):
        self.content = content
        self.error = error
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs

        if self.error:
            raise self.error

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=self.content,
                    )
                )
            ]
        )


class FakeClient:
    def __init__(
        self,
        content: str | None = "PUE measures data-center efficiency.",
        error: Exception | None = None,
    ):
        self.completions = FakeCompletions(
            content=content,
            error=error,
        )
        self.chat = SimpleNamespace(
            completions=self.completions,
        )


def test_default_settings_use_local_ollama():
    settings = load_llm_settings()

    assert settings.base_url == "http://localhost:11434/v1"
    assert settings.api_key == "ollama"
    assert settings.model == "qwen3:8b"


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "https://example.com/v1",
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "hosted-model",
    )

    settings = load_llm_settings()

    assert settings.base_url == "https://example.com/v1"
    assert settings.api_key == "test-key"
    assert settings.model == "hosted-model"


def test_generate_llm_response_returns_text():
    client = FakeClient(
        content="PUE compares facility power with IT power."
    )

    result = generate_llm_response(
        "What is PUE?",
        client=client,
    )

    assert result == (
        "PUE compares facility power with IT power."
    )


def test_generate_llm_response_sends_system_and_user_messages():
    client = FakeClient()

    generate_llm_response(
        "Explain data-center electricity demand.",
        client=client,
    )

    request = client.completions.request

    assert request["model"] == "qwen3:8b"
    assert request["messages"][0]["role"] == "system"
    assert request["messages"][1] == {
        "role": "user",
        "content": "Explain data-center electricity demand.",
    }


def test_empty_user_message_raises_error():
    with pytest.raises(
        ValueError,
        match="User message cannot be empty",
    ):
        generate_llm_response(
            "   ",
            client=FakeClient(),
        )


def test_provider_failure_raises_llm_error():
    client = FakeClient(
        error=ConnectionError("Connection failed"),
    )

    with pytest.raises(
        LLMError,
        match="language model request failed",
    ):
        generate_llm_response(
            "What is PUE?",
            client=client,
        )


def test_empty_provider_response_raises_llm_error():
    client = FakeClient(content="")

    with pytest.raises(
        LLMError,
        match="empty response",
    ):
        generate_llm_response(
            "What is PUE?",
            client=client,
        )