"""
Lesson 05: Variables, Data Types, and Type Conversion
This script defines an AI Model Profile Card using four primary Python data types,
prints their types, and calculates estimated API costs based on user input.
"""

# Store model profile using str, int, float, and bool
# Why: Variables allow us to organize and reuse structured configuration data.
model_name = "llama3"
context_window = 128000
price_per_1k_tokens = 0.00015
runs_locally = True

# Display model details and their respective data types
print("--- AI Model Profile Card ---")
print(f"Model Name: {model_name} | Type: {type(model_name)}")
print(f"Context Window: {context_window} tokens | Type: {type(context_window)}")
print(f"Price per 1K Tokens: ${price_per_1k_tokens} | Type: {type(price_per_1k_tokens)}")
print(f"Runs Locally: {runs_locally} | Type: {type(runs_locally)}")
print("-" * 30)

# Calculate single chat cost from user input
# Why: User input is collected as a string, so int() converts it to perform mathematical operations.
tokens_used = int(input("How many tokens does a chat use? "))
estimated_cost = (tokens_used / 1000) * price_per_1k_tokens

print(f"\nEstimated cost for this chat: ${estimated_cost:.2f}")

# Stretch: Monthly cost calculation
chats_per_day = int(input("How many chats per day? "))
monthly_cost = estimated_cost * chats_per_day * 30

print(f"Estimated monthly cost (30 days): ${monthly_cost:.2f}")