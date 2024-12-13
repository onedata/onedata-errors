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


class TypeLoader:
    """Class for loading and registering error argument types."""

    _types_loaded: bool = False

    @classmethod
    def load_types(cls) -> None:
        """Automatically load and register all error argument types."""
        if cls._types_loaded:
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

        cls._types_loaded = True

    @classmethod
    def are_types_loaded(cls) -> bool:
        """Check if types have been loaded."""
        return cls._types_loaded


def create_error_arg(arg_yaml: dict) -> ErrorArgType:
    """Create error argument from YAML definition."""
    TypeLoader.load_types()

    return TypeRegistry.create(
        type_name=arg_yaml["type"],
        name=arg_yaml["name"],
        nullable=arg_yaml.get("nullable", False),
        print_if_null=arg_yaml.get("print_if_null"),
    )
