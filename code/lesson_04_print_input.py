
"""
Lesson 04: User Input and AI Prompt Building

This program asks the user for their name, business type, and
one business problem, then builds and prints an AI prompt.
"""

# Why: input() collects information directly from the user.
name = input("Enter your name: ").strip()
business = input("Enter your business type (e.g., bakery): ").strip()
problem = input("Enter one problem your business faces: ").strip()

# Why: an f-string inserts user-provided values into the prompt.
prompt = f"Suggest 3 AI solutions for a {business} that struggles with {problem}."

print(f"\nWelcome, {name}!")
print("Final prompt:")
print(prompt)
