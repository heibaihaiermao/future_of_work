"""
===============================================================================
File: output_writer.py

Purpose:
    Provides utility functions for writing application data to output files.

Functions:
    save_json(data, path)
        Serializes Python objects and writes them to a JSON file using
        UTF-8 encoding and human-readable formatting.

Author:
    Souroosh Memarian

Created:
    2026-07-21

Last Modified:
    2026-07-21

Notes:
    - Output files are encoded using UTF-8.
    - JSON content is formatted with an indentation level of 4 spaces.
    - Non-ASCII characters are preserved using ensure_ascii=False,
      allowing accented and multilingual text to be written directly.
    - Existing files at the target path will be overwritten.

===============================================================================
"""

import json


def save_json(data, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )