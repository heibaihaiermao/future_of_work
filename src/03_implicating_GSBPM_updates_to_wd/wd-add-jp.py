import os
import json
import re
from rapidfuzz import fuzz, process


RAW_DIR = r".\data\work-descriptions-raw"
JOB_POSTER_FILE = r".\data\job-posters-normalized\ec_normalized.json"

OUTPUT_DIR = r".\data\work-descriptions-with-job-posters"


MATCH_THRESHOLD = 75


def normalize_title(title):
    """
    Normalize job titles for matching
    """

    if not title:
        return ""

    title = title.lower()

    # remove EC classifications
    title = re.sub(
        r"\(?\bec[\s\-]?\d{1,2}\b\)?",
        "",
        title
    )

    # replace ampersand
    title = title.replace("&", "and")

    # remove punctuation
    title = re.sub(
        r"[^a-z0-9\s]",
        " ",
        title
    )

    # remove common filler words
    remove_words = {
        "position",
        "job",
        "title"
        # "senior",
        # "junior"
    }

    words = [
        w for w in title.split()
        if w not in remove_words
    ]

    title = " ".join(words)

    # normalize spaces
    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()



def extract_job_titles(job_poster_section):
    """
    Convert:

    {
        "Data Production Officer (EC 03)": {...},
        "Data Production Coordinator EC 03": {...}
    }

    into searchable dictionary
    """

    return {
        normalize_title(k): v
        for k, v in job_poster_section.items()
    }



def find_best_job_poster(
        classification,
        position_title,
        job_posters
):

    if classification not in job_posters:
        print(f"Classfication {classification} not found in job poster")
        return None


    candidates = extract_job_titles(
        job_posters[classification]
    )


    if not candidates:
        print(f"Candidate not found in job poster")
        return None


    normalized_target = normalize_title(
        position_title
    )


    # Exact match
    if normalized_target in candidates:
        return candidates[normalized_target]


    best_match = process.extractOne(
        normalized_target,
        candidates.keys(),
        scorer=fuzz.token_set_ratio
    )


    if not best_match:
        return None


    matched_title, score, _ = best_match


    print(
        f"Match: {position_title}"
        f" -> {matched_title}"
        f" ({score})"
    )


    if score >= MATCH_THRESHOLD:
        print(f"Added JP {matched_title} to WD {position_title}")
        return candidates[matched_title]


    return None



def process_file(
        input_file,
        output_file,
        job_posters
):

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)


    classification = data.get(
        "Classification"
    )


    positions = data.get(
        "Positions",
        []
    )


    for position in positions:

        # already populated
        # if "Job Poster" in position:
        #     continue


        position_title = position.get(
            "Position Title",
            ""
        )


        poster = find_best_job_poster(
            classification,
            position_title,
            job_posters
        )


        if poster:

            position["Job Poster"] = poster

        else:

            position["Job Poster"] = {}


    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )



def main():

    with open(
        JOB_POSTER_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        job_posters = json.load(f)["position"]


    for filename in os.listdir(RAW_DIR):

        if not filename.endswith(".json"):
            continue


        input_path = os.path.join(
            RAW_DIR,
            filename
        )


        output_path = os.path.join(
            OUTPUT_DIR,
            filename
        )


        print(
            "\nProcessing:",
            filename
        )


        process_file(
            input_path,
            output_path,
            job_posters
        )


    print(
        "\nCompleted."
    )



if __name__ == "__main__":
    main()