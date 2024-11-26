"""Binaries error argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import List

from ..base import ErrorArgType, PrintEncodingStrategy


class Binaries(ErrorArgType):
    """List of binary strings type."""

    fmt_control_sequence = "~ts"
    print_encoding_strategy = PrintEncodingStrategy.CUSTOM

    @classmethod
    def type_name(cls) -> str:
        return "Binaries"

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"?fmt_csv({erl_var})"]
