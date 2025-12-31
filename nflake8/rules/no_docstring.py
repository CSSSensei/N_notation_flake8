from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.types import Violation
from .ast_utils import violation_at_node
from .base import Rule, Source


class NoDocstring(Rule):
    """Forbid module/class/function docstrings (NNO602)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            return []

        if ast.get_docstring(node) is None:
            return []

        return [
            violation_at_node(
                node,
                "NNO602",
                ErrorCodes.NNO602,
                prefer_docstring_expr=True,
            )
        ]
