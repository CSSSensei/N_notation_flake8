from __future__ import annotations

import ast

from ..core.errors import ErrorCodes
from ..core.patterns import is_required_param_name, is_var_name
from ..core.types import Violation
from .ast_utils import has_decorator, violation_at_node
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
                    is_required=is_required,
                    expected_required=expected_required,
                )
            )

        # Keyword-only params: each has matching default (or None)
        kw_defaults = list(args.kw_defaults or [])
        for a, d in zip(list(args.kwonlyargs), kw_defaults):
            is_required = d is None
            violations.extend(self._check_one_param(a, is_required=is_required))

        # *args / **kwargs are always optional-like
        if args.vararg is not None:
            violations.extend(self._check_one_param(args.vararg, is_required=False))
        if args.kwarg is not None:
            violations.extend(self._check_one_param(args.kwarg, is_required=False))

        return violations

    def _check_one_param(
        self,
        node: ast.arg,
        *,
        is_required: bool,
        expected_required: str | None = None,
    ) -> list[Violation]:
        name = node.arg

        if is_required:
            if expected_required is not None:
                if name == expected_required:
                    return []
                expected = expected_required
            else:
                if is_required_param_name(name):
                    return []
                expected = "n<posint>"

            return [
                violation_at_node(
                    node,
                    "NNO201",
                    ErrorCodes.NNO201.format(expected=expected, name=name),
                )
            ]

        if is_var_name(name):
            return []

        return [
            violation_at_node(
                node,
                "NNO202",
                ErrorCodes.NNO202.format(name=name),
            )
        ]
