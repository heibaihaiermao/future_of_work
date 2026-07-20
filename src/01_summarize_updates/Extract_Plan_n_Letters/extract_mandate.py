import os
import json
import trafilatura
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# =================================
# CONFIG
# =================================

URLS = [
    "https://icn-rci.statcan.ca/999/999_019_2026_02-eng.html",
    "https://icn-rci.statcan.ca/999/999_019_2026_05-eng.html",
    "https://icn-rci.statcan.ca/999/999_019_2026_08-eng.html",
    "https://icn-rci.statcan.ca/999/999_019_2026_11-eng.html",
]

OUTPUT_DIR = "output_json"
OUTPUT_FILE = "mandate_letters.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =================================
# HELPERS
# =================================

def extract_main_content(html):
    try:
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            favor_recall=True
        )

        return text or ""

    except Exception:
        return ""


def extract_structure(html):
    soup = BeautifulSoup(html, "html.parser")

    headings = []

    for tag in ["h1", "h2", "h3"]:
        for h in soup.find_all(tag):
            text = h.get_text(" ", strip=True)

            if text:
                headings.append(text)

    return headings


# =================================
# SCRAPE
# =================================

results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    context = browser.new_context()

    page = context.new_page()

    for url in URLS:

        print(f"Scraping: {url}")

        try:

            response = page.goto(
                url,
                timeout=30000,
                wait_until="networkidle"
            )

            print(
                "Status:",
                response.status if response else "No response"
            )

            html = page.content()

            title = page.title()

            clean_text = extract_main_content(html)

            # fallback if Trafilatura fails
            if not clean_text:

                soup = BeautifulSoup(html, "html.parser")

                clean_text = soup.get_text(
                    separator=" ",
                    strip=True
                )

            result = {
                "url": url,
                "title": title,
                #"headings": extract_structure(html),
                "content": clean_text
            }

            results.append(result)

            print(
                f"  -> extracted {len(clean_text)} characters"
            )

        except Exception as e:

            print(f"ERROR: {e}")

    browser.close()

# =================================
# SAVE
# =================================

output_path = os.path.join(
    OUTPUT_DIR,
    OUTPUT_FILE
)

with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\n✅ Done")
print(f"Saved: {output_path}")