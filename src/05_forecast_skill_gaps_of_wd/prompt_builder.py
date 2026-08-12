"""
===============================================================================
File: prompt_builder.py

Purpose:
    Builds the system prompt used for future skills forecasting and work
    description impact analysis.

    The prompt is composed from reusable text fragments and the target
    work description.

Author:
    Souroosh Memarian (Statistics Canada)

Created:
    2026-07-21

Last Modified:
    2026-07-29

Version:
    2.0.0

Dependencies:
    - json.dumps
    - config
    - data_loader

===============================================================================
"""

from json import dumps

from config import ROOT
from data_loader import load_text

PROMPTS_DIR = (
    ROOT
    /
    "prompts"
)

background = load_text(
    PROMPTS_DIR
    /
    "prompt_01_-_background_prompt.txt"
)

wd_intro = load_text(
    PROMPTS_DIR
    /
    "prompt_03_-_work-description_context_intro.txt"
)

task = load_text(
    PROMPTS_DIR
    /
    "prompt_04_-_task_and_schema.txt"
)


def build_system_prompt(
    work_description
):

    return f"""
{background}

## Context

### Targeted Work-description

{wd_intro}

```json
{dumps(work_description, indent=2)}
{task}

RESPOND IN VALID JSON ONLY. """