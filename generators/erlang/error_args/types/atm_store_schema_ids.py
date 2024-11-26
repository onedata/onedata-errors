"""ATM store schema IDs argument type."""

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


class AtmStoreSchemaIds(ErrorArgType):
    """List of ATM store schema IDs."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.CUSTOM
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    def _generate_json_encoding_expr_lines(self, *, erl_var: str) -> List[str]:
        return [f"lists:map(fun automation:store_type_to_json/1, {erl_var})"]

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"?fmt_csv({json_var})"]

    def _generate_json_decoding_expr_lines(self, *, json_var: str) -> List[str]:
        return [f"lists:map(fun automation:store_type_from_json/1, {json_var})"]
