"""AAI consumer argument type."""

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
    PrintEncodingStrategy,
)


class AaiSubject(ErrorArgType):
    """AAI subject type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        SimpleExpression("aai:subject_to_json({var})")
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        SimpleExpression("aai:subject_to_printable({erl_var})")
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        SimpleExpression("aai:subject_from_json({var})")
    )
