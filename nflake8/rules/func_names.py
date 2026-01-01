from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import is_func_name
from ..core.suggestions import format_with_suggestion, suggest_func_name
from ..core.types import Violation
from .ast_utils import node_location, violation_at_node
from .base import Rule, Source


class FuncNames(Rule):
    """Validate non-method function names (NNO104)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node

        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []

        if source.current_class is not None:
            return []

        if is_func_name(node.name):
            return []

        line, col = node_location(node)

        return [
            violation_at_node(
                node,
                "NNO104",
                format_with_suggestion(
                    ErrorCodes.NNO104.format(name=node.name),
                    suggest=suggest_func_name(filename=source.filename, line=line, col=col),
                ),
            )
        ]
