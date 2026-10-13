"""Synthetic reviewed reading to pending Chunk integration, never source approval."""
import copy
import hashlib
import json
import unittest

from backend.bintanong_contracts.source import Chunk, check_chunk_binding, privileged_key_paths
from backend.bintanong_tools.document_ingest.register import mint_pending_register
from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle


class ReviewedPolicyChunkTests(unittest.TestCase):
    def setUp(self):
        self.data = b"%PDF-synthetic-reviewed-policy"
        self.sha = hashlib.sha256(self.data).hexdigest()
        self.sources = {self.sha: self.data}
        self.version = mint_pending_register([{"filename": "synthetic.pdf", "sha256": self.sha,
            "acquisition_locator": "shelf:synthetic"}], synthetic=True)[0]
        self.event = json.dumps({"source_sha256": self.sha,
            "owner_statement": "Displayed synthetic undergraduate fields match."}).encode()
        self.ev = hashlib.sha256(self.event).hexdigest()
        self.events = {self.ev: self.event}
        self.rows = [self.row("step-1")]
        self.anchors = {"step-1": {"instruction": [self.span("instruction", "Submit the form.")]}}

    def field(self, name, value, pages=None, **extra):
        return {"name": name, "original_value": value, "reviewed_value": value,
            "source_blank": value == "", "decision": "accepted", "review_event_sha256": self.ev,
            "locator": {"physical_pages": pages or [1], "field": name}, **extra}

    def row(self, identity):
        return {"reading_id": identity, "source_sha256": self.sha, "version_id": self.version.version_id,
            "intended_audience": "undergraduate", "applicability": "undergraduate",
            "applicability_evidence_ref": "synthetic-scope-event#"+identity,
            "fields": [self.field("instruction", "Submit the form.")], "gaps": [],
            "preserved_evidence": [{"artifact": "raw-synthetic.json", "sha256": "a"*64}]}

    def span(self, name, text, page=1):
        return {"schema_version": "bintanong-source-span-v1", "byte_sha256": self.sha,
            "version_id": self.version.version_id, "page": page, "printed_page_label": None,
            "locator": {"kind": "text_item", "table_index": None, "cell_ids": [],
                "item_ids": ["synthetic-"+name], "ref": None}, "text": text,
            "bbox": [10, 10, 120, 25], "bbox_origin": "TOPLEFT", "page_size": [600, 800],
            "extraction": {"source_kind": "synthetic", "resolution_method": "deterministic",
                "repair_id": None, "ocr_confidence": None}}

    def prep(self):
        return build_reviewed_policy_bundle(self.rows, sources=self.sources, review_events=self.events)

    def build(self, bundle=None, **options):
        from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
        return build_reviewed_policy_chunks(self.prep() if bundle is None else bundle,
            sources=self.sources, review_events=self.events, source_versions=[self.version],
            field_spans=self.anchors, **options)

    def reason(self, result, identity="step-1"):
        return next(r["reasons"] for r in result["withheld"] if r["reading_id"] == identity)

    def add_row(self, identity, page):
        row = self.row(identity)
        row["fields"][0]["locator"]["physical_pages"] = [page]
        self.rows.append(row)
        self.anchors[identity] = {"instruction": [self.span(identity, "Submit the form.", page)]}

    def test_pending_bound_roundtrip_determinism_and_no_input_mutation(self):
        bundle = self.prep()
        original = copy.deepcopy((bundle, self.anchors))
        result = self.build(bundle)
        self.assertTrue(result["candidate_only"])
        self.assertFalse(result["activation_eligible"])
        self.assertEqual(len(result["chunks"]), 1)
        chunk = Chunk.parse(result["chunks"][0])
        check_chunk_binding(chunk, self.version)
        self.assertEqual(chunk.source_verification, "pending")
        self.assertEqual(chunk.content_review, "pending")
        self.assertEqual(chunk.scope, ("audience:undergraduate",))
        self.assertEqual(privileged_key_paths(chunk.type_fields), [])
        self.assertEqual(result, self.build(bundle))
        self.assertEqual((bundle, self.anchors), original)
        self.assertEqual(result["item_coverage"][0]["chunk_ids"], [chunk.chunk_id])

    def test_named_row_associations_joint_role_and_blank_stay_in_one_chunk(self):
        fields = [self.field("action", "Evaluate request."), self.field("time", "20 minutes"),
            self.field("person", "Evaluator / Records Officer"), self.field("office", "Registry", [2]),
            self.field("continuation_fee", "")]
        self.rows[0]["fields"] = fields
        self.anchors["step-1"] = {f["name"]: [self.span(f["name"], f["reviewed_value"],
            f["locator"]["physical_pages"][0])] for f in fields if not f["source_blank"]}
        result = self.build()
        chunk = result["chunks"][0]
        display = json.loads(chunk["text"])["fields"]
        self.assertEqual([f["value"] for f in display], [f["reviewed_value"] for f in fields])
        associations = chunk["type_fields"]["field_associations"]
        self.assertEqual(associations[-1]["span_indexes"], [])
        self.assertEqual(associations[3]["span_indexes"], [3])
        self.assertEqual(chunk["spans"][3]["page"], 2)

    def test_unknown_mixed_and_excluded_applicability_emit_no_chunk(self):
        for audience, applicability in [("undergraduate", "unknown"), ("mixed", "mixed"),
            ("law", "excluded"), ("medicine", "excluded"), ("staff", "excluded")]:
            with self.subTest(audience=audience):
                self.rows[0].update(intended_audience=audience, applicability=applicability)
                result = self.build()
                self.assertEqual(result["chunks"], [])
                self.assertIn("undergraduate_applicability_required", self.reason(result))

    def test_source_gap_preserves_visible_fragment_and_claims_but_withholds_chunk(self):
        self.rows[0]["gaps"] = [{"gap_id": "cutoff", "field_names": ["instruction"],
            "issue": "source_cutoff", "visible_text": "during", "affected_claims": ["complete process"],
            "locator": {"physical_pages": [1], "field": "instruction"}}]
        result = self.build()
        self.assertEqual(result["chunks"], [])
        self.assertIn("source_gap_requires_context_support", self.reason(result))
        self.assertEqual(result["preparation"]["readings"][0]["gaps"], self.rows[0]["gaps"])

    def test_partial_review_is_not_inherited(self):
        for state in ["pending", "unresolved"]:
            self.rows[0]["fields"][0]["decision"] = state
            result = self.build()
            self.assertFalse(result["chunks"])
            self.assertIn("field_not_confirmed:instruction", self.reason(result))

    def test_preparation_selection_active_flags_or_field_tampering_is_rejected(self):
        bundle = self.prep()
        for change in [lambda b:b.update(activation_eligible=True),
            lambda b:b["selection"].update(undergraduate=[]),
            lambda b:b["coverage"].update(reading_count=0),
            lambda b:b["review_events"][self.ev].update(owner_statement="Different")]:
            with self.subTest(change=change):
                damaged = copy.deepcopy(bundle)
                change(damaged)
                with self.assertRaisesRegex(ValueError, "preparation"):
                    self.build(damaged)

    def test_original_bytes_events_and_version_binding_are_required(self):
        bundle = self.prep()
        self.sources[self.sha] = b"changed"
        with self.assertRaisesRegex(ValueError, "digest"):
            self.build(bundle)
        self.sources[self.sha] = self.data
        self.rows[0]["version_id"] = "ver-other"
        with self.assertRaisesRegex(ValueError, "version"):
            self.build()

    def test_missing_or_mismatched_spans_never_become_located_text(self):
        original = copy.deepcopy(self.anchors)
        damage = [lambda s:s.update(text="Invented ending."), lambda s:s.update(page=2),
            lambda s:s.update(version_id="ver-other"), lambda s:s.update(byte_sha256="b"*64),
            lambda s:s.update(bbox=None), lambda s:s.update(bbox=[-1, 10, 120, 25]),
            lambda s:s.update(page_size=None)]
        for change in damage:
            with self.subTest(change=change):
                self.anchors = copy.deepcopy(original)
                change(self.anchors["step-1"]["instruction"][0])
                result = self.build()
                self.assertFalse(result["chunks"])
                self.assertIn("invalid_field_spans:instruction", self.reason(result))
        self.anchors = {}
        self.assertIn("missing_field_spans:instruction", self.reason(self.build()))

    def test_span_page_sets_and_duplicate_span_identity_cannot_hide_missing_fragment(self):
        self.rows[0]["fields"][0]["locator"]["physical_pages"] = [1, 2]
        self.assertIn("invalid_field_spans:instruction", self.reason(self.build()))
        self.rows[0]["fields"][0]["locator"]["physical_pages"] = [1]
        self.rows[0]["fields"].append(self.field("copied", "Submit the form."))
        self.anchors["step-1"]["copied"] = copy.deepcopy(self.anchors["step-1"]["instruction"])
        self.assertIn("duplicate_source_span", self.reason(self.build()))

    def test_blank_has_no_default_or_invented_glyph_and_null_or_structured_needs_mapping(self):
        for value in [None, {"action": "A", "time": "B"}, ["Yes", "No"]]:
            self.rows[0]["fields"] = [self.field("instruction", value)]
            result = self.build()
            self.assertFalse(result["chunks"])
            self.assertIn("field_requires_scalar_mapping:instruction", self.reason(result))
        self.rows[0]["fields"] = [self.field("instruction", "")]
        self.assertIn("blank_field_has_spans:instruction", self.reason(self.build()))

    def test_required_neighbors_are_bound_and_transitive_context_is_atomic(self):
        self.add_row("step-2", 2)
        self.add_row("step-3", 3)
        deps = {"step-1": ["step-2"], "step-2": ["step-3"]}
        result = self.build(required_readings=deps)
        coverage = {r["reading_id"]:r["chunk_ids"][0] for r in result["item_coverage"]}
        chunks = {c["chunk_id"]:c for c in result["chunks"]}
        self.assertEqual(chunks[coverage["step-1"]]["type_fields"]["required_neighbor_chunk_ids"], [coverage["step-2"]])
        self.rows[2]["applicability"] = "unknown"
        result = self.build(required_readings=deps)
        self.assertEqual(result["chunks"], [])
        self.assertIn("required_context_withheld:step-2", self.reason(result))

    def test_cycles_keep_whole_groups_without_infinite_recursion(self):
        self.add_row("step-2", 2)
        result = self.build(required_readings={"step-1": ["step-2"], "step-2": ["step-1"]})
        self.assertEqual(len(result["chunks"]), 2)
        self.rows[1]["applicability"] = "unknown"
        self.assertFalse(self.build(required_readings={"step-1": ["step-2"], "step-2": ["step-1"]})["chunks"])

    def test_undefined_dependency_and_unknown_anchor_fields_are_rejected(self):
        for deps in [{"step-1": ["unknown"]}, {"unknown": ["step-1"]}, {"step-1": "step-1"}]:
            with self.assertRaisesRegex(ValueError, "required"):
                self.build(required_readings=deps)
        self.anchors["step-1"]["invented"] = []
        with self.assertRaisesRegex(ValueError, "field"):
            self.build()

    def test_token_cap_includes_serialized_field_associations_and_never_truncates(self):
        result = self.build(token_cap=8)
        self.assertFalse(result["chunks"])
        self.assertIn("over_token_cap", self.reason(result))
        for cap in [0, True, 481]:
            with self.assertRaisesRegex(ValueError, "token cap"):
                self.build(token_cap=cap)

    def test_content_or_event_or_dependency_change_produces_new_identity(self):
        first = self.build()["chunks"][0]["chunk_id"]
        self.rows[0]["fields"][0]["reviewed_value"] = "Corrected wording."
        self.rows[0]["fields"][0]["decision"] = "corrected"
        self.anchors["step-1"]["instruction"][0]["text"] = "Corrected wording."
        self.assertNotEqual(first, self.build()["chunks"][0]["chunk_id"])

    def test_required_context_content_change_invalidates_parent_identity(self):
        self.add_row("step-2", 2)
        deps = {"step-1": ["step-2"]}
        before = self.build(required_readings=deps)["chunks"][0]["chunk_id"]
        self.rows[1]["fields"][0]["reviewed_value"] = "Changed required exception."
        self.rows[1]["fields"][0]["decision"] = "corrected"
        self.anchors["step-2"]["instruction"][0]["text"] = "Changed required exception."
        after = self.build(required_readings=deps)["chunks"][0]["chunk_id"]
        self.assertNotEqual(before, after)

    def test_required_context_from_other_source_version_is_withheld(self):
        other_data = b"other synthetic source"
        other_sha = hashlib.sha256(other_data).hexdigest()
        self.sources[other_sha] = other_data
        other_version = mint_pending_register([{"filename":"other.pdf", "sha256":other_sha,
            "acquisition_locator":"shelf:other"}], synthetic=True)[0]
        other_event = json.dumps({"source_sha256":other_sha,"owner_statement":"Other synthetic fields match."}).encode()
        other_ev = hashlib.sha256(other_event).hexdigest()
        self.events[other_ev] = other_event
        self.add_row("other-step", 2)
        self.rows[1].update(source_sha256=other_sha,version_id=other_version.version_id)
        self.rows[1]["fields"][0]["review_event_sha256"] = other_ev
        self.anchors["other-step"]["instruction"][0].update(byte_sha256=other_sha,version_id=other_version.version_id)
        from backend.bintanong_tools.document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
        result = build_reviewed_policy_chunks(self.prep(), sources=self.sources,review_events=self.events,
            source_versions=[self.version,other_version],field_spans=self.anchors,
            required_readings={"step-1":["other-step"]})
        self.assertIn("required_context_other_version",self.reason(result))
        self.assertEqual(len(result["chunks"]),1)


if __name__ == "__main__":
    unittest.main()
