"""Phase 1 Task 3, group 1: shared base, versioning and the single closed-vocabulary source.

Everything here is synthetic. Nothing approves a source, an edition or a curriculum.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import ClassVar

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base

ROOT = Path(__file__).resolve().parents[1]
VOCAB_FILE = ROOT / "knowledge" / "manifests" / "governance-vocabulary.json"
PACKAGE = ROOT / "backend" / "bintanong_contracts"


class Sample(base.Contract):
    SCHEMA_VERSION: ClassVar[str] = "bintanong-sample-v1"
    name: str
    items: tuple[str, ...] = ()


def sample(**over):
    return {"schema_version": "bintanong-sample-v1", "name": "n", "items": ["b", "a"], **over}


def test_vocabulary_is_loaded_from_the_manifest_file():
    assert base.VOCAB == json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    assert base.VOCAB_PATH == VOCAB_FILE


def test_vocabulary_version_is_pinned():
    assert base.VOCAB["vocabulary_version"] == "bintanong-governance-vocabulary-v1"


def test_member_accepts_exactly_the_vocabulary_values():
    class M(base.Contract):
        SCHEMA_VERSION: ClassVar[str] = "bintanong-m-v1"
        state: base.State("acquisition_state")

    for good in base.VOCAB["states"]["acquisition_state"]:
        assert M.parse({"schema_version": "bintanong-m-v1", "state": good}).state == good
    for bad in ["bogus", "approved", "Verified", ""]:
        with pytest.raises(ValidationError):
            M.parse({"schema_version": "bintanong-m-v1", "state": bad})


def test_no_literal_copy_of_a_vocabulary_value_in_the_package():
    """A Literal[...] of governance words would drift from the JSON; the package must load them."""
    words = set()
    for group in base.VOCAB["states"].values():
        words |= set(group)
    words |= set(base.VOCAB["decision"]["outcomes"]) | set(base.VOCAB["roles"])
    words |= set(base.VOCAB["evidence_kinds"]["authorizing"]) | set(base.VOCAB["evidence_kinds"]["non_authorizing"])
    words -= {"user", "system", "pending", "observed", "verified", "partial", "absent", "resolved", "error"}
    offenders = []
    for path in PACKAGE.glob("*.py"):
        for literal in re.findall(r"Literal\[([^\]]*)\]", path.read_text(encoding="utf-8")):
            offenders += [(path.name, w) for w in words if f'"{w}"' in literal]
    assert offenders == []


def test_schema_version_is_required_exact_and_unknown_versions_are_rejected():
    assert Sample.parse(sample()).name == "n"
    bad = sample()
    del bad["schema_version"]
    for payload in (bad, sample(schema_version="bintanong-sample-v2"), sample(schema_version="")):
        with pytest.raises(ValidationError):
            Sample.parse(payload)


def test_unknown_fields_are_rejected_including_privileged_status_words():
    for field in ("approved", "verified", "promotion_status", "approval_id", "extra"):
        with pytest.raises(ValidationError):
            Sample.parse(sample(**{field: True}))


def test_instances_are_immutable_evidence():
    s = Sample.parse(sample())
    with pytest.raises(ValidationError):
        s.name = "other"
    assert isinstance(s.items, tuple)


def test_strict_types_do_not_coerce():
    for bad in (sample(name=1), sample(name=None), sample(items="ab")):
        with pytest.raises(ValidationError):
            Sample.parse(bad)


def test_canonical_json_is_sorted_lf_and_roundtrips_equal():
    s = Sample.parse(sample())
    text = base.canonical_json(s)
    assert text.endswith("\n") and "\r" not in text
    assert list(json.loads(text)) == sorted(json.loads(text))
    assert text == base.canonical_json(Sample.parse(sample()))
    assert Sample.parse(text) == s
    assert base.canonical_json(Sample.parse(text)) == text


def test_parse_rejects_non_json_text_and_wrong_shapes():
    for bad in ("not json", "[]", "null", 5, None):
        with pytest.raises((ValidationError, base.ContractError)):
            Sample.parse(bad)


def test_namespace_of_separates_institutional_and_private_ids():
    assert base.namespace_of("ver-synth-1") == "institutional"
    assert base.namespace_of("doc-x") == "institutional"
    assert base.namespace_of("fact-1") == "private_session"
    assert base.namespace_of("sess-9") == "private_session"
    assert base.namespace_of("chunk-1") is None
    assert base.namespace_of("") is None


def test_require_namespace_refuses_a_private_id_in_an_institutional_slot():
    base.require_namespace("ver-a", "institutional")
    for bad in ("fact-a", "sess-a", "plain"):
        with pytest.raises(base.ContractError):
            base.require_namespace(bad, "institutional")
    with pytest.raises(base.ContractError):
        base.require_namespace("ver-a", "private_session")
