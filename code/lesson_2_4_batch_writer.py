"""
Batch Product Writer
Generates marketing descriptions for business inventory using a single model instance, 
skipping inactive items, and reporting aggregated performance metrics.
"""

import time
from langchain.chat_models import init_chat_model


def main():
    # Requirement 1: Dictionary with 5+ products/services including one with price 0
    products = {
        "Chocolate Cake": 1500,
        "Cupcake": 250,
        "Old Stock Biscuits": 0,  # Price 0 item to skip
        "Brownie": 300,
        "Donut": 200,
    }

    # Requirement 3: Instantiate model once outside the loop
    # Why: Creating the model client object once prior to the loop avoids redundant connection setups on each item.
    llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0.7)

    results = []
    total_tokens = 0
    total_seconds = 0.0

    # Requirement 2 & 5: Loop through products with accumulators
    for name, price in products.items():
        # Why: Skipping zero-priced items using `continue` avoids unnecessary AI calls and conserves computation time.
        if price == 0:
            print(f"Skipping {name} (no price)")
            continue

        prompt = (
            f"Write a single appealing, mouth-watering marketing sentence for a product named "
            f"'{name}' sold at {price} PKR at Sweet Crumbs Bakery."
        )

        messages = [
            {"role": "system", "content": "You write short, engaging product descriptions."},
            {"role": "user", "content": prompt},
        ]

        start = time.perf_counter()
        response = llm.invoke(messages)
        elapsed = time.perf_counter() - start

        tokens_used = response.usage_metadata.get("total_tokens", 0)

        # Requirement 5: Accumulate metrics
        total_tokens += tokens_used
        total_seconds += elapsed

        # Requirement 4: Store in list of dictionaries
        results.append({
            "item": name,
            "price": price,
            "text": response.content.strip(),
        })

    # Requirement 6: Print formatted menu output using enumerate
    print("=" * 50)
    for idx, item_data in enumerate(results, start=1):
        print(f"{idx}. {item_data['item']} ({item_data['price']} PKR)")
        print(f"   {item_data['text']}")
    print("=" * 50)

    # Requirement 6: Summary line
    print(f"{len(results)} descriptions, {total_tokens} tokens, {total_seconds:.1f} seconds")


if __name__ == "__main__":
    main()