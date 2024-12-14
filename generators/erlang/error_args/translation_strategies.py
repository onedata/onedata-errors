"""Encoding/decoding strategies for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass

from .abc import (
    Expression,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PreparedExpression,
    PrintEncodingStrategy,
)
from .expressions import NoopExpression
from .translation_context import JsonDecodingCtx, JsonEncodingCtx, PrintEncodingCtx


@dataclass
class DirectStrategy(JsonEncodingStrategy, JsonDecodingStrategy, PrintEncodingStrategy):
    """Direct encoding/decoding - use variable as-is."""

    def prepare_json_encoding(self, ctx: JsonEncodingCtx) -> PreparedExpression:
        return PreparedExpression(NoopExpression(), ctx.erl_var)

    def prepare_json_decoding(self, ctx: JsonDecodingCtx) -> PreparedExpression:
        return PreparedExpression(NoopExpression(), ctx.json_var)

    def prepare_print_encoding(self, ctx: PrintEncodingCtx) -> PreparedExpression:
        return PreparedExpression(NoopExpression(), ctx.erl_var)


@dataclass
class FromJsonStrategy(PrintEncodingStrategy):
    """Use JSON representation for printing."""

    def prepare_print_encoding(self, ctx: PrintEncodingCtx) -> PreparedExpression:
        return PreparedExpression(NoopExpression(), ctx.json_var)


@dataclass
class CustomStrategy(JsonEncodingStrategy, JsonDecodingStrategy, PrintEncodingStrategy):
    """Custom encoding/decoding with expression."""

    expression: Expression

    def prepare_json_encoding(self, ctx: JsonEncodingCtx) -> PreparedExpression:
        return PreparedExpression(self.expression, ctx.assign_to)

    def prepare_json_decoding(self, ctx: JsonDecodingCtx) -> PreparedExpression:
        return PreparedExpression(self.expression, ctx.assign_to)

    def prepare_print_encoding(self, ctx: PrintEncodingCtx) -> PreparedExpression:
        return PreparedExpression(self.expression, ctx.assign_to)
