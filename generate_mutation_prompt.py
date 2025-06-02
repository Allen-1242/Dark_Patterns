import json

# Load JSON data from file or variable
with open('output_mutations_cleaned.json', 'r') as f:
    data = json.load(f)

# Flatten and sort by global_index
flattened = []
for uid, mutations in data.items():
    for m in mutations:
        flattened.append({
            "uid": m.get("uid"),
            "type": m.get("type"),
            "attributeName": m.get("attributeName"),
            "oldValue": m.get("oldValue"),
            "newValue": m.get("newValue"),
            "global_index": m.get("global_index"),
            "visible_text": m.get("visible_text", "").strip().replace("\n", " "),
            "tag_summary": m.get("tag_summary"),
        })

flattened_sorted = sorted(flattened, key=lambda x: x["global_index"])

# Format output for LLM
formatted_lines = []
for i, entry in enumerate(flattened_sorted):
    uid = entry["uid"]
    typ = entry["type"]
    attr = entry["attributeName"] or "N/A"
    old = entry["oldValue"]
    new = entry["newValue"]
    tag = entry["tag_summary"] or "Unknown"
    text = entry["visible_text"][:100] + ("..." if len(entry["visible_text"]) > 100 else "")

    # Construct the value change description
    if old is None and new is None:
        change = "added"
    elif old == new:
        change = f"remains '{old}'"
    else:
        change = f"'{old}' → '{new}'"

    line = f"[{i}] UID: {uid} | TYPE: {typ} | TAG: {tag} | ATTR: {attr} | {change} | Visible text: \"{text}\""
    formatted_lines.append(line)

# Print or write to a file
for line in formatted_lines:
    print(line)

# Optional: Save to text file
with open('llm_ready_log.txt', 'w') as f:
    f.write("\n".join(formatted_lines))
