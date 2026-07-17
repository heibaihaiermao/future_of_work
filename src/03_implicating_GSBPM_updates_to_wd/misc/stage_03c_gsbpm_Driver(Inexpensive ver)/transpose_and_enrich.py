import os
import json

# ==================================================
# Config
# ==================================================

INPUT_STAGE03 = (
    "input/stage03a_wd_impacts.json"
)

INPUT_GSBPM = (
    "input/gsbpm_driver_impacts.json"
)

WORK_DESCRIPTION_DIR = (
    "input/work-descriptions-raw"
)

OUTPUT_FILE = (
    "output/stage03b_gsbpm_implicated_wds.json"
)

# ==================================================
# Load Stage 03 Output
# ==================================================

with open(INPUT_STAGE03, encoding="utf-8") as f:
    stage03_results = json.load(f)

# ==================================================
# Load GSBPM
# ==================================================

with open(INPUT_GSBPM, encoding="utf-8") as f:
    gsbpm_records = json.load(f)

# ==================================================
# Build GSBPM Lookup
# ==================================================

gsbpm_lookup = {}

for record in gsbpm_records:

    gsbpm_lookup[
        record["gsbpm_id"]
    ] = record

print(
    f"Loaded {len(gsbpm_lookup)} "
    "GSBPM records."
)

# ==================================================
# Load Original Work Descriptions
# ==================================================

wd_lookup = {}

for filename in sorted(
    os.listdir(WORK_DESCRIPTION_DIR)
):

    if not filename.endswith(".json"):
        continue

    path = os.path.join(
        WORK_DESCRIPTION_DIR,
        filename
    )

    with open(path, encoding="utf-8") as f:

        wd_json = json.load(f)

    for position in wd_json.get(
        "Positions",
        []
    ):

        job_family_number = position.get(
            "Job Family Number"
        )

        if not job_family_number:
            continue

        key = str(
            job_family_number
        ).strip()

        wd_lookup[key] = position

print(
    f"Loaded {len(wd_lookup)} "
    "work descriptions."
)

# ==================================================
# Prepare Output Structure
# ==================================================

output_lookup = {}

for gsbpm_id, gsbpm in gsbpm_lookup.items():

    output_lookup[gsbpm_id] = {

        "phase_id":
            gsbpm.get("phase_id"),

        "phase_name":
            gsbpm.get("phase_name"),

        "gsbpm_id":
            gsbpm.get("gsbpm_id"),

        "gsbpm_name":
            gsbpm.get("gsbpm_name"),

        "gsbpm_description":
            gsbpm.get(
                "gsbpm_description"
            ),

        "drivers":
            gsbpm.get(
                "drivers",
                []
            ),

        "implicated_work_descriptions":
            []
    }

# ==================================================
# Transpose + Enrich
# ==================================================

for wd in stage03_results:

    job_family_number = wd.get(
        "job_family_number",
        ""
    )

    source_position = wd_lookup.get(
        job_family_number,
        {}
    )

    for impact in wd.get(
        "impacts",
        []
    ):

        gsbpm_id = impact.get(
            "gsbpm_id"
        )

        if gsbpm_id not in output_lookup:
            continue

        output_lookup[
            gsbpm_id
        ][
            "implicated_work_descriptions"
        ].append(
            {

                "title":
                    wd.get(
                        "position_title"
                    ),

                "classification":
                    source_position.get(
                        "Group/Level"
                    ),

                "rank":
                    impact.get(
                        "rank"
                    ),

                "justification":
                    impact.get(
                        "justification"
                    ),

                "position_information": {

                    "job_family_number":
                        source_position.get(
                            "Job Family Number"
                        ),

                    "group_level":
                        source_position.get(
                            "Group/Level"
                        ),

                    "position_title":
                        source_position.get(
                            "Position Title"
                        ),

                    "supervisor_position":
                        source_position.get(
                            "Supervisor Position"
                        ),

                    "branch_division":
                        source_position.get(
                            "Branch/Division"
                        ),

                    "key_activities":
                        source_position.get(
                            "Key Activities",
                            []
                        ),

                    "technical_activities_skills_responsibilities_or_efforts":
                        source_position.get(
                            "technical activities, skills, responsibilities, or efforts",
                            {}
                        )
                }
            }
        )

# ==================================================
# Remove Empty GSBPMs
# ==================================================

final_output = []

for record in output_lookup.values():

    if not record[
        "implicated_work_descriptions"
    ]:
        continue

    # optional:
    # keep strongest impacts first

    record[
        "implicated_work_descriptions"
    ].sort(
        key=lambda x: x.get(
            "rank",
            999
        )
    )

    final_output.append(
        record
    )

# ==================================================
# Save
# ==================================================

os.makedirs(
    os.path.dirname(
        OUTPUT_FILE
    ),
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_output,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Created "
    f"{len(final_output)} "
    "GSBPM impact records"
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)