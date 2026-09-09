import os
import json
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse

# =========================
# CONFIG
# =========================
CSV_FILE = "Cate_3_learningResources_fr 1.csv"
OUTPUT_DIR = "output_json"
OUTPUT_FILE = "scraped_resources_fr.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_TEXT_LENGTH = 10000  # truncate long pages


# =========================
# HELPERS
# =========================
def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"]
    except:
        return False


def clean_url(url):
    if isinstance(url, str):
        return url.strip().replace("\t", "")
    return None


# -------------------------
# MAIN CONTENT EXTRACTION
# -------------------------
def extract_main_content(html):
    """
    Use trafilatura to extract main readable content
    """
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


# -------------------------
# STRUCTURED EXTRACTION
# -------------------------
def extract_structure(html):
    """
    Extract useful structural signals (headings + lists)
    """
    soup = BeautifulSoup(html, "html.parser")

    headings = []
    for tag in ["h1", "h2", "h3"]:
        for h in soup.find_all(tag):
            text = h.get_text(strip=True)
            if text and len(text) > 3:
                headings.append(text)

    bullet_points = []
    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        if text and len(text) > 5:
            bullet_points.append(text)

    return {
        "headings": headings[:30],
        "bullet_points": bullet_points[:50]
    }


# -------------------------
# QUALITY FILTER
# -------------------------
def is_valid_content(text):
    """
    Filter bad pages (login, access denied, empty)
    """
    if not text or len(text) < 2:
        return False

    blacklist = [
        "access denied",
        "enable javascript",
    ]

    lower = text.lower()
    for b in blacklist:
        if b in lower:
            return False

    return True


# =========================
# LOAD CSV
# =========================
df = pd.read_csv(CSV_FILE)

print(f"Loaded {len(df)} rows")


# =========================
# SCRAPING
# =========================
results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    for idx, row in df.iterrows():
        url = clean_url(row.get("link"))

        if not is_valid_url(url):
            print(f"[{idx}] Invalid URL: {url}")
            continue

        print(f"[{idx}] Scraping: {url}")

        try:
            page.goto(url, timeout=30000)

            # wait for dynamic content
            page.wait_for_timeout(2000)

            html = page.content()

            # --- extract ---
            clean_text = extract_main_content(html)

            if not is_valid_content(clean_text):
                print(f"[{idx}] Skipped (low-quality content)")
                print(clean_text[:300])
                continue

            structure = extract_structure(html)

            # truncate long text
            clean_text = clean_text[:MAX_TEXT_LENGTH]

            result = {
                "url": url,
                "title": row.get("name"),
                "source_description": row.get("description"),
                "clean_text": clean_text,
                "headings": structure["headings"],
                "bullet_points": structure["bullet_points"]
            }

            results.append(result)

        except Exception as e:
            print(f" -> Error: {str(e)}")
            continue

    browser.close()


# =========================
# SAVE OUTPUT
# =========================
output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n✅ Done!")
print(f"Saved to: {output_path}")