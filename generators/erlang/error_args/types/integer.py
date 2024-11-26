"""Integer error argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType


class Integer(ErrorArgType):
    """Integer type."""

    fmt_control_sequence: ClassVar[str] = "~B"
