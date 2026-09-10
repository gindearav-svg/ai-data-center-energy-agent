from src.energy_agent.llm_client import (
    LLMError,
    generate_llm_response,
)


def main() -> None:
    """Demonstrate a real request to the configured LLM."""

    question = (
        "In two concise sentences, explain why PUE matters "
        "when estimating the electricity demand of an AI data center."
    )

    print("Local LLM Demonstration")
    print("-----------------------")
    print(f"\nQuestion:\n{question}")

    try:
        answer = generate_llm_response(question)
    except LLMError as exc:
        print(f"\nError:\n{exc}")
        raise SystemExit(1) from exc

    print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()