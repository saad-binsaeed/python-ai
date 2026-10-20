"""
AI Business Assistant for Sweet Crumbs Bakery (Module 2 Final).
A robust local AI agent that answers business queries using owner data, 
validates/places orders with mandatory human approval, processes WhatsApp messages,
and maintains persistent state safely.
"""

import json
import os
import sys
import time
import httpx
from pydantic import ValidationError

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

# ==========================================
# CONSTANTS & FILE PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESS_FILE = os.path.join(BASE_DIR, "business.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
TRANSCRIPT_FILE = os.path.join(BASE_DIR, "transcript.json")
ERRORS_FILE = os.path.join(BASE_DIR, "errors.log")

MODEL_NAME = "llama3.2"
MAX_STEPS = 5

# ==========================================
# B. HELPER FUNCTIONS
# ==========================================

def load_json(filepath: str, default_value: object = None) -> object:
    """Safely loads data from a JSON file, returning default_value if missing or damaged."""
    if not os.path.exists(filepath):
        return default_value if default_value is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as err:
        log_error(f"Failed to load {filepath}: {str(err)}")
        return default_value if default_value is not None else {}


def save_json(filepath: str, data: object) -> None:
    """Saves data to a JSON file formatted with indent=2 and ensure_ascii=False."""
    # Why: Writing plain JSON with explicit indenting ensures readable data files that can be easily edited or inspected.
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_error(error_message: str) -> None:
    """Appends an error entry with timestamp to errors.log."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(ERRORS_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {error_message}\n")


def calculate_total(items_with_qty: list, prices_dict: dict) -> int:
    """Calculates total order cost in PKR given a list of tuples/dicts and a prices mapping."""
    total = 0
    for item in items_with_qty:
        name = item.get("name", "").lower().strip()
        qty = int(item.get("quantity", 1))
        if name in prices_dict:
            total += prices_dict[name] * qty
    return total


# Assert test for calculate_total (Function requiring no AI)
assert calculate_total([{"name": "brownie", "quantity": 2}], {"brownie": 300}) == 600
assert calculate_total([{"name": "cupcake", "quantity": 1}, {"name": "donut", "quantity": 2}], {"cupcake": 250, "donut": 200}) == 650

# ==========================================
# A. INITIALIZATION & DATA LOADING
# ==========================================

# Exit gracefully if business.json is missing
if not os.path.exists(BUSINESS_FILE):
    print(f"Error: Core configuration file '{BUSINESS_FILE}' was not found. Please create it before starting.")
    sys.exit(1)

BUSINESS_DATA = load_json(BUSINESS_FILE)
PRICES = BUSINESS_DATA.get("prices", {})

# Load initial state
orders_data = load_json(ORDERS_FILE, default_value=[])
transcript_data = load_json(TRANSCRIPT_FILE, default_value=[])

# Tool Usage Counter
tool_usage_counts = {
    "get_price": 0,
    "get_info": 0,
    "order_status": 0,
    "place_order": 0,
    "cancel_order": 0,
}

# Session metrics
metrics = {
    "questions": 0,
    "answered": 0,
    "errors": 0,
    "whatsapp_imports": 0,
    "orders_placed": 0,
}

# ==========================================
# C. AGENT TOOLS
# ==========================================

@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Reads the exact price of an item from the business menu.

    Args:
        item: The name of the menu item (e.g., 'brownie', 'cupcake').
    """
    tool_usage_counts["get_price"] += 1
    cleaned = item.lower().strip()
    if cleaned in PRICES:
        return f"{cleaned.title()} costs {PRICES[cleaned]:,} PKR"
    return f"'{cleaned}' is not on our menu."


@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Reads general business details like hours, city, delivery terms, or contact info.

    Args:
        topic: Key information topic (e.g., 'hours', 'delivery', 'city', 'contact').
    """
    tool_usage_counts["get_info"] += 1
    topic_clean = topic.lower().strip()
    if topic_clean in BUSINESS_DATA:
        return f"{topic_clean}: {BUSINESS_DATA[topic_clean]}"
    return f"Information about '{topic}' is not available in our business record."


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Checks the status and details of an existing order by its Order ID.

    Args:
        order_id: The unique order ID string (e.g., 'A101').
    """
    tool_usage_counts["order_status"] += 1
    oid = order_id.upper().strip()
    current_orders = load_json(ORDERS_FILE, default_value=[])
    
    for order in current_orders:
        if order.get("id") == oid:
            return f"Order {oid} for {order['customer']} is currently '{order['status']}', total {order['total']:,} PKR"
    return f"Order ID '{oid}' was not found in our records."


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Places a new customer order after explicit owner approval in the terminal.

    Args:
        item: Menu item name to order.
        quantity: Number of items requested.
        customer: Name of the customer.
    """
    tool_usage_counts["place_order"] += 1
    item_clean = item.lower().strip()
    if item_clean not in PRICES:
        return f"Cannot place order: '{item_clean}' is not on our menu."

    item_cost = calculate_total([{"name": item_clean, "quantity": quantity}], PRICES)
    
    # Why: Mandating explicit CLI owner approval prevents the LLM from taking autonomous actions or committing real business liability.
    print(f"\n  [approve] {quantity} x {item_clean} for {customer} = {item_cost:,} PKR. Place it? (yes/no): ", end="")
    approval = input().strip().lower()

    if approval == "yes":
        current_orders = load_json(ORDERS_FILE, default_value=[])
        new_id = f"A{101 + len(current_orders)}"
        
        new_order = {
            "id": new_id,
            "customer": customer.title(),
            "items": [{"name": item_clean, "quantity": quantity}],
            "total": item_cost,
            "status": "received",
        }
        current_orders.append(new_order)
        save_json(ORDERS_FILE, current_orders)
        metrics["orders_placed"] += 1
        return f"Order {new_id} placed: {quantity} x {item_clean}, total {item_cost:,} PKR"
    
    return "Order placement was declined by the business owner."


@tool(parse_docstring=True)
def cancel_order(order_id: str) -> str:
    """Cancels an existing order after approval, provided it has not already been delivered.

    Args:
        order_id: Unique order ID to cancel (e.g., 'A101').
    """
    tool_usage_counts["cancel_order"] += 1
    oid = order_id.upper().strip()
    current_orders = load_json(ORDERS_FILE, default_value=[])

    for order in current_orders:
        if order.get("id") == oid:
            if order.get("status") == "delivered":
                return f"Cannot cancel Order {oid}: Item has already been delivered."
            
            print(f"\n  [approve] Cancel order {oid} for {order['customer']}? (yes/no): ", end="")
            confirm = input().strip().lower()
            if confirm == "yes":
                order["status"] = "cancelled"
                save_json(ORDERS_FILE, current_orders)
                return f"Order {oid} status updated to 'cancelled'."
            return f"Cancellation of Order {oid} aborted by owner."

    return f"Order ID '{oid}' not found."


# Setup Tools list & LLM binding
TOOLS_LIST = [get_price, get_info, order_status, place_order, cancel_order]
TOOLS_DICT = {t.name: t for t in TOOLS_LIST}

llm = init_chat_model(MODEL_NAME, model_provider="ollama", temperature=0.1)
llm_with_tools = llm.bind_tools(TOOLS_LIST)

SYSTEM_PROMPT = (
    f"You are the official AI assistant for {BUSINESS_DATA['business_name']}.\n"
    f"Business Details:\n- City: {BUSINESS_DATA['city']}\n- Hours: {BUSINESS_DATA['hours']}\n"
    f"- Delivery: {BUSINESS_DATA['delivery']}\n- Menu Prices: {PRICES}\n"
    "CRITICAL RULES:\n"
    "1. ALWAYS use tools to retrieve prices, check hours, look up order statuses, or place/cancel orders.\n"
    "2. NEVER guess or invent prices, order statuses, or business information.\n"
    "3. Keep answers brief, accurate, and professional."
)

# ==========================================
# E. MAIN COMMAND LOOP & AGENT EXECUTION
# ==========================================

print("=" * 60)
print(f"   {BUSINESS_DATA['business_name']} AI Business Assistant")
print("=" * 60)
print("Ask anything, or use: /import, /orders, /summary, /reset, bye\n")

while True:
    try:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd == "bye":
            print("Assistant: Goodbye! Everything is saved.")
            break

        # Reset memory command
        if cmd == "/reset":
            transcript_data = []
            save_json(TRANSCRIPT_FILE, transcript_data)
            print("Assistant: Memory cleared.\n")
            continue

        # Show active orders list
        if cmd == "/orders":
            current_orders = load_json(ORDERS_FILE, default_value=[])
            print("\nCurrent Orders on File:")
            if not current_orders:
                print("  No active orders found.")
            else:
                for idx, ord_item in enumerate(current_orders, start=1):
                    print(f"  {idx}. {ord_item['id']} | {ord_item['customer']} | {ord_item['total']:,} PKR | {ord_item['status']}")
            print()
            continue

        # Bonus +5: Daily summary
        if cmd == "/summary":
            current_orders = load_json(ORDERS_FILE, default_value=[])
            status_summary = {}
            grand_total = 0

            for ord_item in current_orders:
                st = ord_item.get("status", "unknown")
                tot = ord_item.get("total", 0)
                if st not in status_summary:
                    status_summary[st] = {"count": 0, "value": 0}
                status_summary[st]["count"] += 1
                status_summary[st]["value"] += tot
                grand_total += tot

            print("\nDaily Sales Summary:")
            for st, metrics_data in status_summary.items():
                print(f"  - Status '{st}': {metrics_data['count']} orders | Total: {metrics_data['value']:,} PKR")
            print(f"  Total Business Revenue: {grand_total:,} PKR\n")

            # Call LLM without tools for a concise summary note
            summary_prompt = f"Write a brief 2-line executive note to the owner based on these stats: {status_summary}, Total Revenue: {grand_total} PKR."
            sum_res = llm.invoke([{"role": "user", "content": summary_prompt}])
            print(f"Owner Note: {sum_res.content.strip()}\n")
            continue

        # D. /import: WhatsApp message parsing
        if cmd == "/import":
            metrics["whatsapp_imports"] += 1
            raw_whatsapp = input("Paste the WhatsApp message: ").strip()

            schema = {
                "type": "object",
                "properties": {
                    "is_order": {"type": "boolean"},
                    "customer": {"type": "string"},
                    "address": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "integer"},
                            },
                            "required": ["name", "quantity"],
                        },
                    },
                },
                "required": ["is_order", "items"],
            }

            extractor_llm = init_chat_model(MODEL_NAME, model_provider="ollama", temperature=0, format="json")
            extract_prompt = f"Extract order info from text using schema:\n'{raw_whatsapp}'\nSchema: {json.dumps(schema)}"

            print("\nProcessing WhatsApp Import...")
            response = extractor_llm.invoke([{"role": "user", "content": extract_prompt}])

            try:
                extracted_data = json.loads(str(response.content))
            except json.JSONDecodeError:
                print("  CHECK: Failed to parse AI structured response.")
                continue

            if not extracted_data.get("is_order", False) or not extracted_data.get("items"):
                print("  Not an order: needs a human reply.\n")
                continue

            # Perform strict Python checks against menu & name hallucination
            valid_items = []
            has_checks = False

            for item in extracted_data.get("items", []):
                i_name = str(item.get("name", "")).lower().strip()
                i_qty = int(item.get("quantity", 1))

                if i_name in PRICES:
                    line_total = PRICES[i_name] * i_qty
                    valid_items.append({"name": i_name, "quantity": i_qty})
                    print(f"  {i_qty} x {i_name} = {line_total:,} PKR")
                else:
                    print(f"  CHECK: '{i_name}' is not on the menu")
                    has_checks = True

            cust_name = str(extracted_data.get("customer", "Unknown")).strip()
            address = str(extracted_data.get("address", "Unknown")).strip()

            # Why: Validating whether the extracted customer name exists in raw text prevents the LLM from inventing customer identities.
            if cust_name != "Unknown" and cust_name.lower() not in raw_whatsapp.lower():
                print(f"  CHECK: customer '{cust_name}' is not in the message (invented?)")
                has_checks = True

            calc_total = calculate_total(valid_items, PRICES)
            print(f"  Customer: {cust_name}, Address: {address}")
            print(f"  Total: {calc_total:,} PKR")

            print("  [approve] Save this order? (yes/no): ", end="")
            appr = input().strip().lower()

            if appr == "yes":
                current_orders = load_json(ORDERS_FILE, default_value=[])
                new_id = f"A{101 + len(current_orders)}"
                current_orders.append({
                    "id": new_id,
                    "customer": cust_name.title(),
                    "address": address,
                    "items": valid_items,
                    "total": calc_total,
                    "status": "received",
                })
                save_json(ORDERS_FILE, current_orders)
                metrics["orders_placed"] += 1
                print(f"  Saved as Order {new_id}.\n")
            else:
                print("  Not saved.\n")
            continue

        # C. Agent Chat Execution with Tools
        metrics["questions"] += 1

        # Rebuild sliding window memory: System message + last 8 transcript entries
        agent_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for entry in transcript_data[-8:]:
            if entry["role"] == "user":
                agent_messages.append(HumanMessage(content=entry["content"]))
            elif entry["role"] == "assistant":
                agent_messages.append(AIMessage(content=entry["content"]))

        agent_messages.append(HumanMessage(content=user_input))

        # Agent Loop with MAX_STEPS
        for step in range(MAX_STEPS):
            response = llm_with_tools.invoke(agent_messages)
            agent_messages.append(response)

            if not response.tool_calls:
                # Agent completed response
                print(f"Assistant: {response.content}\n")
                metrics["answered"] += 1
                
                # Append to transcript as plain dicts
                transcript_data.append({"role": "user", "content": user_input})
                transcript_data.append({"role": "assistant", "content": str(response.content)})
                save_json(TRANSCRIPT_FILE, transcript_data)
                break

            # Process tool execution
            for tool_call in response.tool_calls:
                t_name = tool_call["name"]
                t_args = tool_call["args"]
                t_id = tool_call["id"]

                # Why: Explicitly handling invalid tool calls inside try-except blocks ensures bad model arguments do not crash the agent loop.
                if t_name in TOOLS_DICT:
                    try:
                        res = TOOLS_DICT[t_name].invoke(t_args)
                    except ValidationError as ve:
                        res = f"Error: Invalid parameters for tool '{t_name}': {str(ve)}"
                else:
                    res = f"Error: Tool '{t_name}' does not exist."

                # Print tool call execution line
                print(f"  [tool] {t_name}({t_args}) -> {res}")

                agent_messages.append(ToolMessage(content=str(res), tool_call_id=t_id))
        else:
            # Fallback if MAX_STEPS exceeded
            print("Assistant: I apologize, but I am having trouble completing that request right now.\n")

    except (httpx.ConnectError, Exception) as err:
        metrics["errors"] += 1
        log_error(f"Runtime Exception: {type(err).__name__} - {str(err)}")
        print("Assistant: I am offline or having connectivity issues right now. Please verify Ollama is running.\n")

# ==========================================
# F. SESSION REPORT
# ==========================================
current_orders_final = load_json(ORDERS_FILE, default_value=[])

print("=" * 60)
print("Session report")
print(f"Questions: {metrics['questions']} | Answered: {metrics['answered']} | Errors: {metrics['errors']}")
print(f"WhatsApp imports: {metrics['whatsapp_imports']} | Orders placed: {metrics['orders_placed']} | Orders on file: {len(current_orders_final)}")
print("Tool calls:")
for t_name, count in tool_usage_counts.items():
    print(f"  {t_name}: {count}")
print("=" * 60)