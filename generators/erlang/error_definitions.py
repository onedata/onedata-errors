"""
Structures representing Erlang error definitions that are used in code generation.
These structures are populated from YAML definitions and used by generators
to produce Erlang code.
"""

from typing import List, NamedTuple, Optional, Union

from .error_args.base import ErrorArgType


class MacroRef(NamedTuple):
    """
    Represents a macro reference in Erlang code.

    Attributes:
        alias: Name used in error description to reference this macro
        ref: Actual macro reference in Erlang code, e.g. "?NAMES"
        fmt_control_sequence: Format control sequence used for this macro (default: "~ts")
    """

    alias: str
    ref: str
    fmt_control_sequence: str = "~ts"


class OdErrorCtx(NamedTuple):
    """
    Context for error generation containing includes and macro definitions.

    Attributes:
        includes: List of header files to include
        macros: List of macro references used in error formatting
    """

    includes: List[str]
    macros: List[MacroRef]


class OdError(NamedTuple):
    """
    Represents a single error definition.

    Attributes:
        name: Error name (used in macro generation)
        type: Erlang type name for this error
        id: Unique error identifier
        description: Human readable error description
        http_code: HTTP status code to return for this error
        args: List of error arguments
        ctx: Generation context with includes and macros
        to_json: Custom to_json implementation (if provided)
        from_json: Custom from_json implementation (if provided)
    """

    name: str
    type: str
    id: str
    description: str
    http_code: Union[str, int]
    args: List[ErrorArgType]
    ctx: OdErrorCtx
    to_json: Optional[str]
    from_json: Optional[str]

    def get_id_macro(self) -> str:
        """Returns the macro name for error ID."""
        return f"ERROR_{self.name.upper()}_ID"

    def get_type_macro(self) -> str:
        """Returns the macro name for error type."""
        return f"ERROR_{self.name.upper()}_TYPE"

    def get_args_as_erlang_variable_names(self) -> List[str]:
        """Returns list of Erlang variable names for error arguments."""
        return [arg.get_erlang_variable_name() for arg in self.args]

    def get_error_macro(self) -> str:
        """Returns the main error macro definition."""
        if not self.args:
            return f"ERROR_{self.name.upper()}"

        args = ", ".join(self.get_args_as_erlang_variable_names())
        return f"ERROR_{self.name.upper()}({args})"


class OdErrorGroup(NamedTuple):
    """
    Groups related errors together, typically by their directory location.

    Attributes:
        name: Group name (derived from directory path)
        errors: List of errors in this group
    """

    name: str
    errors: List[OdError]
