import json


INPUT_FILE = "input/drivers.json"
OUTPUT_FILE = "output/consolidated_drivers.json"


# --------------------------
# Load Drivers
# --------------------------

with open(INPUT_FILE, encoding="utf-8") as f:
    drivers = json.load(f)


# --------------------------
# Consolidate
# --------------------------

consolidated = []

for i, driver in enumerate(drivers, start=1):

    evidence = driver.get("evidence", [])

    sources = sorted(
        list(
            {
                item["source"]
                for item in evidence
                if "source" in item
            }
        )
    )

    consolidated.append(
        {
            "driver_id": f"D{i:03d}",
            "driver": driver["driver"],
            "description": driver.get(
                "description",
                ""
            ),
            "sources": sources,
            "evidence_count": len(evidence),
            "evidence": evidence
        }
    )


# --------------------------
# Save
# --------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        consolidated,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Consolidated {len(consolidated)} drivers."
)