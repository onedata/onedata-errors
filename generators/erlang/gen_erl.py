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

ERRORS_ERL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "errors.erl")
ERRORS_ERL_TEMPLATE: Final[str] = read_template("errors.erl.template")

OD_ERROR_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "od_error.erl")
OD_ERROR_TEMPLATE: Final[str] = read_template("od_error.erl.template")


INDENT: Final[str] = 4 * " "
HORIZONTAL_COMMENT_LINE: Final[str] = "%%" + 68 * "-"


class OdError(NamedTuple):
    name: str
    type: str
    id: str
    args: List[str]


class OdErrorGroup(NamedTuple):
    name: str
    errors: List[OdError]


def main():
    clean_output_dir()

    error_groups = gather_error_groups()
    generate_errors_hrl(error_groups)
    generate_od_error()


def clean_output_dir() -> None:
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR)


def gather_error_groups() -> List[OdErrorGroup]:
    error_groups = []

    for parent_dir_path, _, file_names in os.walk(ERROR_DEFINITIONS_ROOT_DIR):
        if file_names:
            error_defs = [
                read_error_definition(os.path.join(parent_dir_path, file_name))
                for file_name in file_names
            ]
            error_groups.append(
                OdErrorGroup(
                    name=os.path.relpath(parent_dir_path, ERROR_DEFINITIONS_ROOT_DIR),
                    errors=error_defs,
                )
            )

    return error_groups


def read_error_definition(yaml_definition_path: str) -> OdError:
    with open(yaml_definition_path, "r") as f:
        yaml_data = yaml.safe_load(f)

    error_name = os.path.splitext(os.path.basename(yaml_definition_path))[0]

    return OdError(
        name=error_name,
        type=f"od_error_{error_name}",
        id=yaml_data["id"],
        args=yaml_data.get("args", []),
    )


def generate_errors_hrl(error_groups: List[OdErrorGroup]) -> None:
    lines = []

    for error_group in error_groups:
        lines.append(HORIZONTAL_COMMENT_LINE)
        lines.append(f"%% {error_group.name} errors")
        lines.append(HORIZONTAL_COMMENT_LINE)

        for error_def in error_group.errors:
            lines.append(build_error_type_macro(error_def))
            lines.append(build_error_pattern_macro(error_def))
            lines.append("")

    hrl_content = ERRORS_HRL_TEMPLATE.format(macros="\n".join(lines))

    with open(ERRORS_HRL_FILE_PATH, "w") as f:
        f.write(hrl_content)


def build_error_type_macro(od_error: OdError) -> str:
    return f"-define(ERROR_{od_error.name.upper()}_TYPE, {od_error.type})."


def build_error_pattern_macro(od_error: OdError) -> str:
    error_type_macro = f"?ERROR_{od_error.name.upper()}_TYPE"

    if not od_error.args:
        return f"-define(ERROR_{od_error.name.upper()}, ?ERROR({error_type_macro}))."

    args = ", ".join(f"__{arg.upper()}" for arg in od_error.args)
    return f"-define(ERROR_{od_error.name.upper()}({args}), ?ERROR({error_type_macro}, {{{args}}}))."


def generate_od_error() -> None:
    with open(OD_ERROR_FILE_PATH, "w") as f:
        f.write(OD_ERROR_TEMPLATE)


if __name__ == "__main__":
    main()
