"""GRI entity type as atom argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import ErrorArgType, JsonDecodingStrategy, PrintEncodingStrategy


class GriEntityTypeAsAtom(ErrorArgType):
    """GRI entity type as atom."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.CUSTOM
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"gri:serialize_type({erl_var})"]
