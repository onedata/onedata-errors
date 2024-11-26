"""ATM task argument value builder types argument type."""

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


class AtmTaskArgumentValueBuilderTypes(ErrorArgType):
    """List of ATM task argument value builder types."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.CUSTOM
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    def _generate_json_encoding_expr_lines(self, ctx: JsonEncodingCtx) -> List[str]:
        return [
            f"lists:map(fun atm_task_argument_value_builder:type_to_json/1, {ctx.erl_var})"
        ]

    def _generate_print_encoding_expr_lines(self, ctx: PrintEncodingCtx) -> List[str]:
        return [f"?fmt_csv({ctx.json_var})"]

    def _generate_json_decoding_expr_lines(self, ctx: JsonDecodingCtx) -> List[str]:
        return [
            f"lists:map(fun atm_task_argument_value_builder:type_from_json/1, {ctx.json_var})"
        ]
