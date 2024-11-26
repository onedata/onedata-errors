"""DNS servers argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import (
    INDENT,
    ErrorArgType,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)
from ..context import JsonEncodingCtx, PrintEncodingCtx, JsonDecodingCtx


class DnsServers(ErrorArgType):
    """List of DNS servers."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
        PrintEncodingStrategy.CUSTOM
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = JsonDecodingStrategy.CUSTOM

    DNS_DEFAULTS: ClassVar[str] = '<<"system defaults">>'

    def _generate_json_encoding_expr_lines(self, ctx: JsonEncodingCtx) -> List[str]:
        return [
            "lists:map(fun\n",
            f"{INDENT}(default) -> {self.DNS_DEFAULTS};\n",
            f"{INDENT}(Ip) -> element(2, {{ok, _}} = ip_utils:to_binary(Ip))\n",
            f"end, {ctx.erl_var})",
        ]

    def _generate_print_encoding_expr_lines(self, ctx: PrintEncodingCtx) -> List[str]:
        return [f"?fmt_csv({ctx.json_var})"]

    def _generate_json_decoding_expr_lines(self, ctx: JsonDecodingCtx) -> List[str]:
        return [
            "lists:map(fun\n",
            f"{INDENT}({self.DNS_DEFAULTS}) -> default;\n",
            f"{INDENT}(Ip) -> element(2, {{ok, _}} = ip_utils:to_ip4_address(Ip))\n",
            f"end, {ctx.json_var})",
        ]
