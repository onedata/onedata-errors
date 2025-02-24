"""Translation context classes for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Dict, Optional


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

    def with_assign_to(self, assign_to: Optional[str]) -> "TranslationContext":
        """Return new context with a different target variable name."""
        return replace(self, assign_to=assign_to)


@dataclass
class JsonEncodingCtx(TranslationContext):
    """Context for JSON encoding."""

    erl_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def get_template_vars(self) -> Dict[str, str]:
        return {"erl_var": self.erl_var}


@dataclass
class JsonDecodingCtx(TranslationContext):
    """Context for JSON decoding."""

    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def get_template_vars(self) -> Dict[str, str]:
        return {"json_var": self.json_var}


@dataclass
class PrintEncodingCtx(TranslationContext):
    """Context for print encoding."""

    erl_var: str
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def get_template_vars(self) -> Dict[str, str]:
        return {"erl_var": self.erl_var, "json_var": self.json_var}
