import json
import re
import os
from collections import defaultdict



# LOAD MULTI JSON (clean file)

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



# LOAD FILES

clean_data = load_multi_json("courses_clean.json")

with open("courses_raw.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Map raw by Identifier
raw_map = {c["Identifier"]: c for c in raw_data}



# COMPETENCIES (STRONG + WEAK)

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



# INDICATORS

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

    raw_desc = ""
    if raw:
        raw_desc = raw.get("Description (English/anglais)", "")

    text = " ".join([title, desc, raw_desc, topics]).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    return text, title.lower(), topics.lower()



# PROFICIENCY

def detect_proficiency(text):
    if any(w in text for w in ["advanced", "expert"]):
        return "Advanced"
    elif any(w in text for w in ["apply", "implement", "perform"]):
        return "Intermediate"
    else:
        return "Foundational"



# MATCHING WITH WEIGHTS

def match_competencies(text, title_text, topic_text):
    scores = defaultdict(int)

    for comp, groups in COMPETENCIES.items():

        # strong keywords
        for kw in groups.get("strong", []):
            if kw in text:
                scores[comp] += 2
            if kw in title_text:
                scores[comp] += 4    #  title strongest
            if kw in topic_text:
                scores[comp] += 4    #  topic strong signal

        # weak keywords
        for kw in groups.get("weak", []):
            if kw in text:
                scores[comp] += 1
            if kw in title_text:
                scores[comp] += 2
            if kw in topic_text:
                scores[comp] += 3    #  topic still stronger

    return scores



# MAIN PIPELINE

THRESHOLD = 2
TOP_N = 3   #  cap max competencies

output = []

for course in clean_data:
    course_id = course.get("id")
    raw = raw_map.get(course_id)

    text, title_text, topic_text = build_text(course, raw)

    scores = match_competencies(text, title_text, topic_text)

    # sort by score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    competencies = []

    for comp, score in sorted_scores[:TOP_N]:
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



# SAVE OUTPUT

output_path = os.path.join(os.path.dirname(__file__), "courses_with_competencies.json")

print("Processing complete, saving file...")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f" Done! Output saved to: {output_path}")