from __future__ import annotations

import unittest

from nflake8.rules.member_names import MemberNames
from tests.helpers import run_rule_on_source


class TestMemberNames(unittest.TestCase):
    def test_reports_invalid_public_member_name(self) -> None:
        src = """\
class N1234567890:
    foo = 1
"""
        r = run_rule_on_source(MemberNames(), src)
        self.assertIn("NNO108", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_reports_invalid_private_member_name(self) -> None:
        src = """\
class N1234567890:
    _foo = 1
"""
        r = run_rule_on_source(MemberNames(), src)
        self.assertIn("NNO109", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_allows_valid_public_member_name(self) -> None:
        src = """\
class N1234567890:
    n_1234567890 = 1
"""
        r = run_rule_on_source(MemberNames(), src)
        self.assertNotIn("NNO108", r.codes)

    def test_allows_valid_private_member_name(self) -> None:
        src = """\
class N1234567890:
    _n1234567890 = 1
"""
        r = run_rule_on_source(MemberNames(), src)
        self.assertNotIn("NNO109", r.codes)

    def test_reports_invalid_method_member_name(self) -> None:
        src = """\
class N1234567890:
    def foo(self, n1):
        pass
"""
        r = run_rule_on_source(MemberNames(), src)
        self.assertIn("NNO108", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_allows_valid_method_member_name(self) -> None:
        src = """\
class N1234567890:
    def n_1234567890(self, n1):
        pass
"""
        r = run_rule_on_source(MemberNames(), src)
        self.assertNotIn("NNO108", r.codes)
