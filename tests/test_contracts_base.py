"""Shared contract primitives: versions, timestamps, identifiers and namespace isolation.

Everything here is synthetic. Nothing approves a source, an edition or a curriculum."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import ClassVar

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base
from backend.bintanong_contracts import governance as gov


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
        with pytest.raises(ValidationError, match='is not a acquisition_state in the governance vocabulary'):
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
        with pytest.raises(ValidationError, match='schema_version'):
            Sample.parse(payload)


def test_unknown_fields_are_rejected_including_privileged_status_words():
    for field in ("approved", "verified", "promotion_status", "approval_id", "extra"):
        with pytest.raises(ValidationError, match='Extra inputs are not permitted'):
            Sample.parse(sample(**{field: True}))


def test_instances_are_immutable_evidence():
    s = Sample.parse(sample())
    with pytest.raises(ValidationError, match='Instance is frozen'):
        s.name = "other"
    assert isinstance(s.items, tuple)


def test_strict_types_do_not_coerce():
    for bad in (sample(name=1), sample(name=None), sample(items="ab")):
        with pytest.raises(ValidationError, match='Input should be a valid'):
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
        with pytest.raises((ValidationError, base.ContractError), match='Invalid JSON|valid|object|not JSON-compatible|cannot parse'):
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
        with pytest.raises(base.ContractError, match="required 'institutional"):
            base.require_namespace(bad, "institutional")
    with pytest.raises(base.ContractError, match="id 'ver\\-a' is in namespace 'institutional', required 'privat"):
        base.require_namespace("ver-a", "private_session")


# Private identifiers and Unicode confusables



PRIVATE = "institutional"      # scanning an institutional record for private ids

SESSION = "private_session"    # scanning a private record for institutional ids

@pytest.mark.parametrize("text", [
    "\u0455ess-synth-0001",              # Cyrillic dze, which prints as s
    "fa\u0441t-synth-0001",              # Cyrillic es inside
    "fact\u200b-synth-0001",             # zero-width space
    "fact\u200d-synth-0001",             # zero-width joiner
    "fa\u00adct-synth-0001",             # soft hyphen
    "fact-\u2060synth-0001",             # word joiner
    "\ufefffact-synth-0001",             # byte order mark
    "fact%2dsynth-0001", "fact%2Dsynth-0001", "fact%252dsynth-0001", "see%20fact-synth-0001",
    "%66act-synth-0001",                 # %66 is f
    "s\u0435ss-synth-0001",              # Cyrillic ie
    "sess-synth-0001\u200b",
])
def test_a_private_id_cannot_hide_from_the_scan(text):
    assert base.foreign_ids({"v": text}, PRIVATE), text

@pytest.mark.parametrize("text", [
    "d\u03bfc-synth-handbook",           # Greek omicron
    "\u03bdersion-synth-1".replace("\u03bdersion", "\u03bder"),      # Greek nu: 'ver'
    "\u0435dition-synth-1",              # Cyrillic ie
    "\u0441\u043enflict-synth-0001",     # Cyrillic es and o
    "doc\u200d-synth-handbook", "ver-\u2060synth-1", "ver%2dsynth-1", "edition%2Dsynth-1", "conflict\u00ad-synth-1",
])
def test_an_institutional_id_cannot_hide_inside_a_private_record(text):
    assert base.foreign_ids({"v": text}, SESSION), text

@pytest.mark.parametrize("text", [
    "Fact-checking Office of Records", "edition-specific wording", "50% off", "100%", "Fact%20sheet", "%zz-fact",
    "\u041f\u0440\u0438\u0432\u0435\u0442 \u043c\u0438\u0440", "\u03a0\u03b1\u03c1\u03ac\u03b4\u03b5\u03b9\u03b3\u03bc\u03b1", "caf\u00e9 society",
    "xfact-synth-0001", "verification", "sess", "zero\u200bwidth words", "doc",
])
def test_ordinary_text_is_still_not_an_id(text):
    assert base.foreign_ids({"v": text}, PRIVATE) == []
    assert base.foreign_ids({"v": text}, SESSION) == []

def test_a_cyrillic_es_prints_as_c_not_s():
    # "\u0441ess" reads "cess", which is not a private prefix; only the look-alike of the real prefix letter counts
    assert base.foreign_ids({"v": "\u0441ess-synth-0001"}, PRIVATE) == []

def test_the_keys_of_a_mapping_are_scanned_too():
    assert base.foreign_ids({"fact-synth-0001": "x"}, PRIVATE)
    assert base.foreign_ids({"a": {"sess-synth-0001": [1]}}, PRIVATE)
    assert base.foreign_ids({"ver-synth-1": "x"}, SESSION)

def test_strip_format_removes_only_format_characters():
    assert base.strip_format("a\u200bb\u00adc\u200dd\ufeffe") == "abcde"
    assert base.strip_format("caf\u00e9 \u0441") == "caf\u00e9 \u0441"
    assert base.strip_format("") == ""

# ---------------------------------------------------------------- known false positives (owner decision)
def test_known_false_positives_are_pinned_not_hidden():
    # An institutional file name or hyphenated phrase that reads like an id of the other namespace is flagged.
    # A safe tightening does not exist (see the decision record), so the scan stays strict.
    assert base.foreign_ids({"v": "Fact-Sheet-2024.pdf"}, PRIVATE) == ["fact-sheet-2024"]
    assert base.foreign_ids({"v": "BS-Fact-1"}, PRIVATE) == ["fact-1"]
    assert base.foreign_ids({"v": "doc-to-doc review"}, SESSION) == ["doc-to-doc"]
    assert base.foreign_ids({"v": "Conflict-free-zone"}, SESSION) == ["conflict-free-zone"]

# the closed look-alike map, written out by hand so that a removed or changed entry is noticed
CONFUSABLES = {
    "\u0430": "a", "\u0441": "c", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0455": "s", "\u0456": "i",
    "\u0501": "d", "\u0445": "x", "\u0475": "v", "\u0442": "t", "\u0433": "r", "\u043f": "n",
    "\u03b1": "a", "\u03b5": "e", "\u03bf": "o", "\u03c1": "p", "\u03b9": "i", "\u03bd": "v", "\u03c4": "t",
    "\u03c7": "x", "\u03b7": "n", "\u0131": "i", "\u0251": "a", "\u0192": "f"}

def test_the_look_alike_map_is_exactly_the_reviewed_one():
    assert {chr(k): v for k, v in base._CONFUSABLES.items()} == CONFUSABLES
    assert set(CONFUSABLES.values()) == set("acepsidxvtrnfo")

@pytest.mark.parametrize("char,letter", list(CONFUSABLES.items()))
def test_each_look_alike_reads_as_its_latin_letter(char, letter):
    assert base.scan_form(char) == letter

def test_scan_form_decodes_up_to_three_layers_and_no_more():
    assert base.scan_form("%2566") == "f"                    # %25 -> % -> %66 -> f
    assert base.scan_form("%252566") == "f"
    assert base.scan_form("%25252566") == "%66"             # a fourth layer is left alone
    assert base.scan_form("100%") == "100%"

def test_every_look_alike_survives_folding_so_it_can_fire():
    # the map is applied after NFKC and casefold; a key those would change (final sigma) could never match
    assert all(base.folded(chr(k)) == chr(k) for k in base._CONFUSABLES)


# Contract decision documentation



RECORD = (Path(__file__).resolve().parents[1] / "docs" / "decisions" / "phase-01-contracts.md").read_text(encoding="utf-8")

@pytest.mark.parametrize("text", ["Fact-Sheet-2024.pdf", "BS-Fact-1", "doc-to-doc", "Conflict-free-zone"])
def test_the_known_false_positives_of_the_scan_are_listed(text):
    assert text in RECORD

def test_the_raw_text_limit_of_the_table_serialization_hash_is_listed():
    assert "raw text" in RECORD and "content_hash_mismatch" in RECORD

@pytest.mark.parametrize("text", ["prolog_quote", "rendering must quote", "FrozenDict", "model_copy", "owner decision 22"])
def test_the_new_owner_decisions_and_design_change_are_recorded(text):
    assert text.lower() in RECORD.lower()

def test_the_authorization_date_wording_covers_all_relied_evidence():
    assert "ANY evidence the approved or revoked state relies on" in RECORD
    assert "must not be dated before the acquisition or scope evidence it relies on" not in RECORD

def test_the_record_no_longer_claims_a_value_cannot_carry_prolog():
    assert "cannot carry Prolog syntax" not in RECORD


# Mutation regressions: vocabulary and bounds



VOC = base.VOCAB

# ---------------------------------------------------------------- vocabulary pins (kill vocabulary-file drift)
def test_namespace_prefixes_are_pinned():
    assert VOC["namespaces"] == {
        "institutional": {"id_prefixes": ["doc-", "ver-", "edition-", "conflict-"], "lifecycles": ["register"]},
        "private_session": {"id_prefixes": ["sess-", "fact-"], "lifecycles": ["session_only"]}}

def test_scope_fields_origins_and_runtime_lists_are_pinned():
    assert VOC["scope_fields"] == ["issuer", "campus", "college", "program", "cohort", "printed_revision",
                                   "effective_from", "effective_to"]
    assert VOC["session_origins"] == ["user_statement", "private_upload"]
    assert VOC["runtime"]["routes"] == ["RAG", "Hybrid", "Symbolic"]
    assert VOC["runtime"]["controls"] == ["clarify", "greeting", "unsupported_scope", "evidence_unavailable"]
    assert VOC["supersession_relations"] == ["none", "supersedes", "superseded_by"]
    assert VOC["document_categories"] == ["source_document", "curriculum_proposal_candidate"]
    assert VOC["proposal_categories"] == ["curriculum_proposal_candidate"]
    assert VOC["field_bases"]["allowed"] == ["printed_text", "issuing_office_statement", "reviewer_reading"]
    assert VOC["conflict_resolution_bases"] == ["supersession_evidenced", "scope_distinction_evidenced", "source_owner_ruling"]

def test_the_id_patterns_are_derived_from_the_vocabulary_prefixes():
    assert gov.ID_DOC == base.id_pattern("doc-") and gov.ID_CONFLICT == base.id_pattern("conflict-")
    assert gov.ID_FACT == base.id_pattern("fact-") and gov.ID_SESSION == base.id_pattern("sess-")
    with pytest.raises(KeyError, match="chunk\\-' is not an id prefix in the governance vocabulary"):
        base.id_pattern("chunk-")

def test_a_pinned_revision_is_a_full_commit_or_digest_whatever_the_old_denylist_said():
    assert base.is_pinned_revision("a" * 40) and base.is_pinned_revision("a" * 64)
    for text in ("master", "main", "a" * 39, "a" * 41, "a" * 63, "A" * 40, "g" * 40, " " + "a" * 40, "a" * 40 + "\n"):
        assert not base.is_pinned_revision(text), text


# Mutation regressions: field and relationship guards



def test_the_year_window_of_a_timestamp_is_inclusive_at_both_ends():
    assert base.parse_timestamp("2000-01-01T00:00:00Z") is not None
    assert base.parse_timestamp("2100-12-31T23:59:59Z") is not None
    assert base.parse_timestamp("1999-12-31T23:59:59Z") is None
    assert base.parse_timestamp("2101-01-01T00:00:00Z") is None
    assert base.parse_timestamp("2026-01-01T00:00:00") is None        # a naive time has no zone

def test_a_mapping_that_is_not_json_is_a_contract_error():
    for broken in (float("nan"), float("inf"), object()):
        with pytest.raises(base.ContractError, match="not JSON-compatible"):
            Sample.parse(sample(name=broken))


# Mutation regressions: dates, identifiers and language markers




# 3. base.id_pattern: body '+' became '*'
@pytest.mark.parametrize("prefix", ["doc-", "ver-", "edition-", "conflict-", "fact-", "sess-"])
def test_an_id_needs_a_body_after_its_prefix(prefix):
    pattern = base.id_pattern(prefix)
    assert re.fullmatch(pattern.strip("^$"), prefix) is None
    assert re.fullmatch(pattern.strip("^$"), prefix + "x") is not None
    assert base.namespace_of(prefix) is None
    assert base.namespace_of(prefix + "x1") is not None

# 6. base._strings: mapping keys were not scanned
def test_mapping_keys_are_scanned_for_foreign_ids():
    assert base.foreign_ids({"fact-synth-0001": 1}, "institutional")
    assert base.foreign_ids({"x": {"y": {"sess-synth-0002": []}}}, "institutional")
    assert list(base._strings({"k1": ["v1"], "k2": {"k3": "v3"}})) == ["k1", "v1", "k2", "k3", "v3"]
