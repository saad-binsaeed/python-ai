"""
Persona Bot with Real Facts
An AI assistant configured with business facts, multiple customizable personas, 
and local lookup capabilities for exact pricing.
"""

from langchain.chat_models import init_chat_model

# Requirement 1: Business facts and prices dictionary
FACTS = {
    "business_name": "Sweet Crumbs Bakery",
    "location": "Lahore",
    "specialty": "Freshly baked artisan cakes and pastries",
    "opening_hours": "8:00 AM - 10:00 PM daily",
    "prices": {
        "cupcake": "250 PKR",
        "brownie": "300 PKR",
        "chocolate cake": "1500 PKR",
        "donut": "200 PKR",
    },
}

# Requirement 2: Personas dictionary
PERSONAS = {
    "friendly": "warm and cheerful, uses simple words",
    "formal": "professional, highly polite, and structured",
    "sales": "excited, always suggests one extra item to buy",
}

# Requirement 4: Configuration dictionary
CONFIG = {
    "model_name": "llama3.2",
    "temperature": 0.2,
    "memory_window": 8,
    "default_persona": "friendly",
}


def build_system_message(persona_key: str) -> str:
    # Requirement 3 & 5: Build system message using facts and selected persona
    # Why: Explicitly instructing the model to rely solely on provided facts prevents hallucinations regarding menu items or prices.
    persona_desc = PERSONAS.get(persona_key, PERSONAS[CONFIG["default_persona"]])
    
    facts_summary = (
        f"Business: {FACTS['business_name']} in {FACTS['location']}.\n"
        f"Specialty: {FACTS['specialty']}.\n"
        f"Hours: {FACTS['opening_hours']}.\n"
        f"Prices: {FACTS['prices']}."
    )

    return (
        f"You are an AI assistant for {FACTS['business_name']}.\n"
        f"Tone and Style: {persona_desc}.\n"
        f"Business Context:\n{facts_summary}\n"
        "STRICT RULE: Only use the business facts provided above. "
        "If asked about products or details not listed, clearly state that you do not have that information."
    )


def main():
    llm = init_chat_model(
        CONFIG["model_name"],
        model_provider="ollama",
        temperature=CONFIG["temperature"],
    )

    current_persona = CONFIG["default_persona"]
    messages = [{"role": "system", "content": build_system_message(current_persona)}]

    print("Bot ready. Commands: /persona friendly|formal|sales, /price <item>, bye")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "bye":
            print("Bot: Goodbye!")
            break

        # Requirement 5: Switch persona dynamically using .get()
        if user_input.startswith("/persona"):
            parts = user_input.split(maxsplit=1)
            persona_name = parts[1].strip().lower() if len(parts) > 1 else ""

            # Why: Using .get() with a default persona ensures invalid input falls back smoothly without raising a KeyError.
            if persona_name in PERSONAS:
                current_persona = persona_name
                messages[0]["content"] = build_system_message(current_persona)
                print(f"Bot: Style changed to: {PERSONAS[current_persona]}")
            else:
                current_persona = CONFIG["default_persona"]
                messages[0]["content"] = build_system_message(current_persona)
                print(f"Bot: Unknown persona '{persona_name}'. Reset to default: {PERSONAS[current_persona]}")
            continue

        # Requirement 6: Handle /price direct lookup without LLM call
        if user_input.startswith("/price"):
            parts = user_input.split(maxsplit=1)
            item_query = parts[1].strip().lower() if len(parts) > 1 else ""

            # Why: Direct lookup for deterministic pricing guarantees 100% accuracy and saves API tokens.
            if item_query in FACTS["prices"]:
                formatted_item = item_query.title()
                print(f"Bot: {formatted_item} costs {FACTS['prices'][item_query]}.")
            else:
                print(f"Bot: Sorry, {item_query if item_query else 'that item'} is not on our menu.")
            continue

        # AI Chat flow
        messages.append({"role": "user", "content": user_input})
        messages = [messages[0]] + messages[1:][-CONFIG["memory_window"]:]

        response = llm.invoke(messages)
        messages.append({"role": "assistant", "content": response.content})

        print(f"Bot: {response.content}")


if __name__ == "__main__":
    main()