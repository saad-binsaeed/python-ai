"""
Lesson 1.8 Mini Project: Rule-Based Business Chatbot
Business: DentalCare Clinic
This script runs an interactive rule-based chatbot using a while loop, maintains user 
memory (name), enforces rule priorities, tracks performance metrics, and prepares 
a fallback prompt structure for Module 2 LLM integration.
"""

BOT = "DentalCare Assistant"

print(f"{BOT}: Welcome to DentalCare Clinic!")

# Memory: Collect and store user's name once before entering the loop
# Why: Asking once before the loop prevents prompting the user repeatedly on every turn.
name = input(f"{BOT}: May I have your name, please? ").strip().title()
if not name:
    name = "Valued Patient"

print(f"{BOT}: Hello, {name}! How can I help you today?")
print("(Type 'bye' to exit or 'human' to speak with a receptionist)\n")

# Tracking metrics
message_count = 0
unanswered_count = 0
complaint_count = 0

# Chatbot main loop
# Why: 'while True' creates an indefinite execution loop until explicitly stopped via 'break'.
while True:
    message = input(f"{name}: ").strip().lower()
    
    # Ignore empty inputs
    if not message:
        print(f"{BOT}: Please type a question so I can assist you.")
        continue

    message_count += 1

    # Exit condition
    if message == "bye" or message == "exit" or message == "quit":
        print(f"{BOT}: Goodbye, {name}! Wishing you good oral health.")
        break

    # Stretch Challenge: Human / Agent escalation keyword
    elif "agent" in message or "human" in message:
        print(f"{BOT}: Connecting you to a human receptionist right now. Please hold...")
        break

    # Priority 1: Emergency & Complaints (Handled first before general queries)
    # Why: High-priority messages containing "pain" or "complaint" must trigger immediate assistance.
    elif "emergency" in message or "pain" in message or "complaint" in message or "refund" in message:
        complaint_count += 1
        print(f"{BOT}: Urgent care notice: For severe pain or complaints, please call our emergency line at +92-300-1234567 immediately.")

    # Priority 2: Services & Pricing
    elif "price" in message or "cost" in message or "fee" in message or "treatment" in message:
        print(f"{BOT}: Consultations are 1,000 PKR. Teeth whitening is 8,000 PKR, and cleaning starts at 3,000 PKR.")

    # Priority 3: Operating Hours
    elif "hour" in message or "timing" in message or "open" in message or "schedule" in message:
        print(f"{BOT}: We are open Monday through Saturday from 10:00 AM to 8:00 PM.")

    # Priority 4: Clinic Location
    elif "where" in message or "location" in message or "address" in message:
        print(f"{BOT}: We are located at Suite 4, Medical Center, Main Boulevard, Gulberg, Lahore.")

    # Priority 5: Appointment Booking
    elif "book" in message or "appointment" in message:
        print(f"{BOT}: You can book an appointment online at dentalcare.example.com/book or reply with your preferred date.")

    # Priority 6: Exact greeting match
    # Why: Exact matching ('==') prevents false positives inside longer words like 'which' or 'this'.
    elif message == "hi" or message == "hello" or message.startswith("salam"):
        print(f"{BOT}: Hello again, {name}! How else can I assist you with your dental health?")

    # Priority 7: Fallback rule for unknown queries
    else:
        unanswered_count += 1
        llm_prompt = f"You are the virtual receptionist for DentalCare Clinic. Answer this query in 2 lines for {name}: '{message}'"
        print(f"{BOT}: I'm not entirely sure how to answer that.")
        print(f"  [Module 2 LLM Prompt Preview]: {llm_prompt}")

# End of Session Analytics
print("\n" + "=" * 45)
print("             SESSION SUMMARY                 ")
print("=" * 45)
print(f"Total Messages Processed: {message_count}")
print(f"Unanswered Queries      : {unanswered_count}")
print(f"Urgent/Complaints Handled: {complaint_count}")
print("=" * 45)