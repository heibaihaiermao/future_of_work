MODULE: Map Updated GSBPM to Work Descriptions

PURPOSE:
    Identify which work descriptions (roles) are impacted by updated GSBPM elements.

INPUTS:
    1. Updated GSBPM (Step 2 output) (sample file name:2025-10-01_-_direct_mapping_-_GSBPM_updates_to_work-descriptions_-_prompt.py)
        - contains:
            - id
            - title
            - updated description

    2. Work Descriptions (Step 3 output)(sample input file name: all file under /prompt_construction)
        - contains:
            - title
            - responsibilities / tasks

--------------------------------------------------

STEP 1: AI STEP (Reasoning)

    FUNCTION:
        - Compare updated GSBPM elements with work descriptions
        - Determine which roles are affected by which GSBPM elements

    PROCESS:
        for each GSBPM element:
            for each work description:
                evaluate impact
                if impacted:
                    record (work description → GSBPM id)

    OUTPUT:
        file: all.json

    FORMAT:
        [
            {
                "title": "Work Description Name",
                "implicated phases and sub-processes": [
                    { "id": 2 },
                    { "id": 2.1 }
                ]
            }
        ]

--------------------------------------------------

STEP 2: CODE STEP (Data Transformation)

    FILE:
        collect_by_phase.py

    FUNCTION:
        - Reorganize mapping for downstream use

    INPUT:
        all.json

    TRANSFORMATION:
        from:
            Work Description → [GSBPM IDs]

        to:
            GSBPM ID → [Work Descriptions]

    PROCESS:
        build dictionary:
            wd_ids = {
                WD_title: [id1, id2, ...]
            }

        for each id:
            find all WD_title containing that id

    OUTPUT:
        {
            "2": ["Metadata Production Officer"],
            "2.1": ["Metadata Production Officer"],
            "3": ["Data Analyst"]
        }

--------------------------------------------------

EXAMPLE (END-TO-END)

INPUT (from AI step):
    all.json

    [
        {
            "title": "Metadata Production Officer",
            "implicated phases and sub-processes": [
                { "id": 2 },
                { "id": 2.1 }
            ]
        },
        {
            "title": "Data Analyst",
            "implicated phases and sub-processes": [
                { "id": 3 }
            ]
        }
    ]

OUTPUT (after code step):

    {
        "2": ["Metadata Production Officer"],
        "2.1": ["Metadata Production Officer"],
        "3": ["Data Analyst"]
    }

--------------------------------------------------

SUMMARY:

    Step 2 output + Step 3 output
        → AI reasoning
        → all.json
        → Python script
        → grouped mapping (GSBPM → roles)