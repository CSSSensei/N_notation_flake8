from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import is_const_name, is_iterator_name, is_var_name
from ..core.suggestions import (
    format_with_suggestion,
    suggest_var_name,
)
from ..core.types import Violation
from .ast_utils import node_location, violation_at_node
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

    def __init__(self) -> None:
        self._cached_tree_id: int | None = None
        self._parent_map: dict[ast.AST, ast.AST] = {}

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        current_class = source.current_class

        if _is_direct_class_body_stmt(node, current_class):
            return []

        if isinstance(node, ast.Assign):
            return self._check_var_targets(node.targets, filename=source.filename)

        if isinstance(node, ast.AnnAssign):
            return self._check_var_targets([node.target], filename=source.filename)

        if isinstance(node, ast.AugAssign):
            return self._check_var_targets([node.target], filename=source.filename)

        if isinstance(node, ast.NamedExpr):
            return self._check_var_targets([node.target], filename=source.filename)

        # "with ... as <name>"
        if isinstance(node, ast.withitem):
            if node.optional_vars is None:
                return []
            return self._check_var_targets([node.optional_vars], filename=source.filename)

        # "except ... as <name>"
        if isinstance(node, ast.ExceptHandler):
            if not node.name:
                return []
            if is_var_name(node.name):
                return []
            if is_const_name(node.name):
                return []
            line, col = node_location(node)
            return [
                violation_at_node(
                    node,
                    "NNO101",
                    format_with_suggestion(
                        ErrorCodes.NNO101.format(name=node.name),
                        suggest=suggest_var_name(filename=source.filename, line=line, col=col),
                    ),
                )
            ]

        if isinstance(node, (ast.For, ast.AsyncFor)):
            self._ensure_parent_map(source.tree)
            expected = self._expected_iterator_for_for_node(node)
            expected_name = expected if isinstance(node.target, ast.Name) else None
            return self._check_iter_targets([node.target], expected=expected_name, filename=source.filename)

        if isinstance(node, ast.comprehension):
            self._ensure_parent_map(source.tree)
            expected = self._expected_iterator_for_comprehension(node)
            expected_name = expected if isinstance(node.target, ast.Name) else None
            return self._check_iter_targets([node.target], expected=expected_name, filename=source.filename)

        if isinstance(node, ast.MatchAs):
            if node.name is None:
                return []
            return self._check_bound_name(node, node.name, filename=source.filename)

        if isinstance(node, ast.MatchStar):
            if node.name is None:
                return []
            return self._check_bound_name(node, node.name, filename=source.filename)

        return []

    def _ensure_parent_map(self, tree: ast.AST) -> None:
        tree_id = id(tree)
        if self._cached_tree_id == tree_id:
            return
        self._cached_tree_id = tree_id
        self._parent_map = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                self._parent_map[child] = parent

    def _expected_iterator_for_for_node(self, node: ast.For | ast.AsyncFor) -> str:
        """
        Expected iterator name depends on nesting depth:
          for n in ...:      # depth=1
              for nn in ...: # depth=2
                  for nnn... # depth=3
        """
        depth = 1
        cur: ast.AST = node
        while cur in self._parent_map:
            cur = self._parent_map[cur]
            if isinstance(cur, (ast.For, ast.AsyncFor)):
                depth += 1
        return "n" * depth

    def _expected_iterator_for_comprehension(self, node: ast.comprehension) -> str:
        """
        Expected iterator name depends on generator position:
          [x for n in ... for nn in ...]  # depths 1,2
        """
        parent = self._parent_map.get(node)
        generators = getattr(parent, "generators", None)
        if isinstance(generators, list) and node in generators:
            return "n" * (generators.index(node) + 1)
        return "n"

    def _check_bound_name(self, node: ast.AST, name: str, *, filename: str) -> list[Violation]:
        if is_var_name(name) or is_const_name(name):
            return []
        line, col = node_location(node)
        return [
            violation_at_node(
                node,
                "NNO101",
                format_with_suggestion(
                    ErrorCodes.NNO101.format(name=name),
                    suggest=suggest_var_name(filename=filename, line=line, col=col),
                ),
            )
        ]

    def _check_var_targets(self, targets: list[ast.AST], *, filename: str) -> list[Violation]:
        violations: list[Violation] = []
        for t in targets:
            for name_node in _collect_name_targets(t):
                if is_var_name(name_node.id) or is_const_name(name_node.id):
                    continue
                line, col = node_location(name_node)
                violations.append(
                    violation_at_node(
                        name_node,
                        "NNO101",
                        format_with_suggestion(
                            ErrorCodes.NNO101.format(name=name_node.id),
                            suggest=suggest_var_name(filename=filename, line=line, col=col),
                        ),
                    )
                )
        return violations

    def _check_iter_targets(
        self,
        targets: list[ast.AST],
        *,
        expected: str | None,
        filename: str,
    ) -> list[Violation]:
        violations: list[Violation] = []
        for t in targets:
            for name_node in _collect_name_targets(t):
                if expected is None:
                    if is_iterator_name(name_node.id):
                        continue
                    exp = "n"
                else:
                    if name_node.id == expected:
                        continue
                    exp = expected

                violations.append(
                    violation_at_node(
                        name_node,
                        "NNO110",
                        ErrorCodes.NNO110.format(expected=exp, name=name_node.id),
                    )
                )
        return violations
