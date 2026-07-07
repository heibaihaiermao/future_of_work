import json
import os
from dotenv import load_dotenv

from openai import AzureOpenAI

# ======================================
# CONFIG
# ======================================

INPUT_FILE = "output_json/mandate_letters.json"
OUTPUT_FILE = "output_json/mandate_letters_enriched.json"

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
You are assisting a Future of Work analysis project.

The input is a Statistics Canada mandate letter.
The mandate letter may contain:

- strategic context
- corporate priorities
- modernization initiatives
- workforce expectations
- technology directions

Extract these explicitly.

Do not infer skill gaps.
Do not recommend training.
Do not recommend learning resources.

Preserve the original wording of each priority.
Your task is NOT to identify skill gaps.

Your task is to identify:

1. Field information
2. Strategic context
3. Priorities
4. Technology themes
5. Capability themes
6. Workforce implications

Return ONLY valid JSON.

Schema:

{
  "document_type": "mandate_letter",

  "field": {
    "name": "",
    "recipient": "",
    "date": ""
  },

  "strategic_context": [],

  "priorities": [
    {
      "priority_id": "",
      "title": "",

      "original_description": "",

      "technology_themes": [],

      "capability_themes": [],

      "workforce_implications": []

      "evidence_quotes": []
    }
  ]
}
"""


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    mandates = json.load(f)

results = []

for mandate in mandates:

    print(f"Processing: {mandate['title']}")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": mandate["content"]
            }
        ],
        response_format={"type": "json_object"}
    )

    try:

        enriched = json.loads(
            response.choices[0].message.content
        )

        enriched["source_url"] = mandate["url"]
        enriched["source_title"] = mandate["title"]
        enriched["source_url"] = mandate["url"]
        enriched["source_title"] = mandate["title"]
        enriched["source_content"] = mandate["content"] 

        results.append(enriched)

    except Exception as e:

        print(
            f"Failed parsing {mandate['title']}"
        )

        print(e)


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

print(f"Saved: {OUTPUT_FILE}")