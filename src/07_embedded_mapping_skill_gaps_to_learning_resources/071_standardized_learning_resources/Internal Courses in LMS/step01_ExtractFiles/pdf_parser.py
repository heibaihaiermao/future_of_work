import fitz
import os
import re


def clean_text(text):

    if not text:
        return None

    text = re.sub(r"\s+", " ", str(text))

    return text.strip()


def split_bilingual(value):

    if not value:
        return None, None

    if " / " in value:
        en, fr = value.split(" / ", 1)

        return clean_text(en), clean_text(fr)

    return clean_text(value), None


def extract_course_code(filename):

    match = re.search(r"([A-Z]+-[A-Z]?-?\d+)", filename)

    return match.group(1) if match else None


def process_pdf(file_path):

    doc = fitz.open(file_path)

    fields = {}

    
    # EXTRACT PDF FORM FIELDS
    

    for page in doc:

        widgets = page.widgets()

        if widgets:

            for widget in widgets:

                field_name = widget.field_name
                field_value = widget.field_value

                fields[field_name] = field_value

    data = {}

    
    # COURSE CODE
    

    data["course_code"] = extract_course_code(
        os.path.basename(file_path)
    )

    
    # TITLE
    

    title = fields.get("Text Field0")

    title_en, title_fr = split_bilingual(title)

    data["title_en"] = title_en
    data["title_fr"] = title_fr

    
    # PREREQUISITES
    

    prereq = fields.get("Text Field1")

    prereq_en, prereq_fr = split_bilingual(prereq)

    data["prerequisites_en"] = prereq_en
    data["prerequisites_fr"] = prereq_fr

    
    # TARGET AUDIENCE
    

    audience = fields.get("Text Field3")

    audience_en, audience_fr = split_bilingual(audience)

    data["target_audience_en"] = audience_en
    data["target_audience_fr"] = audience_fr

    
    # HOURS / DAYS
    

    total_hours = fields.get("Text Field4")

    data["total_hours"] = (
        int(total_hours)
        if total_hours and str(total_hours).isdigit()
        else None
    )

    half_days = fields.get("Text Field5")

    data["half_day_count"] = (
        int(half_days)
        if half_days and str(half_days).isdigit()
        else None
    )

    
    # TIME
    

    data["start_time"] = clean_text(
        fields.get("Text Field7")
    )

    data["end_time"] = clean_text(
        fields.get("Text Field8")
    )

    
    # COURSE OUTLINE
    

    data["course_outline_fr"] = clean_text(
        fields.get("Text Field14")
    )

    data["course_outline_en"] = clean_text(
        fields.get("Text Field15")
    )

    
    # DESCRIPTION
    

    description = fields.get("Text Field16")

    data["description_raw"] = clean_text(description)

    # Optional split

    if description:

        if "Ce cours" in description:

            parts = description.split("Ce cours", 1)

            data["description_en"] = clean_text(parts[0])

            data["description_fr"] = clean_text(
                "Ce cours" + parts[1]
            )

        else:
            data["description_en"] = clean_text(description)
            data["description_fr"] = None

    
    # CATEGORY
    

    category_match = re.search(
        r"Category:\s*(.*)",
        description if description else ""
    )

    data["category"] = (
        clean_text(category_match.group(1))
        if category_match else None
    )

    
    # DELIVERY TYPE
    

    data["delivery_type"] = {
        "instructor": fields.get("Check Box8") == "Yes",
        "e_learning": fields.get("Check Box9") == "Yes",
        "self_paced": fields.get("Check Box10") == "Yes",
        "virtual_instructor": fields.get("Check Box11") == "Yes"
    }

    
    # LOCATION
    

    data["location"] = {
        "in_class": fields.get("Check Box12") == "Yes",
        "online": fields.get("Check Box13") == "Yes"
    }

    
    # LANGUAGE
    

    data["language"] = {
        "english": True,
        "french": True
    }

    
    # PARTICIPANTS
    

    min_participants = fields.get("Text Field9")

    data["minimum_participants"] = (
        int(min_participants)
        if min_participants and str(min_participants).isdigit()
        else None
    )

    max_participants = fields.get("Text Field18")

    data["maximum_participants"] = (
        int(max_participants)
        if max_participants and str(max_participants).isdigit()
        else None
    )

    
    # CONTACTS
    

    contacts = []

    contact1_name = fields.get("Text Field10")
    contact1_email = fields.get("Text Field12")

    if contact1_name or contact1_email:

        contacts.append({
            "name": clean_text(contact1_name),
            "email": clean_text(contact1_email)
        })

    contact2_name = fields.get("Text Field11")
    contact2_email = fields.get("Text Field13")

    if contact2_name or contact2_email:

        contacts.append({
            "name": clean_text(contact2_name),
            "email": clean_text(contact2_email)
        })

    data["contacts"] = contacts

    
    # CREATION DATE
    

    data["creation_date"] = clean_text(
        fields.get("Date Field0")
    )

    
    # METADATA
    

    data["source_file"] = os.path.basename(file_path)

    data["source_type"] = "pdf"

    # raw fields for debugging
    data["raw_fields"] = fields

    return data