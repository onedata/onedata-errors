"""Generator for errors.erl interface module."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import List

from ..constants import ERRORS_ERL_FILE_PATH, INDENT
from ..error_definitions import OdError, OdErrorGroup
from .utils import write_to_file


def generate_errors_interface_module(
    error_groups: List[OdErrorGroup], template: str
) -> None:
    """Generate errors.erl interface module from template."""
    types = [
        _generate_error_dialyzer_type(od_error)
        for group in error_groups
        for od_error in group.errors
    ]

    erl_content = template.format(types=" |\n".join(types))

    write_to_file(ERRORS_ERL_FILE_PATH, erl_content)


def _generate_error_dialyzer_type(od_error: OdError) -> str:
    return f"{INDENT}{od_error.type}:t()"
