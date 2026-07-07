import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# ==================================================
# Configuration
# ==================================================

load_dotenv()

API_KEY = os.getenv(
    "AZURE_OPENAI_API_KEY"
)

ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT"
)

API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2025-04-01-preview"
)

MODEL_NAME = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT"
)

INPUT_GSBPM_DRIVER_FILE = (
    "input/gsbpm_driver_impacts.json"
)

INPUT_WD_FILE = (
    "input/work_descriptions.json"
)

OUTPUT_FILE = (
    "output/gsbpm_wd_impacts.json"
)

# ==================================================
# Azure Client
# ==================================================

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)

# ==================================================
# Load Files
# ==================================================

with open(
    INPUT_GSBPM_DRIVER_FILE,
    "r",
    encoding="utf-8"
) as f:

    gsbpm_driver_impacts = json.load(f)

with open(
    INPUT_WD_FILE,
    "r",
    encoding="utf-8"
) as f:

    work_descriptions = json.load(f)

print(
    f"Loaded {len(gsbpm_driver_impacts)} "
    f"GSBPM subprocesses."
)

print(
    f"Loaded {len(work_descriptions)} "
    f"work descriptions."
)

# ==================================================
# System Prompt
# ==================================================

SYSTEM_PROMPT = """
TASK:

Identify work descriptions that are implicated by
a GSBPM subprocess and its associated strategic
drivers.

The GSBPM subprocess represents an area of
statistical production.

The associated drivers represent transformation
forces that are expected to influence how that
subprocess will be performed.

Determine which work descriptions are materially
connected to this subprocess.

For each implicated work description:

- explain what aspect of the subprocess is relevant
- explain what capability or responsibility is needed
- explain how the work description satisfies that need
- reference evidence from the work description

RULES:

- Include ALL relevant work descriptions.
- Do not invent work descriptions.
- Use only supplied work descriptions.
- Consider:
    - key activities
    - responsibilities
    - knowledge requirements
    - communication requirements
    - contextual knowledge

Relevance must be:

- High
- Medium
- Low

Return valid JSON only.

JSON Schema:

{
  "gsbpm_id": "...",
  "gsbpm_name": "...",
  "drivers": [...],
  "implicated_work_descriptions": [
    {
      "title": "...",
      "classification": "...",
      "relevance": "...",
      "justification": "..."
    }
  ]
}
"""

# ==================================================
# LLM Function
# ==================================================

def run_llm(user_prompt):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        response_format={
            "type": "json_object"
        },
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

    return (
        response
        .choices[0]
        .message
        .content
    )

# ==================================================
# Main Loop
# ==================================================

results = []

for subprocess in gsbpm_driver_impacts:

    print(
        f"Processing "
        f"{subprocess['gsbpm_id']} "
        f"- "
        f"{subprocess['gsbpm_name']}"
    )

    user_prompt = f"""
GSBPM Subprocess:

{json.dumps(
    subprocess,
    indent=2,
    ensure_ascii=False
)}

Work Descriptions:

{json.dumps(
    work_descriptions,
    indent=2,
    ensure_ascii=False
)}

Identify all implicated work descriptions.

Return valid JSON only.
"""

    try:

        content = run_llm(
            user_prompt
        )

        result = json.loads(
            content
        )

        results.append(
            result
        )

        print(
            f"✓ Completed "
            f"{subprocess['gsbpm_id']}"
        )

        # Save incremental progress

        os.makedirs(
            os.path.dirname(
                OUTPUT_FILE
            ),
            exist_ok=True
        )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                results,
                f,
                indent=2,
                ensure_ascii=False
            )

    except Exception as e:

        print(
            f"✗ Failed "
            f"{subprocess['gsbpm_id']}"
        )

        print(str(e))

# ==================================================
# Final Save
# ==================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"\nGenerated "
    f"{len(results)} records."
)

print(
    f"Saved to "
    f"{OUTPUT_FILE}"
)