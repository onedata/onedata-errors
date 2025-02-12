"""ATM workflow schemas argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.strategies import CSVPrintEncodingStrategy, PrintEncodingStrategy


class AtmWorkflowSchemaIds(ErrorArgType):
    """List of ATM workflow schema IDs."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    print_encoding_strategy: ClassVar[PrintEncodingStrategy] = CSVPrintEncodingStrategy
