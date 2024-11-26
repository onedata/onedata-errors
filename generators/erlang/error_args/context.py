"""Context classes for error argument type code generation."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass
from typing import Optional


@dataclass
class JsonEncodingCtx:
    erl_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1


@dataclass
class PrintEncodingCtx:
    erl_var: str
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1


@dataclass
class JsonDecodingCtx:
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1 