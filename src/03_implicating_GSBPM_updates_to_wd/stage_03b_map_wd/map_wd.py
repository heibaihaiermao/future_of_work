import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# ==================================================
# Config
# ==================================================

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

GSBPM_FILE = "input/gsbpm_driver_impacts.json"
WD_DIR = "input/work-descriptions-raw"
OUTPUT_FILE = "output/stage03a_wd_subprocess_mapping.json"

BATCH_SIZE = 10

# ==================================================
# Load GSBPM once
# ==================================================

with open(GSBPM_FILE, encoding="utf-8") as f:
    gsbpm = json.load(f)

# Compact version for prompt caching
gsbpm_context = json.dumps(
    gsbpm,
    ensure_ascii=False,
    separators=(",", ":")
)

# ==================================================
# Load WDs
# ==================================================

work_descriptions = []

for file in sorted(Path(WD_DIR).glob("*.json")):
    with open(file, encoding="utf-8") as f:
        work_descriptions.append(json.load(f))

print(f"Loaded {len(work_descriptions)} work descriptions")

# ==================================================
# Cached System Prompt
# ==================================================

SYSTEM_PROMPT = f"""
You are a Statistics Canada workforce transformation expert.

TASK

For each work description:

Identify the GSBPM subprocesses most likely
to be materially affected by the work description
and associated future-state drivers.

The objective is NOT to identify every related
GSBPM subprocess.

The objective is to identify the subprocesses
most likely to drive future changes to the work
description and future skill gaps.

Prefer precision over completeness.

Return up to 3 subprocesses.

If fewer than 3 meaningful subprocesses exist,
return only those supported by evidence.

Do not invent subprocesses merely to reach 3.

RANKING

Rank the selected subprocesses relative to
one another.

Assign:

1 = strongest relationship
2 = second strongest relationship
3 = third strongest relationship

Ranks must be unique.

When ranking, consider:

- direct responsibilities
- ownership
- governance responsibilities
- operational involvement
- decision-making authority
- expected future impact from associated drivers
- expected future changes to the work description
- evidence contained in the work description

INCLUSION RULES

Only include subprocesses supported by evidence
from the work description.

Include a subprocess only when there is a
meaningful and material relationship.

Exclude subprocesses that are:

- merely adjacent
- indirectly connected
- weakly associated
- speculative
- unsupported by evidence

Be conservative.

Do not invent responsibilities.

Do not infer activities that are not present
in the supplied work description.

JUSTIFICATION REQUIREMENTS

For each selected subprocess:

- explain why it is relevant
- reference evidence from the work description
- explain the connection to the subprocess
- explain why the relationship is stronger than
  other possible subprocesses
- explain how associated drivers may influence
  future changes to the work

OUTPUT SCHEMA

{{
  "results": [
    {{
      "job_family_number": "",
      "position_title": "",
      "impacts": [
        {{
          "gsbpm_id": "",
          "rank": 1,
          "justification": ""
        }}
      ]
    }}
  ]
}}

RETURN VALID JSON ONLY.

GSBPM DATA

{gsbpm_context}
"""

# ==================================================
# Batch utility
# ==================================================

def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# ==================================================
# Process batches
# ==================================================

all_results = []

for batch_num, batch in enumerate(
    chunks(work_descriptions, BATCH_SIZE),
    start=1
):

    user_prompt = f"""
WORK DESCRIPTIONS

{json.dumps(batch, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    result_json = json.loads(
        response.choices[0].message.content
    )

    all_results.extend(
        result_json.get("results", [])
    )

    print(
        f"Batch {batch_num} complete. "
        f"Results so far: {len(all_results)}"
    )

    # immediate save after each batch

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            all_results,
            f,
            indent=2,
            ensure_ascii=False
        )

print(
    f"Done. Saved {len(all_results)} records."
)