from __future__ import annotations

from .base import Rule
from .class_names import ClassNames
from .no_docstring import NoDocstring
from .no_type_annotations import NoTypeAnnotations
from .receiver_name import ReceiverName


def get_all_rules() -> list[Rule]:
    return [
        NoDocstring(),
        NoTypeAnnotations(),
        ClassNames(),
        ReceiverName(),
    ]
