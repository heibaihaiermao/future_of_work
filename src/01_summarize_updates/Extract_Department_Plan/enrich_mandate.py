import json
import os
from dotenv import load_dotenv

from openai import AzureOpenAI

# ======================================
# CONFIG
# ======================================

INPUT_FILE = "output_json/departmental_plan.json"
OUTPUT_FILE = "output_json/departmental_plan_enriched.json"

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")

# ======================================
# PROMPT
# ======================================

SYSTEM_PROMPT = """
You are assisting a Statistics Canada Future of Work analysis project.

The input is a Statistics Canada Departmental Plan.

Do NOT identify skill gaps.
Do NOT recommend training.
Do NOT recommend learning resources.

Your task is to identify:

1. Strategic context
2. Strategic priorities
3. Transformation initiatives
4. Technology themes
5. Capability themes
6. Workforce implications
7. Key risks

Preserve the original wording wherever possible.

Return ONLY valid JSON.

Schema:

{
  "document_type": "departmental_plan",

  "year": "",

  "strategic_context": [],

  "strategic_priorities": [
    {
      "priority_id": "",
      "title": "",
      "original_description": "",

      "technology_themes": [],
      "capability_themes": [],
      "workforce_implications": [],

      "evidence_quotes": []
    }
  ],

  "transformation_initiatives": [
    {
      "initiative": "",
      "description": "",
      "technology_themes": [],
      "workforce_implications": []
      "evidence_quotes": []
    }
  ],

  "key_risks": [
    {
      "risk": "",
      "description": ""
    }
  ]
}
"""


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    plan = json.load(f)

important_sections = [
    "Key priorities",
    "Summary of planned results",
    "From the Chief Statistician",
    "Core responsibility: Statistical information",
    "Internal services",
    "Related government priorities",
    "Key risks"
]

content = ""

for section in plan["sections"]:

    if section["title"] in important_sections:

        content += (
            f"\n\nSECTION: {section['title']}\n\n"
            f"{section['content']}"
        )


print(f"Processing: {plan['title']}")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": plan["full_text"]
        }
    ],
    response_format={"type": "json_object"}
)

try:

    enriched = json.loads(
        response.choices[0].message.content
    )

except Exception as e:

    print("Failed parsing response")
    print(e)

    enriched = {}

enriched["source_url"] = plan["source_url"]
enriched["source_title"] = plan["title"]
enriched["source_content"] = plan["full_text"]
enriched["source_sections"] = plan["sections"]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        enriched,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"Saved: {OUTPUT_FILE}")