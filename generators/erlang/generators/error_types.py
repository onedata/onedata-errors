"""Generator for individual error modules."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
import re
from typing import List, Dict

from ..constants import ERROR_TYPES_DIR, INDENT, HTTP_CODE_TO_MACRO
from ..error_definitions import OdError, OdErrorGroup
from .utils import write_to_file


def generate_error_types(error_groups: List[OdErrorGroup], template: str) -> None:
    """Generate individual error module files for each error group."""
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

    encoding_tokens = []
    details_tokens = []

    fmt_placeholders = re.findall(r"\{(\w+)\}", od_error.description)
    fmt_placeholder_to_fmt_var: Dict[str, str] = {}
    fmt_placeholder_to_control_sequence: Dict[str, str] = {}

    for macro in od_error.ctx.macros:
        if macro.alias in fmt_placeholders:
            fmt_placeholder_to_fmt_var[macro.alias] = macro.ref
            fmt_placeholder_to_control_sequence[macro.alias] = macro.fmt_control_sequence

    if od_error.args:
        details_tokens.append(f'{2*INDENT}<<"details">> => #{{\n')

        for arg in od_error.args:
            arg_encoding = arg.generate_to_json_encoding(
                is_printed=arg.name in fmt_placeholders
            )

            if arg_encoding.tokens:
                encoding_tokens.extend(arg_encoding.tokens)

            details_tokens.extend(
                [3 * INDENT, f'<<"{arg.name}">> => {arg_encoding.json_var}', ",\n"]
            )

            fmt_placeholder_to_fmt_var[arg.name] = arg_encoding.print_var
            fmt_placeholder_to_control_sequence[arg.name] = arg.fmt_control_sequence

        if encoding_tokens:
            encoding_tokens.append("\n")

        details_tokens[-1] = f"\n{2*INDENT}}},\n"

    description_tokens = _generate_description_tokens(
        od_error.description,
        fmt_placeholders,
        fmt_placeholder_to_fmt_var,
        fmt_placeholder_to_control_sequence
    )

    tokens = [
        f"to_json(?{od_error.get_error_macro()}) ->\n",
        *encoding_tokens,
        f"{INDENT}#{{\n",
        f'{2*INDENT}<<"id">> => ?{od_error.get_id_macro()},\n',
        *details_tokens,
        f'{2*INDENT}<<"description">> => ',
        *description_tokens,
        f"{INDENT}}}.",
    ]

    return "".join(tokens)


def _generate_description_tokens(
    description: str,
    fmt_placeholders: List[str],
    fmt_placeholder_to_fmt_var: Dict[str, str],
    fmt_placeholder_to_control_sequence: Dict[str, str],
) -> List[str]:
    if fmt_placeholders:
        fmt_str = (
            description.replace("\n", "\\n")
            .format(**fmt_placeholder_to_control_sequence)
            .replace('"', '\\"')
        )
        fmt_vars = [
            fmt_placeholder_to_fmt_var[placeholder] for placeholder in fmt_placeholders
        ]
        return [
            "?fmt(\n",
            f'{3*INDENT}"{fmt_str}",\n',
            f"{3*INDENT}[",
            ", ".join(fmt_vars),
            "]\n",
            f"{2*INDENT})\n",
        ]
    
    description = description.replace("\n", "\\n")
    return [f'<<"{description}">>\n']


def _generate_from_json_callback(od_error: OdError) -> str:
    if od_error.from_json:
        return od_error.from_json.strip()

    tokens = ["from_json(", f'#{{<<"id">> := ?{od_error.get_id_macro()}}}', ") ->\n"]

    if od_error.args:
        tokens.insert(1, "OdErrorJson = ")

        details_var = "DetailsJson"
        tokens.append(f'{INDENT}{details_var} = maps:get(<<"details">>, OdErrorJson')
        if all(arg.nullable for arg in od_error.args):
            tokens.append(", #{}")
        tokens.append("),\n\n")

        for arg in od_error.args:
            tokens.extend(arg.generate_from_json_decoding(details_var=details_var))

        tokens.append("\n")

    tokens.append(f"{INDENT}?{od_error.get_error_macro()}.")

    return "".join(tokens)


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