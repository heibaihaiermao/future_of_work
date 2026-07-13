from collections import defaultdict

import json
from pathlib import Path

# Paths
ORG_JSON = Path("./data/organizational-structure-document/org.json")
UNMATCHED_JSON = Path("./data/organizational-structure-document/unmatched_positions.json")


# Work Description Dictionary
WORK_DESCRIPTION_INDEX = {
    "629044": {"group_and_level": "EC-01", "position_title": "Library Technician 1", "date_revised": "June 22, 2009"},
    "900200": {"group_and_level": "EC-01", "position_title": "Recruit", "date_revised": "June 22, 2009"},
    "362012": {"group_and_level": "EC-02", "position_title": "Junior Evaluation Officer", "date_revised": "October 30, 2019"},
    "629141": {"group_and_level": "EC-02", "position_title": "Metadata Production and Dissemination Officer", "date_revised": "March 21, 2016"},
    "629045": {"group_and_level": "EC-02", "position_title": "Library Technician 2", "date_revised": "January 4, 2010"},
    "679103": {"group_and_level": "EC-02", "position_title": "Junior Data Analyst", "date_revised": "Sept 3, 2019"},
    "700201": {"group_and_level": "EC-02", "position_title": "Operations Officer", "date_revised": "June, 2009"},
    "900208": {"group_and_level": "EC-02", "position_title": "Economist/Sociologist 2", "date_revised": "June, 2009"},
    "900218": {"group_and_level": "EC-02", "position_title": "Data Production and Dissemination Officer", "date_revised": "June, 2009"},
    "362014": {"group_and_level": "EC-03", "position_title": "Evaluation Officer", "date_revised": "October 30, 2019"},
    "629043": {"group_and_level": "EC-03", "position_title": "Library Technician 3", "date_revised": "June 22, 2009"},
    "629140": {"group_and_level": "EC-03", "position_title": "Metadata Production and Dissemination Coordinator", "date_revised": "March 21, 2016"},
    "679104": {"group_and_level": "EC-03", "position_title": "Junior Data Analyst Scientist", "date_revised": "Sept 3, 2019"},
    "700202": {"group_and_level": "EC-03", "position_title": "Operations Coordinator", "date_revised": "June, 2009"},
    "750007": {"group_and_level": "EC-03", "position_title": "Regional Geographer and Management Information Systems Analyst", "date_revised": "Dec 1, 2019"},
    "900209": {"group_and_level": "EC-03", "position_title": "Economist/Sociologist 3", "date_revised": "June, 2009"},
    "900219": {"group_and_level": "EC-03", "position_title": "Data Production and Dissemination Coordinator", "date_revised": "June, 2009"},
    "935018": {"group_and_level": "EC-03", "position_title": "Survey, SM and Statistical Learning Officer", "date_revised": "May 27, 2024"},
    "362011": {"group_and_level": "EC-04", "position_title": "Evaluation Analyst", "date_revised": "October 30, 2019"},
    "629054": {"group_and_level": "EC-04", "position_title": "Library Technician 4", "date_revised": "June 22, 2009"},
    "629139": {"group_and_level": "EC-04", "position_title": "Metadata Development, Dissemination and Evaluation Coordinator", "date_revised": "March 21, 2016"},
    "679105": {"group_and_level": "EC-04", "position_title": "Data Analyst Scientist", "date_revised": "Sept 3, 2019"},
    "700203": {"group_and_level": "EC-04", "position_title": "Operations Development Officer", "date_revised": "June, 2009"},
    "750038": {"group_and_level": "EC-04", "position_title": "Collection Support Unit Manager (CJFL)", "date_revised": "April 1, 2020"},
    "900210": {"group_and_level": "EC-04", "position_title": "Economist/Sociologist 4", "date_revised": "June, 2009"},
    "900220": {"group_and_level": "EC-04", "position_title": "Data Production and Dissemination Development Officer", "date_revised": "June, 2009"},
    "362010": {"group_and_level": "EC-05", "position_title": "Evaluation Analyst", "date_revised": "October 30, 2019"},
    "377001": {"group_and_level": "EC-05", "position_title": "Planning and Research Analyst", "date_revised": "June, 2009"},
    "500001": {"group_and_level": "EC-05", "position_title": "Production and Database Expert", "date_revised": "Nov, 2017"},
    "540003": {"group_and_level": "EC-05", "position_title": "Data Analytics and Integration Officer", "date_revised": "April 1, 2020"},
    "627209": {"group_and_level": "EC-05", "position_title": "Geomatic Specialist", "date_revised": "November 24, 2024"},
    "629137": {"group_and_level": "EC-05", "position_title": "Metadata Development and Evaluation Specialist", "date_revised": "January 22, 2016"},
    "677076": {"group_and_level": "EC-05", "position_title": "International Relations Analyst", "date_revised": "March 1, 2016"},
    "679106": {"group_and_level": "EC-05", "position_title": "Senior Data Analyst Scientist", "date_revised": "Sept 3, 2019"},
    "700204": {"group_and_level": "EC-05", "position_title": "Operations Supervisor", "date_revised": "June, 2009"},
    "751159": {"group_and_level": "EC-05", "position_title": "Regional Program Manager (Data Collection)", "date_revised": "June, 2009"},
    "841150": {"group_and_level": "EC-05", "position_title": "Research Data Centre Analyst", "date_revised": "September 2, 2014"},
    "900211": {"group_and_level": "EC-05", "position_title": "Research Analyst", "date_revised": "June, 2009"},
    "900215": {"group_and_level": "EC-05", "position_title": "Economist/Sociologist 5", "date_revised": "June, 2009"},
    "900221": {"group_and_level": "EC-05", "position_title": "Production and Dissemination Specialist", "date_revised": "June, 2009"},
    "362006": {"group_and_level": "EC-06", "position_title": "Senior Evaluation Analyst", "date_revised": "October 30, 2019"},
    "500007": {"group_and_level": "EC-06", "position_title": "Senior Economic Analyst", "date_revised": "May 1, 2015"},
    "540002": {"group_and_level": "EC-06", "position_title": "Specialist, Data Analytics and Integration", "date_revised": "April 1, 2020"},
    "627147": {"group_and_level": "EC-06", "position_title": "Senior Geomatics Analyst", "date_revised": "April 1, 2021"},
    "629138": {"group_and_level": "EC-06", "position_title": "Unit Head, Metadata Development and Evaluation", "date_revised": "January 22, 2016"},
    "679022": {"group_and_level": "EC-06", "position_title": "Lead Data Scientist", "date_revised": "April 1, 2020"},
    "679107": {"group_and_level": "EC-06", "position_title": "Lead Data Scientist", "date_revised": "Sept 3, 2019"},
    "700205": {"group_and_level": "EC-06", "position_title": "Head of Operations", "date_revised": "June, 2009"},
    "750001": {"group_and_level": "EC-06", "position_title": "District Manager, Regional Operations (Data Collection)", "date_revised": "June 22, 2009"},
    "750019": {"group_and_level": "EC-06", "position_title": "Local Census Manager", "date_revised": "April 1, 2024"},
    "750033": {"group_and_level": "EC-06", "position_title": "Field Operations Manager, Census", "date_revised": "June 6, 2025"},
    "900212": {"group_and_level": "EC-06", "position_title": "Senior Research Analyst", "date_revised": "June, 2009"},
    "900216": {"group_and_level": "EC-06", "position_title": "Unit Head, Subject Matter", "date_revised": "June, 2009"},
    "900222": {"group_and_level": "EC-06", "position_title": "Head, Production and Dissemination", "date_revised": "June, 2009"},
    "362025": {"group_and_level": "EC-07", "position_title": "Evaluation Manager", "date_revised": "October 30, 2019"},
    "377004": {"group_and_level": "EC-07", "position_title": "Planning and Evaluation Manager", "date_revised": "June 22, 2009"},
    "541235": {"group_and_level": "EC-07", "position_title": "Principal Consumer Prices Analyst", "date_revised": "April 1, 2016"},
    "679101": {"group_and_level": "EC-07", "position_title": "Manager Data Science & Analytics", "date_revised": "Sept 3, 2019"},
    "679102": {"group_and_level": "EC-07", "position_title": "Data Science Senior Specialist", "date_revised": "Sept 3, 2019"},
    "750009": {"group_and_level": "EC-07", "position_title": "Area Manager", "date_revised": "May 1, 2020"},
    "900213": {"group_and_level": "EC-07", "position_title": "Principal Researcher", "date_revised": "June, 2009"},
    "900217": {"group_and_level": "EC-07", "position_title": "Chief", "date_revised": "June, 2009"},
    "750002": {"group_and_level": "EC-08", "position_title": "Regional Assistant Director", "date_revised": "July 23, 2010"},
    "900206": {"group_and_level": "EC-08", "position_title": "Assistant Director", "date_revised": "June, 2009"},
    "900214": {"group_and_level": "EC-08", "position_title": "Research Manager", "date_revised": "June, 2009"},
}


TITLE_INDEX = defaultdict(list)

for wd_number, info in WORK_DESCRIPTION_INDEX.items():
    TITLE_INDEX[info["position_title"]].append({
        "work_description_number": wd_number,
        "group_and_level": info["group_and_level"],
        "date_revised": info["date_revised"]
    })

# Load Organization Structure
with open(ORG_JSON, "r", encoding="utf-8") as f:
    org = json.load(f)


unmatched_positions = []

matched = 0
unmatched = 0


# Traverse hierarchy

for field in org:

    field_number = field["field number"]

    for branch in field.get("branches", []):

        branch_name = branch["branch name"]

        for division in branch.get("divisions", []):

            division_name = division["division name"]

            for position in division.get("positions", []):

                job_family = str(position.get("job family", "")).strip()

                if job_family in WORK_DESCRIPTION_INDEX:

                    info = WORK_DESCRIPTION_INDEX[job_family]

                    position["position title"] = info["position_title"]

                    matched += 1

                else:

                    unmatched += 1

                    unmatched_positions.append({
                        "field number": field_number,
                        "branch": branch_name,
                        "division": division_name,
                        "group and level": position.get("group and level"),
                        "job family": job_family
                    })


# Save updated org.json
with open(ORG_JSON, "w", encoding="utf-8") as f:
    json.dump(org, f, indent=4, ensure_ascii=False)


# Save unmatched positions
with open(UNMATCHED_JSON, "w", encoding="utf-8") as f:
    json.dump(unmatched_positions, f, indent=4, ensure_ascii=False)



# Summary
print("=" * 50)
print("Completed")
print("=" * 50)
print(f"Matched Positions   : {matched}")
print(f"Unmatched Positions : {unmatched}")

if unmatched:
    print(f"\nSee {UNMATCHED_JSON} for unmatched records.")