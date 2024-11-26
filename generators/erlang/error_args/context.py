"""Context classes for error argument type translation code generation."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import NamedTuple, Optional


class JsonEncodingCtx(NamedTuple):
    erl_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1


class PrintEncodingCtx(NamedTuple):
    erl_var: str
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1


class JsonDecodingCtx(NamedTuple):
    json_var: str
    assign_to: Optional[str] = None
    indent_level: int = 1
