from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import is_private_member_name, is_public_member_name
from ..core.suggestions import (
    format_with_suggestion,
    suggest_private_member_name,
    suggest_public_member_name,
)
from ..core.types import Violation
from .ast_utils import node_location, violation_at_node
from .base import Rule, Source


def _collect_name_targets(node: ast.AST) -> list[ast.Name]:
    """
    Collect simple assigned name targets (supports unpacking).

    Ignores attributes/subscripts, because those are not class member identifiers:
      - obj.attr = ...
      - arr[i] = ...
    """
    if isinstance(node, ast.Name):
        return [node]

    if isinstance(node, (ast.Tuple, ast.List)):
        out: list[ast.Name] = []
        for elt in node.elts:
            out.extend(_collect_name_targets(elt))
        return out

    if isinstance(node, ast.Starred):
        return _collect_name_targets(node.value)

    return []


def _is_direct_class_body_stmt(node: ast.AST, current_class: ast.ClassDef | None) -> bool:
    if current_class is None:
        return False
    return any(stmt is node for stmt in current_class.body)


class MemberNames(Rule):
    """Validate class members names: n_<...> / _n<...> (NNO108, NNO109)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        current_class = source.current_class

        if current_class is None:
            return []

        if not _is_direct_class_body_stmt(node, current_class):
            return []

        # Methods
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return self._check_member_name(node, node.name, filename=source.filename)

        # Class attributes (incl annotated / augmented)
        if isinstance(node, ast.Assign):
            return self._check_member_targets(node.targets, filename=source.filename)

        if isinstance(node, ast.AnnAssign):
            return self._check_member_targets([node.target], filename=source.filename)

        if isinstance(node, ast.AugAssign):
            return self._check_member_targets([node.target], filename=source.filename)

        return []

    def _check_member_targets(self, targets: list[ast.AST], *, filename: str) -> list[Violation]:
        violations: list[Violation] = []
        for t in targets:
            for name_node in _collect_name_targets(t):
                violations.extend(self._check_member_name(name_node, name_node.id, filename=filename))
        return violations

    def _check_member_name(self, node: ast.AST, name: str, *, filename: str) -> list[Violation]:
        line, col = node_location(node)

        if name.startswith("_"):
            if is_private_member_name(name):
                return []
            return [
                violation_at_node(
                    node,
                    "NNO109",
                    format_with_suggestion(
                        ErrorCodes.NNO109.format(name=name),
                        suggest=suggest_private_member_name(filename=filename, line=line, col=col),
                    ),
                )
            ]

        if is_public_member_name(name):
            return []

        return [
            violation_at_node(
                node,
                "NNO108",
                format_with_suggestion(
                    ErrorCodes.NNO108.format(name=name),
                    suggest=suggest_public_member_name(filename=filename, line=line, col=col),
                ),
            )
        ]
