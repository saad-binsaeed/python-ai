"""
Order Extractor with Structured JSON Output and Validation.
Extracts orders from raw WhatsApp messages, calculates strict totals in Python,
and outputs verified data to orders.json.
"""

import json
import os
from langchain.chat_models import init_chat_model

# Requirement 1: Prices dictionary
PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
    "donut": 200,
}

# Requirement 2: Messy test messages covering all 5 cases
MESSAGES = [
    "Salam! 2 cupcakes aur 1 chocolate cake chahiye. Ali, house 12 Gulberg",  # Roman Urdu multi-item
    "1 pizza and 2 brownies, Bilal, Model Town",                           # Item not on menu
    "Hi, I want 1 chocolate cake. Saad, DHA Phase 5",                      # Normal order
    "hi do you deliver to Johar Town?",                                    # Not an order
    "2 brownies please, Sara, Cavalry Ground",                             # Single item order
]

# Requirement 3: JSON schema definition
schema = {
    "type": "object",
    "properties": {
        "is_order": {"type": "boolean"},
        "customer": {"type": "string"},
        "address": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "integer"},
                },
                "required": ["name", "quantity"],
            },
        },
    },
    "required": ["is_order", "items"],
}

# Why: Setting format="json" and temperature=0 enforces deterministic, schema-compliant JSON outputs from the LLM.
llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0, format="json")

saved_orders = []
total_business_value = 0
total_checks = 0
valid_order_count = 0

for msg in MESSAGES:
    print(f"\nMessage: {msg}")
    prompt = f"Extract order details from this message using the required JSON schema:\n'{msg}'\nSchema: {json.dumps(schema)}"

    response = llm.invoke([{"role": "user", "content": prompt}])

    # Requirement 4: Safe JSON parsing
    try:
        data = json.loads(str(response.content))
    except json.JSONDecodeError:
        print("  Error: AI output was not valid JSON.")
        continue

    # Read keys safely with .get()
    is_order = data.get("is_order", False)
    items = data.get("items", [])
    customer = data.get("customer", "Unknown")
    address = data.get("address", "Unknown")

    if not is_order or not items:
        print("  Not an order: needs a human reply.")
        continue

    valid_order_count += 1
    order_total = 0

    # Why: Performing price calculations in Python rather than relying on LLM math guarantees 100% financial accuracy.
    for item in items:
        item_name = str(item.get("name", "")).lower().strip()
        qty = int(item.get("quantity", 1))

        if item_name in PRICES:
            line_total = PRICES[item_name] * qty
            order_total += line_total
            print(f"  {qty} x {item_name} = {line_total} PKR")
        else:
            print(f"  CHECK: '{item_name}' is not on the menu")
            total_checks += 1

    # Verify if customer name is actually in original string
    if customer != "Unknown" and customer.lower() not in msg.lower():
        print(f"  CHECK: Customer name '{customer}' may be hallucinated.")
        total_checks += 1

    print(f"  Customer: {customer}, Address: {address}")
    print(f"  Total: {order_total} PKR")

    total_business_value += order_total
    saved_orders.append({
        "customer": customer,
        "address": address,
        "items": items,
        "total_pkr": order_total,
    })

# Requirement 5: Save valid orders to JSON
orders_path = os.path.join(os.path.dirname(__file__), "orders.json")
with open(orders_path, "w", encoding="utf-8") as f:
    json.dump(saved_orders, f, indent=2)

# Requirement 6: Print summary report
print("\n" + "=" * 50)
print(f"Orders found: {valid_order_count} | Total value: {total_business_value:,} PKR | Checks: {total_checks}")
print(f"Saved {len(saved_orders)} orders to orders.json")