"""Registry for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import Dict, Type

from .base import ErrorArgType


class TypeRegistry:
    """Registry for error argument types."""

    _types: Dict[str, Type[ErrorArgType]] = {}

    @classmethod
    def register(cls, error_type: Type[ErrorArgType]) -> None:
        """Register a new error argument type."""
        type_name = error_type.type_name()
        if type_name in cls._types:
            raise ValueError(f"Type {type_name} is already registered")

        cls._types[type_name] = error_type

    @classmethod
    def get(cls, type_name: str) -> Type[ErrorArgType]:
        """Get error argument type by name."""
        if type_name not in cls._types:
            raise ValueError(f"Unknown error argument type: {type_name}")

        return cls._types[type_name]

    @classmethod
    def create(cls, type_name: str, **kwargs) -> ErrorArgType:
        """Create new instance of error argument type."""
        type_class = cls.get(type_name)
        return type_class(**kwargs)
