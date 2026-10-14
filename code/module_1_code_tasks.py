# Collect user input
name = input("Your name: ").strip()
business_type = input("Business type: ").strip()
problem = input("Biggest problem: ").strip()

# Output
print(f"\nWelcome, {name}!")
print("--- Your AI Prompt ---")
print(f"Suggest 3 AI solutions for a {business_type} that struggles with {problem}.")