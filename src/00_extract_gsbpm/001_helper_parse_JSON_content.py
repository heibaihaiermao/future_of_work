import json
import re

def parse_json_content(response: str):
    # TODO: only work under assumption of json string is wrapped by ``` and ``` in input
    #       Should generalize it to any format of input string
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
    if not match:
        raise ValueError("No fenced JSON block found")

    json_str = match.group(1).strip()
    return json.loads(json_str)


def _test_parse_JSON_content():
    ## Test cases.
    #   - Use ".split" and ".strip", ".rstrip" or ".lstrip"
    #   - I don't anticipate much regex will be necessary here. It doesn't have to be a one-liner..

    # assert parse_json_content('{"salute": "hello", "subject": ["world"]}') == {"salute": "hello", "subject": ["world"]}
    assert parse_json_content('```json\n{"salute": "hello", "subject": ["world"]}```') == {"salute": "hello", "subject": ["world"]}
    assert parse_json_content("""Here's the content you requested! ```{"salute": "hello", "subject": ["world"]}```""") == {"salute": "hello", "subject": ["world"]}
    assert parse_json_content('```{"salute": "hello", "subject": ["world"]}```\n above this message is the content you requested!') == {"salute": "hello", "subject": ["world"]}