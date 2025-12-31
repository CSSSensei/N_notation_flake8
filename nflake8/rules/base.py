from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Protocol

from ..core.types import Violation


@dataclass(frozen=True, slots=True)
class Source:
    _node: ast.AST
    _current_class: ast.ClassDef | None
    _tree: ast.AST
    _filename: str

    @property
    def node(self) -> ast.AST:
        return self._node

    @property
    def current_class(self) -> ast.ClassDef | None:
        return self._current_class

    @property
    def tree(self) -> ast.AST:
        return self._tree

    @property
    def filename(self) -> str:
        return self._filename


class Rule(Protocol):
    """Protocol for N-notation rules analysis."""

    def check(self, source: Source) -> list[Violation]:
        """Check source for violations and return list of detected violations."""
        ...
