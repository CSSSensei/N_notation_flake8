from __future__ import annotations

import ast

from ..rules.base import Source
from ..rules.registry import get_all_rules
from ..core.types import Violation


def run_ast_checks(*, tree: ast.AST, filename: str) -> list[Violation]:
    walker = _AstWalker(tree=tree, filename=filename)
    walker.visit(tree)
    return walker.violations


class _AstWalker(ast.NodeVisitor):
    def __init__(self, *, tree: ast.AST, filename: str) -> None:
        self._tree = tree
        self._filename = filename
        self._class_stack: list[ast.ClassDef] = []
        self.violations: list[Violation] = []

    @property
    def _current_class(self) -> ast.ClassDef | None:
        return self._class_stack[-1] if self._class_stack else None

    def _check_rules(self, node: ast.AST) -> None:
        source = Source(
            _node=node,
            _current_class=self._current_class,
            _tree=self._tree,
            _filename=self._filename,
        )
        for rule in get_all_rules():
            self.violations.extend(rule.check(source))

    def visit(self, node: ast.AST) -> None:
        self._check_rules(node)
        super().visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node)
        self.generic_visit(node)
        self._class_stack.pop()
