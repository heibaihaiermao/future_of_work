import os
from dotenv import load_dotenv

from config import INPUT_FILE
from config import OUTPUT_FILE

from glossary_parser import load_skill_gaps
from glossary_generator import GlossaryGenerator
from excel_exporter import export_glossary


def main():

    records = load_skill_gaps(INPUT_FILE)

    dotenv_path="../05_forecast_skill_gaps_of_wd/model.env"
    
    load_dotenv(dotenv_path)

    generator = GlossaryGenerator(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-03-01-preview",
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    )

    glossary_entries = []

    for record in records:

        print(
            f"Generating: "
            f"{record['development area']}"
        )

        result = generator.generate_entry(
            record
        )

        glossary_entries.append(
            {
                "skill_gap":
                    record["development area"],

                "explanation":
                    result["explanation"],

                "justification":
                    result["justification"],
            }
        )

    export_glossary(
        glossary_entries,
        OUTPUT_FILE
    )

    print("Done")


if __name__ == "__main__":
    main()