"""--skip-existing trusts a published set only when identity and audit status say so."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus_extractor import batch, pipeline
from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch

pytestmark = pytest.mark.usefixtures("fake_docling")


@pytest.fixture
def env(tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, snapshot):
    source = tmp_path / "pdfs"
    out = tmp_path / "out"
    pdf = pdf_factory(source)
    monkeypatch.setattr(batch, "ensure_docling_env", lambda: None)
    monkeypatch.setattr(batch, "get_shared_converter", lambda *a, **k: converter)
    # BatchConfig.write_md defaults to True; the stub payload is not renderable as markup.
    monkeypatch.setattr(pipeline, "render_prospectus_markup", lambda document, payload: "twin\n")

    def run(**overrides):
        config = BatchConfig(input_root=source, output_root=out, semantic_doc=None,
                             skip_existing=True, **overrides)
        return run_batch(config)

    return SimpleNamespace(pdf=pdf, out=out, converter=converter, state=pipeline_state,
                           run=run, snapshot=snapshot)


def only(summary):
    return summary["records"][0]


def test_repeat_run_of_unchanged_input_skips_and_leaves_identical_files(env):
    assert only(env.run())["status"] == "ok"
    before = env.snapshot(env.out)
    mtimes = {p.name: p.stat().st_mtime_ns for p in env.out.iterdir() if p.is_file()
              and p.name != "batch_manifest.json"}

    record = only(env.run())

    assert record["status"] == "skipped"
    assert "identical run identity" in record["reason"] or "unchanged" in record["reason"]
    assert env.snapshot(env.out) == before
    assert {p.name: p.stat().st_mtime_ns for p in env.out.iterdir() if p.is_file()
            and p.name != "batch_manifest.json"} == mtimes
    assert len(env.converter.calls) == 1
    assert env.state.builds == 1


def test_skip_existing_never_skips_a_failed_audit(env):
    env.state.status = "error"
    assert only(env.run())["status"] == "audit_error"
    second = only(env.run())
    assert second["status"] == "audit_error"
    assert env.state.builds == 2
    assert "previous audit status was error" in second["skip_check"]

    env.state.status = "ok"
    assert only(env.run())["status"] == "ok"
    assert env.state.builds == 3


def test_changed_pdf_bytes_are_not_skipped(env):
    env.run()
    env.pdf.write_bytes(b"%PDF-two")
    record = only(env.run())
    assert record["status"] == "ok"
    assert "changed" in record["skip_check"]
    assert env.state.builds == 2
    assert len(env.converter.calls) == 2


def test_changed_parser_is_not_skipped_but_reuses_the_cached_conversion(env, monkeypatch):
    env.run()
    monkeypatch.setattr(batch, "package_sha256", lambda: "f" * 64)
    record = only(env.run())
    assert record["status"] == "ok"
    assert env.state.builds == 2
    assert len(env.converter.calls) == 1  # D1: re-parse from the identity-matched JSON, no reconversion


def test_a_companion_requested_now_but_missing_from_the_last_run_is_not_skipped(env):
    env.run(write_csv=False)
    record = only(env.run())  # write_csv defaults to True
    assert record["status"] == "ok"
    assert "requested outputs not in last run" in record["skip_check"]


def test_a_half_published_set_is_not_skipped(env):
    env.run()
    (env.out / "a_prospectus.pl").unlink()
    record = only(env.run())
    assert record["status"] == "ok"
    assert "a_prospectus.pl is missing" in record["skip_check"]


def test_a_file_without_a_manifest_is_not_skipped(env):
    env.run()
    (env.out / "a_publish.json").unlink()
    record = only(env.run())
    assert record["status"] == "ok"
    assert record["skip_check"] == "no publish manifest"


def test_force_overrides_skip_existing_and_reconverts(env):
    env.run()
    record = only(env.run(force_reconvert=True))
    assert record["status"] == "ok"
    assert len(env.converter.calls) == 2


def test_error_record_points_at_the_diagnostics_and_keeps_earlier_files(env):
    env.run()
    before = env.snapshot(env.out)
    env.pdf.write_bytes(b"%PDF-two")
    env.converter.fail = True

    record = only(env.run())

    assert record["status"] == "error"
    assert record["error_type"] == "RuntimeError"
    assert record["failed_dir"].endswith("failed" + __import__("os").sep + "a")
    assert env.snapshot(env.out) == before


def test_scan_ignores_the_failed_diagnostics_folder(tmp_path):
    root = tmp_path / "in"
    (root / "failed" / "a").mkdir(parents=True)
    (root / "keep_docling.json").write_text("{}", encoding="utf-8")
    (root / "failed" / "a" / "a_docling.json").write_text("{}", encoding="utf-8")
    found = batch.scan_inputs(root, patterns=["*.json"])
    assert [p.name for p in found] == ["keep_docling.json"]


# --- Phase B markup twin (Task 1 note: a missing _prospectus.md must be regenerated)


def test_a_markup_twin_requested_now_but_missing_from_the_last_run_is_not_skipped(env):
    env.run(write_md=False)
    record = only(env.run())  # write_md defaults to True
    assert record["status"] == "ok"
    assert "requested outputs not in last run" in record["skip_check"]
    assert "a_prospectus.md" in record["skip_check"]
    assert (env.out / "a_prospectus.md").read_bytes() == b"twin\n"


def test_a_deleted_markup_twin_is_regenerated(env):
    env.run()
    (env.out / "a_prospectus.md").unlink()
    record = only(env.run())
    assert record["status"] == "ok"
    assert "a_prospectus.md is missing" in record["skip_check"]
    assert (env.out / "a_prospectus.md").is_file()


def test_batch_records_say_why_they_were_or_were_not_skipped(env):
    record = only(env.run())
    assert record["skip_check"] == "no publish manifest"
    assert record["publish_manifest"].endswith("a_publish.json")


# --- CLI: --force reconverts; otherwise an identity-matched cache is reused (D4)


def test_single_file_cli_reconverts_only_with_force(monkeypatch, tmp_path):
    from backend.bintanong_tools.prospectus_extractor import cli

    seen = []
    monkeypatch.setattr(cli, "process_prospectus", lambda *a, **k: seen.append(k) or {"audit": {"status": "ok"}})
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-one")
    assert cli.main(["-i", str(pdf)]) == 0
    assert cli.main(["-i", str(pdf), "--force"]) == 0
    assert [call["force_reconvert"] for call in seen] == [False, True]


def test_batch_manifest_schema_names_the_new_record_shape():
    from backend.bintanong_tools.prospectus_extractor import common

    assert common.MANIFEST_SCHEMA_VERSION == "palsu-prospectus-batch-manifest-v3.1"
