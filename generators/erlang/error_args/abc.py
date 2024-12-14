"""Abstract base classes and interfaces for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

from .core import Line

if TYPE_CHECKING:
    from .translation_context import JsonDecodingCtx, JsonEncodingCtx, PrintEncodingCtx


class TranslationContext(ABC):
    """Base class for all translation contexts."""

    @property
    @abstractmethod
    def indent_level(self) -> int:
        """Required by all contexts for code generation."""

    @property
    @abstractmethod
    def assign_to(self) -> Optional[str]:
        """Variable name for assignment, if needed."""

    @abstractmethod
    def _format_fields(self) -> Dict[str, str]:
        """Returns dictionary of fields available for template formatting."""

    def format_template(self, template: str) -> str:
        """Format template using available fields."""
        try:
            return template.format(**self._format_fields())
        except KeyError as e:
            raise ValueError(
                f"Template '{template}' uses undefined field {e}. "
                f"Available fields: {list(self._format_fields().keys())}"
            ) from e


class Expression(ABC):
    """Base class for Erlang expressions."""

    @abstractmethod
    def build(self, ctx: "TranslationContext") -> List[Line]:
        """Build code lines using provided context."""


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
