"""Metric config argument type."""

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


class MetricConfig(ErrorArgType):
    """Metric config type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        FunCallExpression("jsonable_record", "to_json", ["{erl_var}", "metric_config"])
    )
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        FunCallExpression("metric_config", "to_binary", ["{erl_var}"])
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        FunCallExpression(
            "jsonable_record", "from_json", ["{json_var}", "metric_config"]
        )
    )
