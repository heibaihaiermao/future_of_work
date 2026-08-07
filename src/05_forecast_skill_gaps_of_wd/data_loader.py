"""
===============================================================================
Module: data_loader.py

Description:
    Utility functions for loading data files from disk.

    - load_json(path):
        Reads a JSON file and deserializes its contents into Python objects
        (e.g., dictionaries, lists, strings, numbers).

    - load_text(path):
        Reads a text file and returns its raw contents as a string.

    All files are opened using UTF-8 encoding.

Author:
    Souroosh Memarian

Created:
    2026-07-20

Last Modified:
    2026-07-20
    
===============================================================================
"""

import json


def load_json(path):
    with open(
        path,
        encoding="utf-8"
    ) as f:
        return json.load(f)


def load_text(path):
    with open(
        path,
        encoding="utf-8"
    ) as f:
        return f.read()