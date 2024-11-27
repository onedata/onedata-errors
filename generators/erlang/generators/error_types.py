"""Generator for individual error modules."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
import re
from typing import Dict, List, NamedTuple, Tuple

from ..constants import ERROR_TYPES_DIR, HTTP_CODE_TO_MACRO, INDENT
from ..error_definitions import OdError, OdErrorGroup
from .utils import write_to_file


class FormatPlaceholders(NamedTuple):
    """Container for format placeholders and their mappings."""

    placeholders: List[str]
    fmt_vars: Dict[str, str]
    control_sequences: Dict[str, str]


def generate_error_types(error_groups: List[OdErrorGroup], template: str) -> None:
    """Generate individual error type modules for each error group."""
    for group in error_groups:
        group_dir = os.path.join(ERROR_TYPES_DIR, group.name)
        os.makedirs(group_dir, exist_ok=True)

        for od_error in group.errors:
            _generate_error_type(od_error, group_dir, template)


def _generate_error_type(od_error: OdError, output_dir: str, template: str) -> None:
    includes = "\n".join(f'-include("{hrl}").' for hrl in od_error.ctx.includes)

    erl_content = template.format(
        includes=includes,
        error_type=od_error.type,
        to_json=_generate_to_json_callback(od_error),
        from_json=_generate_from_json_callback(od_error),
        to_http_code=_generate_to_http_code_callback(od_error),
    )

    file_path = os.path.join(output_dir, f"{od_error.type}.erl")
    write_to_file(file_path, erl_content)


def _generate_to_json_callback(od_error: OdError) -> str:
    if od_error.to_json:
        return od_error.to_json.strip()

    fmt_info = _collect_format_placeholders(od_error)
    encoding_tokens, details_tokens = _generate_encoding_and_details(od_error, fmt_info)

    description_tokens = _generate_description_tokens(od_error.description, fmt_info)

    return "".join(
        [
            f"to_json(?{od_error.get_match_macro()}) ->\n",
            *encoding_tokens,
            f"{INDENT}#{{\n",
            f'{2*INDENT}<<"id">> => ?{od_error.get_id_macro()},\n',
            *details_tokens,
            f'{2*INDENT}<<"description">> => ',
            *description_tokens,
            f"{INDENT}}}.",
        ]
    )


def _collect_format_placeholders(od_error: OdError) -> FormatPlaceholders:
    fmt_placeholders = re.findall(r"\{(\w+)\}", od_error.description)
    fmt_vars: Dict[str, str] = {}
    control_sequences: Dict[str, str] = {}

    for macro in od_error.ctx.macros:
        if macro.alias in fmt_placeholders:
            fmt_vars[macro.alias] = macro.ref
            control_sequences[macro.alias] = macro.fmt_control_sequence

    return FormatPlaceholders(fmt_placeholders, fmt_vars, control_sequences)


def _generate_encoding_and_details(
    od_error: OdError, fmt_info: FormatPlaceholders
) -> Tuple[List[str], List[str]]:
    encoding_tokens: List[str] = []
    details_tokens: List[str] = []

    if not od_error.args:
        return encoding_tokens, details_tokens

    details_tokens.append(f'{2*INDENT}<<"details">> => #{{\n')

    for arg in od_error.args:
        arg_encoding = arg.generate_to_json_encoding(
            is_printed=arg.name in fmt_info.placeholders
        )

        if arg_encoding.tokens:
            encoding_tokens.extend(arg_encoding.tokens)

        details_tokens.extend(
            [3 * INDENT, f'<<"{arg.name}">> => {arg_encoding.json_var}', ",\n"]
        )

        if arg_encoding.print_var:
            fmt_info.fmt_vars[arg.name] = arg_encoding.print_var
            fmt_info.control_sequences[arg.name] = arg.fmt_control_sequence

    if encoding_tokens:
        encoding_tokens.append("\n")

    details_tokens[-1] = f"\n{2*INDENT}}},\n"

    return encoding_tokens, details_tokens


def _generate_description_tokens(
    description: str,
    fmt_info: FormatPlaceholders,
) -> List[str]:
    if fmt_info.placeholders:
        fmt_str = (
            description.replace("\n", "\\n")
            .format(**fmt_info.control_sequences)
            .replace('"', '\\"')
        )
        fmt_vars = ", ".join(
            fmt_info.fmt_vars[placeholder] for placeholder in fmt_info.placeholders
        )
        return [
            "od_error:format_description(\n",
            f'{3*INDENT}"{fmt_str}",\n',
            f"{3*INDENT}[",
            fmt_vars,
            "]\n",
            f"{2*INDENT})\n",
        ]

    description = description.replace("\n", "\\n")
    return [f'<<"{description}">>\n']


def _generate_from_json_callback(od_error: OdError) -> str:
    if od_error.from_json:
        return od_error.from_json.strip()

    return _generate_default_from_json(od_error)


def _generate_default_from_json(od_error: OdError) -> str:
    tokens = ["from_json(", f'#{{<<"id">> := ?{od_error.get_id_macro()}}}', ") ->\n"]

    if od_error.args:
        tokens.insert(1, "OdErrorJson = ")
        tokens.extend(_generate_args_decoding(od_error))

    tokens.append(f"{INDENT}?{od_error.get_new_macro()}.")

    return "".join(tokens)


def _generate_args_decoding(od_error: OdError) -> List[str]:
    """Generate tokens for decoding error arguments from JSON."""
    details_var = "DetailsJson"
    tokens = [f'{INDENT}{details_var} = maps:get(<<"details">>, OdErrorJson']

    if all(arg.nullable for arg in od_error.args):
        tokens.append(", #{}")
    tokens.append("),\n\n")

    for arg in od_error.args:
        tokens.extend(arg.generate_from_json_decoding(details_var=details_var))

    tokens.append("\n")
    return tokens


def _generate_to_http_code_callback(od_error: OdError) -> str:
    http_code = od_error.http_code

    if isinstance(http_code, int):
        http_code_macro = HTTP_CODE_TO_MACRO[http_code]
        return "".join(
            [
                f"-spec to_http_code(t()) -> {http_code_macro}.\n",
                "to_http_code(_) ->\n",
                f"{INDENT}{http_code_macro}.",
            ]
        )

    return http_code
