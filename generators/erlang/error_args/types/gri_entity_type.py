"""GRI entity type argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..expressions import SimpleExpression
from ..translation_strategies import (
    CustomStrategy,
    FromJsonStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class GriEntityType(ErrorArgType):
    """GRI entity type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        SimpleExpression("gri:serialize_type({erl_var})")
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = FromJsonStrategy()
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        SimpleExpression("gri:deserialize_type({json_var})")
    )
