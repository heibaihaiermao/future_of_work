import json
import requests
import os
from pathlib import Path
import time
from urllib.parse import urljoin, urlparse, parse_qs

from playwright.sync_api import sync_playwright

BASE = "https://psjobs-emploisfp.psc-cfp.gc.ca/psrs-srfp/applicant/"
START_URL = "https://psjobs-emploisfp.psc-cfp.gc.ca/psrs-srfp/applicant/page2440?tab=5&mode=archive&title=&departments=125&classificationInfos=EC640&levels=0&referenceNumber=&selectionProcessNumber=&fromDate=2025-06-17&toDate=2026-06-17&search=Search%20archives&log=false"

STATE_FILE = "input/storage_state.json"

OUTPUT_DIR = "output/job-posters-html"
os.makedirs(OUTPUT_DIR, exist_ok=True)

POSTER_FILE = "input/poster_urls.json"

def extract_page_urls(page):
    """Extract pagination URLs from pagelinks"""
    links = page.eval_on_selector_all(
        "span.pagelinks a[href*='requestedPage=']",
        "els => els.map(e => e.getAttribute('href'))"
    )

    full_urls = [
        urljoin(BASE, l) for l in links
    ]

    # deduplicate + keep only page numbers
    return sorted(set(full_urls))


def extract_poster_urls(page):
    """Extract job posters from listing page"""
    links = page.eval_on_selector_all(
        "li.searchResult a[href*='page1800?poster=']",
        "els => els.map(e => e.href)"
    )

    return list(set(links))


def crawl_all_listings(page):
    page.goto(START_URL, wait_until="networkidle")

    all_pages = set()
    all_posters = set()

    # STEP 1: get pagination structure from first page
    page_urls = extract_page_urls(page)
    all_pages.update(page_urls)

    print(f"[DEBUG] Found {len(page_urls)} pages")
    print(f"[DEBUG] all_pages\n {all_pages}")

    # STEP 2: iterate all pages deterministically
    for i, url in enumerate(sorted(all_pages)):
        print(f"[LISTING PAGE] {i+1}: {url}")
        page.goto(url, wait_until="networkidle")

        posters = extract_poster_urls(page)
        print(f"  → {len(posters)} posters")

        all_posters.update(posters)

    return list(all_posters)

def fetch_html(url, cookies):
    r = requests.get(url, cookies=cookies)
    r.raise_for_status()
    return r.text


def save_posters(urls, cookies):
    for i, url in enumerate(urls):
        poster_id = url.split("poster=")[-1]

        try:
            html = fetch_html(url, cookies)

            path = os.path.join(OUTPUT_DIR, f"{poster_id}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"[SAVED] {poster_id}")

        except Exception as e:
            print(f"[ERROR] {poster_id}: {e}")
            

def extract_cookies(storage_state_file):
    with open(storage_state_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    cookies = {}
    for c in state["cookies"]:
        cookies[c["name"]] = c["value"]

    return cookies

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", headless=False)

        # Reuse logged-in session (after manual MFA login once)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        print("Scraping listing pages...")
        poster_urls = crawl_all_listings(page)

        print(f"Total posters found: {len(poster_urls)}")

        with open(POSTER_FILE, "w", encoding="utf-8") as f:
            json.dump(poster_urls, f, indent=2)
        
        cookies = extract_cookies(STATE_FILE)
        save_posters(poster_urls, cookies)

        context.close()
        browser.close()


if __name__ == "__main__":
    main()