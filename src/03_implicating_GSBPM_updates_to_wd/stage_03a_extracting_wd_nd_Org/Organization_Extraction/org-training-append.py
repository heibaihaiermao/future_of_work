import json
from pathlib import Path

JSON_PATH = Path("organizational-structure-document/org.json")

TRAINING_FIELDS = [
    "name",
    "when should an employee take this training",
    "sme",
    "competencies",
    "target learners",
    "target group and level",
    "prerequisite",
    "cost",
    "delivery method",
    "link_en",
    "bilingual",
    "offered_by",
    "requirement",
    "link_fr"
]


# =====================================================
# Load JSON
# =====================================================

with open(JSON_PATH, "r", encoding="utf-8") as f:
    org = json.load(f)


# =====================================================
# Utility Functions
# =====================================================

def save_json():

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(org, f, indent=4, ensure_ascii=False)

    print("\n✓ JSON updated successfully")


def choose_option(title, options):

    print(f"\n{title}")
    print("-" * len(title))

    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:

        try:

            choice = int(input("\nSelect option: "))

            if 1 <= choice <= len(options):
                return options[choice - 1]

        except ValueError:
            pass

        print("Invalid selection.")


def build_training_object():

    print("\nPaste training information.")
    print("Use TAB separators.")
    print()

    print("Expected order:")
    for i, field in enumerate(TRAINING_FIELDS, start=1):
        print(f"{i}. {field}")

    print()

    raw = input("> ")

    parts = raw.split("\t")

    while len(parts) < len(TRAINING_FIELDS):
        parts.append("")

    training = {}

    for field, value in zip(TRAINING_FIELDS, parts):
        training[field] = value.strip()

    return training


# =====================================================
# Field Selection
# =====================================================

field_options = [
    str(field["field number"])
    for field in org
]

selected_field_num = choose_option(
    "Select Field",
    sorted(field_options)
)

field_obj = next(
    f for f in org
    if str(f["field number"]) == selected_field_num
)


# =====================================================
# Branch Selection
# =====================================================

branch_options = [
    str(branch["branch name"])
    for branch in field_obj["branches"]
]

selected_branch_name = choose_option(
    "Select Branch",
    sorted(branch_options)
)

branch_obj = next(
    b for b in field_obj["branches"]
    if str(b["branch name"]) == selected_branch_name
)


# =====================================================
# Branch Action
# =====================================================

branch_action = choose_option(
    "Branch Action",
    [
        "Navigate to Division",
        "Append Branch-Level Training"
    ]
)

if branch_action == "Append Branch-Level Training":

    training = build_training_object()

    branch_obj.setdefault(
        "branch level training",
        []
    ).append(training)

    save_json()

    raise SystemExit


# =====================================================
# Division Selection
# =====================================================

division_options = [
    str(div["division name"])
    for div in branch_obj["divisions"]
]

selected_division_name = choose_option(
    "Select Division",
    sorted(division_options)
)

division_obj = next(
    d for d in branch_obj["divisions"]
    if str(d["division name"]) == selected_division_name
)


# =====================================================
# Division Action
# =====================================================

division_action = choose_option(
    "Division Action",
    [
        "Navigate to Position",
        "Append Division-Level Training"
    ]
)

if division_action == "Append Division-Level Training":

    training = build_training_object()

    division_obj.setdefault(
        "division level training",
        []
    ).append(training)

    save_json()

    raise SystemExit


# =====================================================
# Position Selection
# =====================================================

position_options = []

for position in division_obj["positions"]:

    display = (
        f'{position["group and level"]}'
        f' | Job Family: {position["job family"]}'
    )

    position_options.append(display)

selected_position = choose_option(
    "Select Position",
    position_options
)

position_obj = next(
    p for p in division_obj["positions"]
    if (
        f'{p["group and level"]}'
        f' | Job Family: {p["job family"]}'
    ) == selected_position
)


# =====================================================
# Position Action
# =====================================================

training = build_training_object()

position_obj.setdefault(
    "position training",
    []
).append(training)

save_json()