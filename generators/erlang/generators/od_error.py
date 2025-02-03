"""Generator for od_error.erl file."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import subprocess
from typing import Dict, List, Tuple, TypedDict

from ..constants import INDENT, OD_ERROR_FILE_PATH
from ..error_definitions import OdError, OdErrorGroup
from .utils import write_to_file


class GroupTree(TypedDict):
    errors: List[OdError]
    subgroups: Dict[str, "GroupTree"]


def generate_od_error_behaviour(
    template: str, error_groups: List[OdErrorGroup]
) -> None:
    """Generate od_error.erl behaviour file from template."""
    error_group_type_specs, error_group_type_exports = _generate_error_group_type_specs(
        error_groups
    )

    content = template.format(
        version=generate_version(),
        error_group_type_specs="\n\n".join(error_group_type_specs),
        error_group_type_exports=f",\n{INDENT}".join(error_group_type_exports),
    )
    write_to_file(OD_ERROR_FILE_PATH, content)


def _generate_error_group_type_specs(
    error_groups: List[OdErrorGroup],
) -> Tuple[List[str], List[str]]:
    """Generate hierarchical type specs for error groups."""
    group_tree: GroupTree = {"errors": [], "subgroups": {}}
    for group in error_groups:
        path_parts = group.name.split("/")
        current_dict = group_tree
        for part in path_parts:
            if part not in current_dict["subgroups"]:
                current_dict["subgroups"][part] = {"errors": [], "subgroups": {}}
            current_dict = current_dict["subgroups"][part]

        current_dict["errors"] = group.errors

    return _generate_type_specs_from_tree({"": group_tree})


def _generate_type_specs_from_tree(
    tree: Dict[str, GroupTree], prefix: str = ""
) -> Tuple[List[str], List[str]]:
    """Recursively generate type specs from group tree."""
    specs = []
    exports = []

    for group_name, group_data in tree.items():
        current_prefix = f"{prefix}{group_name}_".lstrip("_")
        type_name = f"{current_prefix}error"

        # Generate type specs for subgroups
        subgroup_specs, subgroup_exports = _generate_type_specs_from_tree(
            group_data["subgroups"], current_prefix
        )
        specs.extend(subgroup_specs)
        exports.extend(subgroup_exports)

        # Collect all types for this group
        type_parts = []

        # Add errors directly from this group
        if group_data["errors"]:
            error_types = [
                f"{INDENT}{error.type}:t()" for error in group_data["errors"]
            ]
            type_parts.extend(error_types)

        if type_name == "error":
            type_parts.append(f"{INDENT}deprecated_error()")

        # Add types from subgroups
        for subgroup_name in group_data["subgroups"]:
            subgroup_type = f"{current_prefix}{subgroup_name}_error()"
            type_parts.append(f"{INDENT}{subgroup_type}")

        if type_parts:
            spec = f"-type {type_name}() ::\n" + " |\n".join(type_parts) + "."
            specs.append(spec)
            exports.append(f"{type_name}/0")

    return specs, exports


def generate_version() -> str:
    """Generate version string based on git commit hash."""
    try:
        # Get the current commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()[:8]
    except (subprocess.CalledProcessError, subprocess.SubprocessError):
        return "unknown"
