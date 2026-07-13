import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")

if not API_KEY or not ENDPOINT:
    raise ValueError("Missing API configuration in .env file")

# =========================
# FILE PATHS
# =========================

INPUT_GSBPM_FILE = "GSPBM_new.json"
INPUT_WD_FILE = "jobDescriptions.json"
OUTPUT_FILE = "all.json"

# =========================
# LOAD GSBPM
# =========================

def load_gsbpm(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    phases = data.get("Phases and sub-proceeses", [])

    cleaned = []
    for p in phases:
        cleaned.append({
            "id": p.get("id"),
            "title": p.get("text"),
            "description": p.get("updated description")
        })

    return cleaned


# =========================
# LOAD WORK DESCRIPTIONS
# =========================

def load_wd(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_positions = []
    for group in data:
        for pos in group.get("Positions", []):
            all_positions.append({
                "title": pos.get("Position Title"),
                "classification": pos.get("Classification"),
                "content": pos  # keep full structure (LLM can use it)
            })

    return all_positions


# =========================
# SYSTEM PROMPT (YOUR DESIGN FIXED)
# =========================

SYSTEM_PROMPT = """
TASK:
Map ONE GSBPM phase (or sub-process) to all directly implicated work-descriptions.

RULES:
- Include ALL relevant work-descriptions
- Each work-description MUST include:
  - "justification"
  - "title"
  - "classification"
- MUST NOT output null classification
- MUST use classification EXACTLY as provided
- DO NOT invent roles
- ONLY use provided work-descriptions
- ONLY output valid JSON
- NO text outside JSON

OUTPUT FORMAT:
[
  {
    "id": "<GSBPM id>",
    "title": "<GSBPM title>",
    "description": "<GSBPM description>",
    "implicated work-descriptions": [
      {
        "justification": "...",
        "title": "...",
        "classification": "EC-02"
      }
    ]
  }
]
"""


# =========================
# LLM CALL
# =========================

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


# =========================
# MAIN
# =========================

def main():
    print("Loading data...")

    gsbpm = load_gsbpm(INPUT_GSBPM_FILE)
    work_descriptions = load_wd(INPUT_WD_FILE)

    print(f"GSBPM elements: {len(gsbpm)}")
    print(f"Work descriptions: {len(work_descriptions)}")

    results = []

    # =========================
    # LOOP THROUGH GSBPM PHASES
    # =========================

    for phase in gsbpm:
        print(f"Processing phase: {phase['id']} - {phase['title']}")

        user_prompt = f"""
GSBPM Phase:
{json.dumps(phase, indent=2)}

Work Descriptions:
{json.dumps(work_descriptions, indent=2)}
"""

        output_text = run_llm(SYSTEM_PROMPT, user_prompt)
        output_text = clean_llm_output(output_text)

        try:
            parsed = json.loads(output_text)

            if isinstance(parsed, list):
                results.extend(parsed)
            else:
                print(" Unexpected format:")
                print(parsed)

        except Exception:
            print(" Failed parsing response:")
            print(output_text)

    # =========================
    # SAVE FINAL OUTPUT
    # =========================

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f" Done. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()