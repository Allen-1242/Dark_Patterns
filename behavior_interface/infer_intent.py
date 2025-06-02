from .intent_rules import INTENT_RULES

def infer_expected_behavior(text, attrs, selector):
    for rule in INTENT_RULES:
        try:
            if rule["match"](text, attrs):
                return {
                    "element_text": text,
                    "element_selector": selector,
                    "element_attributes": attrs,
                    "expected_behavior": rule["expected"],
                    "click_intent": rule["intent"]
                }
        except Exception as e:
            print(f"[!] Rule failed: {e}")
            continue

    return {
        "element_text": text,
        "element_selector": selector,
        "element_attributes": attrs,
        "expected_behavior": "unknown",
        "click_intent": "unknown"
    }
