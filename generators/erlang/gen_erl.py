"""Generator of onedata errors for erlang."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
import shutil
from typing import Final, List, NamedTuple

import yaml

ERROR_DEFINITIONS_ROOT_DIR: Final[str] = "definitions"
OUTPUT_DIR: Final[str] = "generated/erlang"
TEMPLATES_DIR: Final[str] = os.path.join(os.path.dirname(__file__), "templates")


def read_template(template_name: str) -> str:
    with open(os.path.join(TEMPLATES_DIR, template_name)) as f:
        return f.read()


ERRORS_HRL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "errors.hrl")
ERRORS_HRL_TEMPLATE: Final[str] = read_template("errors.hrl.template")

OD_ERRORS_ROOT_DIR: Final[str] = os.path.join(OUTPUT_DIR, "types")
OD_ERROR_MODULE_TEMPLATE: Final[str] = read_template("od_error.erl.template")


HORIZONTAL_COMMENT_LINE: Final[str] = "%%" + 68 * "-"


class ErrorDefinition(NamedTuple):
    name: str
    type: str
    id: str
    args: List[str]
    errno: str
    http_code: str
    description: str


class ErrorGroup(NamedTuple):
    name: str
    error_definitions: List[ErrorDefinition]


def main():
    clean_output_dir()

    error_groups = gather_error_groups()
    generate_errors_hrl(error_groups)
    generate_od_errors(error_groups)


def clean_output_dir() -> None:
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR)


def gather_error_groups() -> List[ErrorGroup]:
    error_groups = []

    for parent_dir_path, _, file_names in os.walk(ERROR_DEFINITIONS_ROOT_DIR):
        if file_names:
            error_defs = [
                read_error_definition(os.path.join(parent_dir_path, file_name))
                for file_name in file_names
            ]
            error_groups.append(
                ErrorGroup(
                    name=os.path.relpath(parent_dir_path, ERROR_DEFINITIONS_ROOT_DIR),
                    error_definitions=error_defs,
                )
            )

    return error_groups


def read_error_definition(yaml_definition_path: str) -> ErrorDefinition:
    with open(yaml_definition_path, "r") as f:
        yaml_data = yaml.safe_load(f)

    error_name = os.path.splitext(os.path.basename(yaml_definition_path))[0]

    return ErrorDefinition(
        name=error_name,
        type=f"od_error_{error_name}",
        id=yaml_data["id"],
        args=yaml_data.get("args", []),
        errno=f"?{yaml_data['errno'].upper()}",
        http_code=f"?HTTP_{yaml_data['http_code'].upper()}",
        description=yaml_data["description"],
    )


def generate_errors_hrl(error_groups: List[ErrorGroup]) -> None:
    lines = []

    for error_group in error_groups:
        lines.append(HORIZONTAL_COMMENT_LINE)
        lines.append(f"%% {error_group.name} errors")
        lines.append(HORIZONTAL_COMMENT_LINE)

        for error_def in error_group.error_definitions:
            lines.append(build_error_type_macro(error_def))
            lines.append(build_error_pattern_macro(error_def))
            lines.append("")

    hrl_content = ERRORS_HRL_TEMPLATE.format(macros="\n".join(lines))

    with open(ERRORS_HRL_FILE_PATH, "w") as f:
        f.write(hrl_content)


def build_error_type_macro(error_def: ErrorDefinition) -> str:
    return f"-define(ERROR_{error_def.name.upper()}_TYPE, {error_def.type})."


def build_error_pattern_macro(error_def: ErrorDefinition) -> str:
    error_type_macro = f"?ERROR_{error_def.name.upper()}_TYPE"

    if not error_def.args:
        return f"-define(ERROR_{error_def.name.upper()}, ?ERROR({error_type_macro}))."

    args = ", ".join(f"__{arg.upper()}" for arg in error_def.args)
    return f"-define(ERROR_{error_def.name.upper()}({args}), ?ERROR({error_type_macro}, {{{args}}}))."


def generate_od_errors(error_groups: List[ErrorGroup]) -> None:
    for error_group in error_groups:
        output_dir = os.path.join(OUTPUT_DIR, error_group.name)
        os.makedirs(output_dir)

        for error_def in error_group.error_definitions:
            generate_od_error(output_dir, error_def)


def generate_od_error(output_dir: str, error_def: ErrorDefinition) -> None:
    output_file_path = os.path.join(output_dir, f"{error_def.type}.erl")
    module_code = OD_ERROR_MODULE_TEMPLATE.format(**error_def._asdict())

    with open(output_file_path, "w") as f:
        f.write(module_code)


if __name__ == "__main__":
    main()
