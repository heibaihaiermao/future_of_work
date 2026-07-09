import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

# --------------------------
# Configuration
# --------------------------

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

INPUT_FILE = "input/normalized_evidence.json"
OUTPUT_FILE = "output/drivers.json"

# --------------------------
# Azure OpenAI Client
# --------------------------

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)

# --------------------------
# Load Evidence
# --------------------------

with open(INPUT_FILE, encoding="utf-8") as f:
    evidence = json.load(f)

# --------------------------
# Prepare Records
# --------------------------

records = []
record_lookup = {}

for idx, record in enumerate(evidence):

    slim_record = {
        "record_id": idx,
        "source": record["source"],
        "source_id": record["source_id"],
        "source_section": record["source_section"],
        "text": record["text"]
    }

    records.append(slim_record)

    record_lookup[idx] = record

# --------------------------
# System Prompt
# --------------------------

SYSTEM_PROMPT = """
You are an expert strategic planning analyst.

TASK

Identify the major enterprise-wide drivers
of transformation.

A driver is a recurring force, trend,
technology, capability, operating model,
or organizational priority that appears
across multiple evidence records.

Examples:

- AI and Automation
- Alternative and Administrative Data
- Enterprise Platforms and Infrastructure
- Workforce Transformation
- Cyber Security and Privacy

RULES

1. Consolidate similar concepts.
2. Do not create duplicate drivers.
3. Return between 8 and 15 drivers.
4. Drivers must be supported by evidence.
5. Prefer operationally meaningful drivers.
6. Avoid vague strategic labels.
7. Focus on technologies, workforce,
   capabilities, modernization,
   governance and future operating models.

IMPORTANT

Return supporting record_ids only.

Do not return quotes.

Do not generate technology themes,
capability themes, or workforce implications.

Your role is only to:

1. identify drivers
2. assign supporting record_ids

These attributes will be derived
programmatically from supporting evidence.

The script will derive those automatically.

OUTPUT JSON ONLY

Schema:

[
  {
    "driver": "AI and Automation",
    "description":
      "Enterprise adoption of AI and automation.",

    "why_this_is_a_driver":
      "Repeated references to AI assistants,
       automation and AI-enabled workflows.",

    "record_ids": [12, 18, 35]
  }
]

Return JSON only.
Do not use markdown.
Do not use code fences.
"""

# --------------------------
# User Prompt
# --------------------------

USER_PROMPT = f"""
Evidence Records:

{json.dumps(records, ensure_ascii=False)}
"""

# --------------------------
# Call Model
# --------------------------

response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": USER_PROMPT
        }
    ],
    temperature=0
)

# --------------------------
# Parse Response
# --------------------------

content = response.choices[0].message.content

try:

    drivers = json.loads(content)

except json.JSONDecodeError:

    print(content)
    raise

# --------------------------
# Build Driver Objects
# --------------------------

final_drivers = []

for driver in drivers:

    technology_themes = set()
    capability_themes = set()
    workforce_implications = set()

    supporting_evidence = []

    for record_id in driver.get(
        "record_ids",
        []
    ):

        record = record_lookup.get(
            record_id
        )

        if not record:
            continue

        supporting_evidence.append(
            {
                "source":
                    record["source"],

                "source_id":
                    record["source_id"],

                "source_section":
                    record["source_section"],

                "quote":
                    record["text"]
            }
        )

        metadata = record.get(
            "metadata",
            {}
        )

        technology_themes.update(
            metadata.get(
                "technology_themes",
                []
            )
        )

        capability_themes.update(
            metadata.get(
                "capability_themes",
                []
            )
        )

        workforce_implications.update(
            metadata.get(
                "workforce_implications",
                []
            )
        )

    final_drivers.append(
        {
            "driver":
                driver["driver"],

            "description":
                driver["description"],

            "why_this_is_a_driver":
                driver.get(
                    "why_this_is_a_driver",
                    ""
                ),

            "technology_themes":
                sorted(
                    technology_themes
                ),

            "capability_themes":
                sorted(
                    capability_themes
                ),

            "workforce_implications":
                sorted(
                    workforce_implications
                ),

            "evidence":
                supporting_evidence
        }
    )

# --------------------------
# Save Output
# --------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_drivers,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Generated {len(final_drivers)} drivers."
)