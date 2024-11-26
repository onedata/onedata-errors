"""Byte size argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import ErrorArgType, PrintEncodingStrategy


class ByteSize(ErrorArgType):
    """Byte size type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.CUSTOM
    )

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"str_utils:format_byte_size({erl_var})"]
