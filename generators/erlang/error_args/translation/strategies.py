"""Encoding/decoding strategies for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .context import JsonDecodingCtx, JsonEncodingCtx, PrintEncodingCtx
from .expressions import (
    Expression,
    NoopExpression,
    PreparedExpression,
    SimpleExpression,
)


# pylint: disable=too-few-public-methods
class JsonEncodingStrategy(ABC):
    """Strategy for JSON encoding."""

    @abstractmethod
    def prepare_json_encoding(self, ctx: "JsonEncodingCtx") -> PreparedExpression:
        """Prepare expression for JSON encoding."""


# pylint: disable=too-few-public-methods
class JsonDecodingStrategy(ABC):
    """Strategy for JSON decoding."""

    @abstractmethod
    def prepare_json_decoding(self, ctx: "JsonDecodingCtx") -> PreparedExpression:
        """Prepare expression for JSON decoding."""


# pylint: disable=too-few-public-methods
class PrintEncodingStrategy(ABC):
    """Strategy for print encoding."""

    @abstractmethod
    def prepare_print_encoding(self, ctx: "PrintEncodingCtx") -> PreparedExpression:
        """Prepare expression for print encoding."""


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
        if ctx.assign_to is None:
            raise ValueError("assign_to must be a non-None string for CustomStrategy.")

        return PreparedExpression(self.expression, ctx.assign_to)

    def prepare_json_decoding(self, ctx: JsonDecodingCtx) -> PreparedExpression:
        if ctx.assign_to is None:
            raise ValueError("assign_to must be a non-None string for CustomStrategy.")

        return PreparedExpression(self.expression, ctx.assign_to)

    def prepare_print_encoding(self, ctx: PrintEncodingCtx) -> PreparedExpression:
        if ctx.assign_to is None:
            raise ValueError("assign_to must be a non-None string for CustomStrategy.")

        return PreparedExpression(self.expression, ctx.assign_to)


CSVPrintEncodingStrategy = CustomStrategy(
    SimpleExpression("od_error:format_csv({json_var})")
)
