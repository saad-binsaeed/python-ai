"""Prompt Cleaner and Safety Sizer.

Normalizes messy user input, estimates token consumption, checks for keywords,
and formats a clean system prompt safely bounded by character limits.
"""


def main():
    raw_name = input("Your name: ")
    raw_question = input("Your question: ")

    # Cleaning whitespace and normalizing casing
    cleaned_name = raw_name.strip().title()
    cleaned_question = raw_question.strip().capitalize()

    # STRETCH GOAL: Bad word filter
    filtered_question = cleaned_question.replace("stupid", "***")

    # Calculate length metrics
    char_count = len(filtered_question)
    # Dividing by 4 to approximate token count since 1 token is roughly 4 characters in English
    estimated_tokens = round(char_count / 4)

    # Keyword detection ignoring letter casing
    # Converting string to lowercase first ensures case-insensitive matching for "python"
    mentions_python = "python" in filtered_question.lower()

    print("========================================")
    print(f"Cleaned question: {filtered_question}")
    print(f"Characters: {char_count}, about {estimated_tokens} tokens")
    print(f"Mentions Python: {mentions_python}")
    print("========================================")

    # Constructing prompt with slicing [:150] to prevent token overflow on long requests
    prompt_template = f"""You are a friendly Python tutor.
Greet {cleaned_name} by name and answer in 3 short lines.
Question: {filtered_question[:150]}"""

    print(prompt_template)

    # STRETCH GOAL: Print cost estimate formatted to 2 decimals using standard f-string specifiers
    estimated_cost = (estimated_tokens / 1000) * 0.5
    print(f"\nEstimated processing cost: {estimated_cost:.2f} PKR")


if __name__ == "__main__":
    main()