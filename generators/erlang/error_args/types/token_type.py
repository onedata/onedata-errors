"""Token type argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.expressions import FunCallExpression
from ..translation.strategies import (
    CustomStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class TokenType(ErrorArgType):
    """Token type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        FunCallExpression("token_type", "to_json", ["{erl_var}"])
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        FunCallExpression("token_type", "to_printable", ["{erl_var}"])
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        FunCallExpression("token_type", "from_json", ["{json_var}"])
    )
