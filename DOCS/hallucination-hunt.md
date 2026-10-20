# Hallucination Hunt Results

## Observations
1. **Unlisted Items (e.g., Pizza):** Model structured 'pizza' into the JSON item array. Python checks successfully flagged it as off-menu and prevented fake price totals.
2. **Missing Names:** For messages without an explicit name, the model sometimes returned "Not specified" or guessed a common name. Python strict string checking validated if the name was in the original text.
3. **Roman Urdu Processing:** Successfully parsed quantities ("2 cupcakes aur 1 chocolate cake") into integer counts.