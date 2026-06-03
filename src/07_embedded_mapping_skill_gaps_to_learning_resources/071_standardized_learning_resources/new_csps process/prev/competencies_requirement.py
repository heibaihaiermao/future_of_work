import json
import re
from collections import defaultdict

# -----------------------------
# LOAD MULTI JSON (for clean file)
# -----------------------------
def load_multi_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = content.split("}\n{")

    data = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            chunk = chunk + "}"
        elif i == len(chunks) - 1:
            chunk = "{" + chunk
        else:
            chunk = "{" + chunk + "}"

        chunk = chunk.strip()

        if chunk:
            data.append(json.loads(chunk))

    return data


# -----------------------------
# LOAD FILES
# -----------------------------
clean_data = load_multi_json("courses_clean.json")

with open("courses_raw.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)


# -----------------------------
# MAP RAW DATA
# -----------------------------
raw_map = {c["Identifier"]: c for c in raw_data}


# -----------------------------
# COMPETENCIES (STRONG + WEAK)
# -----------------------------
COMPETENCIES = {
    "Artificial Intelligence Techniques": {
        "strong": ["artificial intelligence", "machine learning", "chatbot"],
        "weak": ["ai"]
    },
    "Business Acumen": {
        "strong": ["business strategy", "economic"],
        "weak": ["business", "operations"]
    },
    "Data Processing": {
        "strong": ["data analysis", "data management"],
        "weak": ["data", "dataset"]
    },
    "Demonstrating Integrity and Respect (Upholds Integrity and Respect)": {
        "strong": ["ethics", "ethical"],
        "weak": ["integrity", "respect", "diversity", "inclusion"]
    },
    "Knowledge of Emerging Trends": {
        "strong": ["emerging trends", "innovation"],
        "weak": ["trend", "future"]
    },
    "Knowledge of Governance and Support Structures": {
        "strong": ["governance"],
        "weak": ["roles", "responsibilities"]
    },
    "Knowledge of Legal, Policy and Ethical Frameworks": {
        "strong": ["legislation", "regulatory framework"],
        "weak": ["policy", "policies", "act", "framework"]
    },
    "Project Management": {
        "strong": ["project management"],
        "weak": ["project", "planning"]
    },
    "Scientific Research Methods": {
        "strong": ["research methodology"],
        "weak": ["research", "study"]
    },
    "Technical Communication": {
        "strong": ["communication", "communicating"],
        "weak": ["writing", "presentation"]
    },
    "Thinking Things Through (Create Vision and Strategy)": {
        "strong": ["strategic decision", "strategy"],
        "weak": ["analysis", "decision"]
    },
    "Working Effectively with Others (Mobilize People; Collaborate with Partners and Stakeholders)": {
        "strong": ["collaboration", "stakeholder engagement"],
        "weak": ["team", "stakeholders"]
    }
}


# -----------------------------
# INDICATORS
# -----------------------------
GENERIC_INDICATORS = [
    "Demonstrate basic understanding of the competency.",
    "Apply concepts in workplace scenarios.",
    "Support tasks related to this competency.",
    "Communicate concepts clearly to stakeholders."
]


# -----------------------------
# BUILD TEXT
# -----------------------------
def build_text(clean, raw):
    parts = []

    if clean.get("title_en"):
        parts.append(clean["title_en"])

    if clean.get("description_en"):
        parts.append(clean["description_en"])

    if raw and raw.get("Description (English/anglais)"):
        parts.append(raw["Description (English/anglais)"])

    if clean.get("topics"):
        parts.append(clean["topics"])

    text = " ".join(parts)

    # normalize
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    return text


# -----------------------------
# PROFICIENCY
# -----------------------------
def detect_proficiency(text):
    if any(w in text for w in ["advanced", "expert"]):
        return "Advanced"
    elif any(w in text for w in ["apply", "implement", "perform"]):
        return "Intermediate"
    else:
        return "Foundational"


# -----------------------------
# MATCHING
# -----------------------------
def match_competencies(text):
    scores = defaultdict(int)

    for comp, groups in COMPETENCIES.items():
        for kw in groups.get("strong", []):
            if kw in text:
                scores[comp] += 2

        for kw in groups.get("weak", []):
            if kw in text:
                scores[comp] += 1

    return scores


# -----------------------------
# MAIN PIPELINE
# -----------------------------
THRESHOLD = 2  # tuning parameter

output = []

for course in clean_data:
    course_id = course.get("id")
    raw = raw_map.get(course_id)

    text = build_text(course, raw)

    scores = match_competencies(text)

    competencies = []

    for comp, score in scores.items():
        if score >= THRESHOLD:
            competencies.append({
                "competency": comp,
                "proficiency": detect_proficiency(text),
                "description": f"Related to {comp} based on course content.",
                "indicators": GENERIC_INDICATORS
            })

    # fallback
    if not competencies:
        competencies.append({
            "competency": "No match found",
            "proficiency": "unknown",
            "description": None,
            "indicators": None
        })

    new_course = course.copy()
    new_course["competencies"] = competencies

    output.append(new_course)


# -----------------------------
# SAVE OUTPUT
# -----------------------------
with open("courses_with_competencies.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Done! Output saved.")