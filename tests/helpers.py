from __future__ import annotations

import ast
from dataclasses import dataclass

from nflake8.rules.base import Rule, Source
from nflake8.core.types import Violation


@dataclass(frozen=True, slots=True)
class RunResult:
    _violations: list[Violation]

    @property
    def violations(self) -> list[Violation]:
        return self._violations

    @property
    def codes(self) -> list[str]:
        return [v.code for v in self._violations]


def run_rule_on_source(rule: Rule, source_text: str, *, filename: str = "n1.py") -> RunResult:
    tree = ast.parse(source_text)
    violations: list[Violation] = []
    class_stack: list[ast.ClassDef] = []

    def visit(node: ast.AST) -> None:
        current_class = class_stack[-1] if class_stack else None
        violations.extend(
            rule.check(
                Source(
                    _node=node,
                    _current_class=current_class,
                    _tree=tree,
                    _filename=filename,
                )
            )
        )

        if isinstance(node, ast.ClassDef):
            class_stack.append(node)
            for child in ast.iter_child_nodes(node):
                visit(child)
            class_stack.pop()
            return

        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return RunResult(_violations=violations)
