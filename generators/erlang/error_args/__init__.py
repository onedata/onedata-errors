"""Error arguments package for Erlang error generator."""

from .base import ErrorArgToJsonEncoding, ErrorArgType
from .loader import create_error_arg, load_types
from .registry import TypeRegistry

__all__ = [
    "create_error_arg",
    "load_types",
    "ErrorArgType",
    "ErrorArgToJsonEncoding",
    "TypeRegistry",
]
