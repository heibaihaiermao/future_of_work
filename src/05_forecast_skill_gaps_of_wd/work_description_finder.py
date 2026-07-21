"""
===============================================================================
File: work_description_finder.py

Purpose:
    Provides utility functions for locating and retrieving work descriptions
    based on a job classification and position title.

Functions:
    get_job_family(work_descriptions, classification)
        Retrieves the list of positions associated with a specified
        classification.

    select_position(positions, title)
        Finds and returns a single position matching the provided title.

    find_work_description(work_descriptions, classification, title)
        Retrieves a specific work description by combining classification
        and position title lookups.

Author:
    Souroosh Memarian 

Created:
    2026-07-20

Last Modified:
    2026-07-20

Version:
    1.0.0

Notes:
    - Classification comparisons are case-insensitive.
    - Position title comparisons are case-sensitive.
    - A ValueError is raised if a classification cannot be found.
    - A ValueError is raised if a position lookup results in zero or
      multiple matches.

===============================================================================
"""


def get_job_family(
    work_descriptions,
    classification
):

    for family in work_descriptions:

        if family["Classification"].lower() == (
            classification.lower()
        ):
            return family["Positions"]

    raise ValueError(
        f"Classification not found: {classification}"
    )


def select_position(
    positions,
    title
):

    matches = [
        p
        for p in positions
        if p["Position Title"] == title
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Position lookup failed: {title}"
        )

    return matches[0]


def find_work_description(
    work_descriptions,
    classification,
    title
):

    family = get_job_family(
        work_descriptions,
        classification
    )

    return select_position(
        family,
        title
    )