"""Smart Model Router.

Routes user prompts to local or cloud models based on security requirements,
domain specialization, token volume, and user subscription tiers.
"""


def main():
    raw_task_type = input("Task (code / private / chat): ")
    task_type = raw_task_type.strip().lower()

    tokens_input = input("Estimated tokens: ")
    estimated_tokens = int(tokens_input)

    # STRETCH GOAL: Check user tier eligibility
    is_paid_input = input("Is this a paid user? (yes/no): ").strip().lower()
    is_paid = is_paid_input == "yes"

    # Evaluates conditions sequentially to route request to optimal backend
    if task_type == "private":
        chosen_model = "llama3.2 (local, Ollama)"
        price_per_1k = 0.0  # Zero cost because execution occurs on local hardware
    elif task_type == "code":
        chosen_model = "claude (cloud, strong at code)"
        price_per_1k = 0.80
    else:
        chosen_model = "gpt-4o-mini (cloud, standard)"
        price_per_1k = 0.20

    # Token length checks & stretch tier validation
    if estimated_tokens > 4000:
        print("Warning: long request, consider shortening it.")
    elif estimated_tokens > 2000 and not is_paid:
        # Using logical 'and' to restrict long context buffers to paying users only
        print("Upgrade to send long requests.")
    else:
        print("Length is fine.")

    # Calculate final cost
    total_cost = (estimated_tokens / 1000) * price_per_1k

    print(f"Chosen model: {chosen_model}")
    print(f"Estimated cost: {total_cost:.2f} PKR")


if __name__ == "__main__":
    main()