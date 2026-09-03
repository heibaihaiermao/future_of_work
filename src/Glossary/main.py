import os
from dotenv import load_dotenv

from config import INPUT_DIR
from config import GSBPM_FILE
from config import OUTPUT_DIR
from config import EMBEDDING_MODEL

import json
from glossary_parser import load_skill_gaps
from glossary_parser import load_gsbpm_implications
from glossary_generator import GlossaryGenerator
from excel_exporter import export_glossary
from gsbpm_matcher import GSBPMMatcher


def main():

    gsbpm_data = load_gsbpm_implications(GSBPM_FILE)

    dotenv_path="../05_forecast_skill_gaps_of_wd/model.env"
    
    load_dotenv(dotenv_path)

    print("ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))
    print("DEPLOYMENT:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))

    generator = GlossaryGenerator(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-03-01-preview",
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    )

    matcher = GSBPMMatcher(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-03-01-preview",
        embedding_model=EMBEDDING_MODEL
    )

    matcher.build_gsbpm_index(
        gsbpm_data
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for input_file in INPUT_DIR.glob("*.json"):

        print(
            f"\nProcessing {input_file.name}"
        )

        records = load_skill_gaps(
            input_file
        )

        glossary_entries = []

        for record in records:

            print(
                f"Generating: "
                f"{record['development area']}"
            )

            matched_gsbpm = matcher.find_matches(
                record
            )

            result = generator.generate_entry(
                record,
                matched_gsbpm
            )

            glossary_entries.append(
                {
                    "skill_gap":
                        record["development area"],

                    "explanation":
                        result["explanation"],

                    "justification":
                        result["justification"]
                }
            )

        position_name = input_file.stem.replace(
            "_future_skills",
            ""
        )

        output_json = (
            OUTPUT_DIR /
            f"{position_name}_glossary.json"
        )

        with open(
            output_json,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                glossary_entries,
                f,
                indent=2,
                ensure_ascii=False
            )

        output_xlsx = (
            OUTPUT_DIR /
            f"{position_name}_glossary.xlsx"
        )

        export_glossary(
            glossary_entries,
            output_xlsx
        )

        print(
            f"Created {position_name}"
        )

    print("Done")


if __name__ == "__main__":
    main()