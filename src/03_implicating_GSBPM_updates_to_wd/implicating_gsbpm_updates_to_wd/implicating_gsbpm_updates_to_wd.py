import os
import json
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


def normalize_work_descriptions(data):
    if isinstance(data, list):
        return data

    return [data]


def clean_gsbpm_implications(data):
    cleaned = []

    for item in data:
        item = item.copy()

        item.pop(
            "evidence",
            None
        )

        cleaned.append(item)

    print(cleaned)
    return cleaned


def build_user_prompt(gsbpm, work_descriptions):
    return f"""
Analyze how the following GSBPM future-state implication affects existing work descriptions.

---
GSBPM FUTURE STATE
---
{json.dumps(gsbpm, indent=4, ensure_ascii=False)}

---
WORK DESCRIPTIONS
---
{json.dumps(work_descriptions, indent=4, ensure_ascii=False)}
"""


def analyze_work_description_implication(
        client,
        deployment,
        system_prompt,
        gsbpm,
        work_descriptions):

    user_prompt = build_user_prompt(
        gsbpm,
        work_descriptions
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        max_completion_tokens=13107
    )

    return response


if __name__ == "__main__":

    INPUT_DIR = Path("./input")
    PROMPT_PATH = Path("./prompts/prompt.txt")
    OUTPUT_DIR = Path("./output")

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    load_dotenv("../../py.env")

    endpoint = os.getenv(
        "AZURE_OPENAI_ENDPOINT"
    )

    api_key = os.getenv(
        "AZURE_OPENAI_API_KEY"
    )

    deployment = "gpt-4.1"

    api_version = "2025-04-01-preview"

    system_prompt = load_text_file(
        PROMPT_PATH
    )

    gsbpm_path = INPUT_DIR / "gsbpm_implications.json"

    wd_files = [
        file for file in INPUT_DIR.glob("*.json")
        if file.name != "gsbpm_implications.json"
    ]

    if len(wd_files) != 1:
        raise ValueError(
            "Expected exactly one work description JSON file in ./input/"
        )

    wd_path = wd_files[0]

    print(
        f"Loading GSBPM implications from {gsbpm_path}"
    )

    gsbpm_implications = clean_gsbpm_implications(
        load_json_file(gsbpm_path)
    )

    print(
        f"Loading work descriptions from {wd_path}"
    )

    work_descriptions = normalize_work_descriptions(
        load_json_file(wd_path)
    )

    print(
        f"Loaded {len(gsbpm_implications)} GSBPM elements"
    )

    print(
        f"Loaded {len(work_descriptions)} work descriptions"
    )

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key
    )

    results = []

    for index, gsbpm in enumerate(gsbpm_implications):

        print(
            f"[{index + 1}/{len(gsbpm_implications)}] "
            f"Analyzing {gsbpm['gsbpm_id']} "
            f"{gsbpm['gsbpm_name']}"
        )

        try:

            response = analyze_work_description_implication(
                client,
                deployment,
                system_prompt,
                gsbpm,
                work_descriptions
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            cleaned = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            print(cleaned)

            result = json.loads(
                cleaned
            )

            results.append(
                result
            )

        except Exception as e:

            print(
                f"ERROR processing {gsbpm['gsbpm_id']}: {e}"
            )

            results.append(
                {
                    "gsbpm_id": gsbpm["gsbpm_id"],
                    "gsbpm_name": gsbpm["gsbpm_name"],
                    "error": str(e)
                }
            )


    output_path = (
        OUTPUT_DIR /
        f"{wd_path.stem}_gsbpm_wd_implications.json"
    )

    save_json_file(
        output_path,
        results
    )

    print(
        f"Saved output to {output_path}"
    )