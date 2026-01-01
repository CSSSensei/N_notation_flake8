from __future__ import annotations

from functools import lru_cache
from importlib import resources
from typing import Iterable

from . import __version__
from .checks.ast import run_ast_checks
from .checks.project import run_project_checks
from .checks.tokens import run_token_checks


@lru_cache(maxsize=1)
def _load_phasalo_art() -> str:
    return (
        resources.files(__package__)
        .joinpath("phasalo.txt")
        .read_text(encoding="utf-8")
        .lstrip("\n")
    )


class NNotationChecker:
    name = "n-notation"
    version = __version__

    def __init__(self, tree, filename: str, lines=None):
        self._tree = tree
        self._filename = filename
        self._lines = lines

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            "--phasalo",
            default=False,
            action="store_true",
            help="Print PHASALO ascii art and exit.",
        )

    @classmethod
    def parse_options(cls, options) -> None:
        cls._options = options
        if getattr(options, "phasalo", False):
            print(_load_phasalo_art(), end="")
            raise SystemExit(0)

    def _read_text(self) -> str:
        if self._lines is not None:
            return "".join(self._lines)
        try:
            with open(self._filename, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    def run(self) -> Iterable[tuple[int, int, str, type]]:
        # Project checks
        for v in run_project_checks(filename=self._filename):
            yield v.to_flake8(type(self))

        # AST checks
        if self._tree is not None:
            for v in run_ast_checks(tree=self._tree, filename=self._filename):
                yield v.to_flake8(type(self))

        # Token checks
        text = self._read_text()
        for v in run_token_checks(text=text, filename=self._filename):
            yield v.to_flake8(type(self))
