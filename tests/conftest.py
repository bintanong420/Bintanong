"""Shared fakes for the prospectus run tests: no real Docling, no real parse.

Pytest markers (for example the OCR branch's `gpu`) are registered in backend/pyproject.toml,
not here; this file only holds fixtures.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus_extractor import identity, loader, pipeline

RAW_BASE = {"texts": [{"text": "BS Test Program", "label": "text"}], "tables": []}


class FakeDoc:
    def __init__(self, raw):
        self.raw = raw

    @classmethod
    def model_validate(cls, raw):
        return cls(raw)

    def export_to_dict(self):
        return self.raw

    def export_to_markdown(self):
        return "BS Test Program"


class FakeConverter:
    """Stands in for a Docling converter; the raw JSON carries the PDF bytes so tests can see which bytes were converted."""

    def __init__(self, fail: bool = False):
        self.fail = fail
        self.calls: list[str] = []

    def convert(self, path):
        self.calls.append(str(path))
        if self.fail:
            raise RuntimeError("converter exploded")
        marker = Path(path).read_bytes().decode("latin-1")
        return SimpleNamespace(errors=[], document=FakeDoc({**RAW_BASE, "marker": marker}))


@pytest.fixture
def fake_docling(monkeypatch):
    def no_real_converter(*_args, **_kwargs):
        raise AssertionError("a real Docling converter was requested in a unit test")

    monkeypatch.setattr(loader, "ensure_docling_env", lambda: None)
    monkeypatch.setattr(loader, "load_docling", lambda: {"DoclingDocument": FakeDoc})
    monkeypatch.setattr(loader, "_docling_importable", lambda: True)
    monkeypatch.setattr(loader, "get_shared_converter", no_real_converter)
    monkeypatch.setattr(
        identity, "installed_versions",
        lambda: {"docling": "t1", "docling-core": "t1", "docling-parse": "t1"},
    )
    monkeypatch.delenv("PALSU_DOCLING_CELL_MATCHING", raising=False)


@pytest.fixture
def converter():
    return FakeConverter()


@pytest.fixture
def failing_converter():
    return FakeConverter(fail=True)


@pytest.fixture
def pipeline_state(monkeypatch):
    """Replaces parse and audit. `status`, `fail` and `builds` steer and observe it."""
    state = SimpleNamespace(status="ok", fail=None, builds=0)

    def build_payload(document, input_path, semantic_doc_path=None, raw_json_path=None,
                      repair_provider=None, **_phase_c_options):
        state.builds += 1
        if state.fail is not None:
            raise state.fail
        return {
            "schema_version": "stub",
            "nonce": state.builds,
            "program": "P",
            "degree": "D",
            "college": "C",
            "campus": "K",
            "source_file": Path(input_path).name,
            "source_path": str(Path(input_path).resolve()),
            "metadata": {},
            "courses": [],
            "prolog": {"clauses": [f"fact({state.builds})."]},
            "rag": {"semantic_chunks": [{"id": state.builds}], "hierarchical_chunks": []},
            "audit": {
                "status": state.status, "promotion_status": "x", "errors": [], "warnings": [],
                "total_courses": 0, "computed_total_units": 0, "declared_total_units": 0,
                "years_detected": [],
            },
        }

    monkeypatch.setattr(pipeline, "build_payload", build_payload)
    monkeypatch.setattr(
        pipeline, "build_essentials",
        lambda payload: {"nonce": payload["nonce"], "status": payload["audit"]["status"]},
    )
    return state


@pytest.fixture
def pdf_factory():
    def make(folder: Path, name: str = "a.pdf", body: bytes = b"%PDF-one") -> Path:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        path.write_bytes(body)
        return path

    return make


@pytest.fixture
def process():
    def run(pdf, out_dir, active_converter, **kwargs):
        kwargs.setdefault("quiet", True)
        return pipeline.process_prospectus(
            pdf, output_path=Path(out_dir) / "a_prospectus.json",
            export_pl=True, export_jsonl=True, export_csv=True,
            converter=active_converter, semantic_doc_path=None, **kwargs,
        )

    return run


@pytest.fixture
def snapshot():
    def take(folder: Path, exclude=("batch_manifest.json",)) -> dict[str, bytes]:
        return {
            path.name: path.read_bytes()
            for path in sorted(Path(folder).iterdir())
            if path.is_file() and path.name not in exclude
        }

    return take
