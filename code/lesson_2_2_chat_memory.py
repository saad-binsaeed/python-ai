"""
Personal Tutor with Memory
A interactive conversational bot that retains chat history within a sliding window limit 
and supports commands (/reset, /count, bye).
"""

from langchain.chat_models import init_chat_model


def main():
    # Requirement 1: Initialize messages with system prompt
    # Why: Keeping the system prompt at index 0 ensures the model never loses its identity across conversation turns.
    messages = [
        {
            "role": "system",
            "content": "You are a friendly personal tutor. Provide concise, clear answers in 1 to 2 sentences.",
        }
    ]

    llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0.2)

    print("Tutor: Ask me anything. Commands: /reset, /count, bye")

    # Requirement 2: Interactive chat loop
    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        # Requirement 3: Command handling
        if user_input.lower() == "bye":
            print("Tutor: Goodbye!")
            break

        if user_input.lower() == "/count":
            print(f"Tutor: {len(messages)} messages in memory.")
            continue

        if user_input.lower() == "/reset":
            # Why: Re-assigning messages to only contain index 0 clears conversation history while preserving core system instructions.
            messages = [messages[0]]
            print("Tutor: Memory cleared.")
            continue

        # Append user message
        messages.append({"role": "user", "content": user_input})

        # Requirement 4: Memory trimming - keep system prompt + last 8 messages
        # Why: Sliding window memory prevents context bloat and reduces token cost over long sessions.
        messages = [messages[0]] + messages[1:][-8:]

        # Call model
        response = llm.invoke(messages)

        # Append assistant response to memory
        messages.append({"role": "assistant", "content": response.content})

        # Requirement 5: Print response and input tokens sent
        input_tokens = response.usage_metadata.get("input_tokens", 0)
        print(f"Tutor: {response.content}")
        print(f"       (tokens sent: {input_tokens})")


if __name__ == "__main__":
    main()