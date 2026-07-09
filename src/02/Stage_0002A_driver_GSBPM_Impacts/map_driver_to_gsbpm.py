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

INPUT_DRIVERS = "input/drivers.json"
INPUT_GSBPM = "input/GSBPM_v5_2.json"

OUTPUT_FILE = (
    "output/driver_gsbpm_impacts.json"
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
# Load Drivers
# ==================================================

with open(
    INPUT_DRIVERS,
    encoding="utf-8"
) as f:

    drivers = json.load(f)

print(
    f"Loaded {len(drivers)} drivers."
)

# ==================================================
# Load GSBPM
# ==================================================

with open(
    INPUT_GSBPM,
    encoding="utf-8"
) as f:

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
# System Prompt
# ==================================================

SYSTEM_PROMPT = """
You are an expert in:

- Statistics Canada
- Workforce Transformation
- GSBPM
- Statistical Modernization

TASK

Given a strategic driver and a collection of
GSBPM subprocesses:

Identify which subprocesses are materially
affected by the driver.

The driver contains:

- description
- technology themes
- capability themes
- workforce implications

These explain HOW the driver creates change.

Use all of these fields when assessing
GSBPM impacts.

RULES

1. Only return affected subprocesses.
2. Consider direct and significant impacts.
3. Ignore weak or unrelated impacts.
4. Impact strength must be:
   - High
   - Medium
   - Low

5. Use technology themes,
   capability themes,
   and workforce implications
   when explaining impacts.

6. Be specific.

For each affected subprocess provide:

- phase_id
- phase_name
- gsbpm_id
- gsbpm_name
- gsbpm_description
- impact_strength
- impact
- impact_mechanisms

impact_mechanisms should identify the
specific technologies, capabilities,
or workforce implications causing
the impact.

Return JSON only.

Schema:

{
  "driver": "...",
  "technology_themes": [...],
  "capability_themes": [...],
  "workforce_implications": [...],
  "affected_subprocesses": [
    {
      "phase_id": "...",
      "phase_name": "...",

      "gsbpm_id": "...",
      "gsbpm_name": "...",
      "gsbpm_description": "...",

      "impact_strength":
        "High|Medium|Low",

      "impact":
        "...",

      "impact_mechanisms": [
        "..."
      ]
    }
  ]
}
"""

# ==================================================
# Process Drivers
# ==================================================

results = []

for driver in drivers:

    print(
        f"Processing "
        f"- "
        f"{driver['driver']}"
    )

    driver_context = {


        "driver":
            driver["driver"],

        "description":
            driver.get(
                "description",
                ""
            ),

        "why_this_is_a_driver":
            driver.get(
                "why_this_is_a_driver",
                ""
            ),

        "technology_themes":
            driver.get(
                "technology_themes",
                []
            ),

        "capability_themes":
            driver.get(
                "capability_themes",
                []
            ),

        "workforce_implications":
            driver.get(
                "workforce_implications",
                []
            )
    }

    USER_PROMPT = f"""
Driver:

{json.dumps(
    driver_context,
    indent=2,
    ensure_ascii=False
)}

GSBPM Subprocesses:

{json.dumps(
    flat_gsbpm,
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
                            USER_PROMPT
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
            f"{driver['driver']}"
        )

    except Exception as e:

        print(
            f"✗ Failed "
            f"{driver['driver']}"
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
    f"\nGenerated impacts for "
    f"{len(results)} drivers."
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)