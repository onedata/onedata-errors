"""Translation context classes for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass
from typing import Dict, Optional

from .abc import (
    JsonDecodingStrategy,
    JsonEncodingStrategy,
    PreparedExpression,
    PrintEncodingStrategy,
    TranslationContext,
)


@dataclass
class JsonEncodingCtx(TranslationContext):
    """Context for JSON encoding."""

    erl_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def get_template_vars(self) -> Dict[str, str]:
        return {"erl_var": self.erl_var}

    def prepare_expression(self, strategy: JsonEncodingStrategy) -> PreparedExpression:
        return strategy.prepare_json_encoding(self)


@dataclass
class JsonDecodingCtx(TranslationContext):
    """Context for JSON decoding."""

    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def get_template_vars(self) -> Dict[str, str]:
        return {"json_var": self.json_var}

    def prepare_expression(self, strategy: JsonDecodingStrategy) -> PreparedExpression:
        return strategy.prepare_json_decoding(self)


@dataclass
class PrintEncodingCtx(TranslationContext):
    """Context for print encoding."""

    erl_var: str
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def get_template_vars(self) -> Dict[str, str]:
        return {"erl_var": self.erl_var, "json_var": self.json_var}

    def prepare_expression(self, strategy: PrintEncodingStrategy) -> PreparedExpression:
        return strategy.prepare_print_encoding(self)
