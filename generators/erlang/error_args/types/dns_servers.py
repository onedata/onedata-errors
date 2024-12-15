"""DNS servers argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.expressions import ListMapExpression, SimpleExpression
from ..translation.strategies import (
    CustomStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class DnsServers(ErrorArgType):
    """List of DNS servers."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    DNS_DEFAULTS: ClassVar[str] = '<<"system defaults">>'

    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        ListMapExpression(
            fun_clauses=[
                ("default", SimpleExpression(DNS_DEFAULTS)),
                (
                    "Ip",
                    SimpleExpression("element(2, {{ok, _}} = ip_utils:to_binary(Ip))"),
                ),
            ],
            input_template="{erl_var}",
        )
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        SimpleExpression("od_error:format_csv({json_var})")
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        ListMapExpression(
            fun_clauses=[
                (DNS_DEFAULTS, SimpleExpression("default")),
                (
                    "Ip",
                    SimpleExpression(
                        "element(2, {{ok, _}} = ip_utils:to_ip4_address(Ip))"
                    ),
                ),
            ],
            input_template="{json_var}",
        )
    )
