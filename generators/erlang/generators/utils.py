"""Common utilities for generators."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"


def write_to_file(file_path: str, content: str) -> None:
    """Write content to file with UTF-8 encoding."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
