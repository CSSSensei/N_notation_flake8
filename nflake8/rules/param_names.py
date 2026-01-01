from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import is_required_param_name, is_var_name
from ..core.suggestions import format_with_suggestion, suggest_optional_param_name
from ..core.types import Violation
from .ast_utils import has_decorator, node_location, violation_at_node
from .base import Rule, Source


class ParamNames(Rule):
    """Validate function/method parameter names (NNO201, NNO202)."""

    def check(self, source: Source) -> list[Violation]:
        node = source.node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []

        args = node.args

        skip_first_positional = (
            source.current_class is not None and not has_decorator(node, "staticmethod")
        )

        violations: list[Violation] = []

        # Positional params: posonlyargs + args
        pos_params: list[ast.arg] = list(args.posonlyargs) + list(args.args)
        if skip_first_positional and pos_params:
            pos_params = pos_params[1:]

        # Defaults apply to the last N positional params
        defaults = list(args.defaults or [])
        required_pos_count = max(0, len(pos_params) - len(defaults))

        for i, a in enumerate(pos_params):
            is_required = i < required_pos_count
            expected_required = f"n{i + 1}" if is_required else None
            violations.extend(
                self._check_one_param(
                    a,
                    filename=source.filename,
                    is_required=is_required,
                    expected_required=expected_required,
                )
            )

        # Keyword-only params: each has matching default (or None)
        kw_defaults = list(args.kw_defaults or [])
        for a, d in zip(list(args.kwonlyargs), kw_defaults):
            is_required = d is None
            violations.extend(self._check_one_param(a, filename=source.filename, is_required=is_required))

        # *args / **kwargs are always optional-like
        if args.vararg is not None:
            violations.extend(self._check_one_param(args.vararg, filename=source.filename, is_required=False))
        if args.kwarg is not None:
            violations.extend(self._check_one_param(args.kwarg, filename=source.filename, is_required=False))

        return violations

    def _check_one_param(
        self,
        node: ast.arg,
        *,
        filename: str,
        is_required: bool,
        expected_required: str | None = None,
    ) -> list[Violation]:
        name = node.arg

        if is_required:
            if expected_required is not None:
                if name == expected_required:
                    return []
                expected = expected_required
                suggested = expected_required
            else:
                if is_required_param_name(name):
                    return []
                expected = "n<posint>"
                suggested = "n1"

            return [
                violation_at_node(
                    node,
                    "NNO201",
                    format_with_suggestion(
                        ErrorCodes.NNO201.format(expected=expected, name=name),
                        suggest=suggested,
                    ),
                )
            ]

        if is_var_name(name):
            return []

        line, col = node_location(node)
        return [
            violation_at_node(
                node,
                "NNO202",
                format_with_suggestion(
                    ErrorCodes.NNO202.format(name=name),
                    suggest=suggest_optional_param_name(filename=filename, line=line, col=col),
                ),
            )
        ]
