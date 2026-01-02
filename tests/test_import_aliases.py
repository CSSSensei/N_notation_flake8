from __future__ import annotations

import unittest

from nflake8.checks.tokens import run_token_checks


class TestImportAliases(unittest.TestCase):
    def test_import_non_n_module_requires_alias(self) -> None:
        v = run_token_checks(text="import math\n", filename="n1.py")
        self.assertIn("NNO301", [x.code for x in v])

    def test_import_n_module_does_not_require_alias(self) -> None:
        v = run_token_checks(text="import N1.N1_1.n1\n", filename="n1.py")
        self.assertNotIn("NNO301", [x.code for x in v])

    def test_from_import_non_n_name_requires_alias(self) -> None:
        v = run_token_checks(text="from math import sqrt\n", filename="n1.py")
        self.assertIn("NNO302", [x.code for x in v])

    def test_from_import_function_alias_must_be_n(self) -> None:
        bad = run_token_checks(text="from math import sqrt as N0000000001\n", filename="n1.py")
        self.assertIn("NNO303", [x.code for x in bad])

        ok = run_token_checks(text="from math import sqrt as n1234567890\n", filename="n1.py")
        self.assertNotIn("NNO302", [x.code for x in ok])
        self.assertNotIn("NNO303", [x.code for x in ok])

    def test_from_import_class_or_const_alias_must_be_N(self) -> None:
        bad = run_token_checks(text="from typing import List as n1234567890\n", filename="n1.py")
        self.assertIn("NNO303", [x.code for x in bad])

        ok = run_token_checks(text="from typing import List as N1234567890\n", filename="n1.py")
        self.assertNotIn("NNO302", [x.code for x in ok])
        self.assertNotIn("NNO303", [x.code for x in ok])

        ok_derived = run_token_checks(
            text="from typing import Any as N1234567890n0987654321\n",
            filename="n1.py",
        )
        self.assertNotIn("NNO303", [x.code for x in ok_derived])

    def test_from_import_n_name_does_not_require_alias(self) -> None:
        v = run_token_checks(text="from N1.N1_1.n1 import n1234567890\n", filename="n1.py")
        self.assertNotIn("NNO302", [x.code for x in v])
        self.assertNotIn("NNO303", [x.code for x in v])
