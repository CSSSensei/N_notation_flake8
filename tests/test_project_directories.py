from __future__ import annotations

import os
import tempfile
import unittest

from nflake8.checks.project import run_project_checks
from nflake8.core.patterns import README_DECLARATION_BLOCK


class TestProjectDirectories(unittest.TestCase):
    def test_reports_nno420_for_non_n_directory_in_parent_chain(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "pyproject.toml"), "w", encoding="utf-8") as f:
                f.write("[project]\nname='x'\nversion='0.0.0'\n")

            bad_dir = os.path.join(root, "nflake8", "testdata")
            os.makedirs(bad_dir, exist_ok=True)

            file_path = os.path.join(bad_dir, "n1.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")

            violations = run_project_checks(filename=file_path)
            codes = [v.code for v in violations]
            self.assertIn("NNO420", codes)

    def test_allows_only_n_directories_in_parent_chain(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "pyproject.toml"), "w", encoding="utf-8") as f:
                f.write("[project]\nname='x'\nversion='0.0.0'\n")
            with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
                f.write(README_DECLARATION_BLOCK)

            good_dir = os.path.join(root, "N1", "N1_2")
            os.makedirs(good_dir, exist_ok=True)

            file_path = os.path.join(good_dir, "n1.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")

            violations = run_project_checks(filename=file_path)
            codes = [v.code for v in violations]

            self.assertNotIn("NNO420", codes)
            self.assertNotIn("NNO500", codes)
            self.assertNotIn("NNO401", codes)


if __name__ == "__main__":
    unittest.main()
