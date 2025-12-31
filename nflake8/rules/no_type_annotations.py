from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.types import Violation
from .ast_utils import has_any_type_annotations, violation_at_node
from .base import Rule, Source


class NoTypeAnnotations(Rule):
    """Forbid ALL type annotations (vars + args + return) (NNO701)"""

    def check(self, source: Source) -> list[Violation]:
        node = source.node

        if isinstance(node, ast.AnnAssign):
            return [violation_at_node(node, "NNO701", ErrorCodes.NNO701)]

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if has_any_type_annotations(node):
                return [violation_at_node(node, "NNO701", ErrorCodes.NNO701)]

        return []
