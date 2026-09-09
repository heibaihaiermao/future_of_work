import json
from collections import defaultdict

# -----------------------------
# LOAD CSPS FILE (multi-json)
# -----------------------------
def load_multi_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = content.split("}\n{")

    data = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            chunk = chunk + "}"
        elif i == len(chunks) - 1:
            chunk = "{" + chunk
        else:
            chunk = "{" + chunk + "}"

        chunk = chunk.strip()
        if chunk:
            data.append(json.loads(chunk))

    return data


data = load_multi_json("csps.json")

# -----------------------------
# EXTRACT INDICATORS
# -----------------------------
indicator_map = defaultdict(lambda: defaultdict(list))

for course in data:
    for comp in course.get("competencies", []):
        name = comp.get("competency")
        prof = comp.get("proficiency")
        indicators = comp.get("indicators")

        if not name or not prof or not indicators:
            continue

        indicator_map[name][prof].extend(indicators)


# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
clean_map = {}

for comp, prof_dict in indicator_map.items():
    clean_map[comp] = {}

    for prof, inds in prof_dict.items():
        # remove duplicates while preserving order
        unique_inds = list(dict.fromkeys(inds))
        clean_map[comp][prof] = unique_inds


# -----------------------------
# SAVE RESULT
# -----------------------------
with open("indicator_map.json", "w", encoding="utf-8") as f:
    json.dump(clean_map, f, indent=2, ensure_ascii=False)

print("✅ Indicator map extracted successfully!")