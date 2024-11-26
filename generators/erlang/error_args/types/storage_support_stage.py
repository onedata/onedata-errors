"""Storage support stage argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..expressions import SimpleExpression
from ..translation_strategies import (
    CustomStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
)


class StorageSupportStage(ErrorArgType):
    """Storage support stage type."""

    fmt_control_sequence: ClassVar[str] = "~w"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        SimpleExpression("support_stage:serialize(storage, {var})")
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        SimpleExpression("support_stage:deserialize(storage, {var})")
    )
