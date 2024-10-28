"""Generator of onedata errors for erlang."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
import re
import shutil

from typing import Final, List, NamedTuple

from error_arguments import ErrorArg, load_argument

import yaml

ERROR_DEFINITIONS_ROOT_DIR: Final[str] = "definitions"
OUTPUT_DIR: Final[str] = "generated/erlang"
TEMPLATES_DIR: Final[str] = os.path.join(os.path.dirname(__file__), "templates")


def read_template(template_name: str) -> str:
    with open(os.path.join(TEMPLATES_DIR, template_name)) as f:
        return f.read()


ERRORS_HRL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "errors.hrl")
ERRORS_HRL_TEMPLATE: Final[str] = read_template("errors.hrl.template")

ERRORS_ERL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "errors.erl")
ERRORS_ERL_TEMPLATE: Final[str] = read_template("errors.erl.template")

OD_ERROR_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "od_error.erl")
OD_ERROR_TEMPLATE: Final[str] = read_template("od_error.erl.template")

ERROR_TYPES_DIR: Final[str] = os.path.join(OUTPUT_DIR, "types")
ERROR_TEMPLATE: Final[str] = read_template("error.erl.template")


INDENT: Final[str] = 4 * " "
HORIZONTAL_COMMENT_LINE: Final[str] = "%%" + 68 * "-"


class OdError(NamedTuple):
    name: str
    type: str
    id: str
    description: str
    http_code: int
    args: List[ErrorArg]

    def get_id_macro(self) -> str:
        return f"ERROR_{self.name.upper()}_ID"

    def get_type_macro(self) -> str:
        return f"ERROR_{self.name.upper()}_TYPE"

    def get_args_as_erlang_variable_names(self) -> List[str]:
        return [arg.get_erlang_variable_name() for arg in self.args]

    def get_error_macro(self) -> str:
        if not self.args:
            return f"ERROR_{self.name.upper()}"

        args = ", ".join(self.get_args_as_erlang_variable_names())
        return f"ERROR_{self.name.upper()}({args})"


class OdErrorGroup(NamedTuple):
    name: str
    errors: List[OdError]


def main():
    clean_output_dir()

    error_groups = load_error_groups()

    generate_errors_hrl(error_groups)
    generate_od_error_behaviour()
    generate_errors_interface_module(error_groups)
    generate_error_modules(error_groups)


def clean_output_dir() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_error_groups() -> List[OdErrorGroup]:
    error_groups = [
        create_error_group(parent_dir_path, sorted(file_names))
        for parent_dir_path, _, file_names in os.walk(ERROR_DEFINITIONS_ROOT_DIR)
        if file_names
    ]
    return sorted(error_groups, key=lambda x: x.name)


def create_error_group(parent_dir_path: str, file_names: List[str]) -> OdErrorGroup:
    od_errors = [
        load_error_definition(os.path.join(parent_dir_path, file_name))
        for file_name in file_names
    ]
    return OdErrorGroup(
        name=os.path.relpath(parent_dir_path, ERROR_DEFINITIONS_ROOT_DIR),
        errors=od_errors,
    )


def load_error_definition(yaml_definition_path: str) -> OdError:
    yaml_data = read_yaml_file(yaml_definition_path)
    error_name = extract_error_name(yaml_definition_path)
    args = []

    for arg in yaml_data.get("args", []):
        args.append(load_argument(arg))

    return OdError(
        name=error_name,
        type=f"od_error_{error_name}",
        id=yaml_data["id"],
        description=yaml_data["description"],
        http_code=yaml_data["http_code"],
        args=args,
    )


def read_yaml_file(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def extract_error_name(file_path: str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]


def generate_errors_hrl(error_groups: List[OdErrorGroup]) -> None:
    lines = generate_errors_hrl_group_lines(error_groups)
    hrl_content = ERRORS_HRL_TEMPLATE.format(macros="\n".join(lines))
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


def generate_od_error_behaviour() -> None:
    with open(OD_ERROR_FILE_PATH, "w") as f:
        f.write(OD_ERROR_TEMPLATE)


def generate_errors_interface_module(error_groups: List[OdErrorGroup]) -> None:
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

    erl_content = ERRORS_ERL_TEMPLATE.format(
        types=" |\n".join(types), id_to_type_mapping=",\n".join(id_to_type_mapping)
    )

    write_to_file(ERRORS_ERL_FILE_PATH, erl_content)


def generate_error_modules(error_groups: List[OdErrorGroup]) -> None:
    for group in error_groups:
        group_dir = os.path.join(ERROR_TYPES_DIR, group.name)
        os.makedirs(group_dir, exist_ok=True)

        for od_error in group.errors:
            generate_error_module(od_error, group_dir)


def generate_error_module(od_error: OdError, output_dir: str) -> None:
    to_http_code = f"to_http_code(_) -> {od_error.http_code}."

    erl_content = ERROR_TEMPLATE.format(
        error_type=od_error.type,
        to_json=generate_to_json_callback(od_error),
        from_json=generate_from_json_callback(od_error),
        to_http_code=to_http_code,
    )

    file_path = os.path.join(output_dir, f"{od_error.type}.erl")
    write_to_file(file_path, erl_content)


def generate_to_json_callback(od_error: OdError) -> str:
    encoding_tokens = []
    details_tokens = []
    description_tokens = [f'<<"{od_error.description}">>\n']

    if od_error.args:
        details_tokens.append(f'{2*INDENT}<<"details">> => #{{\n')

        fmt_placeholders = re.findall(r"\{(\w+)\}", od_error.description)
        fmt_placeholder_to_print_var = {}
        fmt_placeholder_to_control_sequence = {}

        for arg in od_error.args:
            arg_encoding = arg.generate_to_json_encoding(
                is_printed=arg.name in fmt_placeholders
            )

            if arg_encoding.tokens:
                encoding_tokens.extend(arg_encoding.tokens)
                encoding_tokens.append("\n")

            details_tokens.extend(
                [3 * INDENT, f'<<"{arg.name}">> => {arg_encoding.json_var}', ",\n"]
            )

            fmt_placeholder_to_print_var[arg.name] = arg_encoding.print_var
            fmt_placeholder_to_control_sequence[arg.name] = arg.fmt_control_sequence

        # replace last comma with closing bracket
        details_tokens[-1] = f"\n{2*INDENT}}},\n"

        fmt_str = od_error.description.format(**fmt_placeholder_to_control_sequence)
        print_vars = [
            fmt_placeholder_to_print_var[placeholder]
            for placeholder in fmt_placeholders
        ]
        description_tokens = [
            "?fmt(\n",
            f'{3*INDENT}"{fmt_str}",\n',
            f"{3*INDENT}[",
            ", ".join(print_vars),
            "]\n",
            f"{2*INDENT})\n",
        ]

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
    lines = [
        f"from_json(#{{'id' := ?{od_error.get_id_macro()}, 'details' := Details}}) ->"
    ]
    if od_error.args:
        for arg in od_error.args:
            if arg.nullable:
                lines.append(
                    f'    {arg.name} = maps:get(<<"{arg.name}">>, Details, undefined),'
                )
            else:
                lines.append(f'    {arg.name} = maps:get(<<"{arg.name}">>, Details),')
        lines.append(
            f"    ?{od_error.get_error_macro()}({', '.join(arg.name for arg in od_error.args)});"
        )
    else:
        lines.append(f"    ?{od_error.get_error_macro()};")
    return "\n".join(lines)


def generate_error_dialyzer_type(od_error: OdError) -> str:
    return f"{INDENT}{od_error.type}:t()"


def generate_error_id_to_type_mapping(od_error: OdError) -> str:
    return f"{INDENT}?{od_error.get_id_macro()} => ?{od_error.get_type_macro()}"


def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
