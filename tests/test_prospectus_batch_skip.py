"""--skip-existing trusts a published set only when identity and audit status say so."""

from __future__ import annotations

from datetime import datetime
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus import ProvisionalSource
from backend.bintanong_tools.prospectus_extractor import batch, identity, loader, pipeline, publish, tui
from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_HEADER, _cs_row, _cs_semester_row, _merged, fixture_document,
)

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
    assert record["reason"] == "unchanged: identical run identity"
    assert record["skip_check"] == "identical run identity"
    assert json.loads((env.out / "a_publish.json").read_bytes())["run_identity"]["skip_reusable"] is True
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
    assert record["skip_check"] == "--force given"
    assert len(env.converter.calls) == 2


class FalseySource(ProvisionalSource):
    def __bool__(self):
        return False


class FalseyProvider:
    def __bool__(self):
        return False

    def __call__(self, packet):
        return {"ambiguous": True}

    def __str__(self):
        raise AssertionError("provider must not be serialized")


@pytest.mark.parametrize("context", [
    "source", "falsey_source", "scope", "empty_scope", "empty_entries",
    "empty_generator", "generator", "provider", "falsey_provider",
])
def test_context_publication_cannot_be_reused_by_later_contextless_batch(
    tmp_path, monkeypatch, pdf_factory, converter, context,
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    document = fixture_document(
        [CS_HEADER, _merged("FIRST YEAR", 8), _cs_semester_row(),
         _cs_row(("CS 1", "Discrete Structures", "3", ""),
                 ("CS 2", "Discrete Structures 2", "3", "CS 1"))],
        [("title", "BACHELOR OF SCIENCE IN COMPUTER SCIENCE PROGRAM")],
    )
    monkeypatch.setattr(loader, "evidence_adapter", lambda *args: document)
    monkeypatch.setattr(loader, "get_shared_converter", lambda *a, **k: converter)
    contexts = {
        "source": {"source": ProvisionalSource(identity.file_sha256(pdf), "local/a.pdf")},
        "falsey_source": {"source": FalseySource(identity.file_sha256(pdf), "local/a.pdf")},
        "scope": {"approved_scope": {"program_name": "Computer Science"}},
        "empty_scope": {"approved_scope": {}},
        "empty_entries": {"review_entries": []},
        "empty_generator": {"review_entries": (entry for entry in [])},
        "generator": {"review_entries": (entry for entry in [{}])},
        "provider": {"repair_provider": lambda packet: {"ambiguous": True}},
        "falsey_provider": {"repair_provider": FalseyProvider()},
    }
    payload = pipeline.process_prospectus(
        pdf, output_path=out / "a_prospectus.json", semantic_doc_path=None,
        converter=converter, quiet=True, **contexts[context],
    )
    assert payload["audit"]["status"] in ("ok", "warn")
    assert payload["content_review"] == "pending"
    assert payload["source_verification"] == "pending"
    assert payload["authority"]["eligibility_executable"] is False
    if context == "generator":
        assert payload["authority"]["content_review_detail"]["entries"] == 1
    manifest = publish.read_manifest(out / "a_publish.json")
    assert publish.verify_published(out, manifest) == (True, "all files match")
    config = BatchConfig(input_root=pdf.parent, output_root=out, semantic_doc=None,
                         skip_existing=True, write_csv=False, write_pl=False,
                         write_jsonl=False, write_md=False)
    item = batch.build_batch_items([pdf], config)[0]
    assert batch.skip_check(item, config, identity.package_sha256()) == (
        False, "previous run used supplied context",
    )
    assert payload["run_identity"]["skip_reusable"] is False
    assert manifest["run_identity"]["skip_reusable"] is False
    assert payload["run_identity"]["run_key"] == identity.run_identity(pdf, None)["run_key"]
    record = only(run_batch(config))
    assert record["status"] in ("ok", "warn")
    assert record["skip_check"] == "previous run used supplied context"
    assert len(converter.calls) == 1  # reparsing may still reuse the verified conversion cache
    assert only(run_batch(config))["status"] == "skipped"


@pytest.mark.parametrize("value", ["missing", None, 0, 1, "true", "false", [], {}])
def test_missing_or_nonboolean_skip_eligibility_fails_closed(env, value):
    env.run()
    path = env.out / "a_publish.json"
    manifest = json.loads(path.read_bytes())
    run_id = manifest["run_identity"]
    if value == "missing":
        run_id.pop("skip_reusable", None)
    else:
        run_id["skip_reusable"] = value
    main_path = env.out / "a_prospectus.json"
    payload = json.loads(main_path.read_bytes())
    payload["run_identity"] = run_id
    main_path.write_bytes(json.dumps(payload).encode("utf-8"))
    manifest["files"][main_path.name] = identity.file_sha256(main_path)
    path.write_bytes(json.dumps(manifest).encode("utf-8"))
    assert publish.verify_published(env.out, manifest) == (True, "all files match")
    record = only(env.run())
    assert record["status"] == "ok"
    assert record["skip_check"] == "previous run skip eligibility is unknown"
    assert env.state.builds == 2


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


@pytest.mark.parametrize("force", [False, True])
def test_tui_configuration_changes_and_displays_force_setting(monkeypatch, capsys, force):
    app = tui.ProspectusTUI()
    app.config.force_reconvert = not force
    monkeypatch.setattr(tui, "RICH_AVAILABLE", False)
    monkeypatch.setattr(tui, "ask_text", lambda prompt, default="": default)
    monkeypatch.setattr(tui, "ask_yes_no", lambda prompt, default=True:
                        force if prompt.startswith("Force reconversion") else default)
    monkeypatch.setattr(app, "pause", lambda *args: None)

    app.configure()

    assert app.config.force_reconvert is force
    app.show_config()
    assert f"Force reconversion: {force}" in capsys.readouterr().out


@pytest.mark.parametrize("force", [False, True])
def test_tui_single_file_passes_force_to_actual_pipeline(env, monkeypatch, force):
    env.run()
    app = tui.ProspectusTUI()
    app.config.force_reconvert = force
    app.config.device = "cpu"
    app.config.semantic_doc = None
    app.config.write_pl = False
    app.config.write_jsonl = False
    calls, payloads, messages = [], [], []

    def process(path, **kwargs):
        calls.append((path, kwargs))
        payload = pipeline.process_prospectus(
            path, output_path=env.out / "a_prospectus.json", quiet=True, **kwargs,
        )
        payloads.append(payload)
        return payload

    monkeypatch.setattr(app, "_pick_file", lambda: env.pdf)
    monkeypatch.setattr(app, "pause", lambda message="": messages.append(message))
    monkeypatch.setattr(tui, "process_prospectus", process)

    app.single_file()

    assert calls == [(env.pdf, {
        "export_pl": False, "export_jsonl": False, "export_csv": True, "export_md": True,
        "device": "cpu", "semantic_doc_path": None, "force_reconvert": force,
    })]
    assert messages == ["Extracted 0 courses (OK)."]
    assert payloads[0]["run_identity"]["cache"] == ("converted" if force else "reused")
    assert len(env.converter.calls) == (2 if force else 1)
    assert env.state.builds == 2


@pytest.mark.parametrize("force", [False, True])
def test_tui_batch_force_takes_precedence_over_skip(env, monkeypatch, force):
    env.run()
    app = tui.ProspectusTUI()
    app.config = BatchConfig(input_root=env.pdf.parent, output_root=env.out, semantic_doc=None,
                             skip_existing=True, force_reconvert=force)
    app.last_scan = [env.pdf]
    monkeypatch.setattr(tui, "ask_yes_no", lambda *args, **kwargs: True)
    monkeypatch.setattr(app, "pause", lambda *args: None)

    app.run_batch_interactive()

    record = json.loads((env.out / "batch_manifest.json").read_bytes())["records"][0]
    assert record["status"] == ("ok" if force else "skipped")
    assert record["skip_check"] == ("--force given" if force else "identical run identity")
    assert len(env.converter.calls) == (2 if force else 1)
    assert env.state.builds == (2 if force else 1)


def test_batch_manifest_schema_names_the_new_record_shape():
    from backend.bintanong_tools.prospectus_extractor import common

    assert common.MANIFEST_SCHEMA_VERSION == "palsu-prospectus-batch-manifest-v3.1"


def test_batch_manifest_writes_utf8_lf_without_changing_content(tmp_path):
    records = [{"status": status, "program": "Sining at kultura – ñ"}
               for status in ("ok", "warn", "audit_error", "skipped", "error")]
    before = datetime.now().replace(microsecond=0)

    path = batch.write_manifest(records, tmp_path / "out")

    raw = path.read_bytes()
    assert b"\n" in raw and b"\r" not in raw
    assert "Sining at kultura – ñ".encode("utf-8") in raw
    payload = json.loads(raw)
    assert path == tmp_path / "out" / "batch_manifest.json"
    assert set(payload) == {"schema_version", "generated_at", "summary", "records"}
    assert payload["schema_version"] == "palsu-prospectus-batch-manifest-v3.1"
    assert before <= datetime.fromisoformat(payload["generated_at"]) <= datetime.now()
    assert payload["summary"] == {
        "total": 5, "ok": 1, "warn": 1, "audit_failed": 1, "skipped": 1, "failed": 1,
    }
    assert payload["records"] == records


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


@pytest.mark.parametrize("recursive", [False, True])
@pytest.mark.parametrize("pattern", ["../*.pdf", "nested/../../*.pdf", r"..\*.pdf",
                                      r"nested\..\..\*.pdf", "/outside/*.pdf",
                                      r"\outside\*.pdf", "C:*.pdf", "C:/outside/*.pdf",
                                      r"\\server\share\*.pdf"])
def test_scan_rejects_patterns_that_can_leave_the_selected_root(tmp_path, recursive, pattern):
    root = tmp_path / "inputs"
    (root / "nested").mkdir(parents=True)
    (tmp_path / "course.pdf").write_bytes(b"%PDF-outside")
    for above_root_marker in [False, True]:
        if above_root_marker:
            (tmp_path / "failure.json").write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError, match="Input pattern must stay within input root"):
            batch.scan_inputs(root, recursive=recursive, patterns=[pattern])


@pytest.mark.parametrize("recursive", [False, True])
@pytest.mark.parametrize("pattern", ["nested/*.pdf", "n*/*.pdf", "**/*.pdf"])
def test_scan_preserves_valid_relative_globs(tmp_path, recursive, pattern):
    root = tmp_path / "inputs"
    (root / "nested").mkdir(parents=True)
    keep = root / "nested" / "course.pdf"
    keep.write_bytes(b"%PDF-input")
    assert batch.scan_inputs(root, recursive=recursive, patterns=[pattern]) == [keep]
