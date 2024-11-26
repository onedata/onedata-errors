"""Generator of onedata errors for erlang."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
import re
import shutil
from typing import List

from .constants import (
    ERROR_TYPES_DIR,
    ERRORS_ERL_FILE_PATH,
    ERRORS_HRL_FILE_PATH,
    HORIZONTAL_COMMENT_LINE,
    HTTP_CODE_TO_MACRO,
    INDENT,
    OD_ERROR_FILE_PATH,
    OUTPUT_DIR,
)
from .error_args.loader import TypeLoader
from .error_definitions import OdError, OdErrorGroup
from .loaders.error_definitions_loader import load_error_definitions
from .loaders.template_loader import load_all_templates


def main():
    TypeLoader.load_types()
    templates = load_all_templates()

    clean_output_dir()

    error_groups = load_error_definitions()

    generate_errors_hrl(error_groups, templates.errors_hrl)
    generate_od_error_behaviour(templates.od_error)
    generate_errors_interface_module(error_groups, templates.errors_erl)
    generate_error_modules(error_groups, templates.error)


def clean_output_dir() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_errors_hrl(error_groups: List[OdErrorGroup], template: str) -> None:
    lines = generate_errors_hrl_group_lines(error_groups)
    hrl_content = template.format(macros="\n".join(lines))
    write_to_file(ERRORS_HRL_FILE_PATH, hrl_content)


def generate_errors_hrl_group_lines(error_groups: List[OdErrorGroup]) -> List[str]:
    lines = []
    for error_group in error_groups:
        lines.extend(generate_errors_hrl_group_header(error_group))
        lines.extend(generate_errors_hrl_definitions(error_group.errors))
        lines.append("")

    # delete last empty line
    del lines[-1]

    return lines


def generate_errors_hrl_group_header(error_group: OdErrorGroup) -> List[str]:
    return [
        HORIZONTAL_COMMENT_LINE,
        f"%% {error_group.name} errors",
        HORIZONTAL_COMMENT_LINE,
    ]


def generate_errors_hrl_definitions(od_errors: List[OdError]) -> List[str]:
    lines = []
    for od_error in od_errors:
        lines.extend(
            [
                build_error_id_macro_definition(od_error),
                build_error_type_macro_definition(od_error),
                build_error_macro_definition(od_error),
                "",
            ]
        )

    return lines


def build_error_id_macro_definition(od_error: OdError) -> str:
    return f'-define({od_error.get_id_macro()}, <<"{od_error.id}">>).'


def build_error_type_macro_definition(od_error: OdError) -> str:
    return f"-define({od_error.get_type_macro()}, {od_error.type})."


def build_error_macro_definition(od_error: OdError) -> str:
    error_type_macro = f"?{od_error.get_type_macro()}"
    error_macro = od_error.get_error_macro()

    if od_error.args:
        args = ", ".join(od_error.get_args_as_erlang_variable_names())
        error_expansion = f"?ERROR({error_type_macro}, {{{args}}})"
    else:
        error_expansion = f"?ERROR({error_type_macro})"

    return f"-define({error_macro}, {error_expansion})."


def generate_od_error_behaviour(template: str) -> None:
    write_to_file(OD_ERROR_FILE_PATH, template)


def generate_errors_interface_module(
    error_groups: List[OdErrorGroup], template: str
) -> None:
    types = [
        generate_error_dialyzer_type(od_error)
        for group in error_groups
        for od_error in group.errors
    ]

    id_to_type_mapping = [
        generate_error_id_to_type_mapping(od_error)
        for group in error_groups
        for od_error in group.errors
    ]

    erl_content = template.format(
        types=" |\n".join(types), id_to_type_mapping=",\n".join(id_to_type_mapping)
    )

    write_to_file(ERRORS_ERL_FILE_PATH, erl_content)


def generate_error_modules(error_groups: List[OdErrorGroup], template: str) -> None:
    for group in error_groups:
        group_dir = os.path.join(ERROR_TYPES_DIR, group.name)
        os.makedirs(group_dir, exist_ok=True)

        for od_error in group.errors:
            generate_error_module(od_error, group_dir, template)


def generate_error_module(od_error: OdError, output_dir: str, template: str) -> None:
    includes = "\n".join(f'-include("{hrl}").' for hrl in od_error.ctx.includes)

    erl_content = template.format(
        includes=includes,
        error_type=od_error.type,
        to_json=generate_to_json_callback(od_error),
        from_json=generate_from_json_callback(od_error),
        to_http_code=generate_to_http_code_callback(od_error),
    )

    file_path = os.path.join(output_dir, f"{od_error.type}.erl")
    write_to_file(file_path, erl_content)


def generate_to_json_callback(od_error: OdError) -> str:
    if od_error.to_json:
        return od_error.to_json.strip()

    encoding_tokens = []
    details_tokens = []

    fmt_placeholders = re.findall(r"\{(\w+)\}", od_error.description)
    fmt_placeholder_to_fmt_var = {}
    fmt_placeholder_to_control_sequence = {}

    for macro in od_error.ctx.macros:
        if macro.alias in fmt_placeholders:
            fmt_placeholder_to_fmt_var[macro.alias] = macro.ref
            fmt_placeholder_to_control_sequence[macro.alias] = (
                macro.fmt_control_sequence
            )

    if od_error.args:
        details_tokens.append(f'{2*INDENT}<<"details">> => #{{\n')

        for arg in od_error.args:
            # import pdb; pdb.set_trace()
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

        # replace last comma with closing bracket
        details_tokens[-1] = f"\n{2*INDENT}}},\n"

    if fmt_placeholders:
        fmt_str = (
            od_error.description.replace("\n", "\\n")
            .format(**fmt_placeholder_to_control_sequence)
            .replace('"', '\\"')
        )
        fmt_vars = [
            fmt_placeholder_to_fmt_var[placeholder] for placeholder in fmt_placeholders
        ]
        description_tokens = [
            "?fmt(\n",
            f'{3*INDENT}"{fmt_str}",\n',
            f"{3*INDENT}[",
            ", ".join(fmt_vars),
            "]\n",
            f"{2*INDENT})\n",
        ]
    else:
        description = od_error.description.replace("\n", "\\n")
        description_tokens = [f'<<"{description}">>\n']

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


def generate_from_json_callback(od_error: OdError) -> str:
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


def generate_to_http_code_callback(od_error: OdError) -> str:
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


def generate_error_dialyzer_type(od_error: OdError) -> str:
    return f"{INDENT}{od_error.type}:t()"


def generate_error_id_to_type_mapping(od_error: OdError) -> str:
    return f"{INDENT}?{od_error.get_id_macro()} => ?{od_error.get_type_macro()}"


def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
