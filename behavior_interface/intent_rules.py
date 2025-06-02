# Define intent rules using lambda matchers

INTENT_RULES = [
    {
        "match": lambda text, attrs: "quick add" in text.lower(),
        "intent": "add_to_cart",
        "expected": "inline add to cart"
    },
    {
        "match": lambda text, attrs: "subscribe" in text.lower(),
        "intent": "subscribe_flow",
        "expected": "show subscription options"
    },
    {
        "match": lambda text, attrs: "buy now" in text.lower(),
        "intent": "checkout",
        "expected": "redirect to checkout"
    },
    {
        "match": lambda text, attrs: "start free trial" in text.lower(),
        "intent": "subscription_onboarding",
        "expected": "start a new subscription trial"
    }
    
    #Here we can add more rules as needed. For now let it be 
]
