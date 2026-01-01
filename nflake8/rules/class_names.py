from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import expected_direct_base_name, is_class_name, is_derived_class_name
from ..core.suggestions import (
    format_with_suggestion,
    suggest_class_name,
    suggest_derived_class_suffix,
)
from ..core.types import Violation
from .ast_utils import node_location, violation_at_node
from .base import Rule, Source


class ClassNames(Rule):
    """Validate class names and derived-class base chain (NNO106, NNO107)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        if not isinstance(node, ast.ClassDef):
            return []

        violations: list[Violation] = []

        line, col = node_location(node)

        if not is_class_name(node.name):
            violations.append(
                violation_at_node(
                    node,
                    "NNO106",
                    format_with_suggestion(
                        ErrorCodes.NNO106.format(name=node.name),
                        suggest=suggest_class_name(filename=source.filename, line=line, col=col),
                    ),
                )
            )

        if node.bases and not is_derived_class_name(node.name):
            suggested = (
                suggest_class_name(filename=source.filename, line=line, col=col)
                + suggest_derived_class_suffix(filename=source.filename, line=line, col=col)
            )
            violations.append(
                violation_at_node(
                    node,
                    "NNO105",
                    format_with_suggestion(
                        ErrorCodes.NNO105.format(name=node.name),
                        suggest=suggested,
                    ),
                )
            )
            return violations

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
                            format_with_suggestion(
                                ErrorCodes.NNO107.format(expected=expected_base),
                                suggest=expected_base,
                            ),
                        )
                    )

        return violations
