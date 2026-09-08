import pytest

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

from response_parser import (
    parse_response
)


def test_valid_json():

    response = """
    {
        "skill":"Python"
    }
    """

    result = parse_response(
        response
    )

    assert (
        result["skill"]
        ==
        "Python"
    )


def test_invalid_json():

    response = """
    { invalid json }
    """

    with pytest.raises(
        Exception
    ):

        parse_response(
            response
        )