"""ATM task argument value builder types argument type."""

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


class AtmTaskArgumentValueBuilderTypes(ErrorArgType):
    """List of ATM task argument value builder types."""

    fmt_control_sequence = "~ts"
    json_encoding_strategy = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy = PrintEncodingStrategy.CUSTOM
    json_decoding_strategy = JsonDecodingStrategy.CUSTOM

    @classmethod
    def type_name(cls) -> str:
        return "AtmTaskArgumentValueBuilderTypes"

    def _generate_json_encoding_expr_lines(self, *, erl_var: str) -> List[str]:
        return [
            f"lists:map(fun atm_task_argument_value_builder:type_to_json/1, {erl_var})"
        ]

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"?fmt_csv({json_var})"]

    def _generate_json_decoding_expr_lines(self, *, json_var: str) -> List[str]:
        return [
            f"lists:map(fun atm_task_argument_value_builder:type_from_json/1, {json_var})"
        ]
