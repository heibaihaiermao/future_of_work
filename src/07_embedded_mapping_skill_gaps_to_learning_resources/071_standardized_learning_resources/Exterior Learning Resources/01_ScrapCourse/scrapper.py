import os
import json
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import trafilatura


# CONFIG


CSV_FILE = "Cate_3_learningResources 1.csv"

OUTPUT_DIR = "output_json"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# LOAD CSV


df = pd.read_csv(CSV_FILE)
print(df.columns.tolist())

print(f"Loaded {len(df)} rows")


# HELPER FUNCTION


def extract_page_data(html, url):

    soup = BeautifulSoup(html, "html.parser")

    # ---- Title ----
    title = soup.title.text.strip() if soup.title else "N/A"

    # ---- Headings / Topics ----
    headings = []

    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)

        if text and len(text) > 2:
            headings.append(text)

    # Remove duplicates
    headings = list(dict.fromkeys(headings))

    # ---- Clean Description/Text ----
    clean_text = trafilatura.extract(html)

    if clean_text:
        description = clean_text[:3000]
    else:
        description = ""

    return {
        "url": url,
        "title": title,
        "description": description,
        "topics": headings
    }


# PLAYWRIGHT SCRAPER


results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    
    # LOOP THROUGH CSV
    

    for index, row in df.iterrows():

        try:

            
            # CHANGE COLUMN NAME IF NEEDED
            
            url = row["link\t"]

            if pd.isna(url):
                continue

            print(f"\nScraping: {url}")

            
            # OPEN PAGE
            

            page.goto(
                url,
                wait_until="networkidle",
                timeout=30000
            )

            
            # GET RENDERED HTML
            

            html = page.content()

            
            # EXTRACT METADATA
            

            data = extract_page_data(html, url)

            results.append(data)

            print(f"Saved: {data['title']}")

        except Exception as e:

            print(f"FAILED: {url}")
            print(e)

    browser.close()


# SAVE JSON


output_file = os.path.join(
    OUTPUT_DIR,
    "scraped_resources.json"
)

with open(output_file, "w", encoding="utf-8") as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"\nDone.")
print(f"Saved JSON to: {output_file}")