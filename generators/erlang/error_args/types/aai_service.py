"""AAI service argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import (
    ErrorArgType,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)
from ..context import JsonEncodingCtx, PrintEncodingCtx, JsonDecodingCtx


class AaiService(ErrorArgType):
    """AAI service type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.CUSTOM
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    def _generate_json_encoding_expr_lines(self, ctx: JsonEncodingCtx) -> List[str]:
        return [f"aai:service_to_json({ctx.erl_var})"]

    def _generate_print_encoding_expr_lines(self, ctx: PrintEncodingCtx) -> List[str]:
        return [f"aai:service_to_printable({ctx.erl_var})"]

    def _generate_json_decoding_expr_lines(self, ctx: JsonDecodingCtx) -> List[str]:
        return [f"aai:service_from_json({ctx.json_var})"]
