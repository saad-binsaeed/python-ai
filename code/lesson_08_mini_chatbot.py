"""City Care Clinic Helper Bot.

Automates common patient customer support interactions, routes urgent human escalation 
or complaints, and logs unhandled questions for downstream LLM prompt synthesis.
"""


def main():
    print("City Care Bot: Hi! Ask about timings, fees, location or appointments. Type 'bye' to exit.")

    raw_user_name = input("City Care Bot: What is your name? ")
    user_name = raw_user_name.strip().title()

    total_messages = 0
    unanswered_count = 0
    complaint_count = 0  # STRETCH GOAL: Tracking total complaints received

    # Main infinite loop maintains active session until explicitly broken
    while True:
        user_input = input(f"{user_name}: ")
        cleaned_input = user_input.strip().lower()

        # Terminal condition check
        if cleaned_input == "bye":
            print(f"City Care Bot: Take care, {user_name}!")
            break

        total_messages += 1

        # Priority Rule 1: Complaint & escalation rule must come first to handle unhappy customers immediately
        if "late" in cleaned_input or "complaint" in cleaned_input or "delay" in cleaned_input:
            complaint_count += 1
            print("City Care Bot: Sorry about that. The clinic manager will call you today.")

        # STRETCH GOAL: Agent / Human handoff trigger
        elif "agent" in cleaned_input or "human" in cleaned_input:
            print("City Care Bot: Connecting you to a human agent...")
            break

        # Standard Intent Handling
        # Using exact match / startswith checks for short phrases to prevent partial false positives (e.g. 'hi' inside 'history')
        elif cleaned_input in ["hi", "hello", "hey"] or cleaned_input.startswith("hi "):
            print(f"City Care Bot: Hello {user_name}! How can I help you today?")
        elif "timing" in cleaned_input or "hours" in cleaned_input or "open" in cleaned_input:
            print("City Care Bot: We are open 10 am to 8 pm, Monday to Saturday.")
        elif "fee" in cleaned_input or "cost" in cleaned_input or "charge" in cleaned_input:
            print("City Care Bot: Consultation fee is 2,000 PKR.")
        elif "location" in cleaned_input or "address" in cleaned_input or "where" in cleaned_input:
            print("City Care Bot: We are located at Plot 12-C, Main Boulevard, Gulberg III, Lahore.")
        elif "appointment" in cleaned_input or "book" in cleaned_input:
            print("City Care Bot: To book an appointment, call us at 042-111-222-333.")

        # Fallback Handler: Logs unhandled queries and formats system prompt for Module 2 LLM transition
        else:
            unanswered_count += 1
            ai_prompt = (
                f"You are the friendly assistant of City Care Clinic. "
                f"Answer in 2 lines: {user_input.strip()}"
            )
            print(f"City Care Bot: I am not sure yet. In Module 2, an AI will answer: {ai_prompt}")

    print("========================================")
    print(f"Chat summary: {total_messages} messages, {unanswered_count} unanswered, {complaint_count} complaints.")


if __name__ == "__main__":
    main()