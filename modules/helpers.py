import re


def sanitize_string(input_string: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\.-]", "", input_string)
