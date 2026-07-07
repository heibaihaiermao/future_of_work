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
# Reduce payload size
# --------------------------

records = []

for record in evidence:

    records.append({
        "source": record["source"],
        "source_id": record["source_id"],
        "source_section": record["source_section"],
        "text": record["text"],
        "metadata": record.get("metadata", {})
    })


# --------------------------
# Prompt
# --------------------------

prompt = f"""
You are a strategic planning analyst.

You are given normalized evidence extracted from:

- Departmental Plans
- Future Vision material
- Mandate Letters

Your task is to identify the major enterprise-wide
drivers of transformation.

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

Rules:

1. Consolidate similar concepts.
2. Do not create duplicate drivers.
3. Drivers should be concise.
4. Drivers must be supported by evidence.
5. Return valid JSON only.
6. Return between 8 and 15 drivers.

For each driver provide:

- driver
- description
- evidence

For evidence include:

- source
- source_id
- quote

Evidence records:

{json.dumps(records, ensure_ascii=False)}

Return format:

[
  {{
    "driver": "AI and Automation",
    "description": "Enterprise adoption of AI, automation and intelligent workflows.",
    "evidence": [
      {{
        "source": "...",
        "source_id": "...",
        "quote": "..."
      }}
    ]
  }}
]
"""


# --------------------------
# Call Model
# --------------------------

response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=[
        {
            "role": "system",
            "content": (
                "You are an expert strategic planning analyst."
            )
        },
        {
            "role": "user",
            "content": prompt
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

    print("Failed to parse JSON response.")
    print(content)
    raise


# --------------------------
# Save Output
# --------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        drivers,
        f,
        indent=2,
        ensure_ascii=False
    )


print(
    f"Generated {len(drivers)} drivers."
)