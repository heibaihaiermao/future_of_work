import os
import json

from docx_parser import process_docx
from pdf_parser import process_pdf

INPUT_FOLDER = "input_docs"
OUTPUT_FILE = "output/courses.json"

results = []

for filename in os.listdir(INPUT_FOLDER):

    path = os.path.join(INPUT_FOLDER, filename)

    try:

        if filename.lower().endswith(".docx"):
            data = process_docx(path)

        elif filename.lower().endswith(".pdf"):
            data = process_pdf(path)

        else:
            continue

        if data:
            results.append(data)

        print(f"Processed: {filename}")

    except Exception as e:
        print(f"FAILED: {filename}")
        print(e)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"\nSaved {len(results)} records to {OUTPUT_FILE}")
