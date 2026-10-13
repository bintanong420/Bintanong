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

    def limited_candidate(self):
        self.rows[0]['gaps'] = [{'gap_id': 'cutoff', 'field_names': ['instruction'],
            'issue': 'source_cutoff', 'visible_text': 'Submit the form.',
            'affected_claims': ['remaining instructions', 'complete process'],
            'locator': {'physical_pages': [1], 'field': 'instruction'}}]
        result = self.build(include_source_limits=True)
        chunk = result['chunks'][0]
        return {'chunk': chunk, 'version': self.version.model_dump(mode='json'),
            'spans': chunk['spans'], 'neighbors': [], 'similarity': 0.9}

    def test_opt_in_limit_and_field_names_reach_cited_context_without_input_mutation(self):
        from backend.bintanong_retrieval.context import build_context
        candidate = self.limited_candidate()
        before = copy.deepcopy(candidate)
        chunk = candidate['chunk']
        Chunk.parse(chunk)
        self.assertEqual(chunk['type_fields']['context_format'], 'reviewed-policy-fields-v1')
        self.assertEqual(json.loads(chunk['text'])['source_limits'][0]['visible_text'], 'Submit the form.')
        out = build_context([candidate], 10000, len)
        self.assertIn('Unavailable information:', out['context'])
        self.assertIn('complete process', out['context'])
        self.assertIn('instruction', out['context'])
        self.assertEqual(out['evidence'][0]['text'], chunk['text'])
        self.assertEqual(candidate, before)
        self.assertEqual(len(out['evidence'][0]['citations']), 1)
        self.assertFalse(self.build()['chunks'])

    def test_opt_in_keeps_unknown_scope_and_unsupported_gap_withheld(self):
        self.limited_candidate()
        self.rows[0]['applicability'] = 'unknown'
        self.assertFalse(self.build(include_source_limits=True)['chunks'])
        self.rows[0]['applicability'] = 'undergraduate'
        gap = self.rows[0]['gaps'][0]
        for change in [lambda g:g.update(issue='unknown_policy'),
                       lambda g:g.update(visible_text='Invented ending.'),
                       lambda g:g['locator'].update(physical_pages=[2]),
                       lambda g:g.update(field_names=['instruction', 'instruction'])]:
            before = copy.deepcopy(gap)
            change(gap)
            result = self.build(include_source_limits=True)
            self.assertFalse(result['chunks'])
            self.assertIn('source_gap_requires_context_support', self.reason(result))
            gap.clear(); gap.update(before)
        self.rows[0]['gaps'].append(copy.deepcopy(gap))
        self.assertFalse(self.build(include_source_limits=True)['chunks'])
        for flag in [None, 1, 'true']:
            with self.assertRaises(ValueError): self.build(include_source_limits=flag)

    def test_altered_marked_record_never_falls_back_to_unlimited_span_text(self):
        from backend.bintanong_retrieval.context import build_context
        original = self.limited_candidate()
        for change in [lambda c:c['chunk']['type_fields']['source_limits'].clear(),
                       lambda c:c['chunk'].update(text='Submit the form.'),
                       lambda c:c['chunk']['type_fields']['source_limits'][0].update(message='All complete'),
                       lambda c:c['chunk']['type_fields']['field_associations'][0].update(span_indexes=[True]),
                       lambda c:c['spans'][0].update(text='Invented ending'),
                       lambda c:c['chunk'].update(content_hash='a'*64),
                       lambda c:c['chunk']['type_fields'].update(context_format='unsupported-v2')]:
            with self.subTest(change=change):
                candidate = copy.deepcopy(original); change(candidate)
                out = build_context([candidate], 10000, len)
                self.assertFalse(out['evidence'])
                self.assertIn('invalid_reviewed_context:'+candidate['chunk']['chunk_id'],out['gaps'])

    def test_overlap_does_not_drop_limitation_and_budget_keeps_complete_record(self):
        from backend.bintanong_retrieval.context import build_context
        limited = self.limited_candidate()
        plain = copy.deepcopy(limited)
        plain['chunk'].update(chunk_id='prior', chunker_version='legacy', type_fields={}, text='Submit the form.')
        out = build_context([plain, limited], 10000, len)
        self.assertEqual(len(out['evidence']), 2)
        self.assertIn('Unavailable information:', out['context'])
        self.assertEqual(out['evidence'][1]['text'],limited['chunk']['text'])
        self.assertEqual(len(out['evidence'][1]['citations']),1)
        complete = build_context([limited],10000,len)
        small = build_context([limited],len(complete['context'])-1,len)
        self.assertFalse(small['evidence'])
        self.assertIn('context_budget:'+limited['chunk']['chunk_id'],small['gaps'])
        self.assertFalse(self.build(include_source_limits=True,token_cap=8)['chunks'])

    def test_no_gap_opt_in_preserves_scalar_associations_and_literal_blank(self):
        from backend.bintanong_retrieval.context import build_context
        self.rows[0]['fields'].append(self.field('fee',''))
        chunk = self.build(include_source_limits=True)['chunks'][0]
        candidate={'chunk':chunk,'spans':chunk['spans'],'version':self.version.model_dump(mode='json'),
            'neighbors':[],'similarity':0.9}
        out=build_context([candidate],10000,len)
        self.assertIn('"source_blank":true',out['context'])
        self.assertIn('"name":"fee"',out['context'])
        self.assertEqual(chunk['type_fields']['source_limits'],[])

    def test_stored_rpc_rows_keep_limits_without_contract_only_fields(self):
        from backend.bintanong_retrieval.context import build_context
        candidate=self.limited_candidate()
        original_text=candidate['chunk']['text']
        for key in ['schema_version','spans','register_binding']:
            candidate['chunk'].pop(key,None)
        candidate['chunk'].update(created_at='synthetic',source_verification='verified',content_review='reviewed')
        for i,span in enumerate(candidate['spans']):
            span.pop('schema_version',None)
            span.update(span_id='synthetic-'+str(i),chunk_id=candidate['chunk']['chunk_id'],span_order=i,created_at='synthetic')
        out=build_context([candidate],10000,len)
        self.assertEqual(out['evidence'][0]['text'],original_text)
        candidate['spans'][0]['span_order']=1
        self.assertFalse(build_context([candidate],10000,len)['evidence'])

    def test_removed_format_markers_or_partial_span_set_cannot_hide_limits(self):
        from backend.bintanong_retrieval.context import build_context
        self.rows[0]['fields'].append(self.field('office','Registry'))
        self.anchors['step-1']['office']=[self.span('office','Registry')]
        original=self.limited_candidate()
        for edit in ['markers','missing_span','reordered_spans']:
            candidate=copy.deepcopy(original)
            if edit=='markers':
                candidate['chunk']['type_fields'].pop('context_format')
                candidate['chunk']['type_fields'].pop('source_limits')
            elif edit=='missing_span':candidate['spans']=candidate['spans'][:1]
            else:candidate['spans'].reverse()
            out=build_context([candidate],10000,len)
            self.assertFalse(out['evidence'])

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
