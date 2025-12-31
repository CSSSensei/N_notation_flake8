from __future__ import annotations

import os

from .patterns import README_DECLARATION_BLOCK, ReadmeStatus


_root_by_dir: dict[str, str | None] = {}
_readme_status_by_root: dict[str, ReadmeStatus] = {}
_readme_reported_by_root: set[str] = set()


def was_readme_reported(root: str) -> bool:
    return root in _readme_reported_by_root


def mark_readme_reported(root: str) -> None:
    _readme_reported_by_root.add(root)


def find_project_root(start_path: str) -> str | None:
    start_dir = os.path.abspath(os.path.dirname(start_path))
    if start_dir in _root_by_dir:
        return _root_by_dir[start_dir]

    cur = start_dir
    while True:
        if (
            os.path.isdir(os.path.join(cur, ".git"))
            or os.path.isfile(os.path.join(cur, "pyproject.toml"))
            or os.path.isfile(os.path.join(cur, "setup.cfg"))
            or os.path.isfile(os.path.join(cur, "tox.ini"))
            or os.path.isfile(os.path.join(cur, "README.md"))
        ):
            _root_by_dir[start_dir] = cur
            return cur

        parent = os.path.dirname(cur)
        if parent == cur:
            _root_by_dir[start_dir] = None
            return None
        cur = parent


def get_readme_status(root: str) -> ReadmeStatus:
    if root in _readme_status_by_root:
        return _readme_status_by_root[root]

    path = os.path.join(root, "README.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
    except FileNotFoundError:
        status = ReadmeStatus(_ok=False, _reason="missing")
    except OSError:
        status = ReadmeStatus(_ok=False, _reason="unreadable")
    else:
        normalized = data.replace("\r\n", "\n")
        ok = README_DECLARATION_BLOCK in normalized
        status = ReadmeStatus(_ok=ok, _reason=("ok" if ok else "mismatch"))

    _readme_status_by_root[root] = status
    return status
