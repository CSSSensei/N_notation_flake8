from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import expected_direct_base_name, is_class_name, is_derived_class_name
from ..core.types import Violation
from .ast_utils import violation_at_node
from .base import Rule, Source


class ClassNames(Rule):
    """Validate class names and derived-class base chain (NNO106, NNO107)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        if not isinstance(node, ast.ClassDef):
            return []

        violations: list[Violation] = []

        if not is_class_name(node.name):
            violations.append(
                violation_at_node(
                    node,
                    "NNO106",
                    ErrorCodes.NNO106.format(name=node.name),
                )
            )

        if is_derived_class_name(node.name):
            expected_base = expected_direct_base_name(node.name)
            if expected_base is not None:
                base_names: list[str] = []
                for b in node.bases:
                    if isinstance(b, ast.Name):
                        base_names.append(b.id)

                if expected_base not in base_names:
                    violations.append(
                        violation_at_node(
                            node,
                            "NNO107",
                            ErrorCodes.NNO107.format(expected=expected_base),
                        )
                    )

        return violations
