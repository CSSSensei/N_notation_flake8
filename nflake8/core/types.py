from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Violation:
    _line: int
    _col: int
    _code: str
    _message: str

    @property
    def line(self) -> int:
        return self._line

    @property
    def col(self) -> int:
        return self._col

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    def to_flake8(self, plugin_type: type) -> tuple[int, int, str, type]:
        return (self._line, self._col, f"{self._code} {self._message}", plugin_type)
