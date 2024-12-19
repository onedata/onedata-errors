"""Abstract base classes and interfaces for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Dict, List, Optional

from .core import Line

if TYPE_CHECKING:
    from .context import JsonDecodingCtx, JsonEncodingCtx, PrintEncodingCtx


class TranslationContext(ABC):
    """Base class for all translation contexts."""

    @property
    @abstractmethod
    def indent_level(self) -> int:
        """Required indentation level for code generation."""

    @property
    @abstractmethod
    def assign_to(self) -> Optional[str]:
        """Target variable name for assignment."""

    @abstractmethod
    def get_template_vars(self) -> Dict[str, str]:
        """Returns variables available for template formatting.

        Should be implemented instead of _format_fields.
        """

    def format_template(self, template: str) -> str:
        """Format template using context variables."""
        try:
            return template.format(**self.get_template_vars())
        except KeyError as e:
            available = list(self.get_template_vars().keys())
            raise ValueError(
                f"Invalid template variable {e} in '{template}'. "
                f"Available variables: {available}"
            ) from e

    def with_indent(self, diff: int) -> "TranslationContext":
        """Return new context with increased indentation."""
        return replace(self, indent_level=self.indent_level + diff)


class Expression(ABC):
    """Base class for Erlang expressions."""

    def build(self, ctx: "TranslationContext") -> List[Line]:
        """Build code lines with optional assignment."""
        # Save assign_to and clear it before _build
        nested_ctx = replace(ctx, assign_to=None)

        lines = self._build(nested_ctx)
        if not lines:
            return lines

        # Add assignment only to the first line
        if ctx.assign_to:
            lines[0] = replace(
                lines[0], content=f"{ctx.assign_to} = {lines[0].content}"
            )

        return lines

    @abstractmethod
    def _build(self, ctx: "TranslationContext") -> List[Line]:
        """Build code lines without assignment handling."""


@dataclass
class PreparedExpression:
    """Result of expression preparation phase."""

    expression: "Expression"
    target_var: str


class JsonEncodingStrategy(ABC):
    """Strategy for JSON encoding."""

    @abstractmethod
    def prepare_json_encoding(self, ctx: "JsonEncodingCtx") -> PreparedExpression:
        """Prepare expression for JSON encoding."""


class JsonDecodingStrategy(ABC):
    """Strategy for JSON decoding."""

    @abstractmethod
    def prepare_json_decoding(self, ctx: "JsonDecodingCtx") -> PreparedExpression:
        """Prepare expression for JSON decoding."""


class PrintEncodingStrategy(ABC):
    """Strategy for print encoding."""

    @abstractmethod
    def prepare_print_encoding(self, ctx: "PrintEncodingCtx") -> PreparedExpression:
        """Prepare expression for print encoding."""
