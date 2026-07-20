from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    """Minimal cleanup only: whitespace normalization."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_classification(soup):
    h1 = soup.find("h1")
    if not h1:
        return None

    text = h1.get_text(" ", strip=True)

    # EC-02, EC-01 etc.
    match = re.search(r"(EC-\d+)", text)
    return match.group(1) if match else None

def extract_position_header(soup):
    """Extract Position Title from <p><strong>Position Title:</strong> X"""

    position_title = None
    group_level = None
    branch_division = None
    job_family_number = None
    supervisor_position = None

    for p in soup.find_all("p"):
        strongs = p.find_all("strong")

        for strong in strongs:
            key = clean_text(strong.get_text()).lower()

            if "Job Family Title".lower() in key and "supervisor" not in key or "Position Title".lower() in key:
                position_title = clean_text(strong.next_sibling)

            if "Group and Level".lower() in key and "supervisor" not in key or "Position Classification".lower() in key:
                group_level = clean_text(strong.next_sibling)

            if "Branch/Division".lower() in key or "Organizational Component".lower() in key:
                branch_division = clean_text(strong.next_sibling)

            if "Job Family Number".lower() in key and "supervisor" not in key or "Job/Generic Number".lower() in key or "Job Number".lower() in key:
                job_family_number = clean_text(strong.next_sibling)
            
            if "Position number".lower() in key and "supervisor" in key:
                supervisor_position = clean_text(strong.next_subling)

    return position_title, group_level, branch_division, job_family_number, supervisor_position


def extract_key_activities(section):
    """Extract raw <li> under Key Activities"""
    ul = section.find_next("ul")
    if not ul:
        return []

    return [
        clean_text(li.get_text(" ", strip=True))
        for li in ul.find_all("li")
        if clean_text(li.get_text())
    ]


def extract_technical_sections(work_characteristics):
    """
    Extracts:
    - Communication
    - Knowledge of Specialized Fields
    - Contextual Knowledge
    - Research and Analysis
    etc.
    """

    result = {}

    current_heading = None

    node = work_characteristics.find_next()

    while node:

        if node.name == "h2" or "physical effort" in node.get_text().lower():
            break

        if node.name == "h3":
            current_heading = clean_text(node.get_text())
            result[current_heading] = []

        elif node.name == "p" and current_heading:
            txt = clean_text(node.get_text())
            if txt:
                result[current_heading].append(txt)

        node = node.find_next_sibling()

    return result


def extract_positions(soup):
    classification = extract_classification(soup)

    position_title, group_level, branck_division, job_family_number, supervisor_position = extract_position_header(soup)

    positions = []

    # Locate Key Activities
    key_activities_h2 = None
    for h2 in soup.find_all("h2"):
        if "key activities" in h2.get_text().lower():
            key_activities_h2 = h2
            break

    key_activities = []
    if key_activities_h2:
        key_activities = extract_key_activities(key_activities_h2)

    # Work Characteristics
    work_char_h2 = None
    for h2 in soup.find_all("h2"):
        if "work characteristics" in h2.get_text().lower():
            work_char_h2 = h2
            break

    technical = {}
    if work_char_h2:
        technical = extract_technical_sections(work_char_h2)

    positions.append({
        "Job Family Number": job_family_number,
        "Group/Level": group_level,
        "Position Title": position_title,
        "Supervisor Position": supervisor_position,
        "Branch/Division": branck_division,
        "Key Activities": key_activities,
        "technical activities, skills, responsibilities, or efforts": technical
    })

    return classification, positions


def parse_file(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    classification, positions = extract_positions(soup)

    return {
        "Classification": classification,
        "Positions": positions
    }, positions[0]["Job Family Number"]


INPUT_DIR = Path("data/work-descriptions-input/")
OUTPUT_DIR = Path("data/work-descriptions-raw")

OUTPUT_DIR.mkdir(exist_ok=True)


def convert_filename(name: str, position_num: str) -> str:
    stem = Path(name).stem
    try:
        return Path(postion_num + ".json")
    except:
        print(stem)


for file in INPUT_DIR.glob("*.html"):

    parsed, postion_num = parse_file(file)

    output_file = OUTPUT_DIR / convert_filename(file.name, postion_num)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    print(f"Saved: {output_file.name}")


