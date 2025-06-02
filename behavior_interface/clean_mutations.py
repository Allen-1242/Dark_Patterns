import json
import re

def clean_mutations(raw_mutations, uid_text_map=None):
    uid_text_map = uid_text_map or {}
    seen_targets = set()
    cleaned = []

    for m in raw_mutations:
        uid = m.get("uid")
        target = m.get("target", "") or ""
        text = uid_text_map.get(uid, m.get("text", "")) or ""

        if len(target) > 3000 or "<svg" in target:
            continue

        text = re.sub(r"\s+", " ", text).strip()
        target_clean = re.sub(r"\s+", " ", target).strip()

        key = (m["type"], m.get("attributeName"), text[:30], target_clean[:100])
        if key in seen_targets:
            continue
        seen_targets.add(key)

        cleaned.append({
            "type": m["type"],
            "attributeName": m.get("attributeName"),
            "text": text,
            "target": target_clean[:300],
            "uid": uid
        })

    return cleaned