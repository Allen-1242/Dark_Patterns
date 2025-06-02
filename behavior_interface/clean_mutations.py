from collections import defaultdict

def clean_mutations(mutations, uid_text_map=None, visible_text="", uid_element_map=None):
    """
    Cleans and enriches raw mutation logs with DOM context.
    :param mutations: List of raw mutation records from MutationObserver
    :param uid_text_map: Dict mapping uid to visible text of that element
    :param visible_text: Full page visible text at mutation time (optional)
    :param uid_element_map: Dict mapping uid to Playwright element handles
    :return: Dict of enriched mutations keyed by uid
    """
    enriched = {}
    uid_counter = {}

    for i, mutation in enumerate(mutations):
        uid = mutation.get("uid")
        if not uid:
            continue

        # Count mutation index per UID
        uid_counter[uid] = uid_counter.get(uid, 0) + 1
        index = uid_counter[uid]

        # Base enrichment fields
        entry = {
            "uid": uid,
            "type": mutation.get("type"),
            "attributeName": mutation.get("attributeName"),
            "visible_text": uid_text_map.get(uid, ""),
            "oldValue": mutation.get("oldValue"),
            "newValue": None,  # to be filled if found
            "mutation_index": index,
            "global_index": i
        }

        # Infer newValue from target HTML if oldValue exists
        target_html = mutation.get("target", "")
        attr_name = mutation.get("attributeName")
        if attr_name and mutation.get("oldValue") is not None:
            import re
            pattern = rf'{attr_name}="([^"]*)"'
            match = re.search(pattern, target_html)
            entry["newValue"] = match.group(1) if match else None

        # DOM-driven enrichment if element handle provided
        if uid_element_map and uid in uid_element_map:
            elem = uid_element_map[uid]
            try:
                entry["context_text"] = elem.inner_text().strip()
            except Exception:
                entry["context_text"] = ""
            try:
                entry["tag_summary"] = elem.evaluate("el => el.tagName + ' ' + (el.className || '')")
            except Exception:
                entry["tag_summary"] = ""
        else:
            entry["context_text"] = ""
            entry["tag_summary"] = ""

        # Group entries by UID
        enriched.setdefault(uid, []).append(entry)

    return enriched




def generate_mutation_timeline(mutations, uid_text_map=None):
    """
    Groups mutations by UID and generates a mutation timeline with attribute changes.
    """
    timeline = {}

    # Group mutations by UID
    grouped = defaultdict(list)
    for i, m in enumerate(mutations):
        uid = m.get("uid")
        if not uid:
            continue
        grouped[uid].append((i, m))

    for uid, events in grouped.items():
        record = {
            "uid": uid,
            "target": events[-1][1]["target"],  # most recent target
            "visible_text": uid_text_map.get(uid, "") if uid_text_map else "",
            "events": []
        }

        for index, e in events:
            record["events"].append({
                "index": index,
                "type": e["type"],
                "attributeName": e.get("attributeName"),
                "oldValue": e.get("oldValue"),
                "newValue": extract_attribute(e.get("target", ""), e.get("attributeName"))
            })

        timeline[uid] = record

    return timeline


def extract_attribute(html_str, attr_name):
    """
    Basic extractor to get attribute value from the latest target HTML.
    Not a full HTML parser.
    """
    if not html_str or not attr_name:
        return None
    import re
    pattern = rf'{attr_name}="([^"]+)"'
    match = re.search(pattern, html_str)
    return match.group(1) if match else None
