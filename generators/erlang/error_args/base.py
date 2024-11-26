"""Base class and common utilities for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, NamedTuple, Optional

INDENT: str = 4 * " "


class JsonEncodingStrategy(Enum):
    DIRECT = "direct"
    CUSTOM = "custom"


class PrintEncodingStrategy(Enum):
    DIRECT = "direct"
    FROM_JSON = "from_json"
    CUSTOM = "custom"


class JsonDecodingStrategy(Enum):
    DIRECT = "direct"
    CUSTOM = "custom"


class ErrorArgToJsonEncoding(NamedTuple):
    tokens: List[str]
    json_var: str
    print_var: Optional[str]


class ErrorArgType(ABC):
    """Base class for all error argument types."""

    # Default values for class attributes
    fmt_control_sequence: str = "~w"
    json_encoding_strategy: JsonEncodingStrategy = JsonEncodingStrategy.DIRECT
    print_encoding_strategy: PrintEncodingStrategy = PrintEncodingStrategy.DIRECT
    json_decoding_strategy: JsonDecodingStrategy = JsonDecodingStrategy.DIRECT

    def __init__(self, name: str, nullable: bool = False) -> None:
        self.name = name
        self.nullable = nullable

    @classmethod
    @abstractmethod
    def type_name(cls) -> str:
        """Returns the name of this type as used in YAML definitions."""
        pass

    def get_erlang_variable_name(self) -> str:
        """Returns Erlang variable name for this argument."""
        return self.name[0].upper() + self.name[1:]

    def generate_to_json_encoding(
        self, *, is_printed: bool = False, indent_level: int = 1
    ) -> ErrorArgToJsonEncoding:
        if self.nullable:
            return self._generate_nullable_to_json_encoding(
                is_printed=is_printed, indent_level=indent_level
            )

        return self._generate_to_json_encoding(
            is_printed=is_printed, indent_level=indent_level
        )

    def generate_from_json_decoding(
        self, *, details_var: str, indent_level: int = 1
    ) -> List[str]:
        indent_0 = indent_level * INDENT
        indent_1 = (indent_level + 1) * INDENT
        indent_2 = (indent_level + 2) * INDENT

        erl_var = self.get_erlang_variable_name()
        tokens = []

        maps_get_tokens = ['maps:get(<<"', self.name, '">>, ', details_var, ")"]
        if self.nullable:
            maps_get_tokens.insert(-1, ", null")

        if self.json_decoding_strategy == JsonDecodingStrategy.DIRECT:
            tokens.extend([indent_0, erl_var, " = "])

            if self.nullable:
                tokens.extend(["utils:null_to_undefined(", *maps_get_tokens, ")"])
            else:
                tokens.extend(maps_get_tokens)

            tokens.append(",\n")

        elif self.json_decoding_strategy == JsonDecodingStrategy.CUSTOM:
            json_var = f"{erl_var}Json"

            if self.nullable:
                tokens.extend(
                    [indent_0, erl_var, " = case ", *maps_get_tokens, " of\n"]
                )
                tokens.extend([indent_1, "null ->\n", indent_2, "undefined;\n"])
                tokens.extend([indent_1, json_var, " ->\n"])
                tokens.extend(
                    self._generate_json_decoding(
                        json_var=json_var, indent_level=indent_level + 2
                    )
                )
                tokens.extend(["\n", indent_0, "end,\n"])
            else:
                tokens.extend([indent_0, json_var, " = ", *maps_get_tokens, ",\n"])
                tokens.extend(
                    self._generate_json_decoding(
                        json_var=json_var, assign_to=erl_var, indent_level=indent_level
                    )
                )
                tokens.append(",\n")

        return tokens

    def _generate_to_json_encoding(
        self, *, is_printed: bool = False, indent_level: int = 1
    ) -> ErrorArgToJsonEncoding:
        tokens = []

        erl_var = self.get_erlang_variable_name()
        json_var = erl_var
        print_var = None

        if self.json_encoding_strategy == JsonEncodingStrategy.CUSTOM:
            json_var = f"{erl_var}Json"
            tokens.extend(
                self._generate_json_encoding(
                    erl_var=erl_var,
                    assign_to=json_var,
                    indent_level=indent_level,
                )
                + [",\n"]
            )

        if is_printed:
            if self.print_encoding_strategy == PrintEncodingStrategy.DIRECT:
                print_var = erl_var
            elif self.print_encoding_strategy == PrintEncodingStrategy.FROM_JSON:
                print_var = json_var
            elif self.print_encoding_strategy == PrintEncodingStrategy.CUSTOM:
                print_var = f"{erl_var}Print"
                tokens.extend(
                    self._generate_print_encoding(
                        json_var=json_var,
                        erl_var=erl_var,
                        assign_to=print_var,
                        indent_level=indent_level,
                    )
                    + [",\n"]
                )

        return ErrorArgToJsonEncoding(
            tokens=tokens,
            json_var=json_var,
            print_var=print_var,
        )

    def _generate_nullable_to_json_encoding(
        self, *, is_printed: bool = False, indent_level: int = 1
    ) -> ErrorArgToJsonEncoding:
        strategy = (
            self.json_encoding_strategy,
            self.print_encoding_strategy if is_printed else None,
        )
        encoding_function = self._nullable_encoding_dispatch[strategy]
        return encoding_function(self, indent_level=indent_level)

    def _generate_nullable_direct_json_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        erl_var = self.get_erlang_variable_name()
        json_var = f"{erl_var}Json"

        indent = indent_level * INDENT
        tokens = [f"{indent}{json_var} = utils:undefined_to_null({erl_var}),\n"]

        return ErrorArgToJsonEncoding(tokens=tokens, json_var=json_var, print_var=None)

    def _generate_nullable_direct_json_and_print_from_json_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        encoding = self._generate_nullable_direct_json_encoding(
            indent_level=indent_level
        )
        return encoding._replace(print_var=encoding.json_var)

    def _generate_nullable_direct_json_and_custom_print_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        erl_var = self.get_erlang_variable_name()
        json_var = f"{erl_var}Json"

        print_var = f"{erl_var}Print"
        print_case_var = f"{erl_var}PrintTmp"
        print_encoding_tokens = self._generate_print_encoding(
            json_var=erl_var,
            erl_var=erl_var,
            assign_to=print_case_var,
            indent_level=indent_level + 2,
        ) + [",\n"]

        tokens = self._generate_nullable_case_statement(
            indent_level=indent_level,
            json_var=json_var,
            print_var=print_var,
            erl_var=erl_var,
            encoding_tokens=print_encoding_tokens,
            json_case_var=erl_var,
            print_case_var=print_case_var,
        )
        return ErrorArgToJsonEncoding(
            tokens=tokens, json_var=json_var, print_var=print_var
        )

    def _generate_nullable_custom_json_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        erl_var = self.get_erlang_variable_name()
        json_var = f"{erl_var}Json"
        json_encoding_tokens = self._generate_json_encoding(
            erl_var=erl_var,
            indent_level=indent_level + 2,
        ) + ["\n"]
        tokens = self._generate_nullable_case_statement(
            indent_level=indent_level,
            json_var=json_var,
            erl_var=erl_var,
            encoding_tokens=json_encoding_tokens,
        )
        return ErrorArgToJsonEncoding(tokens=tokens, json_var=json_var, print_var=None)

    def _generate_nullable_custom_json_and_print_from_json_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        encoding = self._generate_nullable_custom_json_encoding(
            indent_level=indent_level
        )
        return encoding._replace(print_var=encoding.json_var)

    def _generate_nullable_custom_json_and_direct_print_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        erl_var = self.get_erlang_variable_name()

        json_var = f"{erl_var}Json"
        json_case_var = f"{erl_var}JsonTmp"
        json_encoding_tokens = self._generate_json_encoding(
            erl_var=erl_var,
            assign_to=json_case_var,
            indent_level=indent_level + 2,
        ) + [",\n"]

        print_var = f"{erl_var}Print"

        tokens = self._generate_nullable_case_statement(
            indent_level=indent_level,
            json_var=json_var,
            print_var=print_var,
            erl_var=erl_var,
            encoding_tokens=json_encoding_tokens,
            json_case_var=json_case_var,
            print_case_var=erl_var,
        )
        return ErrorArgToJsonEncoding(
            tokens=tokens, json_var=json_var, print_var=print_var
        )

    def _generate_nullable_custom_json_and_print_encoding(
        self, *, indent_level: int
    ) -> ErrorArgToJsonEncoding:
        erl_var = self.get_erlang_variable_name()

        json_var = f"{erl_var}Json"
        json_case_var = f"{erl_var}JsonTmp"
        json_encoding_tokens = self._generate_json_encoding(
            erl_var=erl_var,
            assign_to=json_case_var,
            indent_level=indent_level + 2,
        ) + [",\n"]

        print_var = f"{erl_var}Print"
        print_case_var = f"{erl_var}PrintTmp"
        print_encoding_tokens = self._generate_print_encoding(
            erl_var=erl_var,
            json_var=json_case_var,
            assign_to=print_case_var,
            indent_level=indent_level + 2,
        ) + [",\n"]

        tokens = self._generate_nullable_case_statement(
            indent_level=indent_level,
            json_var=json_var,
            print_var=print_var,
            erl_var=erl_var,
            encoding_tokens=json_encoding_tokens + print_encoding_tokens,
            json_case_var=json_case_var,
            print_case_var=print_case_var,
        )
        return ErrorArgToJsonEncoding(
            tokens=tokens, json_var=json_var, print_var=print_var
        )

    def _generate_nullable_case_statement(
        self,
        *,
        erl_var: str,
        json_var: str,
        print_var: Optional[str] = None,
        indent_level: int,
        encoding_tokens: List[str],
        json_case_var: Optional[str] = None,
        print_case_var: Optional[str] = None,
    ) -> List[str]:
        indent_0 = indent_level * INDENT
        indent_1 = (indent_level + 1) * INDENT
        indent_2 = (indent_level + 2) * INDENT

        tokens = []

        if print_var:
            tokens.append(f"{indent_0}{{{json_var}, {print_var}}}")
        else:
            tokens.append(f"{indent_0}{json_var}")

        tokens.append(f" = case {erl_var} of\n")

        tokens.append(f"{indent_1}undefined ->\n")
        tokens.append(f"{indent_2}{'{null, null}' if print_var else 'null'};\n")
        tokens.append(f"{indent_1}_ ->\n")
        tokens.extend(encoding_tokens)

        if json_case_var and print_case_var:
            tokens.append(f"{indent_2}{{{json_case_var}, {print_case_var}}}\n")

        tokens.append(f"{indent_0}end,\n")

        return tokens

    _nullable_encoding_dispatch = {
        (JsonEncodingStrategy.DIRECT, None): _generate_nullable_direct_json_encoding,
        (
            JsonEncodingStrategy.DIRECT,
            PrintEncodingStrategy.DIRECT,
        ): _generate_nullable_direct_json_and_print_from_json_encoding,
        (
            JsonEncodingStrategy.DIRECT,
            PrintEncodingStrategy.FROM_JSON,
        ): _generate_nullable_direct_json_and_print_from_json_encoding,
        (
            JsonEncodingStrategy.DIRECT,
            PrintEncodingStrategy.CUSTOM,
        ): _generate_nullable_direct_json_and_custom_print_encoding,
        (JsonEncodingStrategy.CUSTOM, None): _generate_nullable_custom_json_encoding,
        (
            JsonEncodingStrategy.CUSTOM,
            PrintEncodingStrategy.FROM_JSON,
        ): _generate_nullable_custom_json_and_print_from_json_encoding,
        (
            JsonEncodingStrategy.CUSTOM,
            PrintEncodingStrategy.DIRECT,
        ): _generate_nullable_custom_json_and_direct_print_encoding,
        (
            JsonEncodingStrategy.CUSTOM,
            PrintEncodingStrategy.CUSTOM,
        ): _generate_nullable_custom_json_and_print_encoding,
    }

    def _generate_json_encoding(
        self, *, erl_var: str, assign_to: Optional[str] = None, indent_level: int = 1
    ) -> List[str]:
        return self._postprocess_generated_expression(
            self._generate_json_encoding_expr_lines(erl_var=erl_var),
            assign_to=assign_to,
            indent_level=indent_level,
        )

    def _generate_json_encoding_expr_lines(self, *, erl_var: str) -> List[str]:
        return []

    def _generate_print_encoding(
        self,
        *,
        json_var: str,
        erl_var: str,
        assign_to: Optional[str] = None,
        indent_level: int = 1,
    ) -> List[str]:
        return self._postprocess_generated_expression(
            self._generate_print_encoding_expr_lines(
                erl_var=erl_var, json_var=json_var
            ),
            assign_to=assign_to,
            indent_level=indent_level,
        )

    def _generate_print_encoding_expr_lines(
        self, *, json_var: str, erl_var: str
    ) -> List[str]:
        return []

    def _generate_json_decoding(
        self, *, json_var: str, assign_to: Optional[str] = None, indent_level: int = 1
    ) -> List[str]:
        return self._postprocess_generated_expression(
            self._generate_json_decoding_expr_lines(json_var=json_var),
            assign_to=assign_to,
            indent_level=indent_level,
        )

    def _generate_json_decoding_expr_lines(self, *, json_var: str) -> List[str]:
        return []

    @staticmethod
    def _postprocess_generated_expression(
        expr_lines: List[str], assign_to: Optional[str] = None, indent_level: int = 1
    ) -> List[str]:
        new_expr_lines = []

        if expr_lines:
            indent = indent_level * INDENT
            assignment = f"{assign_to} = " if assign_to else ""

            new_expr_lines.append(f"{indent}{assignment}{expr_lines[0]}")
            new_expr_lines.extend(f"{indent}{line}" for line in expr_lines[1:])

        return new_expr_lines
