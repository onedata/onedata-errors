"""Module responsible for loading error definitions from YAML files."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
from typing import Dict, List

import yaml

from ..constants import ERROR_DEFINITIONS_ROOT_DIR
from ..error_args.loader import create_error_arg
from ..error_definitions import MacroRef, OdError, OdErrorCtx, OdErrorGroup


def load_error_definitions() -> List[OdErrorGroup]:
    """Loads all error definitions groups from definitions directory."""
    error_groups = [
        _create_error_group(parent_dir_path, sorted(file_names))
        for parent_dir_path, _, file_names in os.walk(ERROR_DEFINITIONS_ROOT_DIR)
        if file_names
    ]
    return sorted(error_groups, key=lambda x: x.name)


def _create_error_group(parent_dir_path: str, file_names: List[str]) -> OdErrorGroup:
    od_errors = [
        _load_error_definition(os.path.join(parent_dir_path, file_name))
        for file_name in file_names
    ]
    return OdErrorGroup(
        name=os.path.relpath(parent_dir_path, ERROR_DEFINITIONS_ROOT_DIR),
        errors=od_errors,
    )


def _load_error_definition(yaml_definition_path: str) -> OdError:
    yaml_data = _read_yaml_file(yaml_definition_path)
    error_name = _extract_error_name(yaml_definition_path)
    args = [create_error_arg(arg) for arg in yaml_data.get("args", [])]

    return OdError(
        name=error_name,
        type=f"od_error_{error_name}",
        id=yaml_data["id"],
        description=yaml_data["description"],
        http_code=yaml_data["http_code"],
        args=args,
        ctx=_load_error_ctx(yaml_data),
        to_json=yaml_data.get("x-erl-to_json"),
        from_json=yaml_data.get("x-erl-from_json"),
    )


def _read_yaml_file(file_path: str) -> Dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _extract_error_name(file_path: str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]


def _load_error_ctx(yaml_data: Dict) -> OdErrorCtx:
    includes = []
    macros = []

    if "x-erl-headers" in yaml_data:
        headers = yaml_data["x-erl-headers"]
        includes = headers.get("include", [])
        macros = [_load_macro(macro_yaml) for macro_yaml in headers.get("macros", [])]

    return OdErrorCtx(includes=includes, macros=macros)


def _load_macro(macro_yaml: Dict) -> MacroRef:
    return MacroRef(
        alias=macro_yaml["alias"],
        ref=macro_yaml["ref"],
        fmt_control_sequence=macro_yaml.get("fmt_control_sequence", "~ts"),
    )
