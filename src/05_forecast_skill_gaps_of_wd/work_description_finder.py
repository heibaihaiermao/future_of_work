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


"""
===============================================================================
File: work_description_finder.py
===============================================================================
"""


def find_work_description(
    work_descriptions,
    classification,
    title
):

    for family in work_descriptions:

        if (
            family["Classification"].strip().lower()
            !=
            classification.strip().lower()
        ):
            continue

        matches = [
            position
            for position in family["Positions"]
            if (
                position["Position Title"]
                ==
                title
            )
        ]

        if len(matches) == 1:
            return matches[0]

    raise ValueError(
        f"Position '{title}' not found "
        f"for classification '{classification}'"
    )