"""Module for automatic loading of error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import importlib
import pkgutil
from pathlib import Path

from . import types
from .base import ErrorArgType
from .registry import TypeRegistry

_types_loaded: bool = False


def load_types() -> None:
    """Automatically load and register all error argument types."""
    global _types_loaded
    if _types_loaded:
        return

    types_dir = Path(types.__file__).parent

    for module_info in pkgutil.iter_modules([str(types_dir)]):
        module = importlib.import_module(
            f"generators.erlang.error_args.types.{module_info.name}"
        )

        # Find all classes in module that inherit from ErrorArgType
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, ErrorArgType)
                and attr is not ErrorArgType
            ):
                TypeRegistry.register(attr)

    _types_loaded = True


def create_error_arg(arg_yaml: dict) -> ErrorArgType:
    """Create error argument from YAML definition."""
    load_types()

    return TypeRegistry.create(
        type_name=arg_yaml.get("type", "Binary"),
        name=arg_yaml["name"],
        nullable=arg_yaml.get("nullable", False),
    )
