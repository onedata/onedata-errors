"""AAI (Authentication and Authorization Infrastructure) consumer argument type."""

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


class AaiSubject(ErrorArgType):
    """AAI (Authentication and Authorization Infrastructure) subject type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        FunCallExpression("aai", "subject_to_json", ["{erl_var}"])
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        FunCallExpression("aai", "subject_to_printable", ["{erl_var}"])
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        FunCallExpression("aai", "subject_from_json", ["{json_var}"])
    )
