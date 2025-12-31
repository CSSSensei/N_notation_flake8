from __future__ import annotations

import ast

from ..core.types import Violation


def violation_at_node(
    node: ast.AST,
    code: str,
    message: str,
    *,
    prefer_docstring_expr: bool = False,
) -> Violation:
    """
    Create a Violation located at node.lineno/col_offset

    If prefer_docstring_expr=True, and node is Module/Class/Function, point to the
    first statement expression (where docstring literal lives).
    """
    if prefer_docstring_expr and isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(getattr(node.body[0], "value", None), ast.Constant)
        ):
            if isinstance(node.body[0].value.value, str):
                return violation_at_node(node.body[0], code, message, prefer_docstring_expr=False)

    line = getattr(node, "lineno", 1) or 1
    col = getattr(node, "col_offset", 0) or 0
    return Violation(_line=line, _col=col, _code=code, _message=message)


def has_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    for d in node.decorator_list:
        if isinstance(d, ast.Name) and d.id == name:
            return True
        if isinstance(d, ast.Attribute) and d.attr == name:
            return True
    return False


def first_positional_arg(args: ast.arguments) -> ast.arg | None:
    seq = list(args.posonlyargs) + list(args.args)
    return seq[0] if seq else None


def has_any_type_annotations(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    if node.returns is not None:
        return True

    args = node.args

    for a in list(args.posonlyargs) + list(args.args):
        if a.annotation is not None:
            return True

    for a in list(args.kwonlyargs):
        if a.annotation is not None:
            return True

    if args.vararg is not None and args.vararg.annotation is not None:
        return True
    if args.kwarg is not None and args.kwarg.annotation is not None:
        return True

    return False
