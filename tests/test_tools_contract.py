from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

# We expect this import to fail in Step 2 before implementation
from backend.bintanong_tools.ingest import parse_document


ROOT = Path(__file__).parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "synthetic_academic_guide.pdf"


class ToolsContractTests(unittest.TestCase):
    def test_ingest_cli_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "backend.bintanong_tools.ingest", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ingest", result.stdout.lower())

    def test_evaluate_cli_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "backend.bintanong_tools.evaluate", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("evaluate", result.stdout.lower())

    def test_synthetic_pdf_fixture_exists_and_parses(self) -> None:
        self.assertTrue(FIXTURE_PATH.is_file(), f"Missing fixture {FIXTURE_PATH}")
        header = FIXTURE_PATH.read_bytes()[:5]
        self.assertEqual(header, b"%PDF-", "Fixture is not a valid PDF file")

        # Exercise parse_document
        result = parse_document(FIXTURE_PATH)
        self.assertIn("title", result)
        self.assertIn("text", result)
        self.assertIn("PalSU", result["text"])


if __name__ == "__main__":
    unittest.main()
