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

    def get_id_macro(self) -> str:
        return f"ERROR_{self.name.upper()}_ID"

    def get_type_macro(self) -> str:
        return f"ERROR_{self.name.upper()}_TYPE"

    def get_args_as_erlang_variable_names(self) -> List[str]:
        return [arg[0].upper() + arg[1:] for arg in self.args]

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
    generate_od_error()
    generate_errors_erl(error_groups)


def clean_output_dir() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_error_groups() -> List[OdErrorGroup]:
    error_groups = []

    for parent_dir_path, _, file_names in os.walk(ERROR_DEFINITIONS_ROOT_DIR):
        if file_names:
            file_names.sort()
            error_groups.append(create_error_group(parent_dir_path, file_names))

    return sorted(error_groups, key=lambda x: x.name)


def create_error_group(parent_dir_path: str, file_names: List[str]) -> OdErrorGroup:
    od_errors = [load_error_definition(os.path.join(parent_dir_path, file_name))
                 for file_name in file_names]
    return OdErrorGroup(
        name=os.path.relpath(parent_dir_path, ERROR_DEFINITIONS_ROOT_DIR),
        errors=od_errors
    )


def load_error_definition(yaml_definition_path: str) -> OdError:
    yaml_data = read_yaml_file(yaml_definition_path)
    error_name = extract_error_name(yaml_definition_path)
    return create_od_error(error_name, yaml_data)


def read_yaml_file(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def extract_error_name(file_path: str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]


def create_od_error(error_name: str, yaml_data: dict) -> OdError:
    return OdError(
        name=error_name,
        type=f"od_error_{error_name}",
        id=yaml_data["id"],
        args=yaml_data.get("args", [])
    )


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
        HORIZONTAL_COMMENT_LINE
    ]


def generate_errors_hrl_definitions(od_errors: List[OdError]) -> List[str]:
    lines = []
    for od_error in od_errors:
        lines.extend([
            build_error_id_macro_definition(od_error),
            build_error_type_macro_definition(od_error),
            build_error_macro_definition(od_error),
            ""
        ])

    return lines


def build_error_id_macro_definition(od_error: OdError) -> str:
    return f"-define({od_error.get_id_macro()}, <<\"{od_error.id}\">>)."


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


def generate_od_error() -> None:
    with open(OD_ERROR_FILE_PATH, "w") as f:
        f.write(OD_ERROR_TEMPLATE)


def generate_errors_erl(error_groups: List[OdErrorGroup]) -> None:
    types = [generate_error_dialyzer_type(od_error)
             for group in error_groups
             for od_error in group.errors]

    id_to_type_mapping = [generate_error_id_to_type_mapping(od_error)
                          for group in error_groups
                          for od_error in group.errors]

    erl_content = ERRORS_ERL_TEMPLATE.format(
        types=" |\n".join(types),
        id_to_type_mapping=",\n".join(id_to_type_mapping)
    )

    write_to_file(ERRORS_ERL_FILE_PATH, erl_content)


def generate_error_dialyzer_type(od_error: OdError) -> str:
    return f"{INDENT}{od_error.type}:t()"


def generate_error_id_to_type_mapping(od_error: OdError) -> str:
    return f"{INDENT}?{od_error.get_id_macro()} => ?{od_error.get_type_macro()}"


def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
