"""Automation task argument value builder types argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.expressions import ListMapFunRefExpression
from ..translation.strategies import (
    CSVPrintEncodingStrategy,
    CustomStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class AtmTaskArgumentValueBuilderTypes(ErrorArgType):
    """List of automation task argument value builder types."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        ListMapFunRefExpression(
            module="atm_task_argument_value_builder",
            function="type_to_json",
            input_template="{erl_var}",
        )
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CSVPrintEncodingStrategy
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        ListMapFunRefExpression(
            module="atm_task_argument_value_builder",
            function="type_from_json",
            input_template="{json_var}",
        )
    )
