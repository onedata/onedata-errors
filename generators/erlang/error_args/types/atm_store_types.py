"""ATM store schema IDs argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.expressions import ListMapFunRefExpression, SimpleExpression
from ..translation.strategies import (
    CustomStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PrintEncodingStrategy,
)


class AtmStoreTypes(ErrorArgType):
    """List of ATM store types."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        ListMapFunRefExpression(
            module="automation",
            function="store_type_to_json",
            input_template="{erl_var}",
        )
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        SimpleExpression("od_error:format_csv({json_var})")
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        ListMapFunRefExpression(
            module="automation",
            function="store_type_from_json",
            input_template="{json_var}",
        )
    )
