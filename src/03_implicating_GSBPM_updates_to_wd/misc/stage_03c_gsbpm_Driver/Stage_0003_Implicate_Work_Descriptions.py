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

INPUT_WORK_DESCRIPTIONS_DIR = (
"data/work-descriptions-raw"
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

print(
    f"Loaded {len(gsbpm_driver_impacts)} "
    f"GSBPM subprocesses."
)

# ==================================================
# Load Work Descriptions
# ==================================================

work_descriptions = []

for filename in sorted(
    os.listdir(
        INPUT_WORK_DESCRIPTIONS_DIR
    )
):

    if not filename.endswith(
        ".json"
    ):
        continue

    filepath = os.path.join(
        INPUT_WORK_DESCRIPTIONS_DIR,
        filename
    )

    try:

        with open(
            filepath,
            encoding="utf-8"
        ) as f:

            wd = json.load(f)

        work_descriptions.append(
            wd
        )

    except Exception as e:

        print(
            f"Failed to load "
            f"{filename}: {e}"
        )

print(
    f"Loaded {len(work_descriptions)} "
    f"work descriptions."
)


# ==================================================
# System Prompt
# ==================================================

SYSTEM_PROMPT = """
You are a Statistics Canada workforce transformation,
work description, and GSBPM expert.

TASK

Identify work descriptions that are implicated by
a GSBPM subprocess and its associated strategic
drivers.

The GSBPM subprocess represents an area of
statistical production.

The associated drivers represent transformation
forces that are expected to influence how that
subprocess will be performed in the future and
provide evidence of emerging technologies,
capabilities, workforce changes, and new ways
of working.

Each driver includes:

- description
- technology themes
- capability themes
- workforce implications
- impact assessment
- impact mechanisms

These fields explain what is changing,
why it is changing, and how work is
expected to evolve.

Determine which work descriptions are
materially connected to this subprocess
and are most likely to experience changes
in responsibilities, activities, tools,
methods, knowledge requirements, or
skill requirements because of the associated
drivers.

For each implicated work description:

- explain what aspect of the subprocess is relevant
- explain what capability or responsibility is needed
- explain how the work description satisfies that need
- explain how the associated drivers are expected to affect the work
- reference evidence from the work description
- where applicable, identify technologies, capabilities,
  workforce implications, or impact mechanisms that are
  expected to influence how the work is performed in the future

RULES

- Include ALL relevant work descriptions.
- Do not invent work descriptions.
- Use only supplied work descriptions.
- Consider:

    - key activities
    - responsibilities
    - knowledge requirements
    - communication requirements
    - contextual knowledge
    - technology requirements
    - future operating models
    - workforce implications

- Consider the cumulative effect of multiple drivers.
- Focus on future-state impacts, not only
  current responsibilities.
- Use technology themes, capability themes,
  workforce implications, and impact mechanisms
  as evidence of future change.
- Be explicit about why a work description
  will be affected.
- Do not identify a work description solely because
  it currently supports the subprocess.
  There must be a plausible connection between the
  work description and the future-state changes
  described by the associated drivers.

RELEVANCE

Relevance must be:

- High
- Medium
- Low

Definitions:

High:
The work description directly performs,
manages, designs, governs, or is heavily
affected by the subprocess and associated
drivers.

Medium:
The work description regularly contributes
to the subprocess or will experience
meaningful changes because of the associated
drivers.

Low:
The work description has limited but
plausible involvement in the subprocess
or may be indirectly affected by the
associated drivers.

RETURN JSON ONLY

JSON Schema:

{
  "gsbpm_id": "...",
  "gsbpm_name": "...",
  "drivers": [...],
  "implicated_work_descriptions": [
    {
      "title": "<title of work-description>",

      "classification":
        "<classification of role>",

      "relevance":
        "High|Medium|Low",

      "justification":
        "<explanation of the implicated aspect of the subprocess, \
articulation of the capability or responsibility required, \
justification for why this particular work description is relevant, \
description of how the associated drivers are expected to affect \
the work, and reference to relevant evidence from the work description>"
    },

    "<additional implicated work descriptions>"
  ]
}

JUSTIFICATION REQUIREMENTS:

The justification is the primary analytical field.
 
For each implicated work description, the
justification should:
 

1. Identify the relevant aspect of the GSBPM subprocess.

2. Explain the capability, responsibility, expertise,

or operational need involved.

3. Explain why the specific work description is relevant.

4. Explain how the associated drivers contribute to

future changes in the work.

themes, capability themes, workforce implications,

and impact mechanisms.

5. Where applicable, reference relevant technology
themes, capability themes, workforce implications,
and impact mechanisms.

6. Reference supporting evidence from the work description.

7. Be specific, detailed, and evidence-based.




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