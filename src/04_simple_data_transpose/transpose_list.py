##
# This file does a simple re-organization of a data product,
#
# Beginning with a list of GSBPM phases/sub-process updates,
# then grouping by implicated work-descriptions.
##

import json
from collections import defaultdict
from datetime import date


def today():
    return date.today().isoformat()


if __name__ == "__main__":

    INPUT_FILE_PATH = "../03_implicating_GSBPM_updates_to_wd/implicating_gsbpm_updates_to_wd/output/jobDescriptions_gsbpm_wd_implications.json"

    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as fil:
        gsbpm_updates = json.load(fil)

    # Init. output element
    wd_summary = defaultdict(list)

    for update_i in gsbpm_updates:

        # Collect the common GSBPM update elements
        update_elements = {
            "id": update_i["id"],
            "title": update_i["title"]
        }

        # Look through all work-descriptions implicated by this update
        for wd_i in update_i["implicated work-descriptions"]:

            # Collect work-description-specific information
            wd_elements = {
                "title": wd_i["title"],
                "group/level": wd_i["group/level"],
                "justification": wd_i["justification"]
            }

            # Combine the GSBPM update information with
            # the work-description-specific information
            update_implication = {
                "title": update_elements["title"],
                "id": update_elements["id"],
                "group/level": wd_elements["group/level"],
                "justification": wd_elements["justification"]
            }

            # Attribute by work-description title
            wd_title = wd_i["title"]
            wd_summary[wd_title].append(update_implication)

    # Save results
    with open(
        f"data/results/{today()}_-_work_descriptions_-_with_implicated_GSBPM_updates.json",
        "w",
        encoding="utf-8"
    ) as fil:
        json.dump(
            wd_summary,
            fil,
            ensure_ascii=False,
            indent=2
        )