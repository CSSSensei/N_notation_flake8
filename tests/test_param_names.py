from __future__ import annotations

import unittest

from nflake8.rules.param_names import ParamNames
from tests.helpers import run_rule_on_source


class TestParamNames(unittest.TestCase):
    def test_reports_required_param_invalid_name(self) -> None:
        r = run_rule_on_source(ParamNames(), "def n1234567890(x):\n    pass\n")
        self.assertIn("NNO201", r.codes)

    def test_allows_required_param_n1(self) -> None:
        r = run_rule_on_source(ParamNames(), "def n1234567890(n1):\n    pass\n")
        self.assertNotIn("NNO201", r.codes)

    def test_reports_optional_param_invalid_name(self) -> None:
        r = run_rule_on_source(ParamNames(), "def n1234567890(n1, x=None):\n    pass\n")
        self.assertIn("NNO202", r.codes)

    def test_allows_optional_param_n10digits(self) -> None:
        r = run_rule_on_source(ParamNames(), "def n1234567890(n1, n1234567890=None):\n    pass\n")
        self.assertNotIn("NNO202", r.codes)

    def test_method_skips_receiver_but_checks_other_params(self) -> None:
        src = """\
class N1234567890:
    def n_1234567890(self, x):
        pass
"""
        r = run_rule_on_source(ParamNames(), src)
        self.assertIn("NNO201", r.codes)  # x is required and invalid

    def test_method_with_staticmethod_does_not_skip_first_param(self) -> None:
        src = """\
class N1234567890:
    @staticmethod
    def n_1234567890(x):
        pass
"""
        r = run_rule_on_source(ParamNames(), src)
        self.assertIn("NNO201", r.codes)

    def test_kwonly_required_param(self) -> None:
        r = run_rule_on_source(ParamNames(), "def n1234567890(*, x):\n    pass\n")
        self.assertIn("NNO201", r.codes)

    def test_kwonly_optional_param(self) -> None:
        r = run_rule_on_source(ParamNames(), "def n1234567890(*, n1234567890=None):\n    pass\n")
        self.assertNotIn("NNO202", r.codes)
