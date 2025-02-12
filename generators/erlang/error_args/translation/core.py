"""Core types and utilities for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass
from typing import Literal

LineEnding = Literal["", ",", ";"]


@dataclass
class Line:
    """Represents a single line of code with optional indentation level and line ending."""

    content: str
    indent_level: int = 0
    ending: LineEnding = ""
