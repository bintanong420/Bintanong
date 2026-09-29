from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.bintanong_tools import prospectus_batch


class IsolatedBatchTests(unittest.TestCase):
    def test_child_crash_keeps_prior_result_and_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pdfs"
            output = Path(directory) / "output"
            source.mkdir()
            for name in ("a.pdf", "b.pdf"):
                (source / name).write_bytes(b"%PDF-test")
            seen = []

            def fake_child(command, **_kwargs):
                pdf = Path(command[command.index("-i") + 1])
                candidate = Path(command[command.index("-o") + 1])
                seen.append(pdf.name)
                if pdf.name == "b.pdf":
                    checkpoint = json.loads((output / "isolated_manifest.json").read_text())
                    self.assertEqual(checkpoint["summary"]["completed"], 1)
                    return SimpleNamespace(returncode=-1073741819)
                candidate.write_text(json.dumps({"source_path": str(pdf), "courses": [],
                    "audit": {"status": "warn", "computed_total_units": 0}}))
                return SimpleNamespace(returncode=0)

            with patch.object(prospectus_batch.subprocess, "run", side_effect=fake_child):
                manifest = prospectus_batch.run_isolated(source, output, None)
            self.assertEqual(seen, ["a.pdf", "b.pdf"])
            self.assertEqual(manifest["summary"], {
                "total_expected": 2, "completed": 2, "ok": 0, "warn": 1,
                "audit_error": 0, "processing_error": 1,
            })
            self.assertEqual(manifest["records"][1]["strict_exit_code"], -1073741819)
            self.assertEqual(manifest["records"][1]["status"], "processing_error")
            self.assertTrue((output / "isolated_manifest.json").is_file())

    def test_child_launch_error_does_not_stop_later_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pdfs"
            output = Path(directory) / "output"
            source.mkdir()
            for name in ("a.pdf", "b.pdf"):
                (source / name).write_bytes(b"%PDF-test")
            seen = []

            def fake_child(command, **_kwargs):
                pdf = Path(command[command.index("-i") + 1])
                seen.append(pdf.name)
                if pdf.name == "a.pdf":
                    raise OSError("launch failed")
                candidate = Path(command[command.index("-o") + 1])
                candidate.write_text(json.dumps({"source_path": str(pdf), "courses": [],
                    "audit": {"status": "warn", "computed_total_units": 0}}))
                return SimpleNamespace(returncode=0)

            with patch.object(prospectus_batch.subprocess, "run", side_effect=fake_child):
                manifest = prospectus_batch.run_isolated(source, output, None)
            self.assertEqual(seen, ["a.pdf", "b.pdf"])
            self.assertEqual(manifest["summary"]["processing_error"], 1)
            self.assertEqual(manifest["summary"]["warn"], 1)
            self.assertIn("launch failed", manifest["records"][0]["error"])

    def test_existing_run_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pdfs"
            output = Path(directory) / "output"
            source.mkdir()
            output.mkdir()
            (source / "a.pdf").write_bytes(b"%PDF-test")
            checkpoint = output / "isolated_manifest.json"
            checkpoint.write_text("existing run")
            with patch.object(prospectus_batch.subprocess, "run") as child:
                with self.assertRaises(FileExistsError):
                    prospectus_batch.run_isolated(source, output, None)
            child.assert_not_called()
            self.assertEqual(checkpoint.read_text(), "existing run")


if __name__ == "__main__":
    unittest.main()
