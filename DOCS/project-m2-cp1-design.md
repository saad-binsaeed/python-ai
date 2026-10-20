# Project Design: Sweet Crumbs AI Content Studio

## 1. Facts Data Structure
| Key | Value |
|---|---|
| name | Sweet Crumbs Bakery |
| city | Lahore |
| hours | 9:00 AM to 10:00 PM daily |
| delivery | 200 PKR delivery fee; free for orders above 3,000 PKR |
| specialty | Freshly baked artisan cakes, fudgy brownies, and handmade pastries |
| prices | chocolate cake: 1,500 PKR, cupcake: 250 PKR, brownie: 300 PKR, mango tart: 0 PKR (coming soon) |

## 2. Tones Configuration
| Tone | Description sent to the AI |
|---|---|
| fun | playful and full of energy, short sentences with an enthusiastic tone |
| premium | elegant and calm, focused on craftsmanship, high quality, and luxury |
| urgent | fast-paced, high energy, highlighting limited quantities or fresh batches |

## 3. Model Routing Strategy
| Job | Model and Temperature | Why |
|---|---|---|
| Menu descriptions | `llm_creative` (temp: 0.7) | Marketing text requires creative word choice and varied phrasing across products. |
| Social media posts | `llm_creative` (temp: 0.7) | Generates dynamic, engaging, and varied social posts matching selected brand tone. |
| Customer chat | `llm_precise` (temp: 0.1) | Low temperature minimizes hallucinations and strictly enforces facts-grounded responses. |
| Roman Urdu translation | `llm_precise` (temp: 0.1) | Translation requires exact linguistic mapping and factual adherence to original post text. |

## 4. Feature Test Suite Results
| You type | Expected behavior | Pass? |
|---|---|---|
| `/menu` | Price-0 item skipped, numbered menu printed with formatted prices | Pass |
| `/post fun` | Streams post word-by-word in an energetic style | Pass |
| `/post pirate` | Falls back gracefully to default tone (`fun`) without raising KeyError | Pass |
| `/price CUPCAKE` | Case-insensitive lookup returning "Cupcake costs 250 PKR." | Pass |
| `/price mango tart` | Returns "Mango Tart is coming soon." | Pass |
| `/price pizza` | Returns "Sorry, pizza is not on our menu." without crashing | Pass |
| `My name is Ali` then `What is my name?` | Recalls name correctly from sliding window chat memory | Pass |
| `/reset` then `What is my name?` | Clears memory and politely indicates it does not know the user's name | Pass |
| Press Enter (empty text) | Ignores empty input and re-prompts without calling LLM | Pass |
| `bye` | Terminates session loop and displays full Session Report | Pass |