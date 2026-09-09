import json
from pathlib import Path

ORG_JSON = Path(
    "../data/organizational-structure-document/org_updated.json"
)

WD_FOLDER = Path(
    "../data/work-descriptions-with-job-posters"
)

OUTPUT_JSON = Path(
    "../implicating_gsbpm_updates_to_wd/input/jobDescriptions.json"
)

with open(ORG_JSON, "r", encoding="utf-8") as f:
    org = json.load(f)


def choose_option(title, options):
    print()
    print(title)
    print("-" * len(title))

    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("\nSelect option: "))
            if 1 <= choice <= len(options):
                return choice - 1
        except ValueError:
            pass

        print("Invalid selection.")


def format_job_family(job_family):
    digits = "".join(c for c in str(job_family) if c.isdigit())

    if len(digits) != 6:
        return str(job_family)

    return f"{digits[:3]}-{digits[3:]}"


def find_work_description(job_family):
    formatted = format_job_family(job_family)

    for path in WD_FOLDER.glob("*.json"):
        if formatted in path.stem:
            return path

    return None


def collect_position(position, files, missing):
    job_family = str(position.get("job family", "")).strip()

    exist_position_training = position.get("position training", [])
    print(f"position {position.get("position title")}: {exist_position_training}")

    # If already has position training existed for the position, skip it
    if exist_position_training:
        print(f"Skipping position {position.get("position title")} - {position.get("job family", "")}")
        return

    if not job_family:
        return

    wd = find_work_description(job_family)

    if wd is None:
        missing.append(job_family)
        return

    files.add(wd)
    print(f"Adding position {position.get("position title")} - {position.get("job family", "")}")



def collect_division(division, files, missing):
    for position in division.get("positions", []):
        collect_position(position, files, missing)


def collect_branch(branch, files, missing):
    for division in branch.get("divisions", []):
        collect_division(division, files, missing)


def collect_field(field, files, missing):
    for branch in field.get("branches", []):
        collect_branch(branch, files, missing)


def write_job_descriptions(files):
    result = []

    for file in sorted(files):
        try:
            with open(file, "r", encoding="utf-8") as f:
                obj = json.load(f)

            result.append(obj)
            print(f"Loaded {file.name}")

        except Exception as e:
            print(f"Failed to load {file.name}")
            print(e)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print()
    print(f"Wrote {len(result)} work descriptions.")
    print(OUTPUT_JSON)

if __name__ == "__main__":
    field_options = sorted(
        [
            str(field["field number"])
            for field in org
        ]
    )

    field_index = choose_option(
        "Select Field",
        field_options
    )

    field_obj = next(
        f
        for f in org
        if str(f["field number"]) == field_options[field_index]
    )

    field_action = choose_option(
        "Field Action",
        [
            "Navigate to Branch",
            "Analyze This Field"
        ]
    )

    files = set()
    missing = []

    if field_action == 1:
        collect_field(field_obj, files, missing)
        write_job_descriptions(files)

        if missing:
            print()
            print("Missing work descriptions:")

            for job in sorted(set(missing)):
                print(job)

        raise SystemExit


    branch_options = sorted(
        [
            str(branch["branch name"])
            for branch in field_obj["branches"]
        ]
    )

    branch_index = choose_option(
        "Select Branch",
        branch_options
    )

    branch_obj = next(
        b
        for b in field_obj["branches"]
        if str(b["branch name"]) == branch_options[branch_index]
    )

    branch_action = choose_option(
        "Branch Action",
        [
            "Navigate to Division",
            "Analyze This Branch"
        ]
    )

    if branch_action == 1:
        collect_branch(branch_obj, files, missing)
        write_job_descriptions(files)

        if missing:
            print()
            print("Missing work descriptions:")

            for job in sorted(set(missing)):
                print(job)

        raise SystemExit


    division_options = sorted(
        [
            str(div["division name"])
            for div in branch_obj["divisions"]
        ]
    )

    division_index = choose_option(
        "Select Division",
        division_options
    )

    division_obj = next(
        d
        for d in branch_obj["divisions"]
        if str(d["division name"]) == division_options[division_index]
    )

    division_action = choose_option(
        "Division Action",
        [
            "Navigate to Position",
            "Analyze This Division"
        ]
    )

    if division_action == 1:
        collect_division(division_obj, files, missing)
        write_job_descriptions(files)

        if missing:
            print()
            print("Missing work descriptions:")

            for job in sorted(set(missing)):
                print(job)

        raise SystemExit

    position_options = []

    for position in division_obj.get("positions", []):
        display = (
            f'{position.get("group and level", "")}'
            f' | Job Family: {position.get("job family", "")}'
            f' | {position.get("position title", "")}'
        )

        position_options.append(display)


    if not position_options:
        print("No positions found.")
        raise SystemExit


    position_index = choose_option(
        "Select Position",
        position_options
    )

    position_obj = division_obj["positions"][position_index]


    position_action = choose_option(
        "Position Action",
        [
            "Analyze This Position"
        ]
    )


    if position_action == 0:

        files = set()
        missing = []

        collect_position(
            position_obj,
            files,
            missing
        )

        write_job_descriptions(files)

        if missing:
            print()
            print("Missing work descriptions:")

            for job in sorted(set(missing)):
                print(job)

