"""Generator for errors.hrl file."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import List

from ..constants import ERRORS_HRL_FILE_PATH, HORIZONTAL_COMMENT_LINE
from ..error_definitions import OdError, OdErrorGroup
from .utils import write_to_file


def generate_errors_hrl(error_groups: List[OdErrorGroup], template: str) -> None:
    lines = _generate_errors_hrl_group_lines(error_groups)
    hrl_content = template.format(macros="\n".join(lines))
    write_to_file(ERRORS_HRL_FILE_PATH, hrl_content)


def _generate_errors_hrl_group_lines(error_groups: List[OdErrorGroup]) -> List[str]:
    lines = []
    for error_group in error_groups:
        lines.extend(_generate_errors_hrl_group_header(error_group))
        lines.extend(_generate_errors_hrl_definitions(error_group.errors))
        lines.append("")

    # delete last empty line
    del lines[-1]
    return lines


def _generate_errors_hrl_group_header(error_group: OdErrorGroup) -> List[str]:
    return [
        HORIZONTAL_COMMENT_LINE,
        f"%% {error_group.name} errors",
        HORIZONTAL_COMMENT_LINE,
    ]


def _generate_errors_hrl_definitions(od_errors: List[OdError]) -> List[str]:
    lines = []
    for od_error in od_errors:
        lines.extend(
            [
                _build_error_id_macro_definition(od_error),
                _build_error_type_macro_definition(od_error),
                _build_error_macro_definition(od_error),
                "",
            ]
        )
    return lines


def _build_error_id_macro_definition(od_error: OdError) -> str:
    return f'-define({od_error.get_id_macro()}, <<"{od_error.id}">>).'


def _build_error_type_macro_definition(od_error: OdError) -> str:
    return f"-define({od_error.get_type_macro()}, {od_error.type})."


def _build_error_macro_definition(od_error: OdError) -> str:
    error_type_macro = f"?{od_error.get_type_macro()}"
    error_macro = od_error.get_error_macro()

    if od_error.args:
        args = ", ".join(od_error.get_args_as_erlang_variable_names())
        error_expansion = f"?ERROR({error_type_macro}, {{{args}}})"
    else:
        error_expansion = f"?ERROR({error_type_macro})"

    return f"-define({error_macro}, {error_expansion})."
