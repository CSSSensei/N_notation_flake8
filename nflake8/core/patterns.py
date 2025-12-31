from __future__ import annotations

import re
from dataclasses import dataclass

_VAR_DEC_RE = re.compile(r"n\d{10}\Z")
_VAR_BOOL_RE = re.compile(r"n[01]{10}\Z")
_CONST_RE = re.compile(r"N\d{10}\Z")
_FUNC_RE = _VAR_DEC_RE
_FUNC_BOOL_RE = _VAR_BOOL_RE
_CLASS_RE = re.compile(r"N\d{10}(?:n\d{10})*\Z")
_CLASS_DERIVED_RE = re.compile(r"N\d{10}(?:n\d{10})+\Z")
_MEMBER_PUBLIC_RE = re.compile(r"n_(?:\d{10}|[01]{10})\Z")
_MEMBER_PRIVATE_RE = re.compile(r"_n(?:\d{10}|[01]{10})\Z")
_ITER_RE = re.compile(r"n+\Z")
_REQUIRED_PARAM_RE = re.compile(r"n[1-9]\d*\Z")

_IMPORT_ALIAS_RE = re.compile(r"N[1-9]\d*\Z")
_FROM_ALIAS_RE = re.compile(r"N\d{10}\Z")

_NOQA_COMMENT_RE = re.compile(r"#\s*noqa(?::\s*[A-Z0-9, ]+)?\s*\Z")

README_DECLARATION_BLOCK = (
    "В рамках данного проекта используется N-нотация (N notation) — система правил\n"
    "именования и кодирования, основанная на применении числовых идентификаторов.\n"
    "\n"
    "Применение данной нотации является преднамеренным архитектурным решением.\n"
    "\n"
    "Идентификаторы файлов, директорий, переменных, функций, классов и прочих\n"
    "программных сущностей не предназначены для семантического анализа.\n"
    "\n"
    "Попытки оптимизации читаемости кода путём изменения идентификаторов,\n"
    "введения словесных обозначений или адаптации к иным кодировочным стилям\n"
    "рассматриваются как нарушение архитектурной целостности проекта.\n"
    "\n"
    "Разработчики проекта не несут ответственности за ошибки в интерпретации структуры кода,\n"
    "возникшие вследствие игнорирования настоящего уведомления.\n"
    "\n"
    "Для получения дополнительной информации, пожалуйста,\n"
    "ознакомьтесь с документацией по ссылке: https://github.com/Phasalo/N_notation.\n"
)


def is_var_name(name: str) -> bool:
    # bool is subset of decimal; accept both
    return bool(_VAR_BOOL_RE.fullmatch(name) or _VAR_DEC_RE.fullmatch(name))


def is_const_name(name: str) -> bool:
    return bool(_CONST_RE.fullmatch(name))


def is_func_name(name: str) -> bool:
    return bool(_FUNC_BOOL_RE.fullmatch(name) or _FUNC_RE.fullmatch(name))


def is_class_name(name: str) -> bool:
    return bool(_CLASS_RE.fullmatch(name))


def is_derived_class_name(name: str) -> bool:
    return bool(_CLASS_DERIVED_RE.fullmatch(name))


def is_public_member_name(name: str) -> bool:
    return bool(_MEMBER_PUBLIC_RE.fullmatch(name))


def is_private_member_name(name: str) -> bool:
    return bool(_MEMBER_PRIVATE_RE.fullmatch(name))


def is_iterator_name(name: str) -> bool:
    return bool(_ITER_RE.fullmatch(name))


def is_required_param_name(name: str) -> bool:
    return bool(_REQUIRED_PARAM_RE.fullmatch(name))


def is_import_alias(name: str) -> bool:
    return bool(_IMPORT_ALIAS_RE.fullmatch(name))


def is_from_alias(name: str) -> bool:
    return bool(_FROM_ALIAS_RE.fullmatch(name))


def is_noqa_comment(text: str) -> bool:
    return bool(_NOQA_COMMENT_RE.fullmatch(text))


def expected_receiver_name(class_name: str) -> str:
    if not class_name:
        return "n"
    if class_name[0] != "N":
        return "n" + class_name[1:]
    return "n" + class_name[1:]


def expected_direct_base_name(derived_class_name: str) -> str | None:
    """
    For N<id>n<id>n<id>..., direct base is previous segment:
      N<id>n<id>n<id> -> N<id>n<id>
      N<id>n<id>      -> N<id>
    """
    if not is_derived_class_name(derived_class_name):
        return None
    parts = derived_class_name.split("n")
    # split produces like ["N<rootid>", "<child1id>", "<child2id>", ...]
    if len(parts) == 2:
        return parts[0]
    return "n".join(parts[:-1])


@dataclass(frozen=True, slots=True)
class ReadmeStatus:
    _ok: bool
    _reason: str

    @property
    def ok(self) -> bool:
        return self._ok

    @property
    def reason(self) -> str:
        return self._reason
