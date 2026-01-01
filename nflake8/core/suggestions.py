from __future__ import annotations

import zlib


_MOD = 10**10


def _stable_10_digits(*, kind: str, filename: str, line: int, col: int) -> str:
    """
    Generate a deterministic 10-digit identifier for suggestions.

    Notes:
    - This is NOT meant to be globally unique.
    - It's deterministic for a given (kind, filename, line, col), so messages are stable
      between runs, but will change if code is moved.
    """
    payload = f"{kind}|{filename}|{line}|{col}".encode("utf-8")
    value = zlib.crc32(payload) % _MOD
    return f"{value:010d}"


def suggest_var_name(*, filename: str, line: int, col: int) -> str:
    return f"n{_stable_10_digits(kind='var', filename=filename, line=line, col=col)}"


def suggest_func_name(*, filename: str, line: int, col: int) -> str:
    return f"n{_stable_10_digits(kind='func', filename=filename, line=line, col=col)}"


def suggest_const_name(*, filename: str, line: int, col: int) -> str:
    return f"N{_stable_10_digits(kind='const', filename=filename, line=line, col=col)}"


def suggest_class_name(*, filename: str, line: int, col: int) -> str:
    return f"N{_stable_10_digits(kind='class', filename=filename, line=line, col=col)}"


def suggest_derived_class_suffix(*, filename: str, line: int, col: int) -> str:
    """
    Suffix for derived class names: n<10digits>
    (caller decides the base/root part).
    """
    return f"n{_stable_10_digits(kind='derived', filename=filename, line=line, col=col)}"


def suggest_public_member_name(*, filename: str, line: int, col: int) -> str:
    return f"n_{_stable_10_digits(kind='member_public', filename=filename, line=line, col=col)}"


def suggest_private_member_name(*, filename: str, line: int, col: int) -> str:
    return f"_n{_stable_10_digits(kind='member_private', filename=filename, line=line, col=col)}"


def suggest_iterator_name() -> str:
    # Iterator naming is structural (n, nn, nnn...), so the simplest suggestion is "n".
    return "n"


def suggest_optional_param_name(*, filename: str, line: int, col: int) -> str:
    return suggest_var_name(filename=filename, line=line, col=col)


def format_with_suggestion(message: str, *, suggest: str) -> str:
    return f"{message} (suggest {suggest})"
