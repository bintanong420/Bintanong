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

    def test_isolated_manifest_is_written_with_lf_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pdfs"
            output = Path(directory) / "output"
            source.mkdir()
            (source / "a.pdf").write_bytes(b"%PDF-test")
            with patch.object(prospectus_batch.subprocess, "run", side_effect=OSError("no launch")):
                prospectus_batch.run_isolated(source, output, None)
            raw = (output / "isolated_manifest.json").read_bytes()
            self.assertNotIn(b"\r", raw)
            self.assertIn(b"\n", raw)
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

    def test_parser_hash_covers_every_package_module(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package / "a.py").write_text("A = 1\n", encoding="utf-8")
            (package / "b.py").write_text("B = 1\n", encoding="utf-8")
            before = prospectus_batch.package_sha256(package)
            self.assertEqual(before, prospectus_batch.package_sha256(package))
            (package / "b.py").write_text("B = 2\n", encoding="utf-8")
            self.assertNotEqual(before, prospectus_batch.package_sha256(package))

    def test_child_runs_the_package_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "pdfs"
            source.mkdir()
            (source / "a.pdf").write_bytes(b"%PDF-test")
            commands = []

            def fake_child(command, **_kwargs):
                commands.append(command)
                return SimpleNamespace(returncode=1)

            with patch.object(prospectus_batch.subprocess, "run", side_effect=fake_child):
                prospectus_batch.run_isolated(source, Path(directory) / "out", None)
            self.assertEqual(Path(commands[0][1]).name, "prospectus_extractor")
            self.assertTrue((Path(commands[0][1]) / "__main__.py").is_file())


if __name__ == "__main__":
    unittest.main()
