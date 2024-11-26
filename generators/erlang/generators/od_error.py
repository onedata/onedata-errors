"""Generator for od_error.erl file."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from ..constants import OD_ERROR_FILE_PATH
from .utils import write_to_file


def generate_od_error_behaviour(template: str) -> None:
    """Generate od_error.erl behaviour file from template."""
    write_to_file(OD_ERROR_FILE_PATH, template) 