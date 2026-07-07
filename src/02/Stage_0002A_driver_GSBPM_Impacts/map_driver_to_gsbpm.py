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

INPUT_DRIVERS = "input/consolidated_drivers.json"
INPUT_GSBPM = "input/GSBPM_v5_2.json"

OUTPUT_FILE = "output/driver_gsbpm_impacts.json"


# ==================================================
# Azure OpenAI Client
# ==================================================

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)


# ==================================================
# Load Drivers
# ==================================================

with open(INPUT_DRIVERS, encoding="utf-8") as f:
    drivers = json.load(f)

print(
    f"Loaded {len(drivers)} drivers."
)


# ==================================================
# Load GSBPM
# ==================================================

with open(INPUT_GSBPM, encoding="utf-8") as f:
    gsbpm = json.load(f)


# ==================================================
# Flatten GSBPM
# ==================================================

flat_gsbpm = []

for phase_record in gsbpm:

    phase = phase_record.get("phase", {})

    phase_id = phase.get("id", "")
    phase_name = phase.get("title", "")

    phase_description = phase_record.get(
        "description",
        ""
    )

    for subprocess in phase_record.get(
            "sub-processes", []):

        flat_gsbpm.append({
            "phase_id": phase_id,
            "phase_name": phase_name,
            "phase_description": phase_description,
            "gsbpm_id": subprocess.get("id", ""),
            "gsbpm_name": subprocess.get("text", ""),
            "gsbpm_description": subprocess.get(
                "description",
                ""
            )
        })

print(
    f"Loaded {len(flat_gsbpm)} GSBPM subprocesses."
)

# ==================================================
# Process Drivers
# ==================================================

results = []

for driver in drivers:

    print(
        f"Processing {driver['driver_id']} "
        f"- {driver['driver']}"
    )

    driver_context = {
        "driver_id": driver["driver_id"],
        "driver": driver["driver"],
        "description": driver.get(
            "description",
            ""
        )
    }

    prompt = f"""
You are a Statistics Canada and GSBPM expert.

Given a strategic driver and a list of GSBPM
subprocesses, identify which subprocesses are
materially affected.

Only include affected subprocesses.

For each affected subprocess provide:

- phase_id
- phase_name
- gsbpm_id
- gsbpm_name
- gsbpm_description
- impact_strength
- impact

impact_strength must be:
High, Medium, or Low.

Return JSON only.

Driver:

{json.dumps(driver_context, indent=2, ensure_ascii=False)}

GSBPM:

{json.dumps(flat_gsbpm, ensure_ascii=False)}

Return:

{{
    "driver_id": "{driver['driver_id']}",
    "driver": "{driver['driver']}",
    "affected_subprocesses": [
        {{
            "phase_id": "...",
            "phase_name": "...",
            "gsbpm_id": "...",
            "gsbpm_name": "...",
            "gsbpm_description": "...",
            "impact_strength": "High|Medium|Low",
            "impact": "..."
        }}
    ]
}}
"""

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in GSBPM, "
                    "statistical modernization, "
                    "and organizational transformation. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    try:

        result = json.loads(content)

        results.append(result)

        print(
            f"✓ Completed "
            f"{driver['driver_id']}"
        )

    except json.JSONDecodeError:

        print(
            f"✗ Failed parsing JSON for "
            f"{driver['driver_id']}"
        )

        print(content)


# ==================================================
# Save Results
# ==================================================

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
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"\nGenerated impacts for "
    f"{len(results)} drivers."
)

print(
    f"Saved to: {OUTPUT_FILE}"
)

