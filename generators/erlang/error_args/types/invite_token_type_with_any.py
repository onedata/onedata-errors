"""Invite token type with any argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import INDENT, ErrorArgType, JsonDecodingStrategy, JsonEncodingStrategy


class InviteTokenTypeWithAny(ErrorArgType):
    """Invite token type with any."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    def _generate_json_encoding_expr_lines(self, *, erl_var: str) -> List[str]:
        return [
            f"case {erl_var} of\n",
            f'{INDENT}any -> <<"any">>;\n',
            f"{INDENT}_ -> token_type:invite_type_to_str({erl_var})\n",
            f"end",
        ]

    def _generate_json_decoding_expr_lines(self, *, json_var: str) -> List[str]:
        return [
            f"case {json_var} of\n",
            f'{INDENT}<<"any">> -> any;\n',
            f"{INDENT}_ -> token_type:invite_type_from_str({json_var})\n",
            f"end",
        ]
