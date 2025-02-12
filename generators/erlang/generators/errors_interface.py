"""Generator for errors.erl interface module."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from ..constants import ERRORS_ERL_FILE_PATH
from .utils import write_to_file


def generate_errors_interface_module(template: str) -> None:
    """Generate errors.erl interface module from template."""
    erl_content = template.format()
    write_to_file(ERRORS_ERL_FILE_PATH, erl_content)
