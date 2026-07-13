from docx import Document
import re
import os


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_between(text, start, end=None):

    if end:
        pattern = rf"{re.escape(start)}(.*?){re.escape(end)}"
    else:
        pattern = rf"{re.escape(start)}(.*)"

    match = re.search(
        pattern,
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return clean_text(match.group(1))

    return None


def extract_emails(text):

    return re.findall(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text
    )


def process_docx(file_path):

    doc = Document(file_path)

    
    seen = set()
    parts = []

    for table in doc.tables:

        for row in table.rows:

            for cell in row.cells:

                txt = clean_text(cell.text)

                if txt and txt not in seen:

                    seen.add(txt)

                    parts.append(txt)

    text = "\n".join(parts)

    data = {}

  
    # COURSE CODE
  

    match = re.search(
        r"Course Code:\s*([A-Z]-\d+)",
        text
    )

    data["course_code"] = (
        match.group(1)
        if match else None
    )

  
    # TITLES
  

    title_match = re.search(
        r"Title / Titre \(bilingue\):\s*(.*?)\s*/\s*(.*?)\s*Course Code",
        text,
        re.DOTALL
    )

    if title_match:
        data["title_en"] = clean_text(title_match.group(1))
        data["title_fr"] = clean_text(title_match.group(2))

  
    # PREREQUISITES
  

    prereq_section = extract_between(
        text,
        "Prerequisites:",
        "Domain / Domaine:"
    )

    if prereq_section:

        parts = prereq_section.split("Prérequis")

        data["prerequisites_en"] = clean_text(parts[0])

        if len(parts) > 1:
            data["prerequisites_fr"] = clean_text(parts[1])

  
    # AUDIENCE
  

    data["target_audience_en"] = extract_between(
        text,
        "Target Audience - English:",
        "Clientèle visée - French:"
    )

    data["target_audience_fr"] = extract_between(
        text,
        "Clientèle visée - French:",
        "Description - English:"
    )

  
    # DESCRIPTION
  

    data["description_en"] = extract_between(
        text,
        "Description - English:",
        "Description - French:"
    )

    data["description_fr"] = extract_between(
        text,
        "Description - French:",
        "Duration / Durée:"
    )

  
    # DURATION
  

    day_match = re.search(
        r"# Day / Jour:\s*(\d+)",
        text
    )

    data["days"] = (
        int(day_match.group(1))
        if day_match else None
    )

    hours_match = re.search(
        r"Total of Hours / Total d’heures:\s*(\d+)",
        text
    )

    data["total_hours"] = (
        int(hours_match.group(1))
        if hours_match else None
    )

  
    # TIMES
  

    start_match = re.search(
        r"Start Time / Heure du début:\s*(.*?)End Time",
        text
    )

    data["start_time"] = (
        clean_text(start_match.group(1))
        if start_match else None
    )

    end_match = re.search(
        r"End Time / Heure de la fin:\s*(.*?)Total of Hours",
        text
    )

    data["end_time"] = (
        clean_text(end_match.group(1))
        if end_match else None
    )

  
    # DELIVERY TYPE
  

    data["delivery_type"] = {
        "instructor": "Instructor / Cours magistral ☒" in text,
        "e_learning": "E-learning / Formation en ligne ☒" in text,
        "self_paced": "Self paced / Cours en ligne à rythme libre ☒" in text,
        "virtual_instructor": "Virtual Instructor / Cours en classe virtuelle ☒" in text
    }

  
    # LOCATION
  

    data["location"] = {
        "in_class": "In Class / En classe ☒" in text,
        "online": "Online / Virtuel ☒" in text
    }

  
    # LANGUAGE
  

    data["language"] = {
        "english": "En / Ang" in text,
        "french": "Fr / Fr" in text

    }

  
    # PARTICIPANTS
  

    min_match = re.search(
        r"Minimum Participants:\s*(\d+)",
        text
    )

    max_match = re.search(
        r"Maximum Participants:\s*(\d+)",
        text
    )

    data["minimum_participants"] = (
        int(min_match.group(1))
        if min_match else None
    )

    data["maximum_participants"] = (
        int(max_match.group(1))
        if max_match else None
    )

  
    # COST
  

    cost_match = re.search(
        r"Cost / Prix:\s*\$?(\d+)",
        text
    )

    data["cost"] = (
        int(cost_match.group(1))
        if cost_match else None
    )

  
    # CONTACTS
  

    contact_blocks = re.findall(
        r"Contact #\s*\d+\s*(.*?)\s*Email / Courriel:\s*([\w\.-]+@[\w\.-]+\.\w+)",
        text,
        re.DOTALL
    )

    contacts = []

    for name, email in contact_blocks:

        contacts.append({
            "name": clean_text(name),
            "email": clean_text(email)
        })

    data["contacts"] = contacts

  
    # LAST UPDATE
  

    update_match = re.search(
        r"Last Update / Mise à jour :\s*(\d{4}-\d{2}-\d{2})",
        text
    )

    data["last_update"] = (
        update_match.group(1)
        if update_match else None
    )

  
    # METADATA
  

    data["source_file"] = os.path.basename(file_path)

    data["source_type"] = "docx"

    return data
