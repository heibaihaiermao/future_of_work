import json
from openai import AzureOpenAI

# =========================
# CONFIGURATION
# =========================

API_KEY = ""
ENDPOINT = "/"
MODEL_NAME = "gpt-4.1"

INPUT_GSBPM_FILE = "GSPBM_new.json"
INPUT_WD_FILE = "jobDescriptions.json"
OUTPUT_FILE = "all.json"



# LOAD GSBPM
def load_and_clean_gsbpm(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    phases = data.get("Phases and sub-proceeses", [])

    cleaned = []
    for item in phases:
        cleaned.append({
            "id": item.get("id"),
            "title": item.get("text"),
            "desc": (item.get("updated description") or "")[:300]  # limit size
        })

    return cleaned



# LOAD & FLATTEN WD
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_positions(data):
    all_positions = []

    for group in data:
        positions = group.get("Positions", [])
        for pos in positions:
            all_positions.append(pos)

    return all_positions



# NORMALIZE WD


def normalize_wd(wd):
    content_parts = []

    title = wd.get("Position Title") or "UNKNOWN"

    if title == "UNKNOWN":
        print(" WD missing title:", wd.keys())

    if "Key Activities" in wd:
        content_parts.append(" ".join(wd["Key Activities"]))

    tech = wd.get("technical activities, skills, responsibilities, or efforts", {})
    if isinstance(tech, dict):
        for category, items in tech.items():
            if isinstance(items, list):
                content_parts.append(" ".join(items))

    return {
        "title": title,
        "content": " ".join(content_parts)[:1500]  #  limit WD size
    }



# PROMPT


SYSTEM_PROMPT = """
TASK:
Map ONE work description to relevant GSBPM IDs.

RULES:
- You MUST return at least 1 ID
- Do NOT return empty []
- ONLY return valid JSON
- DO NOT ASK FOLLOW UP QUESTION

FORMAT:
[
  {
    "title": "...",
    "implicated phases and sub-processes": [
      { "id": "1.1" }
    ]
  }
]
"""



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



# MAIN
def main():
    print("Loading data...")

    gsbpm = load_and_clean_gsbpm(INPUT_GSBPM_FILE)

    wd_raw = load_json(INPUT_WD_FILE)
    wd_raw = extract_positions(wd_raw)   #  CRITICAL FIX

    work_descriptions = [normalize_wd(wd) for wd in wd_raw]

    print(f"GSBPM items: {len(gsbpm)}")
    print(f"Work descriptions: {len(work_descriptions)}")

    results = []

    for wd in work_descriptions:
        print(f"Processing: {wd['title']}")

        USER_PROMPT = f"""
GSBPM:
{json.dumps(gsbpm, indent=2)}

Work Description:
{json.dumps(wd, indent=2)}
        """

        output_text = run_llm(SYSTEM_PROMPT, USER_PROMPT)
        output_text = clean_llm_output(output_text)

        try:
            parsed = json.loads(output_text)

            if isinstance(parsed, list) and len(parsed) > 0:
                results.append(parsed[0])
            else:
                print("⚠️ Empty LLM response")

        except Exception as e:
            print("⚠️ Failed parsing one WD")
            print(output_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f" Done. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()