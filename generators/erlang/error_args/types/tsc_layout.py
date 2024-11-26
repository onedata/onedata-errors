"""TSC layout argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar, List

from ..base import INDENT, ErrorArgType, PrintEncodingStrategy
from ..translation_context import PrintEncodingCtx


class TscLayout(ErrorArgType):
    """TSC layout type."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    # TODO: Implement print encoding strategy
    # print_encoding_strategy: ClassVar[PrintEncodingStrategy] = (
    #     PrintEncodingStrategy.CUSTOM
    # )
    # def _generate_print_encoding_expr_lines(self, ctx: PrintEncodingCtx) -> List[str]:
    #     return [
    #         "od_error_utils:format_csv(maps:fold(fun(TimeSeriesName, MetricNames, Acc) ->\n",
    #         f'{INDENT}Acc ++ [?fmt("~ts -> [~ts]", [TimeSeriesName, ?fmt_csv(MetricNames)])]\n',
    #         f"end, [], {ctx.erl_var}))",
    #     ]
