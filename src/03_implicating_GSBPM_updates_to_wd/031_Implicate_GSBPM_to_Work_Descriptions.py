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


INPUT_GSBPM_FILE = "GSPBM_new.json"
INPUT_WD_FILE = "jobDescriptions.json"
OUTPUT_FILE = "all.json"


# LOAD GSBPM


def load_and_clean_gsbpm(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    phases = data.get("Phases and sub-proceeses", [])

    return [
        {
            "id": item.get("id"),
            "title": item.get("text"),
            "description": item.get("updated description")
        }
        for item in phases
    ]


# LOAD RAW WORK DESCRIPTIONS (NO NORMALIZATION)


def load_wd(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_positions = []

    for group in data:
        for pos in group.get("Positions", []):
            all_positions.append(pos)  # RAW JSON

    return all_positions


# PROMPT  FIXED

# SYSTEM_PROMPT = """
# TASK:

# direct update to wd mapping

# The task is to identify work-descriptions that are directly implicated with specific phases of the GSBPM.  

# The context for the task is the GSBPM. Understanding necessary for this task is embedded in the following JSON content

# The work-descriptions describe roles at an NSO. I will prompt you for each GSPBM phase and sub-phase, and you will then respond with a JSON object. The JSON response will list the "id", "title", and "description" of the GSBPM phase or sub-process, then will list implicated work-descriptions in an attribute called "implicated work-descriptions". Each element of the "implicated work-description" list will be a "work-description" object, that has the following attributes in the following order: "justification", "title", "id". In the "justification" attribute, begin by explaining what is the implicating aspect of the phase or sub-process, then explain what is needed for that element, then justify how the identified work description fills that need, ideally quoting from the work-description content.
# RULES:
# - Include ALL relevant work-descriptions
# - DO NOT invent roles
# - ONLY use provided work-descriptions
# - ONLY output valid JSON (no text outside JSON)

# The JSON schema of the response is:
# ```{json schema}
# [{"id": <GSBPM id>,
#   "title": <title of GSBPM phase/sub-process>,
#   "description": <quote of GSBPM JSON of phase/sub-process description>,
#   "implicated work-descriptions: [
#         {"justification": <explanation of implicating aspect, articulation of needs, justification of particular work-description",
#         "title": <title of work-description>,
#         "classification": <classification of role>},
#         <additional implicated work descriptions> ...]},
# <additional GSBPM phases and sub-processes>]

# JUSTIFICATION RULE:
# - Start with what makes the phase implicating
# - Explain what capability/need is required
# - Quote or reference WD content to justify
# """


# LLM CALL
def run_llm(system_prompt, user_prompt):
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version="2025-04-01-preview",
        azure_endpoint=ENDPOINT
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content


def clean_llm_output(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return text.strip()


# MAIN  PHASE-FIRST

def main():
    print("Loading data...")

    gsbpm = load_and_clean_gsbpm(INPUT_GSBPM_FILE)
    work_descriptions = load_wd(INPUT_WD_FILE)
    with open("03_prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()

    print(f"GSBPM items: {len(gsbpm)}")
    print(f"Work descriptions: {len(work_descriptions)}")

    results = []

    # LOOP THROUGH PHASES 
    for phase in gsbpm:
        print(f"Processing phase: {phase['id']} - {phase['title']}")

        user_prompt = f"""
GSBPM Phase:
{json.dumps(phase, indent=2)}

Work Descriptions (RAW JSON):
{json.dumps(work_descriptions, indent=2)}
"""

        output_text = run_llm(SYSTEM_PROMPT, user_prompt)
        output_text = clean_llm_output(output_text)

        try:
            parsed = json.loads(output_text)

            if isinstance(parsed, list):
                results.extend(parsed)
            else:
                print(" Unexpected output format:")
                print(parsed)

        except Exception:
            print(" Failed parsing response:")
            print(output_text)

    # SAVE OUTPUT  NO GROUPING STEP
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f" Done. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()