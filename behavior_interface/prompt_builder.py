import json

def build_llm_prompt(expected_path, mutation_path):
    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    with open(mutation_path, "r", encoding="utf-8") as f:
        mutations = json.load(f)

    mutation_summary = ""
    for m in mutations[:5]:  # Limit for clarity
        summary = f"- Type: {m['type']}, Attr: {m.get('attributeName')}, Text: {m.get('text')}, Target: {m['target'][:200]}"
        mutation_summary += summary + "\n"

    prompt = f"""
You are an expert in ethical interface design.

A user clicked a button with:
- Text: "{expected['element_text']}"
- Intent: {expected['click_intent']}
- Expected behavior: {expected['expected_behavior']}

After clicking, the following DOM mutations occurred:
{mutation_summary}

Was this behavior misleading or deceptive? Respond with "YES" or "NO" and give a short explanation.
"""
    return prompt.strip()
