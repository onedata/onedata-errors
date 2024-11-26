"""Path argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import ErrorArgType, JsonEncodingStrategy, PrintEncodingStrategy
from ..context import JsonEncodingCtx


class Path(ErrorArgType):
    """Path type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.FROM_JSON
    )

    def _generate_json_encoding_expr_lines(self, ctx: JsonEncodingCtx) -> List[str]:
        return [f"str_utils:to_binary(filename:flatten({ctx.erl_var}))"]
