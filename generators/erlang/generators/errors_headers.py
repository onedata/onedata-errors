"""Generator for errors.hrl file."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import List

from ..constants import (
    ERROR_ATTRS_HRL_FILE_PATH,
    ERRORS_HRL_FILE_PATH,
    HORIZONTAL_COMMENT_LINE,
    INDENT,
)
from ..error_definitions import OdError, OdErrorGroup
from ..loaders.template_loader import Templates
from .utils import write_to_file


def generate_errors_headers(
    error_groups: List[OdErrorGroup], templates: Templates
) -> None:
    generate_error_attrs_hrl(error_groups, templates.error_attrs_hrl)
    generate_errors_hrl(error_groups, templates.errors_hrl)


def generate_error_attrs_hrl(error_groups: List[OdErrorGroup], template: str) -> None:
    macros = _generate_error_attrs_id_and_type_macros(error_groups)
    id_to_type_mapping = _build_error_attrs_id_to_type_mapping(error_groups)
    attrs_content = template.format(
        macros=macros, id_to_type_mapping=id_to_type_mapping
    )
    write_to_file(ERROR_ATTRS_HRL_FILE_PATH, attrs_content)


def _generate_error_attrs_id_and_type_macros(
    error_groups: List[OdErrorGroup],
) -> str:
    lines = []
    for error_group in error_groups:
        lines.extend(_generate_errors_hrl_group_header(error_group))

        for od_error in error_group.errors:
            lines.extend(
                [
                    _build_error_id_macro_definition(od_error),
                    _build_error_type_macro_definition(od_error),
                    "",
                ]
            )

        lines.append("")

    # delete last empty line
    del lines[-1]
    return "\n".join(lines).strip()


def _build_error_id_macro_definition(od_error: OdError) -> str:
    return f'-define({od_error.get_id_macro()}, <<"{od_error.id}">>).'


def _build_error_type_macro_definition(od_error: OdError) -> str:
    return f"-define({od_error.get_type_macro()}, {od_error.type})."


def _build_error_attrs_id_to_type_mapping(error_groups: List[OdErrorGroup]) -> str:
    id_to_type_mapping = [
        _generate_error_id_to_type_mapping(od_error)
        for group in error_groups
        for od_error in group.errors
    ]

    return ",\n".join(id_to_type_mapping)


def _generate_error_id_to_type_mapping(od_error: OdError) -> str:
    return f"{INDENT}?{od_error.get_id_macro()} => ?{od_error.get_type_macro()}"


def generate_errors_hrl(error_groups: List[OdErrorGroup], template: str) -> None:
    lines = _generate_errors_hrl_group_lines(error_groups)
    hrl_content = template.format(macros="\n".join(lines))
    write_to_file(ERRORS_HRL_FILE_PATH, hrl_content)


def _generate_errors_hrl_group_lines(error_groups: List[OdErrorGroup]) -> List[str]:
    lines = []
    for error_group in error_groups:
        lines.extend(_generate_errors_hrl_group_header(error_group))
        for od_error in error_group.errors:
            lines.extend(
                [
                    _build_error_match_macro_definition(od_error),
                    _build_error_new_macro_definition(od_error),
                    "",
                ]
            )

        lines.append("")

    # delete last empty line
    del lines[-1]
    return lines


def _build_error_match_macro_definition(od_error: OdError) -> str:
    error_type_macro = f"?{od_error.get_type_macro()}"
    match_macro = od_error.get_match_macro()

    if od_error.args:
        args = ", ".join(od_error.get_args_as_erlang_variable_names())
        error_expansion = f"?ERR({error_type_macro}, {{{args}}})"
    else:
        error_expansion = f"?ERR({error_type_macro})"

    return f"-define({match_macro}, {error_expansion})."


def _build_error_new_macro_definition(od_error: OdError) -> str:
    error_type_macro = f"?{od_error.get_type_macro()}"
    new_macro = od_error.get_new_macro()

    if od_error.args:
        args = ", ".join(od_error.get_args_as_erlang_variable_names())
        error_expansion = f"?ERR({error_type_macro}, {{{args}}}, ErrCtx)"
    else:
        error_expansion = f"?ERR({error_type_macro}, undefined, ErrCtx)"

    return f"-define({new_macro}, {error_expansion})."


def _generate_errors_hrl_group_header(error_group: OdErrorGroup) -> List[str]:
    return [
        HORIZONTAL_COMMENT_LINE,
        f"%% {error_group.name} errors",
        HORIZONTAL_COMMENT_LINE,
    ]
