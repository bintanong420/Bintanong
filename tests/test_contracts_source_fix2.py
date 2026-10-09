"""Phase 1 Task 3, fix pass 2 (source, chunk, token count, embedding, adapter).

Written red first against 86e48a0. Synthetic ids and fictional digests only; the real-output numbers
are measured separately by a scratch script and reported, not asserted here.
"""

from __future__ import annotations

import copy
import math

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, chunk_adapter as ca, embedding, source
import test_contracts_chunk_adapter as ex
import test_contracts_source as s1

span_dict, chunk_dict, digest = s1.span_dict, s1.chunk_dict, s1.digest
SHA40, SHA64 = "a" * 40, "b" * 64


def bad(cls, payload, match):
    with pytest.raises((ValidationError, base.ContractError), match=match):
        cls.parse(payload)


# ---------------------------------------------------------------- M-e: TokenCount
def tc(**over):
    return {"count": 5, "method": f"tokenizer:synthetic@{SHA40}", "exact": True,
            "includes_prefix_and_special_tokens": True, **over}


@pytest.mark.parametrize("method", [f"tokenizer:synthetic@{SHA40}", f"tokenizer:m@{SHA64}", f"tokenizer:org/model-x@{SHA40}"])
def test_an_exact_count_names_its_tokenizer_and_a_pinned_revision(method):
    assert source.TokenCount.model_validate(tc(method=method)).exact


@pytest.mark.parametrize("method", [
    "tokenizer:@", f"tokenizer:@{SHA40}", "tokenizer:m@", "tokenizer:m@main", "tokenizer:m@r1", "tokenizer:m@latest",
    f"tokenizer:m@{SHA40.upper()}", f"tokenizer:m@{SHA40[:-1]}", f"tokenizer:m@{SHA40} ", "tokenizer:m", "tokenizer:",
    f"tokenizer: m@{SHA40}", f"tokenizer:m @{SHA40}", "unspecified", "estimate-v1"])
def test_an_exact_count_with_an_unpinned_or_malformed_method_is_rejected(method):
    with pytest.raises(ValidationError, match='Value error, an e'):
        source.TokenCount.model_validate(tc(method=method))


def test_an_exact_count_of_zero_is_rejected_and_an_estimate_may_be_zero():
    with pytest.raises(ValidationError, match="exact count of 0"):
        source.TokenCount.model_validate(tc(count=0))
    source.TokenCount.model_validate({"count": 0, "method": "estimate-v1", "exact": False,
                                      "includes_prefix_and_special_tokens": False})


# ---------------------------------------------------------------- M-e: EmbeddingRecord
def rec(**over):
    d = {"schema_version": "bintanong-embedding-record-v1", "chunk_id": "c" * 64, "chunk_content_hash": "d" * 64,
         "model_id": "synthetic-model", "model_revision": SHA40, "tokenizer_fingerprint": "1" * 64,
         "preprocessing_fingerprint": "2" * 64, "prompt_fingerprint": "3" * 64, "dimension": 4,
         "normalization": "l2", "vector": [0.5, 0.5, 0.5, 0.5], "token_count": tc()}
    d.update(over)
    return d


@pytest.mark.parametrize("revision", [" main", "main\n", "refs/heads/main", "origin/main", "v1", "stable", "nightly", "x",
                                      "main", "master", "latest", "head", "HEAD", "r1" + "0" * 38, SHA40.upper(), SHA40[:-1],
                                      SHA40 + "0", ""])
def test_a_model_revision_must_be_a_full_lowercase_commit_or_digest(revision):
    with pytest.raises(ValidationError, match='pinned|at least 1 character'):
        embedding.EmbeddingRecord.parse(rec(model_revision=revision))


@pytest.mark.parametrize("revision", [SHA40, SHA64, "0123456789abcdef" * 4])
def test_a_full_commit_or_digest_is_a_pinned_revision(revision):
    assert embedding.EmbeddingRecord.parse(rec(model_revision=revision)).model_revision == revision


@pytest.mark.parametrize("field", ["tokenizer_fingerprint", "preprocessing_fingerprint", "prompt_fingerprint"])
def test_an_all_zero_fingerprint_is_rejected(field):
    with pytest.raises(ValidationError, match="all-zero"):
        embedding.EmbeddingRecord.parse(rec(**{field: "0" * 64}))


def test_the_l2_tolerance_is_one_in_a_million():
    scale = 1 + 2e-6
    with pytest.raises(ValidationError, match="l2-normalized"):
        embedding.EmbeddingRecord.parse(rec(vector=[0.5 * scale] * 4))
    scale = 1 + 4e-7
    embedding.EmbeddingRecord.parse(rec(vector=[0.5 * scale] * 4))
    assert embedding.L2_TOLERANCE == 1e-6


# ---------------------------------------------------------------- M-d: source_label and adapter source
@pytest.mark.parametrize("label", ["file:///a.pdf", "~/a.pdf", "../a.pdf", "D:rel.pdf", "dir\\a.pdf", "C:\\x\\a.pdf", "/abs/a.pdf",
                                   "https://example.invalid/a.pdf", "a/b.pdf", "..", "a\nb.pdf"])
def test_chunk_source_label_must_be_a_plain_file_name(label):
    bad(source.Chunk, chunk_dict(source_label=label), "source_label")


def test_chunk_source_label_accepts_plain_names():
    for label in ("synthetic.pdf", "Student Handbook (2023).pdf", "BSBA-HRM_docling.json"):
        source.Chunk.parse(chunk_dict(source_label=label))


@pytest.mark.parametrize("value", ["file:///a.pdf", "~/a.pdf", "../a.pdf", "D:rel.pdf", "dir\\a.pdf", "https://example.invalid/a.pdf"])
def test_the_adapter_rejects_paths_and_urls_in_source(value):
    raw = ex.one("course")
    assert ex.reason({**raw, "source": value}, page_sizes=ex.PAGE) == "local_path_in_source"


# ---------------------------------------------------------------- M-f: source_text equals the span text
def test_source_text_must_equal_the_joined_span_text_in_span_order():
    other = span_dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c2"], "item_ids": [], "ref": None},
                      text="Second")
    good = chunk_dict(spans=[span_dict(), other], source_text="Printed Second", content_hash=digest("Printed Second", "Summary"))
    source.Chunk.parse(good)
    bad(source.Chunk, {**good, "source_text": "Second Printed", "content_hash": digest("Second Printed", "Summary")},
        "source_text differs from the span text")
    source.Chunk.parse({**good, "source_text": "Printed   Second\n"} | {"content_hash": digest("Printed Second", "Summary")})


def test_the_reviews_accepted_example_is_now_rejected():
    forged = chunk_dict(source_text="Totally different printed rule", content_hash=digest("Totally different printed rule", "Summary"))
    bad(source.Chunk, forged, "source_text differs from the span text")


def test_a_chunk_whose_spans_carry_no_printed_text_may_only_assert_no_source_text():
    layout = chunk_dict(source_text=None, spans=[span_dict(text=None)], content_hash=digest(None, "Summary"))
    c = source.Chunk.parse(layout)
    assert c.source_text is None and not c.spans[0].is_complete
    bad(source.Chunk, {**layout, "source_text": "Asserted", "content_hash": digest("Asserted", "Summary")}, "no printed text")
    bad(source.Chunk, chunk_dict(source_text=None, content_hash=digest(None, "Summary")), "carries printed text")
    bad(source.Chunk, {**layout, "spans": []}, "at least one")
    bad(source.Chunk, chunk_dict(source_text="", content_hash=digest("", "Summary")), "printed source_text")


def test_a_textless_layout_chunk_is_not_retrievable_evidence():
    from backend.bintanong_contracts import runtime
    c = source.Chunk.parse(chunk_dict(source_text=None, spans=[span_dict(text=None)], content_hash=digest(None, "Summary"),
                                      version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                                      document_id="doc-synth-handbook"))
    with pytest.raises(ValidationError, match="printed text"):
        runtime.RetrievedChunk.parse({"rank": 1, "score": 0.5, "knowledge_release_id": "release-synth-1",
                                               "chunk": c.model_dump(mode="json")})


# ---------------------------------------------------------------- M-n: identical spans only
def test_distinct_spans_that_share_a_cell_are_allowed_and_identical_spans_are_not():
    shared = span_dict(locator={"kind": "table_cells", "table_index": 0, "cell_ids": ["t0-c1", "t0-c2"], "item_ids": [], "ref": None},
                       text="Header and body")
    c = source.Chunk.parse(chunk_dict(spans=[span_dict(), shared], source_text="Printed Header and body",
                                      content_hash=digest("Printed Header and body", "Summary")))
    assert len(c.spans) == 2
    bad(source.Chunk, chunk_dict(spans=[span_dict(), span_dict()], source_text="Printed Printed",
                                 content_hash=digest("Printed Printed", "Summary")), "identical")


# ---------------------------------------------------------------- M-m: status claims and type_fields
def bound_dict(**over):
    return chunk_dict(version_id="ver-synth-handbook-2", edition_id="edition-synth-handbook-2",
                      document_id="doc-synth-handbook", **over)


BIND = {"verification_evidence_ref": "ev-b3", "content_review_evidence_ref": None}


def test_verified_or_rejected_needs_a_register_binding():
    for state in ("verified", "rejected"):
        bad(source.Chunk, bound_dict(source_verification=state), "needs a register_binding")
        source.Chunk.parse(bound_dict(source_verification=state, register_binding=BIND))
    bad(source.Chunk, chunk_dict(content_review="reviewed", version_id="ver-synth-handbook-2",
                                 edition_id="edition-synth-handbook-2", document_id="doc-synth-handbook"), "content_review")
    source.Chunk.parse(bound_dict(source_verification="observed", register_binding=BIND))
    source.Chunk.parse(chunk_dict(content_review="reviewed"))            # an unbound extractor label stays a label
    source.Chunk.parse(bound_dict(source_verification="observed"))      # the observed default needs no binding at this level


def test_a_register_binding_must_match_the_claimed_states():
    bad(source.Chunk, chunk_dict(register_binding=BIND), "no version")
    bad(source.Chunk, bound_dict(source_verification="pending", register_binding=BIND), "verification_evidence_ref")
    bad(source.Chunk, bound_dict(source_verification="verified",
                                 register_binding={**BIND, "verification_evidence_ref": None}), "verification_evidence_ref")
    bad(source.Chunk, bound_dict(source_verification="observed",
                                 register_binding={**BIND, "content_review_evidence_ref": "ev-x"}), "content_review_evidence_ref")


def reg(sha=s1.SHA_A):
    return s1._register(sha)


def test_the_binding_check_requires_the_registers_evidence_references():
    r = reg()
    ok = source.Chunk.parse(bound_dict(source_verification="observed", register_binding=BIND))
    source.check_chunk_binding(ok, r)
    for binding in (None, {**BIND, "verification_evidence_ref": "ev-other"}):
        c = source.Chunk.parse(bound_dict(source_verification="observed", **({"register_binding": binding} if binding else {})))
        with pytest.raises(base.ContractError, match="evidence reference"):
            source.check_chunk_binding(c, r)


def test_content_review_is_checked_against_the_register_when_bound():
    r = reg()
    c = source.Chunk.parse(bound_dict(source_verification="observed", content_review="partially_reviewed",
                                      register_binding={**BIND, "content_review_evidence_ref": "ev-x"}))
    with pytest.raises(base.ContractError, match="content review"):
        source.check_chunk_binding(c, r)


def test_bind_chunk_copies_both_states_and_the_evidence_references_from_the_register():
    r = reg()
    b = source.bind_chunk(source.Chunk.parse(chunk_dict(content_review="reviewed")), r)
    assert b.content_review == r.content_review_state.state == "pending"      # the extractor label is replaced
    assert b.register_binding.verification_evidence_ref == r.verification_state.evidence_ref
    assert b.register_binding.content_review_evidence_ref is None
    source.check_chunk_binding(b, r)


@pytest.mark.parametrize("key", ["VERIFIED ", " Approved", "extractor_status", "review_status", "Review Status", "source-verification",
                                 "PROMOTION_STATUS", "Status"])
def test_privileged_type_field_keys_are_found_case_and_space_insensitively(key):
    bad(source.Chunk, chunk_dict(type_fields={key: True}), "privileged")


@pytest.mark.parametrize("fields", [{"outer": {"approved": True}}, {"outer": [{"deep": {"VERIFIED ": 1}}]},
                                    {"a": {"b": {"c": {"extractor_status": "x"}}}}])
def test_privileged_type_field_keys_are_found_at_any_depth(fields):
    bad(source.Chunk, chunk_dict(type_fields=fields), "privileged")


def test_type_fields_cannot_be_mutated_after_validation():
    c = source.Chunk.parse(chunk_dict(type_fields={"course_code": "CS 101", "nested": {"k": [1, 2]}}))
    with pytest.raises(TypeError, match='this mapping is immutable'):
        c.type_fields["approved"] = True
    with pytest.raises(TypeError, match='this mapping is immutable'):
        c.type_fields.update(verified=True)
    with pytest.raises(TypeError, match='this mapping is immutable'):
        del c.type_fields["course_code"]
    with pytest.raises(TypeError, match='this mapping is immutable'):
        c.type_fields["nested"]["k2"] = 1
    assert isinstance(c.type_fields["nested"]["k"], tuple)
    assert source.Chunk.parse(base.canonical_json(c)) == c
    assert copy.deepcopy(c) == c


@pytest.mark.parametrize("chunk_id", ["C" * 64, "c" * 63, "c" * 65, " " + "c" * 63, "c" * 64 + "\n", ""])
def test_chunk_id_is_64_lowercase_hex(chunk_id):
    bad(source.Chunk, chunk_dict(chunk_id=chunk_id), "chunk_id")


# ---------------------------------------------------------------- M-g: spans keep original pages and sections
def test_a_span_keeps_the_original_page_of_a_split_pdf():
    s = source.SourceSpan.parse(span_dict(page=3, page_offset=56, original_page=59))
    assert (s.page, s.page_offset, s.original_page) == (3, 56, 59)
    source.SourceSpan.parse(span_dict(page=3, original_page=59))
    for over, match in ((dict(page=3, page_offset=56, original_page=60), "original_page"),
                        (dict(page=None, original_page=5), "physical page"),
                        (dict(page=None, page_offset=4), "physical page"),
                        (dict(page_offset=-1), "page_offset"), (dict(original_page=0), "original_page"),
                        (dict(byte_sha256=None, page=None, text=None, original_page=5), "physical page|byte digest")):
        bad(source.SourceSpan, span_dict(**over), match)


def test_a_span_can_locate_a_section():
    loc = {"kind": "section", "table_index": None, "cell_ids": [], "item_ids": [], "ref": None,
           "section_path": ["Part I", "Admission"]}
    s = source.SourceSpan.parse(span_dict(locator=loc))
    assert s.locator.section_path == ("Part I", "Admission")
    for broken in ({**loc, "section_path": []}, {**loc, "item_ids": ["a"]}, {**loc, "section_path": [""]},
                   {**loc, "kind": "text_item", "item_ids": ["a"]}):
        bad(source.SourceSpan, span_dict(locator=broken), "locator")
    assert source.SourceSpan.parse(span_dict()).locator.section_path == ()


# ---------------------------------------------------------------- M-n: the adapter on extractor output
def test_the_adapter_still_rejects_an_identical_span_and_names_it():
    raw = copy.deepcopy(ex.one("course"))
    raw["source_spans"].append(copy.deepcopy(raw["source_spans"][0]))
    assert ex.reason(raw, page_sizes=ex.PAGE) == "duplicate_source_location"


def test_the_adapter_accepts_a_distinct_span_sharing_a_cell():
    raw = copy.deepcopy(ex.one("course"))
    first = raw["source_spans"][0]
    twin = copy.deepcopy(first)
    twin["locator"] = {"kind": "table_cells", "table_index": first["locator"]["table_index"],
                       "cell_ids": [first["locator"]["cell_ids"][0], "t0-r9-c9"]}
    twin["text"] = first["text"] + " extra"
    twin["bbox"] = None
    twin["bbox_origin"] = None
    raw["source_spans"].append(twin)
    raw["cell_ids"] = list(dict.fromkeys(i for s in raw["source_spans"] for i in s["locator"].get("cell_ids", [])))
    raw["source_text"] = raw["source_text"] + " " + twin["text"]
    raw["content_hash"] = source.compute_content_hash(raw["source_text"], raw["text"])
    raw["chunk_id"] = ca.make_chunk_id(raw["pdf_sha256"], ca.locator_key(raw["source_spans"]), raw["content_hash"])
    assert ca.adapt_chunk(raw, page_sizes=ex.PAGE).chunk.chunk_id == raw["chunk_id"]


def layout_with_no_text():
    raw = copy.deepcopy(ex.one("hierarchical_layout_fallback", ex.layout_chunks()))
    for sp in raw["source_spans"]:
        sp["text"] = None
    raw["source_text"] = None
    raw["content_hash"] = source.compute_content_hash(None, raw["text"])
    raw["chunk_id"] = ca.make_chunk_id(raw["pdf_sha256"], ca.locator_key(raw["source_spans"]), raw["content_hash"])
    return raw


def test_a_layout_chunk_without_printed_text_maps_only_when_its_source_text_is_none():
    raw = layout_with_no_text()
    c = ca.adapt_chunk(raw).chunk
    assert c.source_text is None and c.spans[0].text is None and c.chunk_id == raw["chunk_id"]


def test_null_span_text_with_a_source_text_is_rejected_with_a_named_reason():
    raw = copy.deepcopy(ex.one("hierarchical_layout_fallback", ex.layout_chunks()))
    raw["source_spans"][0]["text"] = None
    assert ex.reason(raw) == "span_missing_text"


def test_a_source_text_that_differs_from_the_span_text_has_a_named_reason():
    raw = copy.deepcopy(ex.one("course"))
    raw["source_text"] = raw["source_text"] + " and more"
    raw["content_hash"] = source.compute_content_hash(raw["source_text"], raw["text"])
    raw["chunk_id"] = ca.make_chunk_id(raw["pdf_sha256"], ca.locator_key(raw["source_spans"]), raw["content_hash"])
    assert ex.reason(raw, page_sizes=ex.PAGE) == "source_text_differs_from_spans"


def test_a_nested_privileged_key_in_an_extractor_chunk_is_a_named_reason():
    raw = copy.deepcopy(ex.one("course"))
    raw["derived_fields"] = {"nested": {"Approved ": True}}
    assert ex.reason(raw, page_sizes=ex.PAGE).startswith("privileged_field:")


def test_a_chunk_without_printed_text_hashes_its_own_text_in_the_printed_slot_like_the_extractor():
    from backend.bintanong_tools.prospectus_extractor import chunking
    assert source.compute_content_hash(None, "Table  text") == source.compute_content_hash("Table text", "Table text")
    assert source.compute_content_hash(None, "Table text") == chunking.content_hash("Table text", "Table text")
