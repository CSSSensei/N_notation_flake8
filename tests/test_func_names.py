from __future__ import annotations

import unittest

from nflake8.rules.func_names import FuncNames
from tests.helpers import run_rule_on_source


class TestFuncNames(unittest.TestCase):
    def test_reports_invalid_function_name(self) -> None:
        r = run_rule_on_source(FuncNames(), "def foo(n1):\n    pass\n")
        self.assertIn("NNO104", r.codes)

    def test_allows_valid_function_name(self) -> None:
        r = run_rule_on_source(FuncNames(), "def n1234567890(n1):\n    pass\n")
        self.assertNotIn("NNO104", r.codes)

    def test_skips_method_names(self) -> None:
        src = """\
class N1234567890:
    def foo(self, n1):
        pass
"""
        r = run_rule_on_source(FuncNames(), src)
        self.assertNotIn("NNO104", r.codes)
