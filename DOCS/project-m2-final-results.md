# AI Quality Test Results & Fixes

## Case 1: WhatsApp Import Customer Name Hallucination
* **Raw Message:** `1 pizza and 2 brownies, Model Town`
* **Initial AI Behavior:** The model extracted `customer: "Ahmed"` despite no name appearing in the message text.
* **Code Interception:** Added strict string verification checking `if cust_name.lower() not in raw_whatsapp.lower()`.
* **Result:** System flagged `CHECK: customer 'Ahmed' is not in the message (invented?)` and prevented unverified order entry.

## Case 2: Multi-Item Price Calculation Ambiguity
* **User Input:** `I want 2 cupcakes and 1 brownie`
* **Initial AI Behavior:** The LLM attempted to perform arithmetic in text, occasionally getting total PKR wrong.
* **Code Interception:** Offloaded all arithmetic to the pure Python helper `calculate_total()`.
* **Result:** Guaranteed 100% mathematical accuracy ($250 \times 2 + 300 = 800\text{ PKR}$) before requesting owner approval.