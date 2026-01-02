from __future__ import annotations

import unittest

from nflake8.rules.var_names import VarNames
from tests.helpers import run_rule_on_source


class TestVarNames(unittest.TestCase):
    def test_reports_invalid_var_name(self) -> None:
        r = run_rule_on_source(VarNames(), "count = 0\n")
        self.assertIn("NNO101", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_allows_decimal_var_name(self) -> None:
        r = run_rule_on_source(VarNames(), "n1234567890 = 0\n")
        self.assertNotIn("NNO101", r.codes)

    def test_allows_bool_var_name(self) -> None:
        r = run_rule_on_source(VarNames(), "n0101010101 = True\n")
        self.assertNotIn("NNO101", r.codes)

    def test_allows_const_name(self) -> None:
        r = run_rule_on_source(VarNames(), "N1234567890 = 1\n")
        self.assertNotIn("NNO101", r.codes)

    def test_reports_invalid_iterator_name(self) -> None:
        r = run_rule_on_source(VarNames(), "for i in range(3):\n    pass\n")
        self.assertIn("NNO110", r.codes)

    def test_allows_iterator_n(self) -> None:
        r = run_rule_on_source(VarNames(), "for n in range(3):\n    pass\n")
        self.assertNotIn("NNO110", r.codes)

    def test_reports_iterator_nn_at_top_level(self) -> None:
        r = run_rule_on_source(VarNames(), "for nn in range(3):\n    pass\n")
        self.assertIn("NNO110", r.codes)

    def test_allows_nested_iterators_n_then_nn(self) -> None:
        src = """\
for n in range(3):
    for nn in range(3):
        pass
"""
        r = run_rule_on_source(VarNames(), src)
        self.assertNotIn("NNO110", r.codes)

    def test_reports_wrong_nested_iterator_name(self) -> None:
        src = """\
for n in range(3):
    for n in range(3):
        pass
"""
        r = run_rule_on_source(VarNames(), src)
        self.assertIn("NNO110", r.codes)

    def test_allows_comprehension_iterators_n_then_nn(self) -> None:
        src = "n1234567890 = [n for n in range(3) for nn in range(3)]\n"
        r = run_rule_on_source(VarNames(), src)
        self.assertNotIn("NNO110", r.codes)

    def test_skips_direct_class_body_assignments(self) -> None:
        src = """\
class N1234567890:
    foo = 1
"""
        r = run_rule_on_source(VarNames(), src)
        self.assertNotIn("NNO101", r.codes)

    def test_reports_except_as_name(self) -> None:
        src = """\
try:
    1 / 0
except Exception as e:
    pass
"""
        r = run_rule_on_source(VarNames(), src)
        self.assertIn("NNO101", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_reports_with_as_name(self) -> None:
        src = """\
with open("x", "w") as f:
    pass
"""
        r = run_rule_on_source(VarNames(), src)
        self.assertIn("NNO101", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))
