from __future__ import annotations

import unittest

from nflake8.rules.receiver_name import ReceiverName
from tests.helpers import run_rule_on_source


class TestReceiverName(unittest.TestCase):
    def test_reports_self(self) -> None:
        src = """\
class N1234567890:
    def n_1234567890(self, n1):
        pass
"""
        r = run_rule_on_source(ReceiverName(), src)
        self.assertIn("NNO210", r.codes)
        self.assertTrue(any("(suggest " in v.message for v in r.violations))

    def test_allows_correct_receiver(self) -> None:
        src = """\
class N1234567890:
    def n_1234567890(n1234567890, n1):
        pass
"""
        r = run_rule_on_source(ReceiverName(), src)
        self.assertNotIn("NNO210", r.codes)

    def test_skips_staticmethod(self) -> None:
        src = """\
class N1234567890:
    @staticmethod
    def n_1234567890(self, n1):
        pass
"""
        r = run_rule_on_source(ReceiverName(), src)
        self.assertNotIn("NNO210", r.codes)
