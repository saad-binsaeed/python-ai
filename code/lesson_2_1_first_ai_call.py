"""
Lesson 2.1: Core Python for Your First LLM Apps - AI Tutor
This script interacts with a local AI model (Ollama) via LangChain.
It collects a user's topic and expertise level, configures system roles and
temperature controls, and extracts response metadata like token counts and duration.
"""

from langchain.chat_models import init_chat_model

# 1. Collect and clean inputs
# Why: .strip() prevents leading or trailing whitespace from cluttering system prompts.
topic = input("Enter a topic to learn about: ").strip()
level = input("Enter your level (beginner or expert): ").strip().lower()

# Fallback for empty inputs
if not topic:
    topic = "Python Programming"
if level not in ["beginner", "expert"]:
    level = "beginner"

# 2. Build system prompt based on user expertise
system_message = (
    f"You are a helpful AI Tutor. Explain the topic to a {level}. "
    f"Keep your explanation concise, engaging, and limited to 3-4 sentences."
)

# 3. Initialize the model
# Why: Creating the model instance once allows re-use and sets fixed generation parameters like temperature.
# Note: Using temperature=0.2 for focused, consistent educational responses.
llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0.2)

print(f"\n[Generating explanation for '{topic}' as an {level}...]\n")

# 4. Invoke the model
response = llm.invoke([
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"Explain: {topic}"}
])

# 5. Extract and print the answer
print("--- AI Tutor Answer ---")
print(response.text)
print("-" * 25)

# 6. Extract and format response metadata
# Why: Tracking tokens and duration helps monitor API resource usage and cost estimation.
output_tokens = response.usage_metadata.get("total_tokens", 0)
duration_ns = response.response_metadata.get("total_duration", 0)
duration_sec = duration_ns / 1_000_000_000

print(f"Metrics: {output_tokens} total tokens used | Response time: {duration_sec:.1f} seconds")