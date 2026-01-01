from __future__ import annotations

import unittest

from nflake8.rules.class_names import ClassNames
from tests.helpers import run_rule_on_source


class TestClassNames(unittest.TestCase):
    def test_reports_invalid_class_name(self) -> None:
        r = run_rule_on_source(ClassNames(), "class Foo:\n    pass\n")
        self.assertIn("NNO106", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_reports_derived_base_mismatch(self) -> None:
        src = """\
class N1234567890:
    pass

class N1234567890n0000000001(N9999999999):
    pass
"""
        r = run_rule_on_source(ClassNames(), src)
        self.assertIn("NNO107", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_allows_valid_derived_base(self) -> None:
        src = """\
class N1234567890:
    pass

class N1234567890n0000000001(N1234567890):
    pass
"""
        r = run_rule_on_source(ClassNames(), src)
        self.assertNotIn("NNO107", r.codes)

    def test_reports_inheriting_non_derived_name(self) -> None:
        src = """\
class N1337856128:
    pass

class N1337856128(N1337856128):
    pass
"""
        r = run_rule_on_source(ClassNames(), src)
        self.assertIn("NNO105", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))
