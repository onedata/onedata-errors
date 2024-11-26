"""ATM data types argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import List

from ..base import (
    ErrorArgType,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class AtmDataTypes(ErrorArgType):
    """List of ATM data types."""

    fmt_control_sequence = "~ts"
    json_encoding_strategy = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy = PrintEncodingStrategy.CUSTOM
    json_decoding_strategy = JsonDecodingStrategy.CUSTOM

    @classmethod
    def type_name(cls) -> str:
        return "AtmDataTypes"

    def _generate_json_encoding_expr_lines(self, *, erl_var: str) -> List[str]:
        return [f"lists:map(fun atm_data_type:type_to_json/1, {erl_var})"]

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"?fmt_csv({json_var})"]

    def _generate_json_decoding_expr_lines(self, *, json_var: str) -> List[str]:
        return [f"lists:map(fun atm_data_type:type_from_json/1, {json_var})"]
