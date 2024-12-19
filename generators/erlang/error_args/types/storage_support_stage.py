"""Storage support stage argument type."""

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
)


class StorageSupportStage(ErrorArgType):
    """Storage support stage type."""

    fmt_control_sequence: ClassVar[str] = "~w"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        FunCallExpression("support_stage", "serialize", ["storage", "{erl_var}"])
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        FunCallExpression("support_stage", "deserialize", ["storage", "{json_var}"])
    )
