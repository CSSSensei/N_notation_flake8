from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import expected_receiver_name
from ..core.types import Violation
from .ast_utils import first_positional_arg, has_decorator, violation_at_node
from .base import Rule, Source


class ReceiverName(Rule):
    """Validate method receiver name (NNO210)"""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        current_class = source.current_class

        if current_class is None:
            return []

        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []

        if has_decorator(node, "staticmethod"):
            return []

        expected = expected_receiver_name(current_class.name)
        first = first_positional_arg(node.args)
        got = first.arg if first is not None else "<none>"

        if first is not None and got == expected:
            return []

        return [
            violation_at_node(
                node,
                "NNO210",
                ErrorCodes.NNO210.format(expected=expected, name=got),
            )
        ]
