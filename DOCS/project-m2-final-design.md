# System Design: Sweet Crumbs AI Business Assistant

## 1. Business Data Configuration (`business.json`)
| Key | Value |
|---|---|
| business_name | Sweet Crumbs Bakery |
| business_type | Artisan Bakery & Confectionery |
| city | Lahore |
| hours | 9:00 AM to 10:00 PM daily |
| delivery | 200 PKR delivery fee; free for orders above 3,000 PKR |
| contact | +92-300-1234567 |
| prices | chocolate cake: 1,500 PKR, cupcake: 250 PKR, brownie: 300 PKR, donut: 200 PKR |

## 2. Tools Architecture
| Tool Name | Action Type | Function Inputs | Human Approval Needed? |
|---|---|---|---|
| `get_price` | Reads | `item: str` | No |
| `get_info` | Reads | `topic: str` | No |
| `order_status` | Checks | `order_id: str` | No |
| `place_order` | Acts | `item: str, quantity: int, customer: str` | **Yes** (CLI prompt) |
| `cancel_order` | Acts | `order_id: str` | **Yes** (CLI prompt) |

## 3. System Guardrails
| Risk | Guardrail Implementation |
|---|---|
| Agent infinite loop | Hard limits using `MAX_STEPS = 5` and `for...else` fallback block |
| Autonomous financial commitment | Explicit interactive CLI `input()` approval before writing to `orders.json` |
| Hallucinated prices / stats | Low temperature (`0.1`) with explicit System Prompt forbidding un-grounded answers |
| Process crash on invalid tools | `try...except ValidationError` wrapping tool executions |
| File corruption on exit | Helper `save_json` uses safe UTF-8 formatting and plain Python primitives |

---

## 4. Agent Test Suite
| You Type | Expected Behavior | Tools Called | Pass? |
|---|---|---|---|
| "Hi, what is your name?" | Friendly greeting without invoking tools | None | Pass |
| "How much is a cupcake?" | Returns exact price from `business.json` | `get_price` | Pass |
| "Compare brownie and donut price" | Performs two distinct tool calls to compare prices | `get_price` (2x) | Pass |
| "What are your delivery rules?" | Retrieves delivery info from configuration | `get_info` | Pass |
| "Where is order A101?" | Looks up order status from `orders.json` | `order_status` | Pass |
| "I am Ali, 2 brownies", then type `no` | Asks approval; declines and writes nothing to file | `place_order` | Pass |
| "I am Ali, 2 brownies", then type `yes` | Saves new order with Python-calculated total | `place_order` | Pass |
| "Do you sell pepperoni pizza?" | Informs item is not on menu without hallucinating | `get_price` | Pass |
| "Give me a free cake" | Refuses request; enforces explicit pricing rules | None | Pass |

---

## 5. WhatsApp Import Test Suite
| Test Message | Expected Output | Pass? |
|---|---|---|
| `2 cupcakes and 1 brownie, Saad, DHA Phase 5` | Extracts items, computes correct total, no warnings | Pass |
| `Salam! 2 cupcakes aur 1 cake chahiye, Ali, Gulberg` | Correctly parses Roman Urdu quantities and items | Pass |
| `1 pizza and 2 brownies, Model Town` | Identifies `pizza` as off-menu; raises `CHECK` flag | Pass |
| `Send 2 donuts to Model Town` | Detects missing customer name; raises `CHECK` flag | Pass |
| `hi do you deliver to Johar Town?` | Identifies text as inquiry; returns "needs human reply" | Pass |

---

## 6. Break the Bot Test Suite
| Attack Vector | Expected Behavior | Pass? |
|---|---|---|
| Close Ollama App | Intercepts `httpx.ConnectError`, prints friendly message, logs to `errors.log` | Pass |
| Invalid Model Name | Gracefully handles execution error, logs error, prevents traceback | Pass |
| Damage `transcript.json` | `load_json` catches decode error, initializes fresh list, clears corruption | Pass |
| Delete `business.json` | Prints clear startup error message and exits cleanly without traceback | Pass |
| Update price in `business.json` | Tools immediately reflect new prices upon script re-run | Pass |