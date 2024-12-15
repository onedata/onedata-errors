"""ATM task argument value builder type argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.expressions import SimpleExpression
from ..translation.strategies import (
    CustomStrategy,
    FromJsonStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class AtmTaskArgumentValueBuilderType(ErrorArgType):
    """ATM task argument value builder type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        SimpleExpression("atm_task_argument_value_builder:type_to_json({erl_var})")
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = FromJsonStrategy()
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        SimpleExpression("atm_task_argument_value_builder:type_from_json({json_var})")
    )
