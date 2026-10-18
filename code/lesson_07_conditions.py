"""
Lesson 07: Control Flow and Conditions - Smart Model Router
This script routes user requests to different AI models based on the task type,
calculates estimated cost, warns about long context lengths, and enforces tier limits.
"""

# Collect and clean inputs
# Why: .strip().lower() normalizes user input so case variation doesn't break string matching.
task_type = input("Enter task type (code, private, chat): ").strip().lower()
tokens = int(input("Enter estimated tokens: "))
is_paid_input = input("Is this a paid user? (yes/no): ").strip().lower()
is_paid = is_paid_input == "yes"

# Route model and set price per 1k tokens
# Why: Control flow (if/elif/else) allows selecting specialized models and custom pricing dynamically.
if task_type == "code":
    model_name = "CodeLlama 34B"
    price_per_1k = 0.002
elif task_type == "private":
    model_name = "Ollama / Llama3 (Local)"
    price_per_1k = 0.0  # Free for local processing
elif task_type == "chat":
    model_name = "GPT-4o-mini"
    price_per_1k = 0.00015
else:
    model_name = "Default LLM"
    price_per_1k = 0.001

# Calculate total cost
estimated_cost = (tokens / 1000) * price_per_1k

# Context length check
if tokens > 4000:
    print("Warning: Token count exceeds 4000! Processing may be slower or truncated.")
else:
    print("Length is fine.")

# Stretch challenge: Check tier limits for long requests
if not is_paid and tokens > 2000:
    print("Upgrade to send long requests.")

# Display final routing results
print(f"\nSelected Model: {model_name}")
print(f"Estimated Cost: ${estimated_cost:.2f}")