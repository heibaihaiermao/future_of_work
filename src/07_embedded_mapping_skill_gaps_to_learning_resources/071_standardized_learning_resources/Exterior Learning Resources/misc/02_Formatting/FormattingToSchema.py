import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI

# =====================================================
# CONFIG
# =====================================================

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-04-01-preview"
)

MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")

SCRAPED_FILE = "scraped_resources.json"
INDICATOR_MAP_FILE = "indicator_map.json"
CSPS_EXAMPLE_FILE = "csps_examples.json"

PROFILE_OUTPUT = "course_profiles.json"
FINAL_OUTPUT = "external_output.json"

# =====================================================
# HELPERS
# =====================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):

    items = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:
                items.append(json.loads(line))

    return items


def save_json(data, path):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def clean_json_response(text):

    if not text:
        return ""

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def llm_call(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )


    content = response.choices[0].message.content

    return clean_json_response(content)


# =====================================================
# LOAD REFERENCE DATA
# =====================================================

courses = load_json(SCRAPED_FILE)

indicator_map = load_json(INDICATOR_MAP_FILE)

# CSPS examples are JSONL
# csps_examples = load_jsonl(CSPS_EXAMPLE_FILE)

# example_output = csps_examples[0]

def load_jsonl(path):

    items = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:
                items.append(json.loads(line))

    return items


csps_examples = load_jsonl(CSPS_EXAMPLE_FILE)

example_output = csps_examples[0]


# =====================================================
# STAGE 1
# COURSE PROFILE EXTRACTION
# =====================================================

EXTRACTION_SYSTEM_PROMPT = """
You are an expert learning-content analyzer.

Analyze a learning resource and extract:

{
  "summary": "",
  "skills": [],
  "tools": [],
  "topics": [],
  "learning_outcomes": [],
  "difficulty": "",
  "technology": "",
  "estimated_duration": ""
}

Rules:

- Use semantic understanding.
- Infer information from title, content, outline,
  headings, bullet points and descriptions.
- Keep skills concise.
- Rewrite text into clean language.
- Return JSON only.
"""


def extract_course_profile(course):

    prompt = f"""
RESOURCE

{json.dumps(course, indent=2)}
"""

    output = llm_call(
        EXTRACTION_SYSTEM_PROMPT,
        prompt
    )

    return json.loads(output)


# =====================================================
# STAGE 2
# COMPETENCY MAPPING
# =====================================================

# MAPPING_SYSTEM_PROMPT = f"""
# You are an expert Government of Canada competency
# mapping engine.

# COMPETENCY FRAMEWORK

# {json.dumps(indicator_map, indent=2)}

# OUTPUT EXAMPLE

# {json.dumps(example_output, indent=2)}

# Instructions:

# 1. Analyze the course.
# 2. Use semantic reasoning.
# 3. Generate a professional description.
# 4. Select the most relevant competencies.
# 5. Select the most appropriate proficiency level.
# 6. Select ONLY indicators supported by evidence.
# 7. Indicators MUST come from the framework.
# 8. Use between 1 and 3 competencies.
# 9. Technology should be meaningful
#    (python, sql, ai, theory, statistics, etc.)
# 10. Return valid JSON only.

# Required Output:

# {{
#   "title": "",
#   "description": "",
#   "duration": "",
#   "technology": "",
#   "competencies": [
#     {{
#       "competency": "",
#       "proficiency": "",
#       "description": "",
#       "indicators": []
#     }}
#   ]
# }}
# """

MAPPING_SYSTEM_PROMPT = f"""
You are an expert Government of Canada competency
mapping engine.

COMPETENCY FRAMEWORK

{json.dumps(indicator_map, indent=2)}

OUTPUT EXAMPLE

{json.dumps(example_output, indent=2)}

Instructions:

1. Analyze the course.
2. Use semantic reasoning.
3. Rewrite descriptions into professional language.
4. Select the most relevant competencies.
5. Select the most appropriate proficiency level.
6. Select ONLY indicators supported by evidence.
7. Indicators MUST come from the competency framework.
8. Use between 1 and 3 competencies.
9. Technology should be meaningful
   (python, sql, ai, statistics, theory, etc.)
10. Return valid JSON only.

Required Output:

{{
  "title": "",
  "description": "",
  "duration": "",
  "technology": "",
  "competencies": [
    {{
      "competency": "",
      "proficiency": "",
      "description": "",
      "indicators": []
    }}
  ]
}}
"""

# def map_competencies(course, profile):

#     prompt = f"""
# ORIGINAL COURSE

# {json.dumps(course, indent=2)}

# COURSE PROFILE

# {json.dumps(profile, indent=2)}

# Generate the final CSPS JSON object.

# Requirements:

# - Rewrite incomplete descriptions.
# - Infer duration when possible.
# - Determine technology area.
# - Select competency/proficiency.
# - Select matching indicators.
# - Return JSON only.
# """

#     output = llm_call(
#         MAPPING_SYSTEM_PROMPT,
#         prompt
#     )

#     return json.loads(output)
def map_competencies(course, profile):

    prompt = f"""
ORIGINAL COURSE

{json.dumps(course, indent=2)}

COURSE PROFILE

{json.dumps(profile, indent=2)}

Generate the final CSPS competency record.

Requirements:

- Rewrite descriptions into complete sentences.
- Estimate duration if needed.
- Determine technology category.
- Select competencies.
- Select proficiency levels.
- Select indicators from the framework.
- Return JSON only.
"""

    output = llm_call(
        MAPPING_SYSTEM_PROMPT,
        prompt
    )

    return json.loads(output)

# =====================================================
# VALIDATION
# =====================================================

def validate_output(record):

    if "competencies" not in record:
        return record

    for comp in record["competencies"]:

        competency = comp.get("competency")
        proficiency = comp.get("proficiency")

        if competency not in indicator_map:

            print(
                f"WARNING: Unknown competency: "
                f"{competency}"
            )

            continue

        if proficiency not in indicator_map:
                f"WARNING: Invalid proficiency "
                f"'{proficiency}' "
                f"for competency "
                f"'{competency}'"
            

    return record


# =====================================================
# PIPELINE
# =====================================================

def build_profiles():

    profiles = []

    total = len(courses)

    for idx, course in enumerate(courses, start=1):

        print(
            f"[PROFILE {idx}/{total}] "
            f"{course.get('title', 'Untitled')}"
        )

        try:

            profile = extract_course_profile(course)

            profiles.append({
                "title": course.get("title"),
                "profile": profile
            })

        except Exception as ex:

            print("PROFILE ERROR")
            print(ex)

    save_json(
        profiles,
        PROFILE_OUTPUT
    )

    return profiles


def build_csps(profiles):

    results = []

    total = len(courses)

    for idx, course in enumerate(courses, start=1):

        print(
            f"[CSPS {idx}/{total}] "
            f"{course.get('title', 'Untitled')}"
        )

        try:

            profile = profiles[idx - 1]["profile"]

            record = map_competencies(
                course,
                profile
            )

            record = validate_output(record)

            results.append(record)

        except Exception as ex:

            print("COMPETENCY ERROR")
            print(ex)

    save_json(
        results,
        FINAL_OUTPUT
    )


# =====================================================
# MAIN
# =====================================================

def main():

    print("Building profiles...")
    profiles = build_profiles()

    print("Building CSPS output...")
    build_csps(profiles)

    print("Done.")


if __name__ == "__main__":
    main()