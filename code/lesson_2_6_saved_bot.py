"""
Saved Bot with Persistent Memory and Error Logging.
Loads facts from faq.json, maintains state across runs via chat_history.json,
and safely catches connection/response errors into errors.log.
"""

import json
import os
import sys
import httpx
from langchain.chat_models import init_chat_model

# Requirement 2: Load facts from faq.json
faq_path = os.path.join(os.path.dirname(__file__), "faq.json")
if not os.path.exists(faq_path):
    print("Error: Required configuration file 'faq.json' was not found. Exiting.")
    sys.exit(1)

with open(faq_path, "r", encoding="utf-8") as f:
    facts = json.load(f)

system_prompt = (
    f"You are the assistant for {facts['business_name']} in {facts['city']}.\n"
    f"Hours: {facts['hours']}. Delivery: {facts['delivery']}.\n"
    f"Prices: {facts['prices']}.\n"
    "Only answer based on these facts. If you do not know, say so."
)

# Requirement 3: Load chat history with corruption handling
history_path = os.path.join(os.path.dirname(__file__), "chat_history.json")
messages = [{"role": "system", "content": system_prompt}]

if os.path.exists(history_path):
    # Why: Checking for file existence and JSON syntax errors prevents application crashes when loading saved chat history.
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            saved_messages = json.load(f)
            if isinstance(saved_messages, list) and len(saved_messages) > 0:
                messages = saved_messages
                # Verify system message is preserved at index 0
                messages[0] = {"role": "system", "content": system_prompt}
                print(f"Loaded {len(messages) - 1} old messages.")
            else:
                print("History file was damaged. Starting a fresh chat.")
    except (json.JSONDecodeError, Exception):
        print("History file was damaged. Starting a fresh chat.")

llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0.1)

print(f"{facts['business_name']} Bot: Ask me anything. Commands: /reset, bye")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "bye":
        print("Bot: Goodbye! Your chat is saved.")
        break

    if user_input.lower() == "/reset":
        messages = [{"role": "system", "content": system_prompt}]
        if os.path.exists(history_path):
            os.remove(history_path)
        print("Bot: Memory cleared.")
        continue

    # Requirement 4 & 5: Append message, invoke with error safety, save history
    messages.append({"role": "user", "content": user_input})
    messages = [messages[0]] + messages[1:][-8:]

    try:
        response = llm.invoke(messages)
        messages.append({"role": "assistant", "content": str(response.content)})

        # Why: Saving plain dictionaries directly to JSON after every turn guarantees state persistence even if the process is killed.
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

        print(f"Bot: {response.content}")

    except (httpx.ConnectError, Exception) as err:
        # Why: Removing the failed user prompt from history keeps memory clean and prevents sending bad context in subsequent turns.
        messages.pop()  # Remove unhandled user message
        print("Bot: I am offline right now. Please open the Ollama app and try again.")

        log_path = os.path.join(os.path.dirname(__file__), "errors.log")
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"Error: {type(err).__name__} - {str(err)}\n")