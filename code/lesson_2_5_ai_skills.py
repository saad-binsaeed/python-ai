"""
AI Skills Toolkit for Sweet Crumbs Bakery.
Provides reusable AI-powered marketing functions (summarize, translate, reply_to_review)
and pure utility functions with usage tracking.
"""

from langchain.chat_models import init_chat_model

# Requirement 1: Create models once at the top
# Why: Initializing model instances once at startup avoids redundant HTTP setup overhead on every skill call.
llm_precise = init_chat_model("llama3.2", model_provider="ollama", temperature=0.1)
llm_creative = init_chat_model("llama3.2", model_provider="ollama", temperature=0.7)


# Requirement 2: Wrapper function ask_ai
def ask_ai(prompt: str, system: str = "You are a helpful assistant.", creative_mode: bool = False) -> str:
    """Dispatches a prompt to either precise or creative LLM and returns text response."""
    # Why: Centralizing model selection in ask_ai reduces code duplication across all individual skill functions.
    model = llm_creative if creative_mode else llm_precise
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    response = model.invoke(messages)
    return str(response.content).strip()


# Requirement 3 & 4: Skills with type hints, docstrings, and a default parameter
def summarize_text(text: str) -> str:
    """Summarizes customer feedback or long notes into one concise sentence."""
    system = "You are an assistant for Sweet Crumbs Bakery. Summarize the text in one concise sentence."
    return ask_ai(text, system=system, creative_mode=False)


def translate_text(text: str, language: str = "Urdu") -> str:
    """Translates text into the specified target language (defaults to Urdu)."""
    system = f"You are a professional translator. Translate the text into {language} accurately."
    return ask_ai(text, system=system, creative_mode=False)


def reply_to_review(review: str) -> str:
    """Generates a polite, customer-service reply to a bakery review."""
    system = (
        "You are a friendly customer success manager for Sweet Crumbs Bakery in Lahore. "
        "Write a warm, professional reply in 2 sentences."
    )
    return ask_ai(review, system=system, creative_mode=True)


# Requirement 5: Non-AI function with assert tests
def estimate_tokens(text: str) -> int:
    """Estimates the number of tokens in a string using a standard word-count multiplier."""
    # Why: Providing pure Python utilities allows fast local estimations without spending API time or tokens.
    words = text.split()
    return int(len(words) * 1.3)


# Assert tests for non-AI function
assert estimate_tokens("hello world") == 2, f"Expected 2, got {estimate_tokens('hello world')}"
assert estimate_tokens("Sweet Crumbs Bakery Lahore") == 5, f"Expected 5, got {estimate_tokens('Sweet Crumbs Bakery Lahore')}"


def main():
    # Requirement 6: Menu loop and usage counter
    usage = {"summarize": 0, "translate": 0, "reply": 0}

    print("Sweet Crumbs AI Toolkit. Commands: /summarize, /translate, /reply, bye")

    while True:
        cmd = input("\nCommand: ").strip().lower()

        if cmd == "bye":
            break

        if cmd == "/summarize":
            text = input("Text to summarize: ").strip()
            if text:
                summary = summarize_text(text)
                usage["summarize"] += 1
                print(f"AI: {summary}")

        elif cmd == "/translate":
            text = input("Text to translate: ").strip()
            lang = input("Language (Enter for Urdu): ").strip()
            if text:
                result = translate_text(text, language=lang) if lang else translate_text(text)
                usage["translate"] += 1
                print(f"AI: {result}")

        elif cmd == "/reply":
            review = input("Customer review: ").strip()
            if review:
                reply = reply_to_review(review)
                usage["reply"] += 1
                tokens = estimate_tokens(review)
                print(f"AI: {reply}")
                print(f"    (review was about {tokens} tokens)")

        else:
            print("Unknown command. Try /summarize, /translate, /reply or bye.")

    # Requirement 6: Print usage counts with a for loop
    print("\nSkills used today:")
    for skill_name, count in usage.items():
        print(f"  {skill_name}: {count}")


if __name__ == "__main__":
    main()