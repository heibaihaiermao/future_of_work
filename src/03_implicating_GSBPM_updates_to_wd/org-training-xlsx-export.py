import json
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    Alignment,
    PatternFill,
    Border,
    Side
)
from openpyxl.utils import get_column_letter


JSON_PATH = Path("./data/organizational-structure-document/org_updated.json")
OUTPUT_DIR = Path("./data/organizational-structure-document/xlsx_output/division_training_exports")


# ============================================================
# Excel Template
# ============================================================

TEMPLATE_DESCRIPTION = (
    'This tab will summarize position-specific training that employees in each '
    'position in the Division would need to take. One tab for each position in '
    'the Division. This tab should include:\n'
    '1) All required and recommended training that may be position specific, '
    'as submitted by stakeholder responses AND\n'
    '2) LLM-recommended training that can satisfy the observed skill gap\n\n'
    'All AI recommended training should be coded as "Newly recommended" under column M.'
)

HEADERS = [
    "Name of Training",
    "Training Category",
    "Training Provider",
    "When should an employee take this training?",
    "Does this training develop subject-matter expertise in a specific domain?",
    "What skills, knowledge or competency does this training target?",
    "Matched Skill Gap",
    "Skill Gap Explanation",
    "Skill Gap Justification",
    "Classification and Levels of Target Learner",
    "Are there pre-requistites to take it?",
    "Is there a cost and if so, what is it?",
    "How is this training delivered?",
    "Where can Learners access this training?",
    "Training Language of Delivery",
    "Is this training required or recommended?",
]

EXAMPLES = [
    "Name of courses, readings or onboarding requirements",
    "Course/Training, Reading, Conference, Network",
    "(Statcan,CSPS, Name of External Provider)",
    "(Onboarding/Early/Ongoing)",
    "(Yes/No)",
    "(List Competencies in 5-6 words)",
    "(Matched glossary skill gap)",
    "(Glossary explanation)",
    "(Glossary justification)",
    "(Reason this future skill gap was identified)",
    "(List all Job Titles or grouping of positions that the training applies to)",
    "(Yes/No)",
    "",
    "(Online Training, In-person Training, Reading, Conference, Networking Group, Seminar)",
    "(Share link to the course registration OR course code if in LMS)",
    "(English, French)",
    "(Required/Currently Recommended/ Newly Recommended)",
]


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

            field_index[field_num]["branches"][branch_name]["divisions"][
                division_name
            ] = {
                "object": division,
                "positions": {}
            }

            for position in division.get("positions", []):

                key = (
                    f'{position.get("group and level", "")}'
                    f' | Job Family: {position.get("job family", "")}'
                    f' | Position Title: {position.get("position title", "")}'
                )

                field_index[field_num]["branches"][branch_name]["divisions"][
                    division_name
                ]["positions"][key] = position


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
# Training Data Helpers
# ============================================================

def clean_url(value):
    """
    Converts Markdown-style URLs such as:

        [https://example.com](https://example.com)

    into:

        https://example.com

    Also handles plain URLs.
    """

    if not value:
        return ""

    value = str(value).strip()

    # Markdown link:
    # [display text](actual url)
    match = re.search(r"\]\((https?://[^)]+)\)", value)

    if match:
        return match.group(1).strip()

    # Plain URL
    match = re.search(r"https?://\S+", value)

    if match:
        return match.group(0).rstrip(" )")

    return value


def get_training_category(training):
    """
    Converts the source training type into the categories expected
    by the Excel template.

    Examples:
        Article -> Reading
        Course -> Course/Training
        Conference -> Conference
        Network -> Network
    """

    training_type = str(training.get("type", "")).strip()
    delivery_method = str(training.get("DeliveryMethod", "")).strip()

    combined = f"{training_type} {delivery_method}".lower()

    if "article" in combined:
        return "Reading"

    if "conference" in combined:
        return "Conference"

    if "network" in combined:
        return "Network"

    if "seminar" in combined:
        return "Seminar"

    if "course" in combined or "training" in combined:
        return "Course/Training"

    if "reading" in combined:
        return "Reading"

    # Fall back to source value if it doesn't match a known category.
    return training_type or delivery_method


def get_delivery_method(training):
    """
    Gets the English delivery method.
    """

    value = training.get("DeliveryMethod", "")

    if value:
        value = str(value).strip()

    return value


def get_competencies(training):
    """
    Converts:

        "competencies": [
            {
                "competency": "Data Processing",
                "proficiency": "Foundational",
                "indicators": [...]
            }
        ]

    into a compact cell value.

    Currently uses the competency names rather than the indicators.
    """

    competencies = training.get("competencies", [])

    if not competencies:
        return ""

    values = []

    for competency in competencies:

        if isinstance(competency, dict):

            name = competency.get("competency", "")

            if name:
                values.append(str(name).strip())

        elif competency:
            values.append(str(competency).strip())

    return "; ".join(values)


def get_target_learner(position):
    """
    Uses the organizational position rather than the broad course
    audience field.

    Example:

        EC-05 - Senior Analyst
    """

    group_level = str(position.get("group and level", "")).strip()
    position_title = str(position.get("position title", "")).strip()

    if group_level and position_title:
        return f"{group_level} - {position_title}"

    return group_level or position_title


def training_to_excel_row(training, position):
    """
    Converts one JSON training recommendation into one Excel row.

    All training supplied through position training is treated as:

        Newly Recommended
    """

    title = str(training.get("title_en", "")).strip()

    domain = str(training.get("domain", "")).strip()

    row = [
        title,

        get_training_category(training),

        str(training.get("OfferedBy", "")).strip(),

        "",  # When should employee take this training?

        "Yes" if domain else "",

        get_competencies(training),

        training.get(
            "matched_skill_gap",
            ""
        ),

        training.get(
            "skill_gap_explanation",
            ""
        ),

        training.get(
            "skill_gap_justification",
            ""
        ),

        get_target_learner(position),

        "",  # Prerequisites

        "",  # Cost

        get_delivery_method(training),

        clean_url(training.get("link_en", "")),

        "Both" if training.get("title_en") and training.get("title_fr") else "English",

        "Newly Recommended",
    ]

    return row


# ============================================================
# Excel Sheet Name Helpers
# ============================================================

def sanitize_sheet_name(name):
    """
    Excel worksheet names cannot contain:

        : \\ / ? * [ ]

    and cannot exceed 31 characters.
    """

    name = str(name)

    # Replace invalid Excel worksheet characters.
    name = re.sub(r'[:\\/?*\[\]]', "-", name)

    # Remove leading/trailing apostrophes.
    name = name.strip("'")

    # Excel maximum worksheet name length.
    name = name[:31]

    # Excel doesn't allow an empty worksheet name.
    return name or "Position"


def make_unique_sheet_name(base_name, used_names):
    """
    Ensures that shortened worksheet names remain unique.
    """

    base_name = sanitize_sheet_name(base_name)

    if base_name not in used_names:
        used_names.add(base_name)
        return base_name

    counter = 2

    while True:

        suffix = f" ({counter})"

        shortened = base_name[:31 - len(suffix)] + suffix

        if shortened not in used_names:
            used_names.add(shortened)
            return shortened

        counter += 1


def get_position_sheet_name(position, used_names):
    """
    Requested format:

        group and level + position title

    Example:

        EC-05 Senior Analyst
    """

    group_level = str(position.get("group and level", "")).strip()
    position_title = str(position.get("position title", "")).strip()

    base_name = f"{group_level} {position_title}".strip()

    return make_unique_sheet_name(base_name, used_names)


# ============================================================
# Excel Formatting
# ============================================================

def format_position_sheet(ws):

    # --------------------------------------------------------
    # Row 1: Description
    # --------------------------------------------------------

    ws["A1"] = TEMPLATE_DESCRIPTION

    ws["A1"].font = Font(
        bold=True,
        color="FF0000"
    )

    ws["A1"].fill = PatternFill(
        fill_type="solid",
        fgColor="D9D9D9"
    )

    ws["A1"].alignment = Alignment(
        wrap_text=True,
        vertical="top"
    )

    # Merge the description across all 13 columns.
    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=16
    )

    ws.row_dimensions[1].height = 100

    # --------------------------------------------------------
    # Row 3: Headers
    # --------------------------------------------------------

    for column, header in enumerate(HEADERS, start=1):

        cell = ws.cell(
            row=3,
            column=column,
            value=header
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="404040"
        )

        cell.alignment = Alignment(
            wrap_text=True,
            vertical="top"
        )

    ws.row_dimensions[3].height = 60

    # --------------------------------------------------------
    # Row 4: Examples / instructions
    # --------------------------------------------------------

    for column, example in enumerate(EXAMPLES, start=1):

        cell = ws.cell(
            row=4,
            column=column,
            value=example
        )

        cell.font = Font(
            color="000000"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="D9D9D9"
        )

        cell.alignment = Alignment(
            wrap_text=True,
            vertical="top"
        )

    ws.row_dimensions[4].height = 60

    # --------------------------------------------------------
    # Borders for template table cells
    # --------------------------------------------------------

    thin_black = Side(
        style="thin",
        color="000000"
    )

    border = Border(
        left=thin_black,
        right=thin_black,
        top=thin_black,
        bottom=thin_black
    )

    for row in range(3, 5):
        for column in range(1, 17):
            ws.cell(
                row=row,
                column=column
            ).border = border

    # --------------------------------------------------------
    # Column widths
    # --------------------------------------------------------

    widths = [
    35,
    25,
    20,
    25,
    25,
    40,

    40,

    80,

    100,

    40,

    25,
    25,
    30,
    50,
    25,
    25
    ]

    for column, width in enumerate(widths, start=1):
        ws.column_dimensions[
            get_column_letter(column)
        ].width = width

    # No freeze panes.

    # Enable filters for the actual training table.
    ws.auto_filter.ref = "A3:P4"

def add_training_rows(ws, position):

    training_list = position.get("position training", [])

    if not isinstance(training_list, list):
        print(
            f"Warning: position training is not a list for "
            f"{position.get('position title', 'Unknown Position')}"
        )
        return

    row_number = 5

    for training in training_list:

        # ----------------------------------------------------
        # Expected schema:
        #
        # {
        #   "score": ...,
        #   "id": ...,
        #   "title_en": ...,
        #   ...
        # }
        # ----------------------------------------------------

        if not isinstance(training, dict):
            print(
                f"Warning: skipping non-object training entry for "
                f"{position.get('position title', 'Unknown Position')}"
            )
            continue

        row = training_to_excel_row(
            training,
            position
        )

        for column, value in enumerate(row, start=1):

            cell = ws.cell(
                row=row_number,
                column=column,
                value=value
            )

            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top"
            )

        # Make the access URL clickable.
        url = clean_url(training.get("link_en", ""))

        if url.startswith("http"):

            link_cell = ws.cell(
                row=row_number,
                column=14
            )

            link_cell.hyperlink = url
            link_cell.style = "Hyperlink"

        row_number += 1

    # Update filter to include actual training rows.
    if row_number > 5:
        ws.auto_filter.ref = f"A3:P{row_number - 1}"

# ============================================================
# General Onboarding Requirement Template
# ============================================================

GENERAL_ONBOARDING_DESCRIPTION = (
    "This tab will summarize position-specific training that employees in each "
    "position in the Division would need to take. One tab for each position in "
    "the Division. This tab should include:\n"
    "1) All required and recommended training that may be position specific, "
    "as submitted by stakeholder responses AND\n"
    "2) LLM-recommended training that can satisfy the observed skill gap\n\n"
    'All AI recommended training should be coded as "Newly recommended" under column M.'
)

GENERAL_ONBOARDING_HEADERS = [
    "Name of Training",
    "Mandate Level",
    "Training Category",
    "Training Provider",
    "When should an employee take this training?",
    "What skills, knowledge or competency does this training target?",
    "Classification and Levels of Target Learner",
    "Are there pre-requistites to take it?",
    "Is there a cost and if so, what is it?",
    "How is this training delivered?",
    "Where can Learners access this training?",
    "Training Language of Delivery",
    "Is this training required or recommended?",
]

GENERAL_ONBOARDING_EXAMPLES = [
    "Name of courses, readings or onboarding requirements",
    "Agency requirement, Branch requirement, Divisional requirement",
    "Course/Training, Reading, Conference, Network",
    "(Statcan,CSPS, Name of External Provider)",
    "(Onboarding/Early/Ongoing)",
    "(List Competencies in 5-6 words)",
    "(List all Job Titles or grouping of positions that the training applies to)",
    "(Yes/No)",
    "",
    "(Online Training, In-person Training, Reading, Conference, Networking Group, Seminar)",
    "(Share link to the course registration OR course code if in LMS)",
    "(English, French)",
    "(Required/Currently Recommended/ Newly Recommended)",
]


def add_general_onboarding_requirement(ws):

    # --------------------------------------------------------
    # Row 1: Unique description
    # --------------------------------------------------------

    ws["A1"] = GENERAL_ONBOARDING_DESCRIPTION

    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=16
    )

    ws["A1"].font = Font(
        bold=True,
        color="FF0000"
    )

    ws["A1"].alignment = Alignment(
        wrap_text=True,
        vertical="top"
    )

    ws["A1"].fill = PatternFill(
        fill_type="solid",
        fgColor="D9D9D9"
    )

    ws.row_dimensions[1].height = 110

    # --------------------------------------------------------
    # Row 3: Unique headers
    # --------------------------------------------------------

    for column, header in enumerate(
        GENERAL_ONBOARDING_HEADERS,
        start=1
    ):

        cell = ws.cell(
            row=3,
            column=column,
            value=header
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="404040"
        )

        cell.alignment = Alignment(
            wrap_text=True,
            vertical="top"
        )

    ws.row_dimensions[3].height = 60

    # --------------------------------------------------------
    # Row 4: Unique description/instruction row
    # --------------------------------------------------------

    for column, example in enumerate(
        GENERAL_ONBOARDING_EXAMPLES,
        start=1
    ):

        cell = ws.cell(
            row=4,
            column=column,
            value=example
        )

        cell.font = Font(
            color="000000"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="D9D9D9"
        )

        cell.alignment = Alignment(
            wrap_text=True,
            vertical="top"
        )

    ws.row_dimensions[4].height = 60

    # --------------------------------------------------------
    # Borders
    # --------------------------------------------------------

    thin_black = Side(
        style="thin",
        color="000000"
    )

    border = Border(
        left=thin_black,
        right=thin_black,
        top=thin_black,
        bottom=thin_black
    )

    for row in range(3, 5):

        for column in range(1, 17):

            ws.cell(
                row=row,
                column=column
            ).border = border

    # --------------------------------------------------------
    # Column widths
    # --------------------------------------------------------

    widths = [
        35, 25, 20, 25, 25,
        40, 40, 25, 25, 30,
        50, 25, 25
    ]

    for column, width in enumerate(
        widths,
        start=1
    ):

        ws.column_dimensions[
            get_column_letter(column)
        ].width = width

    # Explicitly no freeze pane.
    ws.freeze_panes = None

    ws.auto_filter.ref = "A3:P4"
    ws["A1"] = (
        'This tab will summarize position-specific training that employees in each '
        'position in the Division would need to take. One tab for each position in '
        'the Division. This tab should include:\n\n'
        '1. All required and recommended training that may be position specific, '
        'as submitted by stakeholder responses AND\n\n'
        '2. LLM-recommended training that can satisfy the observed skill gap\n\n'
        'All AI recommended training should be coded as "Newly recommended" under column M.'
    )

    ws.merge_cells("A1:P1")

    # Description formatting
    ws["A1"].font = Font(
        bold=True,
        color="FF0000"
    )
    ws["A1"].fill = PatternFill(
        fill_type="solid",
        fgColor="D9D9D9"
    )
    ws["A1"].alignment = Alignment(
        wrap_text=True,
        vertical="top"
    )

    # Table headers
    for column, header in enumerate(GENERAL_ONBOARDING_HEADERS, start=1):

        cell = ws.cell(
            row=3,
            column=column,
            value=header
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="404040"
        )

        cell.alignment = Alignment(
            wrap_text=True,
            vertical="top"
        )

    # Description/instruction row
    for column, example in enumerate(GENERAL_ONBOARDING_EXAMPLES, start=1):

        cell = ws.cell(
            row=4,
            column=column,
            value=example
        )

        cell.font = Font(
            color="000000"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="D9D9D9"
        )

        cell.alignment = Alignment(
            wrap_text=True,
            vertical="top"
        )

    # Borders
    thin_black = Side(
        style="thin",
        color="000000"
    )

    border = Border(
        left=thin_black,
        right=thin_black,
        top=thin_black,
        bottom=thin_black
    )

    for row in range(3, 5):
        for column in range(1, 17):
            ws.cell(
                row=row,
                column=column
            ).border = border

    # Column widths
    widths = [
        35, 25, 20, 25, 25,
        40, 40, 25, 25, 30,
        50, 25, 25
    ]

    for column, width in enumerate(
        widths,
        start=1
    ):
        ws.column_dimensions[
            get_column_letter(column)
        ].width = width

    # No freeze pane
    ws.freeze_panes = None

# ============================================================
# Export Division
# ============================================================

def export_division_to_xlsx(
    field_number,
    branch_name,
    division_name,
    division_data
):
    """
    Creates one XLSX workbook for the selected Division.

    Workbook structure:

        General Onboarding Requirement
        EC-05 Senior Analyst
        EC-04 Junior Analyst
        ...
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    workbook = Workbook()

    # --------------------------------------------------------
    # First sheet: General Onboarding Requirement
    # --------------------------------------------------------

    general_ws = workbook.active
    general_ws.title = "General Onboarding Requirement"

    # Blank for now, as requested.
    add_general_onboarding_requirement(general_ws)

    # --------------------------------------------------------
    # Position sheets
    # --------------------------------------------------------

    used_sheet_names = {
        "General Onboarding Requirement"
    }

    positions = division_data.get("positions", {})

    for _, position in sorted(
        positions.items(),
        key=lambda item: (
            str(item[1].get("group and level", "")),
            str(item[1].get("position title", ""))
        )
    ):

        sheet_name = get_position_sheet_name(
            position,
            used_sheet_names
        )

        ws = workbook.create_sheet(
            title=sheet_name
        )

        # Build the requested template.
        format_position_sheet(ws)

        # Add position-specific training.
        add_training_rows(
            ws,
            position
        )

    # --------------------------------------------------------
    # Output filename
    # --------------------------------------------------------

    safe_division_name = re.sub(
        r'[<>:"/\\|?*]',
        "-",
        division_name
    )

    filename = (
        # f"{field_number} - "
        # f"{branch_name} - "
        f"{safe_division_name}.xlsx"
    )

    output_path = OUTPUT_DIR / filename

    workbook.save(output_path)

    return output_path


# ============================================================
# Display Division Training
# ============================================================

def display_division_training(division_data):

    division_obj = division_data["object"]

    print("\n")
    print("=" * 70)
    print("DIVISION TRAINING")
    print("=" * 70)

    print_training_list(
        "Division Level Training",
        division_obj.get("division level training", [])
    )

    print("\n")

    positions = division_data.get("positions", {})

    for position_key, position in positions.items():

        print("\n" + "-" * 70)
        print(f"POSITION: {position_key}")
        print("-" * 70)

        print_training_list(
            "Position Training",
            position.get("position training", [])
        )


# ============================================================
# Position Selection and Display
# ============================================================

def select_and_display_position(
    selected_division,
    division_data
):

    selected_position = prompt_selection(
        f"Select Position (Division {selected_division})",
        sorted(division_data["positions"].keys())
    )

    position_data = division_data["positions"][selected_position]

    branch_obj = division_data.get(
        "branch_object",
        {}
    )

    division_obj = division_data["object"]

    print("\n")
    print("=" * 60)
    print("POSITION IDENTIFIED")
    print("=" * 60)

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
# Division Menu
# ============================================================

def division_menu(
    selected_field,
    selected_branch,
    selected_division,
    division_data
):
    """
    Preserves the existing position-selection functionality
    while adding division-level display and XLSX export.
    """

    while True:

        print("\n")
        print("=" * 70)
        print("DIVISION OPTIONS")
        print("=" * 70)

        print(f"Field:    {selected_field}")
        print(f"Branch:   {selected_branch}")
        print(f"Division: {selected_division}")

        print("\n1. Select and display a position")
        print("2. Display all training in this division")
        print("3. Export division to XLSX")
        print("4. Return to division selection")
        print("5. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":

            # Preserve the existing position-level behavior.
            select_and_display_position(
                selected_division,
                division_data
            )

        elif choice == "2":

            display_division_training(
                division_data
            )

        elif choice == "3":

            output_path = export_division_to_xlsx(
                selected_field,
                selected_branch,
                selected_division,
                division_data
            )

            print("\n")
            print("=" * 70)
            print("EXPORT COMPLETE")
            print("=" * 70)
            print(f"Division: {selected_division}")
            print(f"File: {output_path}")

        elif choice == "4":

            return

        elif choice == "5":

            return "EXIT"

        else:

            print("Invalid selection.")


# ============================================================
# Interactive Selection
# ============================================================

def run():

    while True:

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
        # Make branch object available to
        # position-level display
        # -----------------------------------

        for division_name, division_data in branch_data["divisions"].items():

            division_data["branch_object"] = branch_data["object"]

        # -----------------------------------
        # DIVISION
        # -----------------------------------

        selected_division = prompt_selection(
            f"Select Division (Branch {selected_branch})",
            sorted(branch_data["divisions"].keys())
        )

        division_data = branch_data["divisions"][selected_division]

        # -----------------------------------
        # DIVISION MENU
        # -----------------------------------

        result = division_menu(
            selected_field,
            selected_branch,
            selected_division,
            division_data
        )

        if result == "EXIT":
            break


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    run()