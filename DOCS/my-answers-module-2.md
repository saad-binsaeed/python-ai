# Module 2, Checkpoint 1: Quick Checks Answers

## Lesson 2.1: Your First AI Call
* **Q1:** b) The model name and model_provider in init_chat_model
* **Q2:** b) reply.content (or `response.text` / `response.content` in LangChain; `reply.text` among given options)
* **Q3:** b) temperature=0.1
* **Q4:** a) Is the Ollama app running?
* **Q5:** b) The answer appears word by word as it is written, instead of all at the end
* **Q6 (Predicted Output):**
  `200 tokens in 3.5 seconds`

---

## Lesson 2.2: Chat History with Lists
* **Q1:** b) "calculator"
* **Q2:** b) None *(because .append() mutates in-place and returns None)*
* **Q3:** b) The bot does not send the earlier messages in the history, so the model never sees the order number
* **Q4:** a) To keep the system message (the bot's rules), which would otherwise be cut
* **Q5:** b) Each call gets slower and more expensive, and may overflow the context window
* **Q6 (Predicted Output):**
  `['sys', 'u2', 'a2', 'u3'] 6`

---

## Lesson 2.3: Messages are Dictionaries
* **Q1:** b) 0
* **Q2:** c) Raises KeyError
* **Q3:** b) menu["samosa"] = 60
* **Q4:** b) order["customer"]["city"]
* **Q5:** b) Put the real fees from a dictionary into the system message and tell the AI to only use them
* **Q6 (Predicted Output):**
  `{'cupcake': 7, 'brownie': 0, 'donut': 8} 3 True`

---

## Lesson 2.4: Loops that Talk
* **Q1:** b) [3, 4, 5, 6]
* **Q2:** b) for item, price in prices.items():
* **Q3:** b) 300 *(because `total = 0` resets to 0 inside every iteration of the loop)*
* **Q4:** b) continue
* **Q5:** b) The model is created once and reused for every item, instead of being created again each round
* **Q6 (Predicted Output):**
  `2: complaint`
  `3`