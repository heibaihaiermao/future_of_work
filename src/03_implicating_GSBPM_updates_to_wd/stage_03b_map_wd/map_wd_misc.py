import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI


# ==================================================
# Configuration
# ==================================================

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv(
    "AZURE_OPENAI_API_KEY"
)

AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT"
)

AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION"
)

AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT"
)

INPUT_GSBPM = (
    "input/gsbpm_driver_impacts.json"
)

WORK_DESCRIPTION_DIR = (
    "input/work-descriptions-raw"
)

OUTPUT_FILE = (
    "output/wd_gsbpm_impacts.json"
)


# ==================================================
# Azure OpenAI Client
# ==================================================

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)


# ==================================================
# Load GSBPM Records
# ==================================================

with open(
    INPUT_GSBPM,
    encoding="utf-8"
) as f:

    gsbpm_records = json.load(f)

print(
    f"Loaded {len(gsbpm_records)} "
    f"GSBPM records."
)


# ==================================================
# Load Work Descriptions
# ==================================================

work_descriptions = []

for filename in sorted(
    os.listdir(
        WORK_DESCRIPTION_DIR
    )
):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(
        WORK_DESCRIPTION_DIR,
        filename
    )

    try:

        with open(
            filepath,
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        classification = data.get(
            "Classification",
            ""
        )

        for position in data.get(
            "Positions",
            []
        ):

            work_descriptions.append(
                {
                    "source_file":
                        filename,

                    "work_description":
                        {
                            "Classification":
                                data.get(
                                    "Classification"
                                ),

                            "Positions":
                                [position]
                        }
                }
            )

    except Exception as e:

        print(
            f"Failed loading "
            f"{filename}: {e}"
        )

print(
    f"Loaded "
    f"{len(work_descriptions)} "
    f" work descriptions."
)


# ==================================================
# System Prompt
# ==================================================

SYSTEM_PROMPT = """
You are a Statistics Canada workforce
transformation, work description,
and GSBPM expert.

TASK

Evaluate a single work description against
a set of GSBPM subprocesses and their
associated strategic drivers.

Determine which GSBPM subprocesses are
materially connected to the work description.

The GSBPM subprocesses contain information
about future-state transformation including:

- strategic drivers
- technology themes
- capability themes
- workforce implications
- impact assessments
- impact mechanisms

Use this information to determine
how the work description is expected
to be affected now and in the future.

For each implicated subprocess:

- explain the relevant aspect of the subprocess
- explain the capability or responsibility involved
- explain how the work description fulfills that need
- explain how the associated drivers contribute to future changes
- reference evidence from the work description

RULES

- Include ALL relevant subprocesses.
- Do not invent responsibilities.
- Use only supplied information.
- Consider future-state impacts.
- Consider the cumulative effect of
  multiple drivers.
- Reference technology themes,
  capability themes, workforce implications,
  and impact mechanisms when relevant.
- Be explicit about why the subprocess
  is relevant.

RELEVANCE

High:
The work description directly performs,
manages, designs, governs, or is heavily
affected by the subprocess and associated
drivers.

Medium:
The work description regularly contributes
to the subprocess or is expected to
experience meaningful change.

Low:
The work description has plausible
but limited involvement.

RETURN VALID JSON ONLY.

JSON Schema:

{
  "Classification":
    "<Classification from the supplied work description>",

  "Positions": [
    {
      "Job Family Number":
        "<Job Family Number from the supplied work description>",

      "Group/Level":
        "<Group/Level from the supplied work description>",

      "Position Title":
        "<Position Title from the supplied work description>",

      "Supervisor Position":
        "<Supervisor Position from the supplied work description>",

      "Branch/Division":
        "<Branch/Division from the supplied work description>",

      "implicated_gsbpm": [
        {
          "gsbpm_id": "...",

          "gsbpm_name": "...",

          "relevance":
            "High|Medium|Low",

          "justification":
            "<explanation of the implicated aspect of the subprocess, articulation of the capability, responsibility, expertise, or operational need involved, justification of why the work description is relevant, description of how associated drivers are expected to affect the work, and reference to supporting evidence from the work description>"
        }
      ]
    }
  ]
}

JUSTIFICATION REQUIREMENTS

1. Identify the relevant aspect of
   the GSBPM subprocess.

2. Explain the capability,
   responsibility, expertise,
   or operational need involved.

3. Explain why the specific work
   description is relevant.

4. Explain how the associated drivers
   contribute to future changes
   in the work.

5. Where applicable, reference relevant:

   - technology themes
   - capability themes
   - workforce implications
   - impact mechanisms

6. Reference supporting evidence
   from the work description.

7. Be specific, detailed,
   and evidence-based.
"""


# ==================================================
# Process Work Descriptions
# ==================================================

results = []

print(
    f"GSBPM JSON size: "
    f"{len(json.dumps(gsbpm_records)):,} chars"
)

for wd in work_descriptions:

    work_description = wd.get(
        "work_description",
        {}
    )

    positions = work_description.get(
        "Positions",
        []
    )

    title = (
        positions[0].get(
            "Position Title",
            "Unknown Position"
        )
        if positions
        else "Unknown Position"
    )

    classification = (
        work_description.get(
            "Classification",
            ""
        )
    )

    print(
        f"\nProcessing "
        f"{title} "
        f"({classification})"
    )

    user_prompt = f"""
Work Description:

{json.dumps(
    wd,
    indent=2,
    ensure_ascii=False
)}

GSBPM Records:

{json.dumps(
    gsbpm_records,
    indent=2,
    ensure_ascii=False
)}
"""

    try:

        response = (
            client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content":
                            SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content":
                            user_prompt
                    }
                ]
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        result = json.loads(
            content
        )

        results.append(
            result
        )

        print(
            f"✓ Completed "
            f"{title}"
        )

    except json.JSONDecodeError:

        print(
            f"✗ JSON parse failed for "
            f"{title}"
        )

        print(content)

    except Exception as e:

        print(
            f"✗ Failed "
            f"{title}"
        )

        print(str(e))


# ==================================================
# Save Results
# ==================================================

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

print(
    f"\nGenerated "
    f"{len(results)} WD assessments."
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)