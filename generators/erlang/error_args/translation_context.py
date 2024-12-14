"""Context classes for error argument type translation code generation."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass
from typing import Dict, Optional

from .core import TranslationContext


@dataclass
class JsonEncodingCtx(TranslationContext):
    erl_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def _format_fields(self) -> Dict[str, str]:
        return {"erl_var": self.erl_var}


@dataclass
class PrintEncodingCtx(TranslationContext):
    erl_var: str
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def _format_fields(self) -> Dict[str, str]:
        return {"erl_var": self.erl_var, "json_var": self.json_var}


@dataclass
class JsonDecodingCtx(TranslationContext):
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1

    def _format_fields(self) -> Dict[str, str]:
        return {"json_var": self.json_var}
