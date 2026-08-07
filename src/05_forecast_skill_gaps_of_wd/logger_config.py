"""
===============================================================================
File: logger_config.py

Purpose:
    Provides centralized logging configuration for the application.

Functions:
    configure_logging()
        Configures the application's logging system with a standard
        format and default INFO logging level, then returns the root
        logger instance.

Author:
    Souroosh Memarian

Created:
    2026-07-21

Last Modified:
    2026-07-21


Notes:
    - Logging is configured using Python's built-in logging module.
    - Default log level is INFO.
    - Log messages include:
        * Timestamp
        * Log level
        * Message content
    - Returns the root logger for use throughout the application.
    - Calling logging.basicConfig() multiple times in the same process
      may not have any effect if logging has already been configured.

Example Log Output:
    2026-07-21 14:30:15,123 | INFO | Application started

===============================================================================
"""

import logging


def configure_logging():

    logging.basicConfig(
        level=logging.INFO,
        format=
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    return logging.getLogger()