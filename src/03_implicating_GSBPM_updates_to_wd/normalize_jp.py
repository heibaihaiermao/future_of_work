from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

DATA_DIR = Path("./data/job-posters-html")
OUTPUT_FILE = "./data/job-posters-normalized/ec_competencies.json"

# Matches EC-01, EC-01 (non-breaking hyphen), EC–01, etc.
EC_PATTERN = re.compile(r"EC[\-\u2010\u2011\u2012\u2013\u2014]\d+")

result = {}

def clean_text(text):
    """
    Normalize HTML extracted text:
    - remove \n, \t
    - collapse repeated whitespace
    - remove list artifacts
    """
    if not text:
        return ""

    # Replace newlines/tabs with spaces
    text = re.sub(r"[\n\t\r]+", " ", text)

    # Remove standalone bullet/list markers
    text = re.sub(r"\s*-\s*", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

for html_file in DATA_DIR.glob("*.html"):

    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    ####################################################
    # Find the position title containing EC-xx
    ####################################################

    position_name = None
    ec_group = None

    for text in soup.stripped_strings:

        match = EC_PATTERN.search(text)

        if match:
            ec_group = match.group().replace("-", "-").replace("–", "-").replace("—", "-")
            position_name = clean_text(text.strip())
            break

    if position_name is None:
        print(f"Skipping {html_file.name}: no EC group found.")
        continue


    ####################################################
    # Find Who Can Complain
    ####################################################

    complain_h2 = None

    for h2 in soup.find_all("h2"):

        if "file a complaint" in h2.get_text(" ", strip=True).lower():
            complain_h2 = h2
            break

    if complain_h2 is None:
        print(f"Skipping {html_file.name}: no Complaint section.")
        continue

    ####################################################
    # Collect everything until next h2
    ####################################################

    parts = []

    node = complain_h2.find_next_sibling()

    while node:

        if node.name == "h2":
            break

        text = node.get_text(" ", strip=True)

        if text:
            parts.append(text)

        node = node.find_next_sibling()

    complaint = clean_text(" ".join(parts))

    ####################################################
    # Find Criteria section
    ####################################################

    criteria_h2 = None

    for h2 in soup.find_all("h2"):

        if "criteria" in h2.get_text(" ", strip=True).lower():
            criteria_h2 = h2
            break

    if criteria_h2 is None:
        print(f"Skipping {html_file.name}: no Criteria section.")
        continue

    ####################################################
    # Collect everything until next h2
    ####################################################

    parts = []

    node = criteria_h2.find_next_sibling()

    while node:

        if node.name == "h2" and "complaint" in node.get_text(" ", strip=True).lower():
            break

        text = node.get_text(" ", strip=True)

        if text:
            parts.append(text)

        node = node.find_next_sibling()

    description = clean_text(" ".join(parts))

    if description is None:
            print(f"Skipping {html_file.name}: no description.")

    ####################################################
    # Store
    ####################################################

    result.setdefault(ec_group, {})
    result[ec_group][position_name] = {"Assets": description,
                                       "Area of Selection": complaint}

####################################################
# Save JSON
####################################################

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print(f"Saved {OUTPUT_FILE}")