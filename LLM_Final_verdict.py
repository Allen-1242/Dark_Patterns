import ollama
import json

def detect_dark_pattern_json(user_action, resulting_ui_behavior, ui_summary):
    """
    Sends a UI behavior summary to the LLM and requests a structured JSON response
    indicating whether the behavior represents a dark pattern.

    Returns:
        dict with keys: is_dark_pattern, pattern_type, justification
    """

    prompt = f"""
You are a digital design and UX researcher specializing in deceptive patterns (also called "dark patterns").

A user performed an action on a website, and the following UI changes were observed.

Analyze the interaction and return your answer strictly in this JSON format:

{{
  "is_dark_pattern": "Yes" or "No",
  "pattern_type": [ "type1", "type2" ],  // use categories like "bait and switch", "forced continuity", "hidden information"
  "justification": "Your explanation here."
}}

**User Action:**
{user_action}

**Resulting UI Behavior:**
{resulting_ui_behavior}

**Detailed DOM-Based UI Summary:**
{ui_summary}
"""

    response = ollama.chat(
        model='deepseek-r1:7b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    try:
        # Try to extract valid JSON from the response
        parsed = json.loads(response['message']['content'])
        return parsed
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON. Raw response:")
        print(response['message']['content'])
        return None

with open("summary_output.txt", "r") as f:
    summary = f.read()

result = detect_dark_pattern_json(
    "Clicked 'Quick Add' button",
    "“A modal became visible containing product details, review count, pricing information such as '$19', and a 'Subscribe & Save 15%' option.”",
    summary
)

print(json.dumps(result, indent=2))