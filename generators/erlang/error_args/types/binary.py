"""Binary error argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from ..base import ErrorArgType


class Binary(ErrorArgType):
    """Binary string type."""

    fmt_control_sequence = "~ts"

    @classmethod
    def type_name(cls) -> str:
        return "Binary"
