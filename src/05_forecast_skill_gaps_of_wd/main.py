"""
===============================================================================
File: main.py

Purpose:
    Orchestrates the Future Skills Forecasting Pipeline by integrating data
    loading, work description retrieval, prompt generation, Large Language
    Model (LLM) analysis, response parsing, and output persistence.

    The pipeline forecasts future workforce competencies and identifies
    emerging skill requirements based on organizational priorities and
    anticipated business process changes.

Author:
    Souroosh Memarian

Created:
    2026-07-21

Last Modified:
    2026-07-21

Version:
    1.0.0

Dependencies:
    - config
    - loader
    - finder
    - prompt_builder
    - analyzer
    - parser
    - writer
    - pathlib

Workflow:
    1. Load work descriptions.
    2. Load organizational inputs.
    3. Load GSBPM impact assessments.
    4. Identify the relevant work description for each position.
    5. Generate a contextual system prompt.
    6. Submit business process updates for AI-driven analysis.
    7. Parse and validate model responses.
    8. Persist forecasting results to JSON output files.
    9. Skip records with existing output files to support resumable
       execution.

Outputs:
    - One JSON file per work description containing forecasted future
      skills, competency gaps, and workforce implications.

Notes:
    - Output filenames are automatically sanitized to ensure valid file
      paths across operating systems.
    - Existing output files are not overwritten unless manually removed.
    - Designed to support workforce planning, modernization initiatives,
      digital transformation, automation adoption, and AI readiness
      assessments.
    - The pipeline relies on Azure OpenAI for competency forecasting and
      future skills analysis.

===============================================================================
"""

from config import *

from data_loader import (
    load_json
)

from work_description_finder import (
    find_work_description
)

from prompt_builder import (
    build_system_prompt
)

from analyzer import (
    FutureSkillsAnalyzer
)

from response_parser import (
    parse_response
)

from output_writer import (
    save_json
)

from pathlib import Path


def make_output_path(title):

    safe_title = (
        title
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    return (
        OUTPUT_DIR
        /
        f"{safe_title}_future_skills.json"
    )


def main():

    work_descriptions = load_json(
        WORK_DESCRIPTIONS_FILE
    )

    implications = load_json(
        GSBPM_IMPACTS_FILE
    )


    for implication in implications:

        title = implication["title"]

        classification = (
            implication["classification"]
        )

        output_path = (
            make_output_path(title)
        )

        if output_path.exists():

            print(
                f"Skipping {title}"
            )

            continue

        work_description = (
            find_work_description(
                work_descriptions,
                classification,
                title
            )
        )

        system_prompt = (
            build_system_prompt(
                work_description
            )
        )

        analyzer = (
            FutureSkillsAnalyzer(
                system_prompt
            )
        )

        results = []

        for update in implication[
            "implicated phases and sub-processes"
        ]:

            raw = (
                analyzer
                .analyze_update(
                    str(update)
                )
            )

            parsed = parse_response(raw)

            results.append(parsed)

        save_json(
            results,
            output_path
        )

        print(
            f"Saved: {output_path.name}"
        )


if __name__ == "__main__":
    main()