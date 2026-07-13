import os
import json
import pickle
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as fil:
        return json.load(fil)


def load_text_file(path):
    with open(path, "r", encoding="utf-8") as fil:
        return fil.read()


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as fil:
        json.dump(data, fil, indent=4, ensure_ascii=False)


def extract_subprocesses(gsbpm_data):
    subprocesses = []

    for phase in gsbpm_data:
        phase_info = phase["phase"]

        for subprocess in phase["sub-processes"]:
            subprocesses.append({
                "phase_id": phase_info["id"],
                "phase_name": phase_info["title"],
                "gsbpm_id": subprocess["id"],
                "gsbpm_name": subprocess["text"],
                "description": subprocess["description"]
            })

    return subprocesses


def build_user_prompt(subprocess):
    return f"""
Analyze the following GSBPM subprocess.

---
GSBPM SUBPROCESS
---
{json.dumps(subprocess, indent=4, ensure_ascii=False)}

"""


def analyze_gsbpm_subprocess(client, deployment, system_prompt, subprocess, updates):
    user_prompt = build_user_prompt(subprocess)

    return client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "system",
                "content": f"""
STRATEGIC UPDATE DOCUMENTS:

{updates}
"""
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        max_completion_tokens=13107
    )


if __name__ == "__main__":
    INPUT_DIR = Path("./input")
    PROMPT_PATH = Path("./prompts/prompt.txt")
    OUTPUT_DIR = Path("./output")

    OUTPUT_DIR.mkdir(exist_ok=True)

    load_dotenv("../../py.env")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    deployment = "gpt-4.1"
    api_version = "2025-04-01-preview"

    print("Loading input files...")

    system_prompt = load_text_file(PROMPT_PATH)

    gsbpm_data = load_json_file(
        INPUT_DIR / "GSBPM_v5_2.json"
    )

    mandate_letters = load_json_file(
        INPUT_DIR / "mandate_letters_enriched.json"
    )

    departmental_plan = load_json_file(
        INPUT_DIR / "departmental_plan_enriched.json"
    )

    statcan2030 = load_json_file(
        INPUT_DIR / "deck_updates.json"
    )

    updates = {
        "mandate_letters": mandate_letters,
        "departmental_plan": departmental_plan,
        "statcan2030": statcan2030
    }

    subprocesses = extract_subprocesses(gsbpm_data)

    print(f"Found {len(subprocesses)} GSBPM subprocesses")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key
    )

    results = []
    raw_responses = []

    for index, subprocess in enumerate(subprocesses):
        print(
            f"[{index + 1}/{len(subprocesses)}] "
            f"Analyzing {subprocess['gsbpm_id']} "
            f"{subprocess['gsbpm_name']}"
        )

        try:
            response = analyze_gsbpm_subprocess(
                client,
                deployment,
                system_prompt,
                subprocess,
                updates
            )

            raw_content = response.choices[0].message.content

            cleaned = (
                raw_content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            print(cleaned)

            result_json = json.loads(cleaned)

            results.append(result_json)
            raw_responses.append(response)

        except Exception as e:
            print(
                f"ERROR processing {subprocess['gsbpm_id']}: {e}"
            )

            results.append({
                "gsbpm_id": subprocess["gsbpm_id"],
                "gsbpm_name": subprocess["gsbpm_name"],
                "error": str(e)
            })

    output_json = OUTPUT_DIR / "gsbpm_implications.json"

    save_json_file(
        output_json,
        results
    )

    print(f"Saved analysis to {output_json}")

    pickle_path = OUTPUT_DIR / "gsbpm_raw_responses.pkl"

    with open(pickle_path, "wb") as fil:
        pickle.dump(raw_responses, fil)

    print(f"Saved raw responses to {pickle_path}")