from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class EncodingType(Enum):
    DIRECT = "direct"
    CUSTOM = "custom"
    FROM_JSON = "from_json"


@dataclass
class EncodingResult:
    """Wynik generowania kodu dla json/print"""

    tokens: List[str]
    json_var: str
    print_var: Optional[str] = None


@dataclass
class CodeBlock:
    """Reprezentuje blok kodu Erlanga"""

    indent_level: int = 0
    tokens: List[str] = field(default_factory=list)

    def indent(self, level: int = 0) -> str:
        return "    " * (self.indent_level + level)

    def add_line(self, line: str) -> "CodeBlock":
        self.tokens.append(f"{self.indent()}{line}\n")
        return self

    def add_case(self, var: str) -> "CaseBuilder":
        return CaseBuilder(self, var)

    def build(self) -> List[str]:
        return self.tokens


class CaseBuilder:
    """Builder dla konstrukcji case Erlanga"""

    def __init__(self, code_block: CodeBlock, var: str):
        self.code_block = code_block
        self.var = var
        self.clauses: List[tuple[str, List[str]]] = []

    def add_clause(self, pattern: str, body: List[str]) -> "CaseBuilder":
        self.clauses.append((pattern, body))
        return self

    def build(self) -> CodeBlock:
        self.code_block.add_line(f"case {self.var} of")

        for pattern, body in self.clauses:
            self.code_block.add_line(f"{self.indent(1)}{pattern} ->")
            for line in body:
                self.code_block.add_line(f"{self.indent(2)}{line}")

        self.code_block.add_line(f"{self.indent()}end")
        return self.code_block

    def indent(self, level: int = 0) -> str:
        return self.code_block.indent(level)


@dataclass
class ErlangExpressionBuilder:
    """Builder dla wyrażeń Erlanga"""

    var_name: str
    nullable: bool = False
    json_encoding_type: EncodingType = EncodingType.DIRECT
    print_encoding_type: EncodingType = EncodingType.DIRECT
    custom_json_encoder: Optional[str] = None
    custom_print_encoder: Optional[str] = None

    def build_encoding(
        self, code_block: CodeBlock, is_printed: bool = False
    ) -> EncodingResult:
        """Generuje kod dla json i opcjonalnie print w jednym kroku"""
        if not self.nullable:
            return self._build_non_nullable_encoding(code_block, is_printed)
        return self._build_nullable_encoding(code_block, is_printed)

    def _build_non_nullable_encoding(
        self, code_block: CodeBlock, is_printed: bool
    ) -> EncodingResult:
        json_var = f"{self.var_name}Json"
        print_var = None

        # Generate JSON encoding
        if self.json_encoding_type == EncodingType.CUSTOM:
            code_block.add_line(
                f"{json_var} = {self.custom_json_encoder}({self.var_name})"
            )
        else:  # DIRECT
            json_var = self.var_name

        # Generate print encoding if needed
        if is_printed:
            print_var = self._build_print_var(code_block, json_var)

        return EncodingResult(
            tokens=code_block.tokens, json_var=json_var, print_var=print_var
        )

    def _build_nullable_encoding(
        self, code_block: CodeBlock, is_printed: bool
    ) -> EncodingResult:
        json_var = f"{self.var_name}Json"
        print_var = f"{self.var_name}Print" if is_printed else None

        case = code_block.add_case(self.var_name)

        # Handle undefined case
        if is_printed:
            case.add_clause("undefined", ["{null, null}"])
        else:
            case.add_clause("undefined", ["null"])

        # Handle value case
        value_lines = []

        # JSON encoding
        if self.json_encoding_type == EncodingType.CUSTOM:
            json_tmp = f"{json_var}Tmp"
            value_lines.append(f"{json_tmp} = {self.custom_json_encoder}(Value),")
        else:  # DIRECT
            json_tmp = "Value"

        # Print encoding if needed
        if is_printed:
            print_tmp = self._get_print_value("Value", json_tmp)
            value_lines.append(f"{{{json_tmp}, {print_tmp}}}")
        else:
            value_lines.append(json_tmp)

        case.add_clause("Value", value_lines)
        case.build()

        return EncodingResult(
            tokens=code_block.tokens, json_var=json_var, print_var=print_var
        )

    def _build_print_var(self, code_block: CodeBlock, json_var: str) -> str:
        if self.print_encoding_type == EncodingType.DIRECT:
            return self.var_name
        elif self.print_encoding_type == EncodingType.FROM_JSON:
            return json_var
        else:  # CUSTOM
            print_var = f"{self.var_name}Print"
            code_block.add_line(
                f"{print_var} = {self.custom_print_encoder}({self.var_name})"
            )
            return print_var

    def _get_print_value(self, value_var: str, json_var: str) -> str:
        if self.print_encoding_type == EncodingType.DIRECT:
            return value_var
        elif self.print_encoding_type == EncodingType.FROM_JSON:
            return json_var
        else:  # CUSTOM
            return f"{self.custom_print_encoder}({value_var})"

    def set_custom_json_encoding(self, encoder: str) -> "ErlangExpressionBuilder":
        self.json_encoding_type = EncodingType.CUSTOM
        self.custom_json_encoder = encoder
        return self

    def set_custom_print_encoding(self, encoder: str) -> "ErlangExpressionBuilder":
        self.print_encoding_type = EncodingType.CUSTOM
        self.custom_print_encoder = encoder
        return self
