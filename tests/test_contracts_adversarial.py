"""Phase 1 Task 3, group 6: adversarial scenarios across the whole contracts package.

One synthetic chain (register -> extractor chunk -> bound chunk -> retrieval -> bundle -> envelope)
is built from real parts, then attacked one trust boundary at a time. Also: deterministic roundtrips
and schema compatibility with the synthetic examples under knowledge/manifests.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import (
    answer, base, chunk_adapter, embedding, governance as gov, routing_adapter, runtime, source, symbolic)
import contracts_fixtures as fx
import test_contracts_chunk_adapter as ex

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "knowledge" / "manifests"
EXAMPLES = MAN / "examples"
PDF_SHA = ex.PDF_A


def load(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def raises(*, match=None):
    return pytest.raises((ValidationError, base.ContractError), match=match)


# ---------------------------------------------------------------- the chain
def register_for(sha, edition="2", verification="observed"):
    rec = copy.deepcopy(load("synthetic-register.json")[1])
    rec.update(byte_sha256=sha)
    if verification == "pending":
        rec["verification_state"] = {"state": "pending", "evidence_ref": None}
        for f in ("issuer", "printed_revision"):
            rec[f].update(value=None, state="pending", evidence_ref=None, basis=None)
    return gov.SourceDocumentVersion.parse(rec)


def extractor_chunk():
    raw = next(c for c in ex.semantic() if c["chunk_type"] == "course")
    return chunk_adapter.adapt_chunk(raw, page_sizes=ex.PAGE).chunk


def bound_chunk(reg=None):
    reg = reg or register_for(PDF_SHA)
    return source.bind_chunk(extractor_chunk(), reg), reg


def retrieval_for(chunk, release="release-synth-1"):
    return runtime.RetrievalResult.parse({
        "schema_version": "bintanong-retrieval-result-v1", "knowledge_release_id": release,
        "items": [{"rank": 1, "score": 0.9, "knowledge_release_id": release, "chunk": chunk.model_dump(mode="json")}],
        "coverage_status": "sufficient",
        "config": {"top_k": 3, "score_metric": "cosine", "min_score": None,
                   "embedding_model_id": "synthetic-model", "embedding_model_revision": "r1" + "0" * 38}})


def test_the_whole_chain_accepts_honest_synthetic_parts_and_claims_nothing_official():
    chunk, reg = bound_chunk()
    assert chunk.source_verification == "observed" and reg.approval_state.state == "not_requested"
    assert reg.approval_id is None
    ret = retrieval_for(chunk)
    cite = chunk.spans[0]
    bundle = answer.EvidenceBundle.parse({
        "schema_version": "bintanong-evidence-bundle-v1", "request_id": "req-chain-1", "route": "RAG",
        "knowledge_release_id": "release-synth-1", "retrieval": ret.model_dump(mode="json"), "symbolic": None,
        "session_facts": [], "conflicts": [], "permitted_claims": ["policy_passage"]})
    env = answer.AnswerEnvelope.parse({
        "schema_version": "bintanong-answer-envelope-v1", "request_id": "req-chain-1", "status": "answered",
        "language": "en", "text": "Synthetic answer.", "route": "RAG", "decision": None,
        "citations": [{"chunk_id": chunk.chunk_id, "byte_sha256": chunk.byte_sha256, "version_id": chunk.version_id,
                       "page": cite.page, "locator_ref": cite.locator.cell_ids[0]}],
        "validation": {"passed": True, "checks": ["citations_resolve"], "failures": []}})
    answer.check_envelope_against_bundle(env, bundle)


# ---------------------------------------------------------------- fabricated verification / approval
def test_chunk_cannot_claim_more_verification_than_the_register_has():
    chunk, reg = bound_chunk()
    forged = source.Chunk.parse({**chunk.model_dump(mode="json"), "source_verification": "verified"})
    with raises(match="verification"):
        source.check_chunk_binding(forged, reg)


def test_register_cannot_be_verified_or_approved_by_label_audit_or_possession():
    for kind in ("extractor_status_label", "extraction_audit", "filename_observation", "local_possession_note"):
        rec = copy.deepcopy(load("synthetic-register.json")[1])
        rec["evidence"].append({"evidence_id": "ev-z", "kind": kind, "recorded_by": "issuing_office",
                                "recorded_at": "2026-01-01T00:00:00+00:00", "authorization_ref": "auth-fake"})
        rec["approval_state"] = {"state": "approved", "evidence_ref": "ev-z"}
        rec["approval_id"] = "auth-fake"
        with raises():
            gov.SourceDocumentVersion.parse(rec)


def test_the_extractor_content_review_label_is_not_source_verification():
    raw = copy.deepcopy(next(c for c in ex.semantic() if c["chunk_type"] == "course"))
    raw["content_review"] = "reviewed"
    chunk = chunk_adapter.adapt_chunk(raw, page_sizes=ex.PAGE).chunk
    assert chunk.content_review == "reviewed" and chunk.source_verification == "pending"
    assert chunk_adapter.adapt_chunk({**raw, "content_review": "reviewed"}, page_sizes=ex.PAGE).chunk.version_id is None


# ---------------------------------------------------------------- incompatible editions, source mutation
def test_two_editions_of_one_document_cannot_share_a_retrieval_result():
    a = fx.item(1, 1, 0.9, edition="1")
    b = fx.item(2, 2, 0.8, edition="2")
    with raises(match="edition"):
        runtime.RetrievalResult.parse(fx.retrieval([a, b]))


def test_source_mutation_is_detected_by_digest_at_span_chunk_and_binding_level():
    chunk, reg = bound_chunk()
    mutated_reg = register_for("f" * 64)
    with raises(match="digest"):
        source.check_chunk_binding(chunk, mutated_reg)
    with raises(match="digest"):
        source.check_span_binding(chunk.spans[0], mutated_reg)
    with raises(match="digest"):
        source.bind_chunk(extractor_chunk(), mutated_reg)


def test_same_filename_different_bytes_is_a_different_edition():
    a = gov.SourceDocumentVersion.parse(load("synthetic-register.json")[0])
    b = gov.SourceDocumentVersion.parse(load("synthetic-register.json")[1])
    assert a.filename == b.filename and a.byte_sha256 != b.byte_sha256
    gov.check_register([a, b])
    clash = gov.SourceDocumentVersion.parse({**b.model_dump(mode="json"), "edition_id": a.edition_id})
    with raises(match="edition"):
        gov.check_register([a, clash])


# ---------------------------------------------------------------- duplicate locations, page labels, geometry
def test_duplicate_source_locations_are_rejected_at_every_layer():
    raw = copy.deepcopy(next(c for c in ex.semantic() if c["chunk_type"] == "course"))
    raw["source_spans"].append(copy.deepcopy(raw["source_spans"][0]))
    with pytest.raises(chunk_adapter.ChunkMappingError) as info:
        chunk_adapter.adapt_chunk(raw, page_sizes=ex.PAGE)
    assert info.value.reason == "duplicate_source_location"
    data = extractor_chunk().model_dump(mode="json")
    data["spans"].append(copy.deepcopy(data["spans"][0]))
    with raises(match="duplicate"):
        source.Chunk.parse(data)


def test_missing_printed_page_labels_stay_missing_through_the_chain():
    chunk, _ = bound_chunk()
    assert all(s.printed_page_label is None for s in chunk.spans)
    again = source.Chunk.parse(base.canonical_json(chunk))
    assert all(s.printed_page_label is None and s.page is not None for s in again.spans)
    data = chunk.model_dump(mode="json")
    data["spans"][0]["printed_page_label"] = ""
    with raises():
        source.Chunk.parse(data)


@pytest.mark.parametrize("patch", [
    {"bbox_origin": None}, {"page_size": None}, {"page_size": [10.0, 10.0]},     # outside the 10x10 page
    {"bbox": [30.0, 2.0, 1.0, 40.0]},
])
def test_invalid_geometry_cannot_enter_through_the_chunk(patch):
    data = extractor_chunk().model_dump(mode="json")
    data["spans"][0].update(patch)
    with raises():
        source.Chunk.parse(data)


# ---------------------------------------------------------------- copied private facts
def test_private_facts_cannot_become_institutional_ids_or_storage():
    fact = gov.SessionFact.parse(load("synthetic-session-fact.json"))
    # an institutional record refuses a private id anywhere
    rec = copy.deepcopy(load("synthetic-register.json")[1])
    rec["acquisition_locators"].append(fact.fact_id)
    with raises():
        gov.SourceDocumentVersion.parse(rec)
    # a private fact refuses an institutional id as its value
    data = fact.model_dump(mode="json")
    data["fact"]["value"] = "ver-synth-handbook-1"
    with raises():
        gov.SessionFact.parse(data)
    # a chunk refuses to be labelled with a private id
    data = extractor_chunk().model_dump(mode="json")
    data["source_label"] = fact.fact_id
    with raises():
        source.Chunk.parse(data)
    # a session fact has no fields through which it could be promoted
    for key in ("approval_id", "version_id", "edition_id", "ledger_entry", "verified"):
        with raises():
            gov.SessionFact.parse({**fact.model_dump(mode="json"), key: "x"})


def test_a_student_statement_alone_never_supports_a_decision():
    fact = fixture_fact("unconfirmed")
    sym = fixture_symbolic("eligible")
    with raises(match="unconfirmed"):
        answer.EvidenceBundle.parse(fixture_bundle(sym, [fact], ["decision_eligible"]))


# ---------------------------------------------------------------- route / outcome confusion
def test_legacy_direct_never_becomes_a_route_or_a_control_outcome():
    with pytest.raises(routing_adapter.LegacyRoutingError, match="OWNER"):
        routing_adapter.from_legacy_routing({"route": "Direct", "confidence": 1.0, "reason": "hello"})
    for payload in ({"route": "Direct", "control": None}, {"route": None, "control": "Direct"}):
        with raises():
            runtime.RoutingDecision.parse({
                "schema_version": "bintanong-routing-decision-v1", "confidence": None, "predicate_request": None,
                "required_facts": [], "missing_facts": [], "reason": "r", **payload})


def test_a_control_outcome_is_never_dispatched_and_never_carries_a_citation():
    greeting = runtime.RoutingDecision.parse({
        "schema_version": "bintanong-routing-decision-v1", "route": None, "control": "greeting", "confidence": None,
        "predicate_request": None, "required_facts": [], "missing_facts": [], "reason": "hello"})
    with raises(match="control"):
        runtime.dispatch_route(greeting)
    # a greeting turn cannot be wrapped as an answered, cited response
    with raises():
        answer.AnswerEnvelope.parse({
            "schema_version": "bintanong-answer-envelope-v1", "request_id": "req-1", "status": "answered",
            "language": "en", "text": "Hi", "route": None, "decision": None, "citations": [],
            "validation": {"passed": True, "checks": [], "failures": []}})


def test_error_and_unsupported_outcomes_never_surface_as_a_verdict():
    for outcome, status in (("error", "answered"), ("unsupported", "answered"), ("unknown", "answered"),
                            ("error", "abstained"), ("unsupported", "clarification_needed")):
        with raises():
            answer.AnswerEnvelope.parse({
                "schema_version": "bintanong-answer-envelope-v1", "request_id": "req-1", "status": status,
                "language": "en", "text": "x", "route": "Symbolic", "decision": fixture_decision(outcome),
                "citations": [], "validation": {"passed": status == "answered", "checks": [],
                                                 "failures": [] if status == "answered" else ["x"]}})


# ---------------------------------------------------------------- stale derived state
def test_stale_derived_state_is_detected():
    chunk, _ = bound_chunk()
    rec = embedding.EmbeddingRecord.parse({
        "schema_version": "bintanong-embedding-record-v1", "chunk_id": chunk.chunk_id,
        "chunk_content_hash": chunk.content_hash, "model_id": "m", "model_revision": "r1" + "0" * 38,
        "tokenizer_fingerprint": "1" * 64, "preprocessing_fingerprint": "2" * 64, "prompt_fingerprint": "3" * 64,
        "dimension": 2, "normalization": "l2", "vector": [0.6, 0.8],
        "token_count": {"count": 9, "method": "tokenizer:m@r1", "exact": True,
                        "includes_prefix_and_special_tokens": True}})
    embedding.check_embedding_matches_chunk(rec, chunk)
    changed = source.Chunk.parse({**chunk.model_dump(mode="json"), "text": "Edited explanation.",
                                  "content_hash": source.compute_content_hash(chunk.source_text, "Edited explanation.")})
    with raises(match="stale"):
        embedding.check_embedding_matches_chunk(rec, changed)
    # an old retrieval cannot be placed in a bundle for a newer release
    ret = retrieval_for(chunk, release="release-synth-1")
    with raises(match="release"):
        answer.EvidenceBundle.parse({
            "schema_version": "bintanong-evidence-bundle-v1", "request_id": "req-1", "route": "RAG",
            "knowledge_release_id": "release-synth-2", "retrieval": ret.model_dump(mode="json"), "symbolic": None,
            "session_facts": [], "conflicts": [], "permitted_claims": ["policy_passage"]})
    # a binding made to a verification state that later changed is stale
    reg_later = register_for(PDF_SHA, verification="pending")
    with raises(match="stale"):
        source.check_chunk_binding(chunk, reg_later)


# ---------------------------------------------------------------- unsupported rules, partial Hybrid
def test_unsupported_rules_stay_unsupported():
    req = runtime.PredicateRequest.parse({"predicate": "can_enroll_fictional", "inputs": [
        {"name": "course", "value": "FICTIONAL-101", "fact_ref": None}]})
    with pytest.raises(symbolic.UnsupportedRequest):
        symbolic.EMPTY_REGISTRY.goal(req)
    result = symbolic.SymbolicResult.parse({
        "schema_version": "bintanong-symbolic-result-v1", "decision": fixture_decision("eligible"),
        "capability": "x", "inputs": [], "rule_ids": ["rule-1"], "rule_bundle_version": "b1"})
    with raises(match="registry"):
        symbolic.EMPTY_REGISTRY.check_result(result)


def test_partial_hybrid_results_are_refused_not_completed_from_passages():
    chunk, _ = bound_chunk()
    ret = retrieval_for(chunk)
    for symbolic_half, claims in ((None, ["policy_passage"]),
                                  (fixture_symbolic("error"), ["policy_passage"]),
                                  (fixture_symbolic("unsupported"), ["policy_passage"])):
        with raises():
            answer.EvidenceBundle.parse({
                "schema_version": "bintanong-evidence-bundle-v1", "request_id": "req-1", "route": "Hybrid",
                "knowledge_release_id": "release-synth-1", "retrieval": ret.model_dump(mode="json"),
                "symbolic": symbolic_half, "session_facts": [fixture_fact("user_confirmed").model_dump(mode="json")],
                "conflicts": [], "permitted_claims": claims})
    with raises():  # a failed symbolic half may only be reported as an error
        answer.AnswerEnvelope.parse({
            "schema_version": "bintanong-answer-envelope-v1", "request_id": "req-1", "status": "answered",
            "language": "en", "text": "From the handbook...", "route": "Hybrid",
            "decision": fixture_decision("error"), "citations": [], "validation": {"passed": True, "checks": [], "failures": []}})


# ---------------------------------------------------------------- fixtures for the scenarios above
def fixture_decision(outcome):
    d = next(d for d in load("synthetic-decisions.json") if d["outcome"] == outcome)
    return {**d, "synthetic": False}


def fixture_symbolic(outcome):
    has_rules = outcome in ("eligible", "ineligible")
    return {"schema_version": "bintanong-symbolic-result-v1", "decision": fixture_decision(outcome),
            "capability": "enrollment_eligibility",
            "inputs": [{"name": "course", "value": "FICTIONAL-101", "fact_ref": "fact-synth-0001"}],
            "rule_ids": ["rule-1"] if has_rules else [], "rule_bundle_version": "b1" if has_rules else None}


def fixture_fact(state):
    f = load("synthetic-session-fact.json")
    if state != "unconfirmed":
        f["evidence"] = [{"evidence_id": "ev-u", "kind": "user_confirmation", "recorded_by": "user",
                          "recorded_at": "2026-01-01T00:00:00+00:00"}]
        f.update(confirmation_state=state, confirmation_evidence_ref="ev-u")
    return gov.SessionFact.parse(f)


def fixture_bundle(sym, facts, claims):
    chunk, _ = bound_chunk()
    return {"schema_version": "bintanong-evidence-bundle-v1", "request_id": "req-1", "route": "Hybrid",
            "knowledge_release_id": "release-synth-1",
            "retrieval": retrieval_for(chunk).model_dump(mode="json"), "symbolic": sym,
            "session_facts": [f.model_dump(mode="json") for f in facts], "conflicts": [], "permitted_claims": claims}


# ================================================================ determinism and schema compatibility
EXAMPLE_MODELS = [
    ("synthetic-register.json", gov.SourceDocumentVersion, "source-register-v1"),
    ("synthetic-conflict.json", gov.SourceConflict, "source-conflict-v1"),
    ("synthetic-session-fact.json", gov.SessionFact, "session-fact-v1"),
    ("synthetic-decisions.json", symbolic.DecisionOutcome, "decision-v1"),
]


def example_records():
    for name, model, schema in EXAMPLE_MODELS:
        data = load(name)
        for i, rec in enumerate(data if isinstance(data, list) else [data]):
            yield pytest.param(name, model, schema, rec, id=f"{name}[{i}]")


@pytest.mark.parametrize("name,model,schema,rec", list(example_records()))
def test_every_synthetic_example_validates_and_roundtrips_deterministically(name, model, schema, rec):
    m = model.parse(rec)
    text = base.canonical_json(m)
    assert "\r" not in text and text.endswith("\n") and not text.endswith("\n\n")
    assert model.parse(text) == m
    assert base.canonical_json(model.parse(text)) == text
    # the parsed example keeps every value the example file states
    assert _contains(json.loads(text), rec)
    _assert_sorted(text)


def _contains(got, want):
    if isinstance(want, dict):
        return all(k in got and _contains(got[k], v) for k, v in want.items())
    if isinstance(want, list):
        return len(got) == len(want) and all(_contains(g, w) for g, w in zip(got, want))
    return got == want


def _assert_sorted(text):
    def keys_in_order(pairs):
        keys = [k for k, _ in pairs]
        assert keys == sorted(keys), keys
        return dict(pairs)
    json.loads(text, object_pairs_hook=keys_in_order)


@pytest.mark.parametrize("name,model,schema", [(n, m, s) for n, m, s in EXAMPLE_MODELS])
def test_model_fields_equal_the_schema_properties(name, model, schema):
    sch = json.loads((MAN / "schemas" / f"{schema}.schema.json").read_text(encoding="utf-8"))
    assert set(model.model_fields) == set(sch["properties"])
    assert set(sch["required"]) == set(sch["properties"])
    assert model.SCHEMA_VERSION == sch["properties"]["schema_version"]["const"]


def _mutants(rec):
    pool = [None, "", 0, True, "zz", [], {}, "ver-x", "fact-x", -1, 1.5]

    def walk(node, path):
        if isinstance(node, dict):
            for k in list(node):
                yield path + [k], "delete"
                yield from walk(node[k], path + [k])
        elif isinstance(node, list):
            for i in range(len(node)):
                yield from walk(node[i], path + [i])
        if path:
            for p in pool:
                yield path, p
    for path, repl in walk(rec, []):
        out = copy.deepcopy(rec)
        parent = out
        for step in path[:-1]:
            parent = parent[step]
        if repl == "delete":
            if isinstance(parent, dict):
                del parent[path[-1]]
        else:
            if parent[path[-1]] == repl and type(parent[path[-1]]) is type(repl):
                continue
            parent[path[-1]] = repl
        yield out


@pytest.mark.parametrize("name,model,schema", EXAMPLE_MODELS)
def test_the_package_is_at_least_as_strict_as_the_json_schema(name, model, schema):
    jsonschema = pytest.importorskip("jsonschema")
    sch = json.loads((MAN / "schemas" / f"{schema}.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(sch)
    data = load(name)
    checked = 0
    for rec in (data if isinstance(data, list) else [data]):
        for mutant in _mutants(rec):
            if validator.is_valid(mutant):
                continue
            checked += 1
            with raises():
                model.parse(mutant)
    assert checked > 100
