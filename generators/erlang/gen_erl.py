"""Generator of onedata errors for erlang."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
import shutil

from .constants import OUTPUT_DIR
from .generators.error_types import generate_error_types
from .generators.errors_headers import generate_errors_headers
from .generators.errors_interface import generate_errors_interface_module
from .generators.od_error import generate_od_error_behaviour
from .loaders.error_definitions_loader import load_error_definitions
from .loaders.template_loader import load_templates


def main():
    clean_output_dir()

    templates = load_templates()
    error_groups = load_error_definitions()

    generate_errors_headers(error_groups, templates)
    generate_od_error_behaviour(templates.od_error)
    generate_errors_interface_module(error_groups, templates.errors_erl)
    generate_error_types(error_groups, templates.error)


def clean_output_dir() -> None:
    """Clean and recreate output directory."""
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


if __name__ == "__main__":
    main()
