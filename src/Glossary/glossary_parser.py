import json


def load_skill_gaps(input_file):

    records = []

    with open(input_file, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except Exception:
                print("Skipping invalid line")

    return records

def load_gsbpm_implications(input_file):

    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)
