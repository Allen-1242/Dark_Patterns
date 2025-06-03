import sys
import os
import json
import time

from playwright.sync_api import sync_playwright
from behavior_interface.infer_intent import infer_expected_behavior
from behavior_interface.clean_mutations import clean_mutations, generate_mutation_timeline

# Ensure local modules can be imported
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

import json
import sys
import time
from playwright.sync_api import sync_playwright

def scrape_dom_all_clickables(url, output_prefix="output"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"Navigating to {url}")
        page.goto(url)
        page.wait_for_load_state("networkidle")

        print("Injecting MutationObserver...")
        page.evaluate(MUTATION_OBSERVER_SCRIPT)

        # Get all clickable elements (buttons, links, inputs with type=submit/button)
        clickables = page.query_selector_all("button, a, input[type='submit'], input[type='button']")
        print(f"Found {len(clickables)} clickable elements.")

        for i, element in enumerate(clickables):
            try:
                element_text = element.inner_text().strip()
            except:
                element_text = "(no text)"
            print(f"\n[{i}] Clicking: {element_text}")

            try:
                # Inject observer fresh before each click
                page.evaluate(MUTATION_OBSERVER_SCRIPT)

                element.click(timeout=3000)
                time.sleep(3)

                visible_text = page.evaluate("() => document.body.innerText")
                html = page.content()
                mutations = page.evaluate("() => window.mutationLogs")

                prefix = f"{output_prefix}_{i}"
                with open(f"{prefix}_visible_text.txt", "w", encoding="utf-8") as f:
                    f.write(visible_text.strip())
                with open(f"{prefix}_dom_snapshot.html", "w", encoding="utf-8") as f:
                    f.write(html)
                with open(f"{prefix}_mutations.json", "w", encoding="utf-8") as f:
                    json.dump(mutations, f, indent=2)
                print(f"Saved snapshot and {len(mutations)} mutations for element {i}.")

                # Process mutation context if needed
                uids = [m.get("uid") for m in mutations if "uid" in m]
                uid_element_map = {uid: page.query_selector(f"[data-uid='{uid}']") for uid in set(uids)}

                cleaned = clean_mutations(
                    mutations,
                    uid_text_map={uid: (page.query_selector(f"[data-uid='{uid}']").inner_text().strip() if page.query_selector(f"[data-uid='{uid}']") else "") for uid in uids},
                    visible_text=visible_text,
                    uid_element_map=uid_element_map
                )
                with open(f"{prefix}_mutations_cleaned.json", "w", encoding="utf-8") as f:
                    json.dump(cleaned, f, indent=2)
                print(f"[✓] Cleaned {sum(len(v) for v in cleaned.values())} mutation records.")

            except Exception as e:
                print(f"Failed to click or process element {i}: {e}")

        browser.close()

# CLI usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape_dom.py <url>")
    else:
        url = sys.argv[1]
        scrape_dom_all_clickables(url)

# FastAPI endpoint to run the scraper
def run_scraper_on_url(url, output_prefix="output"):
    scrape_dom_all_clickables(url, output_prefix)
    return f"Scraping complete. Output prefix: {output_prefix}"
