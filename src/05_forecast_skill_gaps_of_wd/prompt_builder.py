"""
===============================================================================
File: prompt_builder.py

Purpose:
    Generates standardized system prompts for Large Language Model (LLM)
    interactions related to workforce planning, skills forecasting, and
    future competency analysis.

Functions:
    build_system_prompt(organizational_inputs, work_description)
        Constructs a structured system prompt that provides organizational
        context, work description details, and analysis requirements for
        forecasting future skill needs and competency gaps.

Author:
    Souroosh Memarian
Created:
    2026-07-21

Last Modified:
    2026-07-21

Version:
    1.0.0

Dependencies:
    - json.dumps

Notes:
    - Embeds organizational inputs and work description data directly into
      the system prompt as formatted JSON.
    - Guides the LLM to focus on future-state workforce requirements and
      competency forecasting.
    - Emphasizes identification of skill gaps rather than summarization of
      current job responsibilities.
    - Instructs the model to return responses in valid JSON format only.
    - Designed to support workforce modernization, business transformation,
      automation readiness, and AI-adoption initiatives.

Analysis Areas:
    - Business process changes
    - Future-state operating models
    - Critical skills forecasting
    - Technical skills forecasting
    - AI-related competencies
    - Automation-related competencies
    - Data competencies
    - Governance competencies
    - Metadata competencies
    - Platform competencies

===============================================================================
"""

from json import dumps


def build_system_prompt(
    work_description
):

    return f"""
You are an expert workforce planner,
strategic HR analyst,
future-of-work specialist,
and skills forecasting consultant.

OBJECTIVE

Forecast future critical skills required
for this role.

CONTEXT

WORK DESCRIPTION

{dumps(work_description, indent=2)}

ANALYSIS REQUIREMENTS

You must:

1. Analyze business process changes.

2. Analyze future-state operating model.

3. Forecast future critical skills.

4. Forecast future technical skills.

5. Forecast AI-related skills.

6. Forecast automation-related skills.

7. Forecast data competencies.

8. Forecast governance competencies.

9. Forecast metadata competencies.

10. Forecast platform competencies.

Focus primarily on SKILL GAPS.

Do not spend time rewriting the work description.

A skill gap is present whenever future
business processes require competencies
that are absent or weakly represented in
the current work description.

Return valid JSON only.
"""