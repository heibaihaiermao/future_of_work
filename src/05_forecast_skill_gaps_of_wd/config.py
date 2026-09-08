"""
===============================================================================
File: config.py

Purpose:
    Defines application-wide configuration settings, file locations, and
    directory paths used throughout the project.

Configuration:
    ROOT
        Root directory of the application.

    DATA_DIR
        Directory containing input and output data files.

    WORK_DESCRIPTIONS_FILE
        Path to the work descriptions dataset.

    GSBPM_IMPACTS_FILE
        Path to the dataset containing GSBPM update implications for work
        descriptions.

    OUTPUT_DIR
        Directory where generated outputs and analysis results are stored.

Author:
    Souroosh Memarian

Created:
    2026-07-21

Last Modified:
    2026-08-24

Version:
    1.0.0

Dependencies:
    - pathlib

Notes:
    - All paths are defined using pathlib.Path for improved readability,
      portability, and cross-platform compatibility.
    - The output directory is automatically created if it does not already
      exist.
    - Centralizing configuration values simplifies maintenance and reduces
      hard-coded file paths throughout the application.
    - Relative paths are resolved from the directory containing this file.

===============================================================================
"""

from pathlib import Path

ROOT = Path(__file__).parent

DATA_DIR = ROOT / "data"

WORK_DESCRIPTIONS_FILE = (
    DATA_DIR / "wd_update_input" / "test_JD.json"
)

GSBPM_IMPACTS_FILE = (
    DATA_DIR / "wd_update_input" / "test_implicated.json"
)

OUTPUT_DIR = DATA_DIR / "outputs"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)