from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from backend.bintanong_tools.prospectus import ProvisionalSource


class ProvisionalSourceTests(unittest.TestCase):
    def test_verifies_exact_pdf_bytes_and_stays_pending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "prospectus.pdf"
            original = b"%PDF-1.4\noriginal"
            pdf.write_bytes(original)
            source = ProvisionalSource(hashlib.sha256(original).hexdigest(), "local/prospectus.pdf")

            self.assertEqual(source.source_verification, "pending")
            with self.assertRaises(TypeError):
                ProvisionalSource(source.pdf_sha256, source.source_locator, source_verification="approved")
            self.assertIsNone(source.verify_pdf(pdf))

            pdf.write_bytes(b"%PDF-1.4\nchanged")
            with self.assertRaises(ValueError):
                source.verify_pdf(pdf)


if __name__ == "__main__":
    unittest.main()
