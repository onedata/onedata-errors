"""ATM data types argument type."""

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


class AtmDataTypes(ErrorArgType):
    """List of ATM data types."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        ListMapFunRefExpression(
            module="atm_data_type", function="type_to_json", input_template="{erl_var}"
        )
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CSVPrintEncodingStrategy
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        ListMapFunRefExpression(
            module="atm_data_type",
            function="type_from_json",
            input_template="{json_var}",
        )
    )
