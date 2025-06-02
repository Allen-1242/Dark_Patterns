import sys
import os
import json
import time

from playwright.sync_api import sync_playwright
from behavior_interface.infer_intent import infer_expected_behavior
from behavior_interface.clean_mutations import clean_mutations

# Fix module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

MUTATION_OBSERVER_SCRIPT = """
() => {
  let idCounter = 0;
  window.mutationLogs = [];
  const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
      const el = mutation.target;
      if (!el.dataset.uid) el.dataset.uid = "uid-" + (idCounter++);
      const record = {
        type: mutation.type,
        target: el.outerHTML,
        uid: el.dataset.uid,
        text: el.innerText || "",
        attributeName: mutation.attributeName || null,
        oldValue: mutation.oldValue || null
      };
      window.mutationLogs.push(record);
    }
  });

  observer.observe(document.body, {
    attributes: true,
    childList: true,
    subtree: true,
    attributeOldValue: true
  });
}
"""

def scrape_dom(url, selector_to_click="text='Close'", output_prefix="output"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"Navigating to {url}")
        page.goto(url)
        page.wait_for_load_state("networkidle")

        print("Injecting MutationObserver...")
        page.evaluate(MUTATION_OBSERVER_SCRIPT)

        # Click the element
        print(f"Clicking selector: {selector_to_click}")
        try:
            page.click(selector_to_click, timeout=3000)
        except Exception as e:
            print(f"Click failed: {e}")

        print("Waiting for mutations...")
        time.sleep(3)

        # Save DOM after mutation
        html = page.content()
        with open(f"{output_prefix}_dom_snapshot.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Save mutation logs (raw)
        mutations = page.evaluate("() => window.mutationLogs")
        with open(f"{output_prefix}_mutations.json", "w", encoding="utf-8") as f:
            json.dump(mutations, f, indent=2)
        print(f"Saved DOM snapshot and {len(mutations)} mutations.")

        # Extract UIDs
        uids = [m.get("uid") for m in mutations if "uid" in m]
        uid_text_map = {}
        for uid in uids:
            try:
                elem = page.query_selector(f"[data-uid='{uid}']")
                uid_text_map[uid] = elem.inner_text().strip() if elem else ""
            except Exception:
                uid_text_map[uid] = ""

        # Clean mutation logs with added text context
        cleaned = clean_mutations(mutations, uid_text_map)
        with open(f"{output_prefix}_mutations_cleaned.json", "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2)
        print(f"[✓] Cleaned {len(cleaned)} mutation records.")

        # Capture expected behavior
        try:
            element = page.query_selector(selector_to_click)
            element_text = element.inner_text().strip()
            element_attrs = {
                attr: element.get_attribute(attr)
                for attr in ["class", "href", "data-quick-add", "data-sell", "onclick"]
                if element.get_attribute(attr)
            }

            expected = infer_expected_behavior(
                text=element_text,
                attrs=element_attrs,
                selector=selector_to_click
            )

            with open(f"{output_prefix}_expected.json", "w", encoding="utf-8") as f:
                json.dump(expected, f, indent=2)
            print("Expected behavior inferred and saved.")

        except Exception as e:
            print(f"Failed to infer expected behavior: {e}")

        # Save visible text of the full page
        try:
            visible_text = page.evaluate("() => document.body.innerText")
            with open(f"{output_prefix}_visible_text.txt", "w", encoding="utf-8") as f:
                f.write(visible_text.strip())
        except Exception as e:
            print(f"Failed to extract visible text: {e}")

        browser.close()


# CLI usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape_dom.py <url> [selector]")
    else:
        url = sys.argv[1]
        selector = sys.argv[2] if len(sys.argv) > 2 else "text='Close'"
        scrape_dom(url, selector)
