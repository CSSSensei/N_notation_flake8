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
            direct_base: str | None = None
            if len(node.bases) == 1 and isinstance(node.bases[0], ast.Name):
                base_name = node.bases[0].id
                if is_class_name(base_name):
                    direct_base = base_name

            suggested_root = direct_base
            if suggested_root is None:
                suggested_root = suggest_class_name(
                    filename=source.filename,
                    line=line,
                    col=col,
                )

            suggested_suffix = suggest_derived_class_suffix(
                filename=source.filename,
                line=line,
                col=col,
            )
            suggested = suggested_root + suggested_suffix

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
                for base_node in node.bases:
                    if isinstance(base_node, ast.Name):
                        base_names.append(base_node.id)

                if expected_base not in base_names:
                    suggest_value = expected_base
                    if len(base_names) == 1 and is_class_name(base_names[0]):
                        actual_base = base_names[0]
                        last_segment = node.name.split("n")[-1]
                        suggest_value = f"{actual_base}n{last_segment}"

                    violations.append(
                        violation_at_node(
                            node,
                            "NNO107",
                            format_with_suggestion(
                                ErrorCodes.NNO107.format(expected=expected_base),
                                suggest=suggest_value,
                            ),
                        )
                    )

        return violations
