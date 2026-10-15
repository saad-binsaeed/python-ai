"""
AI Prompt Kit
-------------
Asks a local business owner 5 questions, then prints 3 ready-to-use
AI prompts (Marketing, Customer Service, Growth) that can be pasted
into Ollama, Claude or ChatGPT.

Who it is for: small business owners (bakery, clinic, salon, tuition
centre, mobile shop) who want AI help but don't know what to type.
"""

# Why input(): we need the owner's real details so the prompts are
# specific to their business instead of vague.
business_name = input("Business name: ")
business_type = input("Business type (e.g. bakery): ")
city = input("City: ")
customers = input("Main customers (e.g. students, families): ")

# Why int(): input() always returns text. Converting the budget to a
# whole number means we could do maths with it later (Module 2).
budget = int(input("Monthly budget (PKR): "))

# Why a separator variable: we build the line once and reuse it, so the
# output stays consistent and we don't retype it.
line = "=" * 41

print()
print(line)
print(f"   AI Prompt Kit for {business_name}")
print(line)

# Why each prompt names a role, task, audience and tone/number:
# specific prompts get specific answers, vague prompts get vague ones.
prompt_1 = (
    f"Write a short Instagram post for {business_name}, a {business_type} "
    f"in {city}. Target {customers}. Friendly tone, 1 call to action."
)

prompt_2 = (
    f"You are the manager of {business_name}, a {business_type} in {city}. "
    f"Write a polite reply to a customer whose order arrived late. "
    f"Apologise and offer a small discount. Keep it under 80 words."
)

prompt_3 = (
    f"Suggest 3 low-cost AI tools a {business_type} in {city} can use "
    f"to attract {customers} with a budget of {budget} PKR per month. "
    f"For each idea, give the tool name and one sentence on how to use it."
)

print()
print("[1] Marketing")
print(prompt_1)
print()
print("[2] Customer Service")
print(prompt_2)
print()
print("[3] Growth")
print(prompt_3)
print()
print(line)
print("Copy each prompt into Ollama, Claude or ChatGPT.")
print(line)