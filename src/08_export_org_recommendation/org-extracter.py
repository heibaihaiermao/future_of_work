import pandas as pd
import json

# Load Excel file
excel_file = "data/organizational-structure-document/Field 5 & 8 - EC Position Information.xlsx"
output_file = "data/organizational-structure-document/org.json"

df = pd.read_excel(excel_file)

# Root storage
fields = {}

for _, row in df.iterrows():

    # ----------------------------
    # Extract values
    # ----------------------------
    field_number = row.iloc[9]   # Column J
    branch_name = row.iloc[8]    # Column I
    division_name = row.iloc[7]  # Column H

    group = row.iloc[1]          # Column B
    level = row.iloc[2]          # Column C

    job_family = row.iloc[3]     # Column D

    # Skip rows missing critical data
    if pd.isna(field_number):
        continue

    field_number = str(field_number).strip()
    branch_name = "" if pd.isna(branch_name) else str(branch_name).strip()
    division_name = "" if pd.isna(division_name) else str(division_name).strip()

    group = "" if pd.isna(group) else str(group).strip()

    # Format level as 2-digit
    if pd.isna(level):
        level = ""
    else:
        try:
            level = f"{int(level):02d}"
        except:
            level = str(level).strip()

    group_and_level = f"{group}-{level}" if group and level else group

    job_family = "" if pd.isna(job_family) else str(job_family).strip()

    # ----------------------------
    # Field
    # ----------------------------
    if field_number not in fields:
        fields[field_number] = {
            "field number": field_number,
            "branches": []
        }

    field_obj = fields[field_number]

    # ----------------------------
    # Branch
    # ----------------------------
    branch_obj = next(
        (
            b
            for b in field_obj["branches"]
            if b["branch name"] == branch_name
        ),
        None
    )

    if branch_obj is None:
        branch_obj = {
            "branch name": branch_name,
            "branch level training": [],
            "divisions": []
        }
        field_obj["branches"].append(branch_obj)

    # ----------------------------
    # Division
    # ----------------------------
    division_obj = next(
        (
            d
            for d in branch_obj["divisions"]
            if d["division name"] == division_name
        ),
        None
    )

    if division_obj is None:
        division_obj = {
            "division name": division_name,
            "division level training": [],
            "positions": []
        }
        branch_obj["divisions"].append(division_obj)

    # ----------------------------
    # Position
    # ----------------------------
    existing_position = next(
        (
            p
            for p in division_obj["positions"]
            if (
                p["group and level"] == group_and_level
                and p["job family"] == job_family
            )
        ),
        None
    )

    if existing_position is None:
        division_obj["positions"].append({
            "group and level": group_and_level,
            "job family": job_family,
            "position training": []
        })

# Convert dictionary to final list structure
result = list(fields.values())

# Save JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print(f"Created output json with {len(result)} field(s)")