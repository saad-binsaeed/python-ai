"""
AI Tutor Script
A utility script that prompts the user for a topic and learning level, 
invokes a local LLM via init_chat_model, and reports the answer along with token usage and duration.
"""

import time
from langchain.chat_models import init_chat_model


def main():
    # Requirement 1: Prompt for topic and level, cleaning input with .strip()
    topic = input("Topic:   ").strip()
    level = input("Level (beginner or expert): ").strip().lower()

    if not topic or not level:
        print("Topic and level cannot be empty.")
        return

    # Requirement 2: System message specifying role, answer length, and learning level
    # Why: Explicitly defining persona and response constraints prevents overly verbose or complex answers.
    system_prompt = (
        f"You are a helpful tutor explaining topics at a {level} level. "
        "Explain the topic clearly and concisely in 2 to 3 sentences."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Explain {topic}"},
    ]

    # Requirement 3: Initialize model with temperature 0.2 and call .invoke()
    # Why: Setting temperature to 0.2 produces consistent, grounded explanations suitable for an educational context.
    model = init_chat_model("llama3.2", model_provider="ollama", temperature=0.2)

    start_time = time.perf_counter()
    response = model.invoke(messages)
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time

    # Extract token usage metadata from response
    total_tokens = response.usage_metadata.get("total_tokens", 0)

    # Requirement 4: Print formatted output
    print("\n" + "=" * 40)
    print(response.content)
    print("=" * 40)
    print(f"{total_tokens} tokens in {elapsed_time:.1f} seconds")


if __name__ == "__main__":
    main()