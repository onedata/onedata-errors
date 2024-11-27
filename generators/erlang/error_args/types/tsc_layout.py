"""TSC layout argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..expressions import CodeLine, CodeLines
from ..translation_strategies import CustomStrategy, PrintEncodingStrategy


class TscLayout(ErrorArgType):
    """TSC layout type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CustomStrategy(
        CodeLines(
            [
                CodeLine(
                    "od_error:format_csv(maps:fold(fun(TimeSeriesName, MetricNames, Acc) ->"
                ),
                CodeLine(
                    'Acc ++ [str_utils:format_bin("~ts -> [~ts]", '
                    "[TimeSeriesName, od_error:format_csv(MetricNames)])]",
                    extra_indent=1,
                ),
                CodeLine("end, [], {erl_var}))", ending=","),
            ]
        )
    )
