from playwright.sync_api import sync_playwright
import time

URL = "https://flattummyco.com/products/flattummytea?variant=312671605&selling_plan=1368260696"

def analyze_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle')

        dom_before = page.content()
        with open("dom_before.html", "w", encoding="utf-8") as f:
            f.write(dom_before)

        # Example: Click the first visible button
        btn = page.query_selector("button")  # Improve this selector to target "Subscribe Now" or similar
        if btn:
            print("Clicking:", btn.inner_text())
            btn.click()
            time.sleep(3)  # Wait for possible redirect or modal
        else:
            print("No button found")

        dom_after = page.content()
        with open("dom_after.html", "w", encoding="utf-8") as f:
            f.write(dom_after)

        browser.close()

if __name__ == "__main__":
    analyze_click()
