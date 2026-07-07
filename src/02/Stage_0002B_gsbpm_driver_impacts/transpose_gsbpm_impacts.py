import json
import os

# ==================================================
# Configuration
# ==================================================

INPUT_FILE = "input/driver_gsbpm_impacts.json"

OUTPUT_FILE = "output/gsbpm_driver_impacts.json"


# ==================================================
# Load Stage 2A Output
# ==================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    driver_impacts = json.load(f)

print(
    f"Loaded {len(driver_impacts)} drivers."
)


# ==================================================
# Transpose Driver -> GSBPM
# ==================================================

gsbpm_map = {}

for driver_record in driver_impacts:

    driver_id = driver_record.get(
        "driver_id",
        ""
    )

    driver_name = driver_record.get(
        "driver",
        ""
    )

    affected_subprocesses = (
        driver_record.get(
            "affected_subprocesses",
            []
        )
    )

    for subprocess in affected_subprocesses:

        gsbpm_id = subprocess.get(
            "gsbpm_id",
            ""
        )

        if gsbpm_id not in gsbpm_map:

            gsbpm_map[gsbpm_id] = {

                "phase_id":
                    subprocess.get(
                        "phase_id",
                        ""
                    ),

                "phase_name":
                    subprocess.get(
                        "phase_name",
                        ""
                    ),

                "gsbpm_id":
                    gsbpm_id,

                "gsbpm_name":
                    subprocess.get(
                        "gsbpm_name",
                        ""
                    ),

                "gsbpm_description":
                    subprocess.get(
                        "gsbpm_description",
                        ""
                    ),

                "drivers": []
            }

        gsbpm_map[gsbpm_id][
            "drivers"
        ].append(
            {
                "driver_id":
                    driver_id,

                "driver":
                    driver_name,

                "impact_strength":
                
                    subprocess.get(
                        "impact_strength",
                        ""
                    ),

                "impact":
                    subprocess.get(
                        "impact",
                        ""
                    )
            }
        )


# ==================================================
# Sort Drivers Within Each GSBPM
# ==================================================

for record in gsbpm_map.values():

    record["drivers"] = sorted(
        record["drivers"],
        key=lambda x: x["driver_id"]
    )


# ==================================================
# Convert Dictionary To List
# ==================================================

results = sorted(
    gsbpm_map.values(),
    key=lambda x: (
        x["phase_id"],
        x["gsbpm_id"]
    )
)


# ==================================================
# Save
# ==================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Generated "
    f"{len(results)} GSBPM records."
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)

