from __future__ import annotations

import os
import re

from ..core.errors import ErrorCodes
from ..core.root import (
    find_project_root,
    get_readme_status,
    mark_readme_reported,
    was_readme_reported,
)
from ..core.types import Violation

_FILENAME_RE = re.compile(r"n\d+\.py\Z")
_DIR_RE = re.compile(r"N\d+(?:_\d+)*\Z")


def run_project_checks(*, filename: str) -> list[Violation]:
    v: list[Violation] = []

    base = os.path.basename(filename)
    if base and not _FILENAME_RE.fullmatch(base):
        v.append(
            Violation(
                _line=1,
                _col=0,
                _code="NNO401",
                _message=ErrorCodes.NNO401.format(name=base),
            )
        )

    root = find_project_root(filename)
    if root is None:
        return v

    # Check parent-chain directories
    rel_dir = os.path.relpath(os.path.dirname(filename), root)
    if rel_dir not in (".", ""):
        parts = [p for p in rel_dir.split(os.sep) if p and p != "."]
        for p in parts:
            if not _DIR_RE.fullmatch(p):
                v.append(
                    Violation(
                        _line=1,
                        _col=0,
                        _code="NNO420",
                        _message=ErrorCodes.NNO420.format(name=p),
                    )
                )
                break

    status = get_readme_status(root)
    if not status.ok and not was_readme_reported(root):
        mark_readme_reported(root)
        v.append(
            Violation(
                _line=1,
                _col=0,
                _code="NNO500",
                _message=ErrorCodes.NNO500,
            )
        )

    return v
