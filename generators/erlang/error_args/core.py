"""Core abstractions for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from abc import ABC, abstractmethod
from typing import Dict, Optional


class TranslationContext(ABC):
    """Base class for all translation contexts."""

    @property
    @abstractmethod
    def indent_level(self) -> int:
        """Required by all contexts for code generation."""

    @property
    @abstractmethod
    def assign_to(self) -> Optional[str]:
        """Variable name for assignment, if needed."""

    @abstractmethod
    def _format_fields(self) -> Dict[str, str]:
        """Returns dictionary of fields available for template formatting.

        This is an implementation detail - contexts should override this method
        to provide their specific fields.
        """

    def format_template(self, template: str) -> str:
        """Format template using available fields.

        Args:
            template: Template string with named placeholders

        Returns:
            Formatted string

        Raises:
            ValueError: If template uses undefined fields
        """
        try:
            return template.format(**self._format_fields())
        except KeyError as e:
            raise ValueError(
                f"Template '{template}' uses undefined field {e}. "
                f"Available fields: {list(self._format_fields().keys())}"
            ) from e
