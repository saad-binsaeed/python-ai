"""
Lesson 06: Strings and Prompts - Prompt Cleaner
This script collects user input, cleans string formatting, calculates character
and token counts, checks for target keywords, censors flagged terms, and formats
a clean multi-line f-string AI prompt.
"""

# Collect user input
raw_name = input("Enter your name: ")
raw_question = input("Enter your question: ")

# Clean string inputs
# Why: .strip() removes whitespace, .title() capitalizes each word in a name,
# and .capitalize() ensures the sentence starts with an uppercase letter.
clean_name = raw_name.strip().title()
clean_question = raw_question.strip().capitalize()

# Stretch: Replace bad/flagged words before building the prompt
clean_question = clean_question.replace("stupid", "***").replace("dumb", "***")

# Calculate character and estimated token counts
char_count = len(clean_question)
# Why: 1 token is roughly equivalent to 4 characters in standard LLM tokenization.
estimated_tokens = round(char_count / 4)

# Check if the question mentions "python" (case-insensitive)
mentions_python = "python" in clean_question.lower()

# Estimate cost assuming $0.00015 per 1,000 tokens (Stretch challenge)
estimated_cost = (estimated_tokens / 1000) * 0.00015

# Build a multi-line f-string prompt limiting the question to 150 characters
formatted_prompt = f"""--- Cleaned Prompt Output ---
Hello, {clean_name}!

Here is your sanitized request:
"{clean_question[:150]}"

--- Details ---
* Character Count: {char_count}
* Estimated Tokens: {estimated_tokens}
* Mentions Python: {mentions_python}
* Estimated Cost: ${estimated_cost:.2f}
"""

print(formatted_prompt)