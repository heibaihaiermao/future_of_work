import json
from pathlib import Path


OUTPUT = []


def append_record(
        source,
        source_id,
        source_section,
        text,
        metadata=None):

    OUTPUT.append({
        "source": source,
        "source_id": source_id,
        "source_section": source_section,
        "text": text,
        "metadata": metadata or {}
    })


# --------------------------
# Departmental Plan
# --------------------------

def normalize_departmental_plan(path):

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # strategic priorities
    for priority in data.get("strategic_priorities", []):

        append_record(
            source="departmental_plan",
            source_id=priority["priority_id"],
            source_section="strategic_priority",
            text=priority["title"],
            metadata={
                "technology_themes":
                    priority.get("technology_themes", []),

                "capability_themes":
                    priority.get("capability_themes", []),

                "workforce_implications":
                    priority.get("workforce_implications", [])
            }
        )

        for quote in priority.get("evidence_quotes", []):

            append_record(
                source="departmental_plan",
                source_id=priority["priority_id"],
                source_section="evidence_quote",
                text=quote
            )

    # transformation initiatives
    for initiative in data.get("transformation_initiatives", []):

        append_record(
            source="departmental_plan",
            source_id=initiative["initiative"],
            source_section="transformation_initiative",
            text=initiative["description"],
            metadata={
                "technology_themes":
                    initiative.get("technology_themes", []),

                "workforce_implications":
                    initiative.get("workforce_implications", [])
            }
        )

        for quote in initiative.get("evidence_quotes", []):

            append_record(
                source="departmental_plan",
                source_id=initiative["initiative"],
                source_section="evidence_quote",
                text=quote
            )


# --------------------------
# Future Vision Deck
# --------------------------

def normalize_deck(path):

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for item in data:

        update = item.get("update", {})

        source_id = update.get("reference", "unknown")

        append_record(
            source="future_vision_deck",
            source_id=source_id,
            source_section="slide_update",
            text=update.get("description", ""),
            metadata={
                "strategic_priorities":
                    update.get("strategic priorities", [])
            }
        )


# --------------------------
# Mandate Letters
# --------------------------

def normalize_mandate_letters(path):

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for letter in data:

        field_name = letter.get("field", {}).get(
            "name",
            "unknown_field"
        )

        recipient = letter.get("field", {}).get(
            "recipient",
            "unknown_recipient"
        )

        for i, paragraph in enumerate(
                letter.get("strategic_context", [])):

            append_record(
                source="mandate_letter",
                source_id=f"{field_name}_{recipient}",
                source_section="strategic_context",
                text=paragraph,
                metadata={
                    "field": field_name,
                    "recipient": recipient
                }
            )

        for priority in letter.get("priorities", []):

            source_id = (
                f"{field_name}_"
                f"{recipient}_"
                f"{priority.get('priority_id', 'unknown')}"
            )

            # priority title
            append_record(
                source="mandate_letter",
                source_id=source_id,
                source_section="priority",
                text=priority.get("title", ""),
                metadata={
                    "field": field_name,
                    "recipient": recipient,

                    "technology_themes":
                        priority.get("technology_themes", []),

                    "capability_themes":
                        priority.get("capability_themes", []),

                    "workforce_implications":
                        priority.get("workforce_implications", [])
                }
            )

            # description
            append_record(
                source="mandate_letter",
                source_id=source_id,
                source_section="priority_description",
                text=priority.get(
                    "original_description",
                    ""
                ),
                metadata={
                    "field": field_name,
                    "recipient": recipient
                }
            )

            # evidence quotes
            for quote in priority.get(
                    "evidence_quotes", []):

                append_record(
                    source="mandate_letter",
                    source_id=source_id,
                    source_section="evidence_quote",
                    text=quote,
                    metadata={
                        "field": field_name,
                        "recipient": recipient
                    }
            )


# --------------------------
# Main
# --------------------------

if __name__ == "__main__":

    normalize_departmental_plan(
        "input/departmental_plan_enriched.json"
    )

    normalize_deck(
        "input/deck_updates.json"
    )

    normalize_mandate_letters(
        "input/mandate_letters_enriched.json"
    )

    with open(
        "output/normalized_evidence.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            OUTPUT,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Normalized {len(OUTPUT)} evidence records."
    )