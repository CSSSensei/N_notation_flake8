from __future__ import annotations

import unittest

from nflake8.rules.no_type_annotations import NoTypeAnnotations
from tests.helpers import run_rule_on_source


class TestNoTypeAnnotations(unittest.TestCase):
    def test_reports_var_annotation(self) -> None:
        r = run_rule_on_source(NoTypeAnnotations(), "n1234567890: int = 1\n")
        self.assertIn("NNO701", r.codes)

    def test_reports_arg_annotation(self) -> None:
        r = run_rule_on_source(NoTypeAnnotations(), "def n1234567890(n1: int):\n    pass\n")
        self.assertIn("NNO701", r.codes)

    def test_reports_return_annotation(self) -> None:
        r = run_rule_on_source(NoTypeAnnotations(), "def n1234567890(n1) -> int:\n    return 1\n")
        self.assertIn("NNO701", r.codes)

    def test_allows_no_annotations(self) -> None:
        r = run_rule_on_source(NoTypeAnnotations(), "def n1234567890(n1):\n    return 1\n")
        self.assertNotIn("NNO701", r.codes)
