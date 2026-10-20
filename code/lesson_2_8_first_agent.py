"""
AI Agent for Sweet Crumbs Bakery.
Uses tools to inspect pricing, check order statuses, and place human-confirmed orders.
"""

import json
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain.chat_models import init_chat_model
from pydantic import ValidationError

# Data stores
PRICES = {"chocolate cake": 1500, "cupcake": 250, "brownie": 300, "donut": 200}
ORDERS = {"A102": "Out for delivery", "A103": "Baking in oven"}


# Requirement 1: Tools with @tool(parse_docstring=True) and type hints
@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Reads the price of an item from the menu.

    Args:
        item: The name of the menu item (e.g., 'brownie', 'cupcake').
    """
    item_clean = item.lower().strip()
    if item_clean in PRICES:
        return f"{item_clean} costs {PRICES[item_clean]} PKR"
    return f"{item_clean} is not on our menu."


@tool(parse_docstring=True)
def check_order_status(order_id: str) -> str:
    """Checks the current status of an existing order.

    Args:
        order_id: The unique order identifier (e.g., 'A102').
    """
    oid = order_id.upper().strip()
    status = ORDERS.get(oid, "Order ID not found.")
    return f"Order {oid} is {status}"


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Places a new order after human confirmation.

    Args:
        item: Item name to order.
        quantity: Number of items.
        customer: Name of the customer.
    """
    item_clean = item.lower().strip()
    if item_clean not in PRICES:
        return f"Cannot place order: {item_clean} is not on our menu."

    total = PRICES[item_clean] * quantity

    # Human-in-the-loop approval requirement
    # Why: Requiring explicit CLI confirmation before executing state-changing tool actions prevents unintended purchases or writes.
    confirm = input(f"  [approve] {quantity} x {item_clean} for {customer} = {total} PKR. Place it? (yes/no) ").strip().lower()

    if confirm == "yes":
        new_id = "A104"
        ORDERS[new_id] = "Placed"
        return f"Order {new_id} placed: {quantity} x {item_clean}, total {total} PKR"
    return "Order cancelled by user."


# Requirement 2: Bind tools to model
tools_list = [get_price, check_order_status, place_order]
TOOLS = {t.name: t for t in tools_list}

llm = init_chat_model("llama3.2", model_provider="ollama", temperature=0.1)
llm_with_tools = llm.bind_tools(tools_list)

system_msg = SystemMessage(
    content="You are an helpful agent for Sweet Crumbs Bakery. Use tools to check prices, order status, or place orders."
)
messages = [system_msg]
MAX_STEPS = 5

print("Sweet Crumbs Agent: ask about prices, orders, or place an order. Type 'bye' to exit.")

while True:
    user_input = input("\nYou: ").strip()
    if not user_input or user_input.lower() == "bye":
        print("Goodbye!")
        break

    messages.append(HumanMessage(content=user_input))

    # Requirement 2 & 3: Agent reasoning loop with MAX_STEPS and fallback
    for _ in range(MAX_STEPS):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # Check if the model called any tools
        if not response.tool_calls:
            print(f"Agent: {response.content}")
            break

        for tool_call in response.tool_calls:
            t_name = tool_call["name"]
            t_args = tool_call["args"]
            t_id = tool_call["id"]

            # Handle tool execution with safety checks
            # Why: Catching KeyError and ValidationError prevents unknown or malformed model tool calls from crashing the application.
            if t_name in TOOLS:
                try:
                    res = TOOLS[t_name].invoke(t_args)
                except ValidationError as e:
                    res = f"Error: Invalid tool arguments - {str(e)}"
            else:
                res = f"Error: Tool '{t_name}' does not exist."

            # Requirement 4: Print tool calls
            print(f"  [tool] {t_name}({t_args}) -> {res}")

            messages.append(ToolMessage(content=str(res), tool_call_id=t_id))
    else:
        # Fallback if MAX_STEPS reached
        print("Agent: I'm sorry, I could not complete that request in time.")