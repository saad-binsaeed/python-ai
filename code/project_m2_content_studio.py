"""
AI Content Studio for Sweet Crumbs Bakery
A complete local AI marketing tool built for small business owners.
Handles batch menu generation, social media post streaming, deterministic
price lookups, and grounded customer support chat with sliding window memory.
"""

import time
from langchain.chat_models import init_chat_model

# ==========================================
# A. SETUP AND DATA
# ==========================================

# Config dictionary controlling model options and memory limit
CONFIG = {
    "model_name": "llama3.2",
    "max_messages": 8,
    "cloud_cost_per_1k_tokens": 0.00015,  # Example cost estimate: $0.00015 per 1,000 tokens
}

# Facts dictionary with 5+ keys and nested prices (including price 0 item)
FACTS = {
    "business_name": "Sweet Crumbs Bakery",
    "city": "Lahore",
    "hours": "9:00 AM to 10:00 PM daily",
    "delivery": "200 PKR delivery fee; free delivery for orders above 3,000 PKR",
    "specialty": "Freshly baked artisan cakes, fudgy brownies, and handmade pastries",
    "prices": {
        "chocolate cake": 1500,
        "cupcake": 250,
        "brownie": 300,
        "mango tart": 0,  # Price 0 item (coming soon)
    },
}

# Tones dictionary with 3 distinct styles
TONES = {
    "fun": "playful and full of energy, short sentences with an enthusiastic tone",
    "premium": "elegant and calm, focused on craftsmanship, high quality, and luxury",
    "urgent": "fast-paced, high energy, highlighting limited quantities or fresh batches",
}

# Two models created ONCE at the top
# Why: Reusing two static model instances with appropriate temperatures optimizes system memory and ensures precise grounding for chat versus high variety for marketing copy.
llm_precise = init_chat_model(CONFIG["model_name"], model_provider="ollama", temperature=0.1)
llm_creative = init_chat_model(CONFIG["model_name"], model_provider="ollama", temperature=0.7)

# Build system prompt grounding the bot strictly in business facts
# Why: Injecting deterministic business facts into the system message prevents hallucinations and ensures the model explicitly admits when information is missing.
system_prompt = (
    f"You are the official AI assistant for {FACTS['business_name']} located in {FACTS['city']}.\n"
    f"Operating Hours: {FACTS['hours']}.\n"
    f"Delivery Policy: {FACTS['delivery']}.\n"
    f"Specialty: {FACTS['specialty']}.\n"
    f"Available Menu Prices: {FACTS['prices']}.\n"
    "STRICT GROUNDING RULE: Answer customer questions using ONLY the facts above. "
    "If a customer asks about items, services, or details not listed in the facts (such as pizza or savory food), "
    "politely inform them that you do not sell or provide that service."
)

# Chat memory list initialized with system prompt at index 0
messages = [{"role": "system", "content": system_prompt}]

# Session report accumulators
count_chat = 0
count_menu = 0
count_post = 0
count_price = 0
total_tokens = 0
total_seconds = 0.0

# ==========================================
# B. THE COMMAND LOOP
# ==========================================

print("=" * 50)
print(f"   {FACTS['business_name']} AI Content Studio")
print("=" * 50)
print("Commands: /menu, /post <tone>, /price <item>, /reset, bye\n")

while True:
    raw_input = input("You: ").strip()

    # Rule 9: Skip empty inputs
    if not raw_input:
        continue

    user_cmd = raw_input.lower()

    # Rule 9: Exit command
    if user_cmd == "bye":
        print("Studio: Goodbye!")
        break

    # Reset command
    if user_cmd == "/reset":
        messages = [messages[0]]
        print("Studio: Memory cleared.")
        continue

    # ==========================================
    # C. /menu: BATCH DESCRIPTIONS
    # ==========================================
    if user_cmd == "/menu":
        count_menu += 1
        menu_items = []

        print("\n" + "-" * 50)
        # Why: Iterating over facts directly and checking for zero-priced items prevents wasted LLM inference costs on unreleased items.
        for name, price in FACTS["prices"].items():
            if price == 0:
                print(f"Studio: Skipping {name.title()} (coming soon)")
                continue

            prompt = (
                f"Write a mouth-watering, one-sentence description for {name.title()} "
                f"sold at {price} PKR by {FACTS['business_name']} in {FACTS['city']}."
            )

            start = time.perf_counter()
            response = llm_creative.invoke([{"role": "user", "content": prompt}])
            elapsed = time.perf_counter() - start

            tokens = response.usage_metadata.get("total_tokens", 0)
            total_tokens += tokens
            total_seconds += elapsed

            menu_items.append({
                "name": name.title(),
                "price": price,
                "description": response.content.strip(),
            })

        print("-" * 50)
        for idx, item in enumerate(menu_items, start=1):
            print(f"{idx}. {item['name']} ({item['price']:,} PKR)")
            print(f"   {item['description']}")
        print("-" * 50)

        # Bonus +5: Menu cost estimate
        menu_tokens_est = sum(len(item["description"].split()) for item in menu_items) * 2  # Approx token count display
        cost_est = (total_tokens / 1000) * CONFIG["cloud_cost_per_1k_tokens"]
        print(f"Estimated equivalent cloud API cost: ${cost_est:.4f}\n")
        continue

    # ==========================================
    # D. /post <tone>: STREAMED SOCIAL MEDIA POST
    # ==========================================
    if user_cmd.startswith("/post"):
        count_post += 1
        parts = raw_input.split(maxsplit=1)
        selected_tone = parts[1].strip().lower() if len(parts) > 1 else "fun"

        # Why: Using .get() with a default tone prevents KeyError exceptions when users provide unsupported tone names.
        tone_description = TONES.get(selected_tone, TONES["fun"])

        post_prompt = (
            f"Write a short, engaging Instagram post for {FACTS['business_name']}.\n"
            f"Tone: {tone_description}.\n"
            f"Key facts to include: Specialty ({FACTS['specialty']}), City ({FACTS['city']}), Hours ({FACTS['hours']})."
        )

        print(f"\nStudio ({selected_tone} tone - streaming):")
        start = time.perf_counter()
        
        full_post_text = ""
        # Stream output word by word / chunk by chunk
        for chunk in llm_creative.stream([{"role": "user", "content": post_prompt}]):
            content = chunk.content
            print(content, end="", flush=True)
            full_post_text += content
        print("\n")
        
        elapsed = time.perf_counter() - start
        total_seconds += elapsed

        # Bonus +5: Post in two languages (Roman Urdu translation)
        print("Studio (Roman Urdu Version):")
        translation_prompt = f"Translate the following marketing post into natural Roman Urdu:\n{full_post_text}"
        trans_response = llm_precise.invoke([{"role": "user", "content": translation_prompt}])
        print(f"{trans_response.content.strip()}\n")

        total_tokens += trans_response.usage_metadata.get("total_tokens", 0)
        continue

    # ==========================================
    # E. /price <item>: DETERMINISTIC PRICE LOOKUP
    # ==========================================
    if user_cmd.startswith("/price"):
        count_price += 1
        parts = raw_input.split(maxsplit=1)
        query_item = parts[1].strip().lower() if len(parts) > 1 else ""

        # Deterministic dictionary lookup without AI call
        if query_item in FACTS["prices"]:
            price_val = FACTS["prices"][query_item]
            if price_val == 0:
                print(f"Studio: {query_item.title()} is coming soon.")
            else:
                print(f"Studio: {query_item.title()} costs {price_val:,} PKR.")
        else:
            print(f"Studio: Sorry, {query_item if query_item else 'that item'} is not on our menu.")
        print()
        continue

    # ==========================================
    # E. CHAT WITH MEMORY
    # ==========================================
    count_chat += 1
    messages.append({"role": "user", "content": raw_input})

    # Memory trimming: Keep system message + last max_messages
    messages = [messages[0]] + messages[1:][-CONFIG["max_messages"]:]

    start = time.perf_counter()
    response = llm_precise.invoke(messages)
    elapsed = time.perf_counter() - start

    messages.append({"role": "assistant", "content": response.content})

    input_tokens = response.usage_metadata.get("input_tokens", 0)
    total_tokens += response.usage_metadata.get("total_tokens", 0)
    total_seconds += elapsed

    print(f"Studio: {response.content}")
    print(f"        (memory: {len(messages)} messages, {input_tokens} tokens sent)\n")

# ==========================================
# F. SESSION REPORT
# ==========================================
print("=" * 50)
print("Session report")
print(f"Chat answers: {count_chat} | Menu descriptions: {count_menu} | Posts: {count_post} | Price answers: {count_price}")
print(f"AI usage: {total_tokens:,} tokens in {total_seconds:.1f} seconds")
print("=" * 50)