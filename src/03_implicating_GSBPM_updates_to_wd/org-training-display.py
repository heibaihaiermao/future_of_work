import json
from pathlib import Path

JSON_PATH = Path("./data/organizational-structure-document/org.json")


# ============================================================
# Load organization structure
# ============================================================

with open(JSON_PATH, "r", encoding="utf-8") as f:
    org_data = json.load(f)


# ============================================================
# Build indexes
# ============================================================

field_index = {}

for field in org_data:

    field_num = str(field["field number"])

    field_index[field_num] = {
        "object": field,
        "branches": {}
    }

    for branch in field.get("branches", []):

        branch_name = str(branch["branch name"])

        field_index[field_num]["branches"][branch_name] = {
            "object": branch,
            "divisions": {}
        }

        for division in branch.get("divisions", []):

            division_name = str(division["division name"])

            field_index[field_num]["branches"][branch_name]["divisions"][division_name] = {
                "object": division,
                "positions": {}
            }

            for position in division.get("positions", []):

                key = (
                    f'{position.get("group and level", "")}'
                    f' | Job Family: {position.get("job family", "")}'
                    f' | Position Title: {position.get("position title", "")}'
                )

                field_index[field_num]["branches"][branch_name]["divisions"][division_name]["positions"][key] = position


# ============================================================
# CLI Helpers
# ============================================================

def prompt_selection(title, options):

    print(f"\n{title}")
    print("-" * len(title))

    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")

    while True:

        try:
            choice = int(input("\nSelect option: "))

            if 1 <= choice <= len(options):
                return options[choice - 1]

            print("Invalid selection.")

        except ValueError:
            print("Please enter a number.")


def print_training_list(title, training_list):

    print(f"\n{title}")
    print("-" * len(title))

    if not training_list:
        print("No training assigned.")
        return

    for idx, training in enumerate(training_list, start=1):

        print(f"\n[{idx}]")

        if isinstance(training, dict):

            for k, v in training.items():
                print(f"{k}: {v}")

        else:
            print(training)


# ============================================================
# Interactive Selection
# ============================================================

def run():

    # -----------------------------------
    # FIELD
    # -----------------------------------

    selected_field = prompt_selection(
        "Select Field",
        sorted(field_index.keys())
    )

    field_data = field_index[selected_field]

    # -----------------------------------
    # BRANCH
    # -----------------------------------

    selected_branch = prompt_selection(
        f"Select Branch (Field {selected_field})",
        sorted(field_data["branches"].keys())
    )

    branch_data = field_data["branches"][selected_branch]

    # -----------------------------------
    # DIVISION
    # -----------------------------------

    selected_division = prompt_selection(
        f"Select Division (Branch {selected_branch})",
        sorted(branch_data["divisions"].keys())
    )

    division_data = branch_data["divisions"][selected_division]

    # -----------------------------------
    # POSITION
    # -----------------------------------

    selected_position = prompt_selection(
        f"Select Position (Division {selected_division})",
        sorted(division_data["positions"].keys())
    )

    position_data = division_data["positions"][selected_position]

    # =====================================================
    # Display training
    # =====================================================

    branch_obj = branch_data["object"]
    division_obj = division_data["object"]

    print("\n")
    print("=" * 60)
    print("POSITION IDENTIFIED")
    print("=" * 60)

    print(f"Field: {selected_field}")
    print(f"Branch: {selected_branch}")
    print(f"Division: {selected_division}")
    print(f"Position: {selected_position}")

    print_training_list(
        "Branch Level Training",
        branch_obj.get("branch level training", [])
    )

    print_training_list(
        "Division Level Training",
        division_obj.get("division level training", [])
    )

    print_training_list(
        "Position Training",
        position_data.get("position training", [])
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    run()