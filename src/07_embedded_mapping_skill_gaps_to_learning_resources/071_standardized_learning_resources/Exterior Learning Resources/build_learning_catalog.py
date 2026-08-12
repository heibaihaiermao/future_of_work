
import json
import os
import re
import time
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv
from openai import AzureOpenAI



load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2025-04-01-preview",
)

MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")

INPUT_XLSX = "External_Learning_Resource.xlsx"   # <- point at your file
SHEET_NAME = "in"

INDICATOR_MAP_FILE = "indicator_map.json"

OUTPUT_FILE = "external_output.json"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


PRICE_PER_1M_INPUT = 2.00
PRICE_PER_1M_CACHED_INPUT = 0.50  # ~75% off — applies automatically to the
                                   # repeated framework portion of the stage-2
                                   # prompt once Azure's prompt cache warms up
PRICE_PER_1M_OUTPUT = 8.00

usage_totals = {
    "input_tokens": 0,
    "cached_input_tokens": 0,
    "output_tokens": 0,
    "calls": 0,
}


def print_running_cost():
    uncached_input = usage_totals["input_tokens"] - usage_totals["cached_input_tokens"]
    cost = (
        uncached_input * PRICE_PER_1M_INPUT / 1_000_000
        + usage_totals["cached_input_tokens"] * PRICE_PER_1M_CACHED_INPUT / 1_000_000
        + usage_totals["output_tokens"] * PRICE_PER_1M_OUTPUT / 1_000_000
    )
    cache_rate = (
        usage_totals["cached_input_tokens"] / usage_totals["input_tokens"] * 100
        if usage_totals["input_tokens"] else 0
    )
    print(
        f"  [usage so far: {usage_totals['calls']} calls, "
        f"{usage_totals['input_tokens']:,} in ({cache_rate:.0f}% cached) / "
        f"{usage_totals['output_tokens']:,} out tokens, ~${cost:.2f}]"
    )



def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def clean_json_response(text):
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def llm_call(system_prompt, user_prompt):
    """Calls the model with basic retry/backoff. Tracks token usage/cost
    as a running total. Raises on final failure."""
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            if getattr(response, "usage", None):
                usage_totals["input_tokens"] += response.usage.prompt_tokens
                usage_totals["output_tokens"] += response.usage.completion_tokens
                usage_totals["calls"] += 1

                details = getattr(response.usage, "prompt_tokens_details", None)
                cached = getattr(details, "cached_tokens", 0) if details else 0
                usage_totals["cached_input_tokens"] += cached or 0

            content = response.choices[0].message.content
            return json.loads(clean_json_response(content))

        except Exception as ex:
            last_error = ex
            print(f"  LLM call failed (attempt {attempt}/{MAX_RETRIES}): {ex}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)

    raise last_error



indicator_map = load_json(INDICATOR_MAP_FILE)




def load_rows(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet)

    df = df.rename(
        columns={
            "name": "title",
            "description": "description",
            "why_recommend": "why_recommend",
            "Language of Training": "language_of_training",
            "Time to complete": "duration",
            "Target Learner (Beginner, Intermediate, Advanced)": "target_learner",
            "Cost": "cost",
            "score_of_content": "score",
            "link": "link",
        }
    )

    df = df.dropna(subset=["title"])
    df = df.fillna("")

    return df.to_dict(orient="records")




DOMAIN_TO_ORG = {
    "www.kaggle.com": "Kaggle",
    "learn.microsoft.com": "Microsoft Learn",
    "docs.aws.amazon.com": "AWS Documentation",
    "docs.oracle.com": "Oracle Documentation",
    "www.youtube.com": "YouTube",
    "www.geeksforgeeks.org": "GeeksforGeeks",
    "pll.harvard.edu": "Harvard PLL",
    "cs50.harvard.edu": "Harvard CS50",
    "www.w3schools.com": "W3Schools",
    "openclassrooms.com": "OpenClassrooms",
    "www.freecodecamp.org": "freeCodeCamp",
    "git-scm.com": "Git",
    "developer.mozilla.org": "MDN Web Docs",
    "www.atlassian.com": "Atlassian",
    "cran.r-project.org": "CRAN (The R Project)",
    "www.edx.org": "edX",
    "r4ds.hadley.nz": "R for Data Science",
    "docs.python.org": "Python Software Foundation",
    "docs.gitlab.com": "GitLab",
    "docs.github.com": "GitHub",
    "www.tutorialspoint.com": "TutorialsPoint",
    "www.datacamp.com": "DataCamp",
    "www.bing.com": "Microsoft Bing",
    "www.kubeflow.org": "Kubeflow",
    "docs.n8n.io": "n8n",
    "www.tensorflow.org": "TensorFlow",
    "pytorch.org": "PyTorch",
    "python.langchain.com": "LangChain",
    "docs.qgis.org": "QGIS",
    "grafikart.fr": "Grafikart",
    "github.com": "GitHub",
    "docs.docker.com": "Docker",
    "kubernetes.io": "Kubernetes",
    "code.visualstudio.com": "Visual Studio Code",
    "pandas.pydata.org": "pandas",
    "scikit-learn.org": "scikit-learn",
    "react.dev": "React",
    "fr.react.dev": "React",
    "expressjs.com": "Express.js",
    "dotnet.microsoft.com": ".NET (Microsoft)",
    "learn.arcgis.com": "Esri ArcGIS",
    "www.databricks.com": "Databricks",
    "shiny.posit.co": "Posit (Shiny)",
    "jupyterlab.readthedocs.io": "JupyterLab",
    "archive.ics.uci.edu": "UCI Machine Learning Repository",
}


def offered_by_from_link(link):
    """Look up a known org name from the link's domain; fall back to a
    title-cased guess from the domain itself. Review/extend
    DOMAIN_TO_ORG as new sources show up in the sheet."""
    try:
        domain = urlparse(link).netloc.lower()
    except Exception:
        return ""

    if domain in DOMAIN_TO_ORG:
        return DOMAIN_TO_ORG[domain]

    # Fallback: strip common subdomains + www, take the main label
    parts = domain.split(".")
    parts = [p for p in parts if p not in ("www", "docs", "learn", "developer")]
    if not parts:
        return domain
    return parts[0].capitalize()


COST_EN = {"free": "N", "paid": "Y"}
COST_FR = {"free": "Non", "paid": "Oui"}


def associated_cost(cost_value):
    """Returns (AssociatedCost, AssociatedCost-fr). Anything not
    recognizably 'free' is treated as paid — adjust if your Cost column
    ever uses other labels."""
    normalized = str(cost_value).strip().lower()
    key = "free" if normalized.startswith("free") else "paid"
    return COST_EN[key], COST_FR[key]


_DURATION_RANGE_RE = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*hours?\s*$", re.IGNORECASE)
_DURATION_SINGLE_RE = re.compile(r"^\s*(\d+)\s*hours?\s*$", re.IGNORECASE)
_DURATION_LESS_THAN_RE = re.compile(r"^\s*less than\s*(\d+)\s*hours?\s*$", re.IGNORECASE)


def duration_to_fr(duration_value):
    """Deterministic translation for the 'X hours' / 'X-Y hours' /
    'Less than X hours' patterns this sheet uses. Anything that doesn't
    match (e.g. the 'N/A (dataset repository...)' rows) is passed
    through unchanged rather than guessed at."""
    text = str(duration_value).strip()

    m = _DURATION_RANGE_RE.match(text)
    if m:
        lo, hi = m.group(1), m.group(2)
        return f"{lo} à {hi} heures"

    m = _DURATION_SINGLE_RE.match(text)
    if m:
        n = m.group(1)
        return "1 heure" if n == "1" else f"{n} heures"

    m = _DURATION_LESS_THAN_RE.match(text)
    if m:
        n = m.group(1)
        return "Moins d'une heure" if n == "1" else f"Moins de {n} heures"

    return text  # unrecognized pattern — leave as-is, don't mistranslate


DELIVERY_METHOD_EN = "Online"
DELIVERY_METHOD_FR = "En ligne"



# STAGE 1 — PROFILE + COMPETENCY MAPPING (merged into one call)
# Profile extraction and competency mapping used to be two separate LLM
# round trips. They're merged here: it's the same reasoning chain, and
# splitting it only meant paying for two system-prompt sends and two
# generations per row instead of one. The framework dump below is the
# expensive, repeated part of this prompt — it's what Azure's automatic
# prompt caching (1024+ token identical prefix) should be discounting
# after the first call. See print_running_cost() for the real hit rate.

MAPPING_SYSTEM_PROMPT = f"""
You are an expert learning-content analyzer and Government of Canada
competency mapping engine.

COMPETENCY FRAMEWORK

{json.dumps(indicator_map, indent=2, ensure_ascii=False)}

Instructions:

1. Analyze the resource's title, description, why_recommend note,
   target learner level, and stated duration.
2. Build a short internal profile (skills, tools, topics, learning
   outcomes) — return it under "profile" for traceability, but don't
   over-invest here; it's a means to competency selection, not the
   final product.
3. Rewrite the description into 2-4 sentences of professional,
   catalog-ready language, grounded only in the given inputs — do not
   invent details the source material doesn't support.
4. Select the most relevant competencies (1-3 of them).
5. Select the most appropriate proficiency level for each — proficiency
   levels are competency-specific; some competencies only have one
   level defined, don't invent others.
6. Select ONLY indicators supported by evidence, copied verbatim from
   the framework — never paraphrase an indicator.
7. Each competency object has ONLY "competency", "proficiency", and
   "indicators" — no per-competency description field.
8. Return valid JSON only.

Required Output:

{{
  "profile": {{
    "summary": "",
    "skills": [],
    "tools": [],
    "topics": [],
    "learning_outcomes": []
  }},
  "description": "",
  "competencies": [
    {{
      "competency": "",
      "proficiency": "",
      "indicators": []
    }}
  ]
}}
"""


def map_competencies(row):
    prompt = f"""
RESOURCE

{json.dumps({
    "title": row["title"],
    "description": row["description"],
    "why_recommend": row["why_recommend"],
    "target_learner": row["target_learner"],
    "duration": row["duration"],
}, indent=2, ensure_ascii=False)}

Generate the profile + competency record as specified.
"""

    return llm_call(MAPPING_SYSTEM_PROMPT, prompt)



# STAGE 2 — FRENCH TRANSLATION (French-taught rows only)


TRANSLATION_SYSTEM_PROMPT = """
You are a professional EN->FR translator for a Government of Canada
learning catalog. Translate naturally and accurately; do not add or
omit information. Return JSON only:

{
  "title_fr": "",
  "description_fr": ""
}
"""


def translate_to_french(title_en, description_en):
    prompt = f"""
title: {title_en}
description: {description_en}
"""
    return llm_call(TRANSLATION_SYSTEM_PROMPT, prompt)



# VALIDATION
def validate_output(record):
    """Checks the model's competency selections against the real
    framework structure: indicator_map[competency][proficiency] = list
    of indicator strings. Flags unknown competencies/proficiencies and
    any indicator that isn't verbatim from the framework (a sign the
    model paraphrased or invented one instead of selecting it)."""

    if "competencies" not in record:
        return record

    for comp in record["competencies"]:
        competency = comp.get("competency")
        proficiency = comp.get("proficiency")
        indicators = comp.get("indicators", [])

        if competency not in indicator_map:
            print(f"  WARNING: Unknown competency: {competency}")
            continue

        proficiencies_for_competency = indicator_map[competency]

        if proficiency not in proficiencies_for_competency:
            print(
                f"  WARNING: Invalid proficiency '{proficiency}' "
                f"for competency '{competency}'"
            )
            continue

        valid_indicators = set(proficiencies_for_competency[proficiency])
        for indicator in indicators:
            if indicator not in valid_indicators:
                print(
                    f"  WARNING: Indicator not found verbatim in framework "
                    f"for '{competency}' / '{proficiency}': {indicator[:80]}..."
                )

    return record


# RECORD ASSEMBLY
def build_record(row):
    is_french_taught = str(row["language_of_training"]).strip().lower() == "french"

    mapped = map_competencies(row)
    mapped = validate_output(mapped)

    description_en = mapped.get("description") or row["description"]

    title_fr, description_fr, link_fr = "", "", ""
    if is_french_taught:
        translated = translate_to_french(row["title"], description_en)
        title_fr = translated.get("title_fr", "")
        description_fr = translated.get("description_fr", "")
        link_fr = row["link"]  # the sheet's link already points to the French-taught version

    offered_by = offered_by_from_link(row["link"])
    cost_en, cost_fr = associated_cost(row["cost"])

    return {
        "title_en": row["title"],
        "description_en": description_en,
        "link_en": row["link"],
        "title_fr": title_fr,
        "description_fr": description_fr,
        "link_fr": link_fr,
        "DeliveryMethod": DELIVERY_METHOD_EN,
        "DeliveryMethod-fr": DELIVERY_METHOD_FR,
        "duration": row["duration"],
        "duration_fr": duration_to_fr(row["duration"]),
        "OfferedBy": offered_by,
        "OfferedBy-fr": offered_by,  # org names left as-is; edit per-row if a French org name differs
        "AssociatedCost": cost_en,
        "AssociatedCost-fr": cost_fr,
        "competencies": mapped.get("competencies", []),
    }



# PIPELINE (resumable, checkpointed after every row)
def load_existing_results():
    if os.path.exists(OUTPUT_FILE):
        try:
            existing = load_json(OUTPUT_FILE)
            return {rec["link_en"]: rec for rec in existing if rec.get("link_en")}
        except Exception:
            return {}
    return {}


def run():
    rows = load_rows(INPUT_XLSX, SHEET_NAME)
    total = len(rows)

    results_by_link = load_existing_results()
    if results_by_link:
        print(f"Resuming — {len(results_by_link)} rows already done.")

    for idx, row in enumerate(rows, start=1):
        link = row.get("link")
        title = row.get("title", "Untitled")

        if link in results_by_link:
            continue

        print(f"[{idx}/{total}] {title}")

        try:
            record = build_record(row)
            results_by_link[link] = record

        except Exception as ex:
            print(f"  ERROR — skipping this row: {ex}")
            continue

        print_running_cost()

        # checkpoint after every row so a crash doesn't lose progress
        save_json(list(results_by_link.values()), OUTPUT_FILE)

    print(f"Done. {len(results_by_link)}/{total} rows written to {OUTPUT_FILE}")
    print_running_cost()


if __name__ == "__main__":
    run()