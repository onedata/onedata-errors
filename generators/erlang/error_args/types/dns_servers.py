"""DNS servers argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import List

from ..base import (
    INDENT,
    ErrorArgType,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class DnsServers(ErrorArgType):
    """List of DNS servers."""

    fmt_control_sequence = "~ts"
    json_encoding_strategy = JsonEncodingStrategy.CUSTOM
    print_encoding_strategy = PrintEncodingStrategy.CUSTOM
    json_decoding_strategy = JsonDecodingStrategy.CUSTOM

    DNS_DEFAULTS = '<<"system defaults">>'

    @classmethod
    def type_name(cls) -> str:
        return "DnsServers"

    def _generate_json_encoding_expr_lines(self, *, erl_var: str) -> List[str]:
        return [
            "lists:map(fun\n",
            f"{INDENT}(default) -> {self.DNS_DEFAULTS};\n",
            f"{INDENT}(Ip) -> element(2, {{ok, _}} = ip_utils:to_binary(Ip))\n",
            f"end, {erl_var})",
        ]

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return [f"?fmt_csv({json_var})"]

    def _generate_json_decoding_expr_lines(self, *, json_var: str) -> List[str]:
        return [
            "lists:map(fun\n",
            f"{INDENT}({self.DNS_DEFAULTS}) -> default;\n",
            f"{INDENT}(Ip) -> element(2, {{ok, _}} = ip_utils:to_ip4_address(Ip))\n",
            f"end, {json_var})",
        ]
