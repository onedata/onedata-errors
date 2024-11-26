"""Encoding/decoding strategies for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass
from typing import Union

from .expressions import Expression


@dataclass
class DirectStrategy:
    """Direct encoding/decoding - use variable as-is."""


@dataclass
class FromJsonStrategy:
    """Use JSON representation for printing."""


@dataclass
class CustomStrategy:
    """Custom encoding/decoding with expression."""

    expression: Expression


JsonEncodingStrategy = Union[DirectStrategy, CustomStrategy]
JsonDecodingStrategy = Union[DirectStrategy, CustomStrategy]
PrintEncodingStrategy = Union[DirectStrategy, FromJsonStrategy, CustomStrategy]
