import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI



# LOAD ENV VARIABLES


load_dotenv()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")

if not API_KEY or not ENDPOINT:
    raise ValueError("Missing API configuration in .env file")



# FILE PATHS


COURSES_FILE = "courses.json"
INDICATOR_MAP_FILE = "indicator_map.json"
EXAMPLES_FILE = "courses_with_competencies.json"

OUTPUT_FILE = "courses_ai_competencies.json"



# LOAD JSON FILES


def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


courses = load_json(COURSES_FILE)
indicator_map = load_json(INDICATOR_MAP_FILE)
examples = load_json(EXAMPLES_FILE)



# FEW SHOT EXAMPLES


few_shot_examples = examples[:3]



# OPTIONAL RULE-BASED HINTS


RULE_HINTS = {

    "Technical Communication": [
        "communication",
        "communicating",
        "conversation",
        "dialogue",
        "stakeholder",
        "difficult conversations",
        "trust"
    ],

    "Working Effectively with Others": [
        "team",
        "employees",
        "collaboration",
        "leadership",
        "support your team"
    ],

    "Thinking Things Through (Create Vision and Strategy)": [
        "strategy",
        "uncertainty",
        "adaptability",
        "change",
        "planning",
        "action plan"
    ],

    "Project Management": [
        "deliver",
        "manage",
        "coordination",
        "execution",
        "implementation"
    ],

    "Business Acumen": [
        "business",
        "operations",
        "organizational",
        "governance"
    ]
}



# BUILD COURSE SEARCH TEXT


def build_course_text(course):

    fields = [

        course.get("title_en", ""),
        course.get("description_en", ""),
        course.get("course_outline_en", ""),
        course.get("target_audience_en", ""),
        course.get("category", "")

    ]

    return " ".join(
        [str(field).lower() for field in fields if field]
    )



# RULE-BASED COMPETENCY HINTS


def get_candidate_competencies(course):

    text = build_course_text(course)

    scores = {}

    for competency, keywords in RULE_HINTS.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in text:
                score += 1

        if score > 0:
            scores[competency] = score

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [x[0] for x in ranked[:5]]



# FILTER INDICATOR MAP


# def build_filtered_indicator_map(candidate_competencies):

#     filtered = {}

#     for competency in candidate_competencies:

#         if competency in indicator_map:
#             filtered[competency] = indicator_map[competency]

#     return filtered



# SYSTEM PROMPT


SYSTEM_PROMPT = """
TASK:

You are an expert competency classification system for
Government of Canada learning products.

Analyze the course metadata and determine the BEST matching
competencies and proficiency levels.

You MUST:
- use semantic understanding
- analyze title, description, outline, audience, and context
- select the top 1-3 MOST relevant competencies
- determine the MOST appropriate proficiency level

IMPORTANT RULES:

- ONLY use competencies found in the competency framework
- ONLY use proficiency levels found in the framework
- DO NOT invent competencies
- DO NOT invent proficiency levels
- DO NOT generate indicators
- DO NOT rewrite the course object
- Return ONLY valid JSON
- Prefer semantic reasoning over keyword matching

OUTPUT FORMAT:

{
  "competencies": [
    {
      "competency": "",
      "proficiency": ""
    }
  ]
}
"""



# AZURE OPENAI CLIENT


client = AzureOpenAI(
    api_key=API_KEY,
    api_version="2025-04-01-preview",
    azure_endpoint=ENDPOINT
)



# CLEAN LLM OUTPUT


def clean_llm_output(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()



# ANALYZE COURSE


def analyze_course(course):

    # candidate_competencies = get_candidate_competencies(course)

    # filtered_indicator_map = build_filtered_indicator_map(
    #     candidate_competencies
    # )
    
    candidate_competencies = get_candidate_competencies(course)

    #filtered_indicator_map = indicator_map


    user_prompt = f"""
COMPETENCY FRAMEWORK:

{json.dumps(indicator_map, indent=2)}

EXAMPLE OUTPUTS:

{json.dumps(few_shot_examples, indent=2)}

RULE-BASED CANDIDATES:

{json.dumps(candidate_competencies, indent=2)}

COURSE TO ANALYZE:

{json.dumps(course, indent=2)}

Determine the best competencies and proficiency levels.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content

    content = clean_llm_output(content)

    try:

        parsed = json.loads(content)

        return parsed

    except Exception as e:

        print("\nJSON PARSE ERROR")
        print(content)

        return {
            "competencies": []
        }



# VALIDATE AI OUTPUT


def validate_competencies(competencies):

    validated = []

    for comp in competencies:

        competency = comp.get("competency")
        proficiency = comp.get("proficiency")

        if competency not in indicator_map:
            continue

        competency_levels = indicator_map[competency]

        if proficiency not in competency_levels:
            continue

        validated.append({
            "competency": competency,
            "proficiency": proficiency
        })

    return validated



# ENRICH WITH INDICATORS


def enrich_competencies(validated_competencies):

    enriched = []

    for comp in validated_competencies:

        competency = comp["competency"]
        proficiency = comp["proficiency"]

        indicators = indicator_map[competency][proficiency]

        enriched.append({
            "competency": competency,
            "proficiency": proficiency,
            "indicators": indicators
        })

    return enriched



# PROCESS SINGLE COURSE


def process_course(course):

    ai_result = analyze_course(course)

    raw_competencies = ai_result.get("competencies", [])

    validated = validate_competencies(raw_competencies)

    enriched = enrich_competencies(validated)

    # PRESERVE ORIGINAL COURSE STRUCTURE
    final_course = dict(course)

    # APPEND COMPETENCIES
    final_course["competencies"] = enriched

    return final_course



# MAIN


def main():

    output = []

    total = len(courses)

    for idx, course in enumerate(courses):

        course_id = course.get("course_code", "UNKNOWN")

        print(f"[{idx+1}/{total}] Processing {course_id}")

        try:

            processed = process_course(course)

            output.append(processed)

        except Exception as e:

            print(f"ERROR processing {course_id}: {e}")

            failed_course = dict(course)

            failed_course["competencies"] = []

            output.append(failed_course)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"\n✅ Saved output to: {OUTPUT_FILE}")




if __name__ == "__main__":

    main()