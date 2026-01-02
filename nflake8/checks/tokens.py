from __future__ import annotations

import ast
import io
import sys
import tokenize
from dataclasses import dataclass
from typing import Iterable

from ..core.errors import ErrorCodes
from ..core.patterns import (
    is_class_name,
    is_const_name,
    is_func_name,
    is_import_alias,
    is_noqa_comment,
    is_var_name,
)
from ..core.types import Violation


def run_token_checks(*, text: str, filename: str) -> list[Violation]:
    v: list[Violation] = []

    # Comments (allow only noqa)
    for tok in _iter_tokens(text):
        if tok.type == tokenize.COMMENT and not is_noqa_comment(tok.string):
            v.append(
                Violation(
                    _line=tok.start[0],
                    _col=tok.start[1],
                    _code="NNO601",
                    _message=ErrorCodes.NNO601,
                )
            )

    # Imports (aliasing + grouping + ordering)
    v.extend(_check_imports(text))

    return v


def _iter_tokens(text: str) -> Iterable[tokenize.TokenInfo]:
    # tokenize works on readline
    return tokenize.generate_tokens(io.StringIO(text).readline)


@dataclass(frozen=True, slots=True)
class _ImportStmt:
    _lineno: int
    _end_lineno: int
    _group: str  # "stdlib" | "third_party" | "local"
    _alias_key: int | None
    _code: str | None
    _col: int

    @property
    def lineno(self) -> int:
        return self._lineno

    @property
    def end_lineno(self) -> int:
        return self._end_lineno

    @property
    def group(self) -> str:
        return self._group

    @property
    def alias_key(self) -> int | None:
        return self._alias_key

    @property
    def code(self) -> str | None:
        return self._code

    @property
    def col(self) -> int:
        return self._col


def _check_imports(text: str) -> list[Violation]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    lines = text.splitlines()
    imports: list[_ImportStmt] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(_collect_import(node))
        elif isinstance(node, ast.ImportFrom):
            imports.extend(_collect_importfrom(node))
        else:
            # do not enforce "imports only at top"; just stop the first block
            # grouping/order rules apply within the first contiguous block only
            break

    v: list[Violation] = []

    # aliasing errors
    for stmt in imports:
        if stmt.code is not None:
            tmpl = getattr(ErrorCodes, stmt.code, "import alias violation")
            v.append(
                Violation(
                    _line=stmt.lineno,
                    _col=stmt.col,
                    _code=stmt.code,
                    _message=tmpl,
                )
            )

    # grouping, ordering, blank lines
    v.extend(_check_import_grouping_and_order(imports, lines))

    return v


def _collect_import(node: ast.Import) -> list[_ImportStmt]:
    out: list[_ImportStmt] = []
    end_lineno = getattr(node, "end_lineno", node.lineno) or node.lineno

    for alias in node.names:
        module0 = alias.name.split(".")[0]
        group = _classify_import(module0, module_is_relative=False)

        if _is_n_module_path(alias.name):
            code = None
            key = None
        elif alias.asname is None or not is_import_alias(alias.asname):
            code = "NNO301"
            key = None
        else:
            code = None
            key = int(alias.asname[1:])

        out.append(
            _ImportStmt(
                _lineno=node.lineno,
                _end_lineno=end_lineno,
                _group=group,
                _alias_key=key,
                _code=code,
                _col=getattr(node, "col_offset", 0) or 0,
            )
        )

    return out


def _collect_importfrom(node: ast.ImportFrom) -> list[_ImportStmt]:
    out: list[_ImportStmt] = []
    end_lineno = getattr(node, "end_lineno", node.lineno) or node.lineno

    is_relative = bool(node.level and node.level > 0)
    module0 = (node.module or "").split(".")[0] if node.module else ""
    group = _classify_import(module0, module_is_relative=is_relative)

    for alias in node.names:
        imported_name = alias.name

        if _is_n_object_name(imported_name):
            code = None
            key = None
        elif alias.asname is None:
            code = "NNO302"
            key = None
        elif not _is_valid_from_alias(imported_name, alias.asname):
            code = "NNO303"
            key = None
        else:
            code = None
            key = _alias_sort_key(alias.asname)

        out.append(
            _ImportStmt(
                _lineno=node.lineno,
                _end_lineno=end_lineno,
                _group=group,
                _alias_key=key,
                _code=code,
                _col=getattr(node, "col_offset", 0) or 0,
            )
        )

    return out


def _classify_import(module0: str, *, module_is_relative: bool) -> str:
    if module_is_relative:
        return "local"
    if module0.startswith("N") and len(module0) >= 2 and module0[1].isdigit():
        return "local"
    if module0.startswith("n") and len(module0) >= 2 and module0[1].isdigit():
        return "local"
    stdlib_names = getattr(sys, "stdlib_module_names", None)
    if stdlib_names and module0 in stdlib_names:
        return "stdlib"
    return "third_party"


def _is_n_module_path(path: str) -> bool:
    # N-directories: N<digits>[_<digits>]...
    # Module files:  n<digits>
    parts = path.split(".")
    for p in parts:
        if p.startswith("N") and len(p) > 1 and p[1].isdigit():
            continue
        if p.startswith("n") and len(p) > 1 and p[1].isdigit():
            continue
        return False
    return True


def _is_n_object_name(name: str) -> bool:
    return bool(
        is_var_name(name)
        or is_func_name(name)
        or is_const_name(name)
        or is_class_name(name)
    )


def _is_valid_from_alias(imported_name: str, asname: str) -> bool:
    # If original looks like Class/Const (Uppercase), alias must be N-notation class/const.
    if imported_name and imported_name[0].isupper():
        return bool(is_const_name(asname) or is_class_name(asname))
    # Otherwise treat as function/variable (lowercase/underscore/etc).
    return bool(is_var_name(asname) or is_func_name(asname))


def _alias_sort_key(asname: str) -> int | None:
    if not asname:
        return None
    if asname[0] == "N":
        # N<10 digits> or derived class N<10 digits>n<10 digits>...
        digits = asname[1:11]
        if len(digits) == 10 and digits.isdigit():
            return int(digits)
        return None
    if asname[0] == "n":
        payload = asname[1:]
        if len(payload) == 10 and payload.isdigit():
            return int(payload)
        if len(payload) == 10 and set(payload) <= {"0", "1"}:
            return int(payload, 2)
        return None
    return None


def _check_import_grouping_and_order(imports: list[_ImportStmt], lines: list[str]) -> list[Violation]:
    v: list[Violation] = []
    if not imports:
        return v

    order = {"stdlib": 0, "third_party": 1, "local": 2}

    # group order monotonic
    max_seen = -1
    for stmt in imports:
        cur = order[stmt.group]
        if cur < max_seen:
            v.append(
                Violation(
                    _line=stmt.lineno,
                    _col=stmt.col,
                    _code="NNO310",
                    _message=ErrorCodes.NNO310,
                )
            )
        max_seen = max(max_seen, cur)

    for prev, cur in zip(imports, imports[1:]):
        if prev.group == cur.group:
            continue

        between = lines[prev.end_lineno : cur.lineno - 1]
        blank_count = sum(1 for s in between if s.strip() == "")
        if blank_count != 1:
            v.append(
                Violation(
                    _line=cur.lineno,
                    _col=cur.col,
                    _code="NNO311",
                    _message=ErrorCodes.NNO311,
                )
            )

    # numeric ordering inside each group
    last_key_by_group: dict[str, int] = {}
    for stmt in imports:
        if stmt.alias_key is None:
            continue
        last = last_key_by_group.get(stmt.group)
        if last is not None and stmt.alias_key < last:
            v.append(
                Violation(
                    _line=stmt.lineno,
                    _col=stmt.col,
                    _code="NNO312",
                    _message=ErrorCodes.NNO312,
                )
            )
        last_key_by_group[stmt.group] = stmt.alias_key

    return v
