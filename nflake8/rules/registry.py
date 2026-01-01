from __future__ import annotations

from .base import Rule
from .class_names import ClassNames
from .func_names import FuncNames
from .member_names import MemberNames
from .no_docstring import NoDocstring
from .no_type_annotations import NoTypeAnnotations
from .param_names import ParamNames
from .receiver_name import ReceiverName
from .var_names import VarNames


def get_all_rules() -> list[Rule]:
    return [
        ClassNames(),
        FuncNames(),
        MemberNames(),
        NoDocstring(),
        NoTypeAnnotations(),
        ParamNames(),
        ReceiverName(),
        VarNames(),
    ]
