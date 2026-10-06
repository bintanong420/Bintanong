"""--skip-existing trusts a published set only when identity and audit status say so."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus_extractor import batch, loader, pipeline
from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch

pytestmark = pytest.mark.usefixtures("fake_docling")


@pytest.fixture
def env(tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, snapshot):
    source = tmp_path / "pdfs"
    out = tmp_path / "out"
    pdf = pdf_factory(source)
    monkeypatch.setattr(loader, "get_shared_converter", lambda *a, **k: converter)
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
    (root / "failed" / "a" / "failure.json").write_text("{}", encoding="utf-8")
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


@pytest.mark.parametrize("name", ["a_docling.json", "a_docling.meta.json"])
@pytest.mark.parametrize("deleted", [False, True])
def test_changed_or_missing_cache_refuses_skip(env, name, deleted):
    env.run()
    path = env.out / name
    if deleted:
        path.unlink()
    else:
        path.write_bytes(b"{}")
    record = only(env.run())
    assert record["status"] == "ok"
    assert record["skip_check"] == (f"{name} is missing" if deleted
                                     else f"{name} changed since it was published")
    assert len(env.converter.calls) == 2


def test_old_v1_manifest_refuses_skip(env):
    import json
    env.run()
    path = env.out / "a_publish.json"
    old = json.loads(path.read_bytes())
    old["schema"] = "palsu-prospectus-publish-v1"
    path.write_text(json.dumps(old), encoding="utf-8")
    record = only(env.run())
    assert record["status"] == "ok"
    assert record["skip_check"] == "no publish manifest"
    assert env.state.builds == 2


@pytest.mark.parametrize("ancestor", ["failed", "FAILED", ".venv", "node_modules"])
def test_scan_keeps_inputs_below_ignored_looking_absolute_ancestors(tmp_path, ancestor):
    root = tmp_path / ancestor / "inputs"
    root.mkdir(parents=True)
    pdf = root / "failed.pdf"
    pdf.write_bytes(b"%PDF-input")
    assert batch.scan_inputs(root) == [pdf]
    assert batch.scan_pdfs(root) == [pdf]


@pytest.mark.parametrize("recursive", [False, True])
def test_scan_keeps_failed_inputs_and_honors_requested_patterns(tmp_path, recursive):
    root = tmp_path / "inputs"
    legitimate = root / "courses" / "failed"
    legitimate.mkdir(parents=True)
    for relative in ["failed.pdf", "keep_docling.json", "courses/failed/course.pdf",
                     "courses/failed/course_docling.json"]:
        (root / relative).write_bytes(b"input")
    # A filename that matches an ignored directory name is still a requested input.
    (root / ".git").write_bytes(b"input")
    assert [p.relative_to(root).as_posix() for p in batch.scan_inputs(root, recursive)] == (
        ["courses/failed/course.pdf", "failed.pdf"] if recursive else ["failed.pdf"]
    )
    assert [p.relative_to(root).as_posix() for p in batch.scan_inputs(
        root, recursive, patterns=["*.json", ".git", "*.json"]
    )] == ([".git", "courses/failed/course_docling.json", "keep_docling.json"]
          if recursive else [".git", "keep_docling.json"])


@pytest.mark.parametrize("failed_name", ["failed", "FAILED"])
def test_scan_excludes_only_marked_failure_runs_and_their_descendants(tmp_path, failed_name):
    root = tmp_path / "inputs"
    diagnostic = root / "results" / failed_name / "diagnosed"
    sibling = diagnostic.parent / "legitimate"
    (diagnostic / "nested").mkdir(parents=True)
    sibling.mkdir()
    (diagnostic / "failure.json").write_text("{}", encoding="utf-8")
    for folder in [diagnostic, diagnostic / "nested", sibling]:
        (folder / "course.pdf").write_bytes(b"%PDF-input")
        (folder / "course_docling.json").write_text("{}", encoding="utf-8")
    (diagnostic.parent / "direct.pdf").write_bytes(b"%PDF-input")
    (diagnostic.parent / "direct_docling.json").write_text("{}", encoding="utf-8")
    assert batch.scan_inputs(root) == [diagnostic.parent / "direct.pdf", sibling / "course.pdf"]
    assert batch.scan_inputs(root, patterns=["*.json"]) == [
        diagnostic.parent / "direct_docling.json", sibling / "course_docling.json"]
    assert batch.scan_inputs(root, recursive=False, patterns=["*.pdf", "*.json"]) == []


@pytest.mark.parametrize("ignored", ["palsu_jsonified_output", "docling_jsonified_output",
                                      ".venv", ".docling-venv", "__pycache__", ".git", "node_modules"])
def test_scan_still_ignores_standard_root_relative_directories(tmp_path, ignored):
    root = tmp_path / "inputs"
    (root / "courses" / ignored / "nested").mkdir(parents=True)
    keep = root / "keep.pdf"
    keep.write_bytes(b"%PDF-input")
    (root / "courses" / ignored / "nested" / "drop.pdf").write_bytes(b"%PDF-input")
    assert batch.scan_inputs(root) == [keep]


@pytest.mark.parametrize("selected", ["failed", "failed/diagnosed", "archive"])
def test_scan_honors_diagnostic_markers_within_the_selected_root(tmp_path, selected):
    output = tmp_path / "output"
    diagnostic = output / "failed" / "diagnosed"
    sibling = output / "failed" / "legitimate"
    archive = output / "archive"
    for folder in [diagnostic / "nested", sibling, archive / "nested"]:
        folder.mkdir(parents=True)
        (folder / "course.pdf").write_bytes(b"%PDF-input")
        (folder / "course_docling.json").write_text("{}", encoding="utf-8")
    (diagnostic / "failure.json").write_text("{}", encoding="utf-8")
    (archive / "failure.json").write_text("{}", encoding="utf-8")
    # Above-root markers must not classify the selected legitimate tree as diagnostics.
    (output / "failure.json").write_text("{}", encoding="utf-8")
    root = output / selected
    expected = [sibling / "course.pdf", sibling / "course_docling.json"] if selected == "failed" else []
    assert batch.scan_inputs(root, patterns=["*.pdf", "*.json"]) == sorted(expected)
    assert batch.scan_inputs(sibling, patterns=["*.pdf", "*.json"]) == [
        sibling / "course.pdf", sibling / "course_docling.json"]
    assert batch.scan_inputs(root, recursive=False, patterns=["*.pdf", "*.json"]) == []
