import os
import json

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


# =====================================
# CONFIG
# =====================================

URL = (
    "https://www.statcan.gc.ca/en/about/"
    "transparency/departmental-plan/2026-2027"
)

OUTPUT_DIR = "output_json"
OUTPUT_FILE = "departmental_plan.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================
# HELPERS
# =====================================

def extract_sections(soup):
    """
    Extract major sections using H2/H3 structure.
    """

    sections = []

    current_section = None

    main = soup.find("main")

    if not main:
        main = soup

    for elem in main.find_all(
        ["h1", "h2", "h3", "p", "li"]
    ):

        if elem.name in ["h1", "h2", "h3"]:

            if current_section:
                sections.append(current_section)

            current_section = {
                "title": elem.get_text(
                    " ",
                    strip=True
                ),
                "content": ""
            }

        else:

            text = elem.get_text(
                " ",
                strip=True
            )

            if not text:
                continue

            if current_section:
                current_section["content"] += (
                    text + "\n"
                )

    if current_section:
        sections.append(current_section)

    return sections


# =====================================
# SCRAPE
# =====================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    print(f"Scraping: {URL}")

    page.goto(
        URL,
        wait_until="networkidle",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    html = page.content()

    browser.close()


# =====================================
# PARSE
# =====================================

soup = BeautifulSoup(
    html,
    "html.parser"
)

main = soup.find("main")

if main:
    full_text = main.get_text(
        "\n",
        strip=True
    )
else:
    full_text = soup.get_text(
        "\n",
        strip=True
    )

title_tag = soup.find("h1")

title = (
    title_tag.get_text(strip=True)
    if title_tag
    else "Departmental Plan"
)

sections = extract_sections(soup)


# =====================================
# OUTPUT
# =====================================

result = {
    "document_type": "departmental_plan",
    "title": title,
    "year": "2026-2027",
    "source_url": URL,
    "sections": sections,
    "full_text": full_text
}


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
        result,
        f,
        indent=2,
        ensure_ascii=False
    )

print()
print("✅ Done")
print(f"Saved to: {output_path}")