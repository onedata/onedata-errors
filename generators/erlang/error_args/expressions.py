"""Expression models for error argument types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Literal, Tuple, Union

from .translation_context import JsonDecodingCtx, JsonEncodingCtx, PrintEncodingCtx

TranslationContext = Union[JsonEncodingCtx, PrintEncodingCtx, JsonDecodingCtx]


@dataclass
class Line:
    """Represents a single line of code with optional indentation level and line ending."""

    content: str
    indent_level: int = 0
    ending: Literal["", ",", ";"] = ""


class Expression(ABC):
    """Base class for Erlang expressions."""

    @abstractmethod
    def build(self, ctx: TranslationContext) -> List[Line]:
        """Build code lines using provided context."""


class SimpleExpression(Expression):
    """Single line expression."""

    def __init__(self, template: str):
        self.template = template

    def build(self, ctx: TranslationContext) -> List[Line]:
        if isinstance(ctx, JsonEncodingCtx):
            expr = self.template.format(var=ctx.erl_var)
        elif isinstance(ctx, JsonDecodingCtx):
            expr = self.template.format(var=ctx.json_var)
        elif isinstance(ctx, PrintEncodingCtx):
            expr = self.template.format(erl_var=ctx.erl_var, json_var=ctx.json_var)
        else:
            raise ValueError(f"Unsupported context type: {type(ctx)}")

        return [Line(expr, ending=",", indent_level=ctx.indent_level)]


class ListMapExpression(Expression):
    """List map expression."""

    def __init__(self, fun_clauses: List[Tuple[str, Expression]], input_template: str):
        self.fun_clauses = fun_clauses
        self.input_template = input_template

    def build(self, ctx: TranslationContext) -> List[Line]:
        lines = [Line("lists:map(fun", indent_level=ctx.indent_level)]

        for i, (pattern, expr) in enumerate(self.fun_clauses):
            # Adding a semicolon for all clauses except the last one
            ending = ";" if i < len(self.fun_clauses) - 1 else ""
            lines.append(Line(f"({pattern}) ->", indent_level=ctx.indent_level + 1))

            clause_ctx = ctx._replace(assign_to=None, indent_level=ctx.indent_level + 2)
            clause_lines = expr.build(clause_ctx)

            if clause_lines:
                clause_lines[-1].ending = ending

            lines.extend(clause_lines)

        input_list = self.input_template.format(
            var=ctx.erl_var if isinstance(ctx, JsonEncodingCtx) else ctx.json_var
        )
        lines.append(
            Line(f"end, {input_list}", ending=",", indent_level=ctx.indent_level)
        )

        return lines


class ListMapFunRefExpression(Expression):
    """List map with function reference expression."""

    def __init__(self, module: str, function: str, input_template: str):
        self.module = module
        self.function = function
        self.input_template = input_template

    def build(self, ctx: TranslationContext) -> List[Line]:
        input_list = self.input_template.format(
            var=ctx.erl_var if isinstance(ctx, JsonEncodingCtx) else ctx.json_var
        )
        return [
            Line(
                f"lists:map(fun {self.module}:{self.function}/1, {input_list}",
                ending=",",
                indent_level=ctx.indent_level,
            )
        ]


class CaseExpression(Expression):
    """Case expression."""

    def __init__(self, match_template: str, clauses: List[Tuple[str, Expression]]):
        self.match_template = match_template
        self.clauses = clauses

    def build(self, ctx: TranslationContext) -> List[Line]:
        match_var = self.match_template.format(
            var=ctx.erl_var if isinstance(ctx, JsonEncodingCtx) else ctx.json_var
        )
        lines = [Line(f"case {match_var} of", indent_level=ctx.indent_level)]

        for i, (pattern, expr) in enumerate(self.clauses):
            # Adding a semicolon for all clauses except the last one
            ending = ";" if i < len(self.clauses) - 1 else ""
            lines.append(Line(f"{pattern} ->", indent_level=ctx.indent_level + 1))

            clause_ctx = ctx._replace(assign_to=None, indent_level=ctx.indent_level + 2)
            clause_lines = expr.build(clause_ctx)

            if clause_lines:
                clause_lines[-1].ending = ending

            lines.extend(clause_lines)

        lines.append(Line("end", ending=",", indent_level=ctx.indent_level))

        return lines


def format_lines(lines: List[Line], ctx: TranslationContext) -> List[str]:
    """Format lines with proper indentation and assignment."""
    if not lines:
        return []

    assignment = f"{ctx.assign_to} = " if ctx.assign_to else ""

    formatted_lines = []
    first_line = lines[0]
    formatted_lines.append(
        f"{'    ' * first_line.indent_level}{assignment}{first_line.content}{first_line.ending}\n"
    )

    for line in lines[1:]:
        formatted_lines.append(
            f"{'    ' * line.indent_level}{line.content}{line.ending}\n"
        )

    return formatted_lines
