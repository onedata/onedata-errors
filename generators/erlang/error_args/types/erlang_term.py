"""Erlang term argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from ..base import ErrorArgType


class ErlangTerm(ErrorArgType):
    """Erlang term type."""

    fmt_control_sequence = "~tp"

    @classmethod
    def type_name(cls) -> str:
        return "ErlangTerm"
