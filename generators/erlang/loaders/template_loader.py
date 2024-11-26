"""Module responsible for loading and managing templates."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
from typing import NamedTuple

from ..constants import TEMPLATES_DIR


class Templates(NamedTuple):
    errors_hrl: str
    errors_erl: str
    od_error: str
    error: str


def load_all_templates() -> Templates:
    return Templates(
        errors_hrl=_read_template("errors.hrl.template"),
        errors_erl=_read_template("errors.erl.template"),
        od_error=_read_template("od_error.erl.template"),
        error=_read_template("error.erl.template"),
    )


def _read_template(template_name: str) -> str:
    with open(os.path.join(TEMPLATES_DIR, template_name), encoding="utf-8") as f:
        return f.read()
