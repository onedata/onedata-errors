"""Expression models for error argument types."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

from dataclasses import dataclass
from typing import List, Tuple

from .abc import Expression, TranslationContext
from .core import Line, LineEnding


@dataclass
class CodeLine:
    """Represents a line of code that can use context variables and additional indentation."""

    template: str
    indent_level: int = 0
    ending: LineEnding = ""


# pylint: disable=too-few-public-methods
class CodeLines(Expression):
    """Expression composed of multiple lines with support for variable interpolation."""

    def __init__(self, lines: List[CodeLine]):
        self.lines = lines

    def _build(self, ctx: TranslationContext) -> List[Line]:
        result = []
        for code_line in self.lines:
            result.append(
                Line(
                    content=ctx.format_template(code_line.template),
                    indent_level=ctx.indent_level + code_line.indent_level,
                    ending=code_line.ending,
                )
            )
        return result


# pylint: disable=too-few-public-methods
class NoopExpression(Expression):
    """Expression that generates no code."""

    def _build(self, _ctx: TranslationContext) -> List[Line]:
        return []


class FunCallExpression(Expression):
    """Expression representing a function call with module, function and arguments."""

    def __init__(self, module: str, function: str, args: List[str]):
        self.module = module
        self.function = function
        self.args = args

    def is_simple_var_call(self) -> bool:
        """Check if expression is just a function call with single variable."""
        return len(self.args) == 1

    def _build(self, ctx: TranslationContext) -> List[Line]:
        formatted_args = [ctx.format_template(arg) for arg in self.args]
        expr = f"{self.module}:{self.function}({', '.join(formatted_args)})"
        return [Line(expr, ending=",", indent_level=ctx.indent_level)]


# pylint: disable=too-few-public-methods
class SimpleExpression(Expression):
    """Single line expression."""

    def __init__(self, template: str):
        self.template = template

    def _build(self, ctx: TranslationContext) -> List[Line]:
        expr = ctx.format_template(self.template)
        return [Line(expr, ending=",", indent_level=ctx.indent_level)]


# pylint: disable=too-few-public-methods
class ListMapExpression(Expression):
    """List map expression."""

    def __init__(self, fun_clauses: List[Tuple[str, Expression]], input_template: str):
        self.fun_clauses = fun_clauses
        self.input_template = input_template

    def _build(self, ctx: TranslationContext) -> List[Line]:
        lines = [Line("lists:map(fun", indent_level=ctx.indent_level)]

        for i, (pattern, expr) in enumerate(self.fun_clauses):
            lines.append(Line(f"({pattern}) ->", indent_level=ctx.indent_level + 1))

            clause_lines = expr.build(ctx.with_indent(2))

            if clause_lines:
                # Adding a semicolon for all clauses except the last one
                ending: LineEnding = ";" if i < len(self.fun_clauses) - 1 else ""
                clause_lines[-1].ending = ending

            lines.extend(clause_lines)

        input_list = ctx.format_template(self.input_template)

        lines.append(
            Line(f"end, {input_list})", ending=",", indent_level=ctx.indent_level)
        )

        return lines


# pylint: disable=too-few-public-methods
class ListMapFunRefExpression(Expression):
    """List map with function reference expression."""

    def __init__(self, module: str, function: str, input_template: str):
        self.module = module
        self.function = function
        self.input_template = input_template

    def _build(self, ctx: TranslationContext) -> List[Line]:
        input_list = ctx.format_template(self.input_template)

        return [
            Line(
                f"lists:map(fun {self.module}:{self.function}/1, {input_list})",
                ending=",",
                indent_level=ctx.indent_level,
            )
        ]


# pylint: disable=too-few-public-methods
class CaseExpression(Expression):
    """Case expression."""

    def __init__(self, match_template: str, clauses: List[Tuple[str, Expression]]):
        self.match_template = match_template
        self.clauses = clauses

    def _build(self, ctx: TranslationContext) -> List[Line]:
        match_var = ctx.format_template(self.match_template)

        lines = [Line(f"case {match_var} of", indent_level=ctx.indent_level)]

        for i, (pattern, expr) in enumerate(self.clauses):
            lines.append(Line(f"{pattern} ->", indent_level=ctx.indent_level + 1))

            clause_lines = expr.build(ctx.with_indent(2))

            if clause_lines:
                # Adding a semicolon for all clauses except the last one
                ending: LineEnding = ";" if i < len(self.clauses) - 1 else ""
                clause_lines[-1].ending = ending

            lines.extend(clause_lines)

        lines.append(Line("end", ending=",", indent_level=ctx.indent_level))

        return lines
