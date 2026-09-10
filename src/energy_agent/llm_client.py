import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_API_KEY = "ollama"
DEFAULT_MODEL = "qwen3:4b"

SYSTEM_PROMPT = """
You are an AI data-center energy analysis assistant.

Explain energy concepts clearly and concisely.
Do not invent electricity prices, emissions values, or regional statistics.
When project data is required, state that a data tool must be used.
""".strip()


class LLMError(RuntimeError):
    """Raised when the language model cannot return a usable response."""


@dataclass(frozen=True)
class LLMSettings:
    """Connection settings for an OpenAI-compatible LLM provider."""

    base_url: str
    api_key: str
    model: str


def load_llm_settings() -> LLMSettings:
    """Load LLM configuration from environment variables."""

    return LLMSettings(
        base_url=os.getenv(
            "LLM_BASE_URL",
            DEFAULT_BASE_URL,
        ),
        api_key=os.getenv(
            "LLM_API_KEY",
            DEFAULT_API_KEY,
        ),
        model=os.getenv(
            "LLM_MODEL",
            DEFAULT_MODEL,
        ),
    )


def create_llm_client(
    settings: LLMSettings | None = None,
) -> OpenAI:
    """Create a client for an OpenAI-compatible LLM endpoint."""

    active_settings = settings or load_llm_settings()

    return OpenAI(
        base_url=active_settings.base_url,
        api_key=active_settings.api_key,
    )


def generate_llm_response(
    user_message: str,
    client: Any | None = None,
    settings: LLMSettings | None = None,
) -> str:
    """Send a user message to the configured language model."""

    if not user_message.strip():
        raise ValueError("User message cannot be empty.")

    active_settings = settings or load_llm_settings()
    active_client = client or create_llm_client(active_settings)

    try:
        response = active_client.chat.completions.create(
            model=active_settings.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content
    except Exception as exc:
        raise LLMError(
            "The language model request failed. "
            "Confirm that Ollama is running and the model is installed."
        ) from exc

    if not content or not content.strip():
        raise LLMError(
            "The language model returned an empty response."
        )

    return content.strip()