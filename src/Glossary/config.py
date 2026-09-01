from pathlib import Path

INPUT_FILE = Path("./input/Data_Production_and_Dissemination_Officer_future_skills.json")
GSBPM_FILE = Path("../02/Implicate_on_GSBPM/output/gsbpm_implications.json")
OUTPUT_FILE = Path("./output/skill_gap_glossary.xlsx")

# OpenAI / Azure OpenAI settings

MODEL_NAME = "gpt-5.4"

EMBEDDING_MODEL = "text-embedding-3-small"

TOP_GSBPM_MATCHES = 3

SYSTEM_PROMPT = """
You are an HR capability analyst.

Given:
- skill gap name
- description
- change to work
- justification

Generate:

1. explanation
A concise 2-3 sentence explanation that explains the capability
in plain professional language.

2. justification
A concise 2-3 sentence explanation describing why this skill gap was selected, referencing the exact change drivers (Mandate letters, Departmental Plan, Statcan 2030 Future Slide) and how it  determined and influenced the future work requirements.

Return JSON only.

{
    "explanation": "...",
    "justification": "..."
}
"""