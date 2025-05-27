import os
import re
from pathlib import Path


def get_project_root() -> Path:
    return Path(os.getcwd())


def get_logging_config():
    # Get the absolute path of the logger.ini file in the config directory
    config_file_path = os.path.join(get_project_root(), "logger.ini")
    return config_file_path


def clean_string_whitespace(args):
    return re.sub(r'[^a-zA-Z0-9]', '', args)


def get_content_at_line(string, line_number):
    # Split the string into lines
    lines = string.split('\n')

    # Check if the line number is valid
    if 1 <= line_number <= len(lines):
        # Return the content of the line at the specified line number
        return lines[line_number - 1]
    else:
        # Return None if the line number is out of range
        return None
