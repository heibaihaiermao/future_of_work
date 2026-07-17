from assistant import Assistant, persistent_send

from json import loads, dumps, dump as jdump
from tqdm import tqdm

from os.path import exists
from os import makedirs

import warnings

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="AzureOpenAI.beta.assistants"
)

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="AzureOpenAI.beta.threads"
)


###############################################################################
# Utils
###############################################################################

def read(path):

    with open(path, "r", encoding="utf-8") as fil:
        return fil.read()


def write_json(path, obj):

    with open(path, "w", encoding="utf-8") as fil:

        jdump(
            obj,
            fil,
            ensure_ascii=False,
            indent=2
        )


def preprocess_message(message):

    message = message.strip()

    if message.startswith("```json"):
        message = message[7:]

    if message.startswith("```"):
        message = message[3:]

    if message.endswith("```"):
        message = message[:-3]

    return message.strip()


def postprocess_message(message):

    if isinstance(message, list):

        if len(message) == 1:
            return message[0]

    return message


def process_message(message):

    message = preprocess_message(message)

    message = loads(message)

    message = postprocess_message(message)

    return message


###############################################################################
# Load Inputs
###############################################################################

background = read(
    "prompts/prompt_01_-_background_prompt.txt"
)

stage04_records = loads(
    read(
        "stage04_wd_future_impact_input.json"
    )
)


###############################################################################
# Trim large records before prompting
###############################################################################

TOP_IMPACTS = 3


def build_prompt_payload(record):

    impacts = sorted(
        record.get("impacted_gsbpm", []),
        key=lambda x: x.get("rank", 999)
    )

    impacts = impacts[:TOP_IMPACTS]

    return {

        "title":
            record.get("title"),

        "classification":
            record.get("classification"),

        "position_information":
            record.get(
                "position_information",
                {}
            ),

        "impacted_gsbpm":
            impacts
    }


###############################################################################
# Stage 5 Prompt
###############################################################################

def forecast_competency_gaps(record):

    payload = build_prompt_payload(
        record
    )

    prompt = f"""
{background}

You are conducting Stage 5
Future of Work analysis.

The supplied record contains:

1. Current work description
2. Current activities
3. Technical responsibilities
4. Impacted GSBPM subprocesses
5. Future drivers
6. Workforce implications
7. Impact mechanisms

Your task is NOT to repeat
the GSBPM analysis.

Instead identify:

- Activities reduced
- Activities expanded
- Activities transformed
- New activities

- Skills declining
- Skills growing
- New skills

- Competency gaps

- Upskilling requirements

- Automation exposure

- Workforce impacts

- Proposed updates to the
  work description

INPUT:

{dumps(payload, indent=2)}

Return VALID JSON ONLY.

Schema:

{{
  "position_title": "",
  "classification": "",

  "activities_reduced": [
    {{
      "activity": "",
      "reason": ""
    }}
  ],

  "activities_expanded": [
    {{
      "activity": "",
      "reason": ""
    }}
  ],

  "activities_transformed": [
    {{
      "activity": "",
      "future_state": "",
      "reason": ""
    }}
  ],

  "activities_new": [
    {{
      "activity": "",
      "reason": ""
    }}
  ],

  "skills_declining": [
    {{
      "skill": "",
      "reason": ""
    }}
  ],

  "skills_growing": [
    {{
      "skill": "",
      "reason": ""
    }}
  ],

  "skills_new": [
    {{
      "skill": "",
      "driver": "",
      "reason": ""
    }}
  ],

  "competency_gaps": [
    {{
      "gap": "",
      "driver": "",
      "reason": ""
    }}
  ],

  "upskilling_requirements": [
    {{
      "skill": "",
      "priority": "Low|Medium|High",
      "reason": ""
    }}
  ],

  "automation_exposure":
    "Low|Medium|High",

  "future_work_impacts": [
    {{
      "impact": "",
      "severity":
        "Low|Medium|High",
      "reason": ""
    }}
  ],

  "proposed_work_description_updates": [
    {{
      "section": "",
      "proposed_update": "",
      "reason": ""
    }}
  ],

  "summary": ""
}}

RESPOND IN VALID JSON ONLY.
"""

    return prompt


###############################################################################
# Output Paths
###############################################################################

OUTPUT_DIR = (
    "data/stage5_competency_gap_outputs"
)

if not exists(OUTPUT_DIR):

    makedirs(OUTPUT_DIR)


def make_output_path(record):

    title = (
        record.get("title")
        or "unknown"
    )

    title = (
        title
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    return (
        f"{OUTPUT_DIR}/"
        f"{title}_-_stage5.json"
    )


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":

    system_prompt = """
You are an expert workforce
transformation analyst.

Always respond using the exact
JSON schema requested.

Return JSON only.

Do not return markdown.
Do not return explanations.
"""

    buddy = Assistant(
        system_prompt
    )

    send = lambda prompt: (
        persistent_send(
            buddy.send_message,
            prompt
        )
    )

    for record in tqdm(stage04_records):

        title = record.get("title")

        if not title:
            continue

        try:

            prompt = (
                forecast_competency_gaps(
                    record
                )
            )

            response = send(
                prompt
            )

            result = process_message(
                response
            )

            output_path = (
                make_output_path(
                    record
                )
            )

            write_json(
                output_path,
                result
            )

            print(
                f"Saved: "
                f"{output_path}"
            )

        except Exception as ex:

            print(
                f"FAILED: "
                f"{title}"
            )

            print(ex)