from __future__ import annotations

import unittest

from nflake8.rules.no_docstring import NoDocstring
from tests.helpers import run_rule_on_source


class TestNoDocstring(unittest.TestCase):
    def test_reports_module_docstring(self) -> None:
        r = run_rule_on_source(NoDocstring(), '"""x"""\n\nN1234567890 = 1\n')
        self.assertIn("NNO602", r.codes)

    def test_allows_no_docstring(self) -> None:
        r = run_rule_on_source(NoDocstring(), "N1234567890 = 1\n")
        self.assertNotIn("NNO602", r.codes)
