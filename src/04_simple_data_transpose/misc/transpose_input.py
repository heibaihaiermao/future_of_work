from json import load, dump
from collections import defaultdict


INPUT_FILE = "input/stage03b_gsbpm_implicated_wds.json"
OUTPUT_FILE = "output/stage04_wd_future_impact_input.json"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    stage03b = load(f)


wd_index = {}


for gsbpm_record in stage03b:

    gsbpm_summary = {
        "phase_id": gsbpm_record.get("phase_id"),
        "phase_name": gsbpm_record.get("phase_name"),
        "gsbpm_id": gsbpm_record.get("gsbpm_id"),
        "gsbpm_name": gsbpm_record.get("gsbpm_name"),
        "gsbpm_description": gsbpm_record.get("gsbpm_description"),
        "drivers": gsbpm_record.get("drivers", [])
    }

    for wd in gsbpm_record.get(
        "implicated_work_descriptions",
        []
    ):

        title = wd.get("title")
        classification = wd.get("classification")

        key = (
            classification,
            title
        )

        if key not in wd_index:

            wd_index[key] = {
                "title": title,
                "classification": classification,
                "position_information":
                    wd.get("position_information", {}),
                "impacted_gsbpm": []
            }

        wd_index[key]["impacted_gsbpm"].append({

            "gsbpm_id":
                gsbpm_summary["gsbpm_id"],

            "gsbpm_name":
                gsbpm_summary["gsbpm_name"],

            "phase_id":
                gsbpm_summary["phase_id"],

            "phase_name":
                gsbpm_summary["phase_name"],

            "rank":
                wd.get("rank"),

            "justification":
                wd.get("justification"),

            "drivers":
                gsbpm_summary["drivers"]
        })


# Sort impacts by rank

for wd in wd_index.values():

    wd["impacted_gsbpm"] = sorted(
        wd["impacted_gsbpm"],
        key=lambda x: x.get("rank", 999)
    )


result = list(wd_index.values())

result = sorted(
    result,
    key=lambda x: (
        x.get("classification") or "",
        x.get("title") or ""
    )
)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    dump(
        result,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    f"{len(result)} work descriptions written to "
    f"{OUTPUT_FILE}"
)