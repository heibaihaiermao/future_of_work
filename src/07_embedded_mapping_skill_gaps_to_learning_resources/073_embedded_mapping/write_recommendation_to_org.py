import json
import logging
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

RECOMMENDATIONS_DIR = Path(
    r".\data\0733_recommendations"
)

ORG_FILE = Path(
    r"..\..\03_implicating_GSBPM_updates_to_wd"
    r"\data\organizational-structure-document\org.json"
)

OUTPUT_FILE = Path(
    r"..\..\03_implicating_GSBPM_updates_to_wd"
    r"\data\organizational-structure-document\org_updated.json"
)


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# Helper functions
# ============================================================

def load_json(file_path):
    """
    Load a JSON file with error handling.
    Returns None if the file cannot be loaded.
    """

    try:
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return None

        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        logger.error(
            f"Invalid JSON in file '{file_path}': "
            f"line {e.lineno}, column {e.colno}: {e.msg}"
        )
        return None

    except OSError as e:
        logger.error(
            f"Unable to read file '{file_path}': {e}"
        )
        return None

    except Exception as e:
        logger.exception(
            f"Unexpected error while reading '{file_path}': {e}"
        )
        return None


def extract_position_title(filename):
    """
    Extract the position title from a recommendation filename.

    Example:
        Data_Production_and_Dissemination_Officer_-_recommendations.json

    becomes:
        Data Production and Dissemination Officer
    """

    suffix = "_-_recommendations.json"

    if not filename.endswith(suffix):
        return None

    position_name = filename[:-len(suffix)]

    if not position_name:
        return None

    # Convert underscores to spaces.
    position_name = position_name.replace("_", " ")

    # Normalize accidental whitespace.
    position_name = " ".join(position_name.split())

    return position_name


def normalize_title(title):
    """
    Normalize position titles for comparison.

    This makes matching resilient to:
    - leading/trailing whitespace
    - repeated spaces
    - capitalization differences
    """

    if not isinstance(title, str):
        return ""

    return " ".join(title.strip().lower().split())


def find_position_training(org_data, target_title):
    """
    Scan the entire organizational structure and find all positions
    whose 'position title' matches target_title.

    Returns:
        list of matching position dictionaries
    """

    matches = []

    normalized_target = normalize_title(target_title)

    if not isinstance(org_data, list):
        logger.error(
            "Organization data is not a list. "
            "Expected the top-level org.json structure to be a list."
        )
        return matches

    for field_index, field in enumerate(org_data):

        if not isinstance(field, dict):
            logger.warning(
                f"Skipping invalid field at index {field_index}: "
                f"expected object, got {type(field).__name__}"
            )
            continue

        branches = field.get("branches", [])

        if not isinstance(branches, list):
            logger.warning(
                f"Field '{field.get('field number', '<unknown>')}' "
                f"has invalid 'branches'; expected a list."
            )
            continue

        for branch_index, branch in enumerate(branches):

            if not isinstance(branch, dict):
                logger.warning(
                    f"Skipping invalid branch at field index "
                    f"{field_index}, branch index {branch_index}."
                )
                continue

            divisions = branch.get("divisions", [])

            if not isinstance(divisions, list):
                logger.warning(
                    f"Branch '{branch.get('branch name', '<unknown>')}' "
                    f"has invalid 'divisions'; expected a list."
                )
                continue

            for division_index, division in enumerate(divisions):

                if not isinstance(division, dict):
                    logger.warning(
                        f"Skipping invalid division at field index "
                        f"{field_index}, branch index {branch_index}, "
                        f"division index {division_index}."
                    )
                    continue

                positions = division.get("positions", [])

                if not isinstance(positions, list):
                    logger.warning(
                        f"Division '{division.get('division name', '<unknown>')}' "
                        f"has invalid 'positions'; expected a list."
                    )
                    continue

                for position_index, position in enumerate(positions):

                    if not isinstance(position, dict):
                        logger.warning(
                            f"Skipping invalid position at "
                            f"field={field_index}, "
                            f"branch={branch_index}, "
                            f"division={division_index}, "
                            f"position={position_index}"
                        )
                        continue

                    position_title = position.get("position title")

                    if position_title is None:
                        logger.warning(
                            f"Position is missing 'position title' at "
                            f"field={field_index}, "
                            f"branch={branch_index}, "
                            f"division={division_index}, "
                            f"position={position_index}"
                        )
                        continue

                    if normalize_title(position_title) == normalized_target:
                        matches.append(position)

    return matches


def append_training(position, recommendation_data, source_file):
    """
    Append filtered course recommendations to the position's
    'position training' array.

    Only the following fields are retained when they exist:
        - title
        - description
        - id
        - title_en
        - description_en
        - link_en
        - OfferedBy

    Returns:
        True  -> at least one recommendation was appended
        False -> no new recommendation was appended
    """

    if "position training" not in position:
        logger.warning(
            f"Position '{position.get('position title', '<unknown>')}' "
            f"is missing 'position training'. Creating it."
        )
        position["position training"] = []

    if not isinstance(position["position training"], list):
        logger.warning(
            f"Position '{position.get('position title', '<unknown>')}' "
            f"has invalid 'position training'. Replacing it with an empty list."
        )
        position["position training"] = []

    # Fields we want to preserve from each course recommendation.
    fields_to_keep = [
        "title",
        "description",
        "id",
        "title_en",
        "description_en",
        "link_en",
        "OfferedBy"
    ]

    appended = False

    # recommendation_data is expected to be a dictionary such as:
    #
    # {
    #     "AI/automation output review": [
    #         {...course 1...},
    #         {...course 2...}
    #     ],
    #     "another category": [
    #         {...course 3...}
    #     ]
    # }
    #
    # Iterate through every recommendation category.
    if not isinstance(recommendation_data, dict):
        logger.warning(
            f"Recommendation file '{source_file.name}' does not contain "
            f"a JSON object at the top level. Skipping."
        )
        return False

    for category, recommendations in recommendation_data.items():

        if not isinstance(recommendations, list):
            logger.warning(
                f"Category '{category}' in '{source_file.name}' "
                f"is not a list. Skipping category."
            )
            continue

        # Process every actual course recommendation.
        for recommendation in recommendations:

            if not isinstance(recommendation, dict):
                logger.warning(
                    f"Invalid recommendation under category '{category}' "
                    f"in '{source_file.name}'. Expected an object. Skipping."
                )
                continue

            # Keep only the requested fields that actually exist.
            filtered_recommendation = {
                key: recommendation[key]
                for key in fields_to_keep
                if key in recommendation
            }

            # Don't append an empty object.
            if not filtered_recommendation:
                logger.warning(
                    f"Recommendation under category '{category}' "
                    f"in '{source_file.name}' contains none of the "
                    f"requested fields. Skipping."
                )
                continue

            # Prevent exact duplicate courses.
            if filtered_recommendation in position["position training"]:
                logger.warning(
                    f"Recommendation '{filtered_recommendation.get('title', '<unknown>')}' "
                    f"is already present for position "
                    f"'{position.get('position title', '<unknown>')}'. "
                    f"Skipping duplicate."
                )
                continue

            position["position training"].append(
                filtered_recommendation
            )

            appended = True

            logger.info(
                f"Added course "
                f"'{filtered_recommendation.get('title', '<unknown>')}' "
                f"to '{position.get('position title', '<unknown>')}'."
            )

    return appended


# ============================================================
# Main processing
# ============================================================

def main():

    logger.info("Starting recommendation-to-organization mapping.")

    # --------------------------------------------------------
    # Validate input directories/files
    # --------------------------------------------------------

    if not RECOMMENDATIONS_DIR.exists():
        logger.error(
            f"Recommendations directory does not exist: "
            f"{RECOMMENDATIONS_DIR}"
        )
        return

    if not RECOMMENDATIONS_DIR.is_dir():
        logger.error(
            f"Recommendations path is not a directory: "
            f"{RECOMMENDATIONS_DIR}"
        )
        return

    # --------------------------------------------------------
    # Load organizational structure
    # --------------------------------------------------------

    logger.info(
        f"Loading organizational structure from: {ORG_FILE}"
    )

    org_data = load_json(ORG_FILE)

    if org_data is None:
        logger.error(
            "Unable to load organizational structure. "
            "Processing aborted."
        )
        return

    logger.info(
        "Organizational structure loaded successfully."
    )

    # --------------------------------------------------------
    # Find recommendation files
    # --------------------------------------------------------

    try:
        recommendation_files = sorted(
            RECOMMENDATIONS_DIR.glob("*.json")
        )

    except OSError as e:
        logger.error(
            f"Unable to scan recommendations directory: {e}"
        )
        return

    if not recommendation_files:
        logger.warning(
            f"No JSON files found in: {RECOMMENDATIONS_DIR}"
        )
        return

    logger.info(
        f"Found {len(recommendation_files)} JSON recommendation file(s)."
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    files_processed = 0
    files_skipped = 0
    positions_matched = 0
    positions_not_found = 0
    recommendations_appended = 0
    duplicates_skipped = 0

    # --------------------------------------------------------
    # Process each recommendation file
    # --------------------------------------------------------

    for recommendation_file in recommendation_files:

        logger.info(
            f"Processing: {recommendation_file.name}"
        )

        # Extract position title from filename.
        position_title = extract_position_title(
            recommendation_file.name
        )

        if position_title is None:
            logger.warning(
                f"Skipping file with unexpected filename format: "
                f"{recommendation_file.name}"
            )
            files_skipped += 1
            continue

        logger.info(
            f"Extracted position title: '{position_title}'"
        )

        # Load recommendation JSON.
        recommendation_data = load_json(
            recommendation_file
        )

        if recommendation_data is None:
            logger.warning(
                f"Skipping recommendation file because it "
                f"could not be loaded: {recommendation_file}"
            )
            files_skipped += 1
            continue

        # Find matching positions.
        matching_positions = find_position_training(
            org_data,
            position_title
        )

        if not matching_positions:
            logger.warning(
                f"No matching position found for "
                f"'{position_title}' "
                f"(source: {recommendation_file.name})"
            )

            positions_not_found += 1
            continue

        positions_matched += len(matching_positions)

        logger.info(
            f"Found {len(matching_positions)} matching position(s) "
            f"for '{position_title}'."
        )

        # Append recommendation to every matching position.
        for position in matching_positions:

            position_name = position.get(
                "position title",
                "<unknown>"
            )

            appended = append_training(
                position,
                recommendation_data,
                recommendation_file
            )

            if appended:
                recommendations_appended += 1

                logger.info(
                    f"Added recommendation to '{position_name}'."
                )

            else:
                duplicates_skipped += 1

        files_processed += 1

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    try:

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                org_data,
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info(
            f"Successfully wrote updated organization structure to: "
            f"{OUTPUT_FILE}"
        )

    except OSError as e:
        logger.error(
            f"Unable to write output file '{OUTPUT_FILE}': {e}"
        )
        return

    except Exception as e:
        logger.exception(
            f"Unexpected error while writing output: {e}"
        )
        return

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    logger.info("=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)

    logger.info(
        f"Recommendation files found: {len(recommendation_files)}"
    )

    logger.info(
        f"Recommendation files processed: {files_processed}"
    )

    logger.info(
        f"Files skipped: {files_skipped}"
    )

    logger.info(
        f"Matching positions found: {positions_matched}"
    )

    logger.info(
        f"Position titles with no match: {positions_not_found}"
    )

    logger.info(
        f"Recommendations appended: {recommendations_appended}"
    )

    logger.info(
        f"Duplicate recommendations skipped: {duplicates_skipped}"
    )

    logger.info(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()