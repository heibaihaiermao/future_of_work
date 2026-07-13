import json
import re
import os
from collections import defaultdict

# -----------------------------
# LOAD MULTI JSON
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
clean_data = load_multi_json("csps_clean.json")

with open("csps_raw.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Map raw by Identifier
raw_map = {c["Identifier"]: c for c in raw_data}

#  Load indicator map
with open("indicator_map.json", "r", encoding="utf-8") as f:
    INDICATOR_MAP = json.load(f)


# -----------------------------
# COMPETENCIES
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
        "weak": ["data"]
    },
    "Knowledge of Governance and Support Structures": {
        "strong": ["governance"],
        "weak": ["roles", "responsibilities"]
    },
    "Knowledge of Legal, Policy and Ethical Frameworks": {
        "strong": ["legislation", "regulatory framework"],
        "weak": ["policy", "policies", "act"]
    },
    "Project Management": {
        "strong": ["project management"],
        "weak": ["project"]
    },
    "Technical Communication": {
        "strong": ["communication", "communicating", "communications"],
        "weak": ["writing", "presentation"]
    },
    "Thinking Things Through (Create Vision and Strategy)": {
        "strong": ["strategy", "strategic"],
        "weak": ["analysis", "decision"]
    },
    "Working Effectively with Others (Mobilize People; Collaborate with Partners and Stakeholders)": {
        "strong": ["collaboration", "stakeholder"],
        "weak": ["team"]
    }
}

#  fallback indicators
GENERIC_INDICATORS = [
    "Demonstrate basic understanding of the competency.",
    "Apply concepts in workplace scenarios.",
    "Support tasks related to this competency.",
    "Communicate concepts clearly to stakeholders."
]



# BUILD TEXT

def build_text(clean, raw):
    title = clean.get("title_en", "")
    desc = clean.get("description_en", "")
    topics = clean.get("topics", "")

    raw_desc = raw.get("Description", "") if raw else ""

    text = " ".join([title, desc, topics, raw_desc]).lower()
    return text, title.lower(), str(topics).lower()



# PROFICIENCY DETECTION

def detect_proficiency(text):
    if any(w in text for w in ["lead", "director", "executive"]):
        return "Lead"
    elif any(w in text for w in ["advanced", "expert"]):
        return "Advanced"
    elif any(w in text for w in ["apply", "implement", "perform"]):
        return "Intermediate"
    else:
        return "Foundational"



# COMPETENCY MATCHING

def match_competencies(text, title_text, topic_text):
    scores = defaultdict(int)

    for comp, keywords in COMPETENCIES.items():

        # Strong keywords
        for kw in keywords["strong"]:
            if kw in text:
                scores[comp] += 3

        # Weak keywords
        for kw in keywords["weak"]:
            if kw in text:
                scores[comp] += 1

        # Boost if in title
        for kw in keywords["strong"]:
            if kw in title_text:
                scores[comp] += 2

        # Boost if in topics
        for kw in keywords["weak"]:
            if kw in topic_text:
                scores[comp] += 1

    return scores


# -----------------------------
# MAIN PIPELINE
# -----------------------------
THRESHOLD = 2
TOP_N = 3

output = []

for course in clean_data:
    course_id = course.get("id")
    raw = raw_map.get(course_id)

    text, title_text, topic_text = build_text(course, raw)

    scores = match_competencies(text, title_text, topic_text)

    sorted_comps = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    selected_comps = [
        comp for comp, score in sorted_comps
        if score >= THRESHOLD
    ][:TOP_N]


    course_result = dict(course)
    course_result["competencies"] = []
    for comp in selected_comps:
        proficiency = detect_proficiency(text)

        # ✅ NEW: Indicator lookup
        indicators = INDICATOR_MAP.get(comp, {}).get(proficiency)

        # ✅ fallback
        if not indicators:
            indicators = GENERIC_INDICATORS

        course_result["competencies"].append({
            "competency": comp,
            "proficiency": proficiency,
            "indicators": indicators
        })

    # If nothing matched
    if not course_result["competencies"]:
        course_result["competencies"].append({
            "competency": "No match found",
            "proficiency": "unknown",
            "indicators": None
        })

    output.append(course_result)


# -----------------------------
# SAVE OUTPUT
# -----------------------------
output_path = os.path.join(os.path.dirname(__file__), "csps_with_competencies.json")

print("Processing complete, saving file...")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Done! Output saved to: {output_path}")