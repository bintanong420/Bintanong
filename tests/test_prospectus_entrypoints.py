"""The extractor must start the same way from every supported entry point."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "backend" / "bintanong_tools"
SHIM = TOOLS / "bintanong_jsonifer_prolog" / "bintanong_prospectus_jsonifier.py"

ENTRY_POINTS = {
    "module": ["-m", "backend.bintanong_tools.prospectus_extractor"],
    "package directory": [str(TOOLS / "prospectus_extractor")],
    "legacy shim": [str(SHIM)],
}


@pytest.mark.parametrize("entry", ENTRY_POINTS.values(), ids=ENTRY_POINTS.keys())
def test_self_test_passes_from_every_entry_point(entry):
    done = subprocess.run([sys.executable, *entry, "--self-test"], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    assert "80/80" in done.stdout


def test_shim_reexports_private_names_used_by_existing_tests():
    from backend.bintanong_tools import prospectus_extractor
    from backend.bintanong_tools.bintanong_jsonifer_prolog import bintanong_prospectus_jsonifier as shim

    for name in ("_row_field_candidates", "_two_course_codes_in_cell", "build_audit", "ColumnGroup",
                 "docling_to_normalized_table", "evidence_from_grids", "parse_curriculum_evidence",
                 "BatchConfig", "build_batch_items", "scan_inputs", "LoadedDocument", "main"):
        assert hasattr(shim, name), name
    assert shim.parse_curriculum_evidence is prospectus_extractor.parse_curriculum_evidence


def test_relaunch_reuses_the_original_command_line(monkeypatch):
    from backend.bintanong_tools.prospectus_extractor import docling_env

    calls = []
    monkeypatch.delenv("_PALSU_RELAUNCHED", raising=False)
    monkeypatch.setattr(docling_env, "_docling_importable", lambda: False)
    monkeypatch.setattr(docling_env, "_venv_python", lambda: Path("venv-python"))
    monkeypatch.setattr(docling_env.sys, "orig_argv", ["python", "-m", "pkg", "-i", "x.pdf"])
    monkeypatch.setattr(docling_env.subprocess, "call", lambda cmd, env: calls.append((cmd, env)) or 0)
    with pytest.raises(SystemExit):
        docling_env.ensure_docling_env()
    assert calls[0][0] == ["venv-python", "-m", "pkg", "-i", "x.pdf"]
    assert calls[0][1]["_PALSU_RELAUNCHED"] == "1"
