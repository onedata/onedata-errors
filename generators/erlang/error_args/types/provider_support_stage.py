"""Provider support stage argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import ErrorArgType, JsonDecodingStrategy, JsonEncodingStrategy
from ..context import JsonEncodingCtx, JsonDecodingCtx


class ProviderSupportStage(ErrorArgType):
    """Provider support stage type."""

    fmt_control_sequence: ClassVar[str] = "~w"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    def _generate_json_encoding_expr_lines(self, ctx: JsonEncodingCtx) -> List[str]:
        return [f"support_stage:serialize(provider, {ctx.erl_var})"]

    def _generate_json_decoding_expr_lines(self, ctx: JsonDecodingCtx) -> List[str]:
        return [f"support_stage:deserialize(provider, {ctx.json_var})"]
