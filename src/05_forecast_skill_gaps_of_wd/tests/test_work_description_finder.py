import pytest

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

from work_description_finder import (
    find_work_description
)


def test_find_match():

    work_descriptions = [

        {
            "title":
            "Economist",

            "classification":
            "EC"
        }

    ]

    result = (
        find_work_description(
            work_descriptions,
            "EC",
            "Economist"
        )
    )

    assert (
        result["title"]
        ==
        "Economist"
    )


def test_missing_match():

    work_descriptions = []

    with pytest.raises(
        Exception
    ):

        find_work_description(
            work_descriptions,
            "EC",
            "Economist"
        )