import json

# ==================================================
# NOTE
# ==================================================
#
# This enrichment step replaces the previous Stage03B
# LLM enrichment process.
#
# Purpose:
#
#   Stage03A
#       ↓
#   Rule-Based Enrichment
#       ↓
#   Stage05
#
# We intentionally enrich Stage03A using deterministic
# joins against gsbpm_driver_impacts.json rather than
# performing another expensive GPT analysis pass.
#
# To reduce token usage for Stage05, the output keeps:
#
#   - job_family_number
#   - position_title
#   - gsbpm_id
#   - gsbpm_name
#   - rank
#   - justification
#   - driver
#   - impact_strength
#   - impact
#
# Full driver metadata remains available in
# gsbpm_driver_impacts.json and can be reattached later
# if future requirements change.
#
# OPTIONAL fields have been left commented out below.
#
# ==================================================


# ==================================================
# File Paths
# ==================================================

STAGE03A_FILE = (
    "input/stage03a_wd_impacts.json"
)

GSBPM_DRIVER_FILE = (
    "input/gsbpm_driver_impacts.json"
)

OUTPUT_FILE = (
    "output/stage03a_enriched.json"
)


# ==================================================
# Load Inputs
# ==================================================

with open(
    STAGE03A_FILE,
    "r",
    encoding="utf-8"
) as f:

    stage03a = json.load(f)


with open(
    GSBPM_DRIVER_FILE,
    "r",
    encoding="utf-8"
) as f:

    gsbpm_driver_impacts = json.load(f)


print(
    f"Loaded {len(stage03a)} Stage03A records"
)

print(
    f"Loaded {len(gsbpm_driver_impacts)} "
    f"GSBPM subprocesses"
)


# ==================================================
# Create GSBPM Lookup
# ==================================================

gsbpm_lookup = {

    row["gsbpm_id"]: row

    for row in gsbpm_driver_impacts
}


# ==================================================
# Enrich Stage03A
# ==================================================

enriched_records = []


for wd in stage03a:

    output_record = {

        "job_family_number":
            wd.get(
                "job_family_number"
            ),

        "position_title":
            wd.get(
                "position_title"
            ),

        "impacts": []
    }

    for impact in wd.get(
        "impacts",
        []
    ):

        gsbpm_id = impact.get(
            "gsbpm_id"
        )

        gsbpm = gsbpm_lookup.get(
            gsbpm_id
        )

        if gsbpm is None:

            print(
                f"WARNING: "
                f"GSBPM ID not found: "
                f"{gsbpm_id}"
            )

            continue

        simplified_drivers = []

        for driver in gsbpm.get(
            "drivers",
            []
        ):

            driver_record = {

                "driver":
                    driver.get(
                        "driver"
                    ),

                "impact_strength":
                    driver.get(
                        "impact_strength"
                    ),

                "impact":
                    driver.get(
                        "impact"
                    )

                ##################################################
                # OPTIONAL DRIVER ENRICHMENT
                #
                # Disabled by default to reduce token usage.
                #
                # Uncomment if future analysis requires
                # deeper context.
                ##################################################

                # ,
                # "description":
                #     driver.get(
                #         "description"
                #     ),
                #
                # "why_this_is_a_driver":
                #     driver.get(
                #         "why_this_is_a_driver"
                #     ),
                #
                # "technology_themes":
                #     driver.get(
                #         "technology_themes",
                #         []
                #     ),
                #
                # "capability_themes":
                #     driver.get(
                #         "capability_themes",
                #         []
                #     ),
                #
                # "workforce_implications":
                #     driver.get(
                #         "workforce_implications",
                #         []
                #     ),
                #
                # "impact_mechanisms":
                #     driver.get(
                #         "impact_mechanisms",
                #         []
                #     ),
            }

            simplified_drivers.append(
                driver_record
            )

        enriched_impact = {

            "gsbpm_id":
                gsbpm_id,

            "gsbpm_name":
                gsbpm.get(
                    "gsbpm_name"
                ),

            "rank":
                impact.get(
                    "rank"
                ),

            "justification":
                impact.get(
                    "justification"
                ),

            "drivers":
                simplified_drivers

            ##################################################
            # OPTIONAL GSBPM ENRICHMENT
            #
            # Disabled by default to reduce Stage05
            # token consumption.
            ##################################################

            # ,
            # "phase_id":
            #     gsbpm.get(
            #         "phase_id"
            #     ),
            #
            # "phase_name":
            #     gsbpm.get(
            #         "phase_name"
            #     ),
            #
            # "gsbpm_description":
            #     gsbpm.get(
            #         "gsbpm_description"
            #     )
        }

        output_record[
            "impacts"
        ].append(
            enriched_impact
        )

    enriched_records.append(
        output_record
    )


# ==================================================
# Save Output
# ==================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        enriched_records,
        f,
        indent=2,
        ensure_ascii=False
    )


print(
    f"Saved "
    f"{len(enriched_records)} "
    f"records to:"
)

print(
    OUTPUT_FILE
)