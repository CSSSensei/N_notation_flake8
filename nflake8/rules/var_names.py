from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import is_const_name, is_iterator_name, is_var_name
from ..core.types import Violation
from .ast_utils import violation_at_node
from .base import Rule, Source


def _collect_name_targets(node: ast.AST) -> list[ast.Name]:
    """
    Collect simple assigned name targets.

    Ignores attributes/subscripts, because those are not variable identifiers:
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


class VarNames(Rule):
    """Validate variable and iterator names (NNO101, NNO110)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        current_class = source.current_class

        if _is_direct_class_body_stmt(node, current_class):
            return []

        if isinstance(node, ast.Assign):
            return self._check_var_targets(node.targets)

        if isinstance(node, ast.AnnAssign):
            return self._check_var_targets([node.target])

        if isinstance(node, ast.AugAssign):
            return self._check_var_targets([node.target])

        if isinstance(node, ast.NamedExpr):
            return self._check_var_targets([node.target])

        # "with ... as <name>"
        if isinstance(node, ast.withitem):
            if node.optional_vars is None:
                return []
            return self._check_var_targets([node.optional_vars])

        # "except ... as <name>"
        if isinstance(node, ast.ExceptHandler):
            if not node.name:
                return []
            if is_var_name(node.name):
                return []
            if is_const_name(node.name):
                return []
            return [
                violation_at_node(
                    node,
                    "NNO101",
                    ErrorCodes.NNO101.format(name=node.name),
                )
            ]

        if isinstance(node, (ast.For, ast.AsyncFor)):
            return self._check_iter_targets([node.target])

        if isinstance(node, ast.comprehension):
            return self._check_iter_targets([node.target])

        if isinstance(node, ast.MatchAs):
            if node.name is None:
                return []
            return self._check_bound_name(node, node.name)

        if isinstance(node, ast.MatchStar):
            if node.name is None:
                return []
            return self._check_bound_name(node, node.name)

        return []

    def _check_bound_name(self, node: ast.AST, name: str) -> list[Violation]:
        if is_var_name(name) or is_const_name(name):
            return []
        return [
            violation_at_node(
                node,
                "NNO101",
                ErrorCodes.NNO101.format(name=name),
            )
        ]

    def _check_var_targets(self, targets: list[ast.AST]) -> list[Violation]:
        violations: list[Violation] = []
        for t in targets:
            for name_node in _collect_name_targets(t):
                if is_var_name(name_node.id) or is_const_name(name_node.id):
                    continue
                violations.append(
                    violation_at_node(
                        name_node,
                        "NNO101",
                        ErrorCodes.NNO101.format(name=name_node.id),
                    )
                )
        return violations

    def _check_iter_targets(self, targets: list[ast.AST]) -> list[Violation]:
        violations: list[Violation] = []
        for t in targets:
            for name_node in _collect_name_targets(t):
                if is_iterator_name(name_node.id):
                    continue
                violations.append(
                    violation_at_node(
                        name_node,
                        "NNO110",
                        ErrorCodes.NNO110.format(name=name_node.id),
                    )
                )
        return violations
