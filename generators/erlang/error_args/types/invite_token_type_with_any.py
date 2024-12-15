"""Invite token type with any argument type."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from typing import ClassVar

from ..base import ErrorArgType
from ..translation.expressions import CaseExpression, SimpleExpression
from ..translation.strategies import (
    CustomStrategy,
    JsonDecodingStrategy,
    JsonEncodingStrategy,
)


class InviteTokenTypeWithAny(ErrorArgType):
    """Invite token type with any."""

    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        CaseExpression(
            match_template="{erl_var}",
            clauses=[
                ("any", SimpleExpression('<<"any">>')),
                ("_", SimpleExpression("token_type:invite_type_to_str({erl_var})")),
            ],
        )
    )
    json_decoding_strategy: ClassVar[JsonDecodingStrategy] = CustomStrategy(
        CaseExpression(
            match_template="{json_var}",
            clauses=[
                ('<<"any">>', SimpleExpression("any")),
                ("_", SimpleExpression("token_type:invite_type_from_str({json_var})")),
            ],
        )
    )
