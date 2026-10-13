"""Synthetic reviewed readings; no institutional source data or approvals."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ReviewedPolicyPreparationTests(unittest.TestCase):
    def setUp(self):
        self.pdf = b"synthetic original source"
        self.source = digest(self.pdf)
        self.event = json.dumps({"source_sha256": self.source,
            "owner_statement": "The displayed synthetic readings match.",
            "recorded_at": "2026-10-13T12:00:00+08:00"}).encode()
        self.event_id = digest(self.event)
        self.sources = {self.source: self.pdf}
        self.events = {self.event_id: self.event}
        self.reading = {"reading_id": "synthetic-row", "source_sha256": self.source,
            "version_id": "ver-synthetic", "intended_audience": "undergraduate",
            "applicability": "unknown", "applicability_evidence_ref": None,
            "fields": [self.field("description", "Review records", "Review records")],
            "gaps": [], "preserved_evidence": [{"artifact": "raw-table.json",
                "sha256": "a" * 64, "reason": "strict_reader_refusal"}]}

    def field(self, name, original, reviewed, **changes):
        result = {"name": name, "original_value": original, "reviewed_value": reviewed,
            "source_blank": False, "decision": "accepted",
            "review_event_sha256": self.event_id,
            "locator": {"physical_pages": [7], "field": name,
                "basis": "original synthetic layout", "raw_ref": "#/tables/0"}}
        result.update(changes)
        return result

    def build(self, readings=None):
        from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
        return build_reviewed_policy_bundle(readings or [self.reading],
            sources=self.sources, review_events=self.events)

    def test_confirmed_reading_stays_inactive_and_unknown_scope_is_withheld(self):
        result = self.build()
        self.assertTrue(result["candidate_only"])
        self.assertFalse(result["activation_eligible"])
        self.assertEqual(result["selection"]["undergraduate"], [])
        self.assertEqual(result["selection"]["unresolved"], ["synthetic-row"])
        self.assertEqual(result["readings"][0]["fields"][0]["decision"], "accepted")
        self.assertNotIn("chunks", result)

    def test_raw_and_reviewed_values_blanks_and_refusals_survive_without_mutation(self):
        self.reading["fields"] = [self.field("description", "cover", "diploma cover",
            decision="corrected"), self.field("percentage", "", "", source_blank=True)]
        before = copy.deepcopy(self.reading)
        result = self.build()
        self.assertEqual(result["readings"][0], before)
        self.assertEqual(self.reading, before)
        result["readings"][0]["fields"][0]["reviewed_value"] = "changed"
        self.assertEqual(self.reading, before)

    def test_changed_source_or_event_bytes_are_rejected(self):
        for mapping, key in [(self.sources, self.source), (self.events, self.event_id)]:
            with self.subTest(mapping=key):
                original = mapping[key]
                mapping[key] = b"changed"
                with self.assertRaisesRegex(ValueError, "digest"):
                    self.build()
                mapping[key] = original

    def test_an_event_from_another_source_cannot_confirm_a_field(self):
        event = json.dumps({"source_sha256": "b" * 64}).encode()
        self.events[digest(event)] = event
        self.reading["fields"][0]["review_event_sha256"] = digest(event)
        with self.assertRaisesRegex(ValueError, "source"):
            self.build()

    def test_pending_field_does_not_inherit_whole_step_confirmation(self):
        self.reading["fields"].append(self.field("condition", None, None,
            decision="pending", review_event_sha256=None))
        result = self.build()
        self.assertEqual(result["coverage"]["field_decisions"], {"accepted": 1,
            "corrected": 0, "unresolved": 0, "pending": 1})
        self.assertEqual(result["readings"][0]["fields"][1]["decision"], "pending")

    def test_source_gap_is_retained_with_the_confirmed_visible_fragment(self):
        self.reading["fields"] = [self.field("details", "during", "during")]
        self.reading["gaps"] = [{"gap_id": "cutoff", "field_names": ["details"],
            "issue": "source_cutoff", "visible_text": "during",
            "affected_claims": ["remaining steps", "process completion"],
            "locator": {"physical_pages": [7], "field": "details"}}]
        self.assertEqual(self.build()["readings"][0]["gaps"], self.reading["gaps"])

    def test_unknown_and_mixed_audiences_are_never_selected_by_default(self):
        for audience in ["unknown", "mixed"]:
            self.reading["intended_audience"] = audience
            self.assertEqual(self.build()["selection"]["unresolved"], ["synthetic-row"])

    def test_excluded_audiences_are_preserved_only_as_exclusions(self):
        for audience in ["medicine", "law", "graduate", "laboratory_school", "faculty", "staff"]:
            self.reading["intended_audience"] = audience
            result = self.build()
            self.assertEqual(result["selection"]["excluded"], ["synthetic-row"])
            self.assertEqual(result["selection"]["undergraduate"], [])

    def test_explicit_scope_evidence_can_select_undergraduate_preparation_only(self):
        self.reading.update(applicability="undergraduate",
            applicability_evidence_ref="scope-review.json#synthetic-row")
        self.reading["fields"][0]["reviewed_value"] = "Undergraduate Nursing; Registrar's staff"
        result = self.build()
        self.assertEqual(result["selection"]["undergraduate"], ["synthetic-row"])
        self.assertFalse(result["activation_eligible"])

    def test_scope_cannot_be_inferred_from_a_shared_heading(self):
        self.reading["original_heading"] = "Undergraduate / professional audience"
        self.reading["applicability"] = "undergraduate"
        with self.assertRaisesRegex(ValueError, "applicability"):
            self.build()

    def test_service_action_associations_pages_role_fragments_and_shared_fee_survive(self):
        actions = [{"action": "Evaluate request", "processing_time": "20 minutes",
            "responsible_person": "Evaluator / Records Officer", "office": "Registry",
            "conditions": None, "role_fragments": ["Evaluator /", "Records Officer"],
            "office_fragments": [{"page": 7, "text": "Reg"}, {"page": 8, "text": "istry"}]}]
        self.reading["fields"] = [self.field("subactions", actions, actions),
            self.field("shared_fee", {"text": "None", "source_page": 7},
                {"text": "None", "source_page": 7, "applies_to": "step-1"}),
            self.field("continuation_fee", "", "", source_blank=True)]
        self.reading["fields"][0]["locator"]["physical_pages"] = [7, 8]
        result = self.build()["readings"][0]
        self.assertEqual(result["fields"], self.reading["fields"])

    def test_invalid_or_unbound_readings_are_rejected(self):
        variants = [dict(source_sha256="b" * 64), dict(fields=[]), dict(reading_id=""),
            dict(intended_audience="student-ish"), dict(applicability="approved")]
        for change in variants:
            with self.subTest(change=change):
                row = copy.deepcopy(self.reading)
                row.update(change)
                with self.assertRaises(ValueError):
                    self.build([row])

    def test_duplicate_ids_missing_events_invalid_pages_and_blank_defaults_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.build([self.reading, self.reading])
        for change in [dict(review_event_sha256=None), dict(decision="approved"),
            dict(locator={"physical_pages": [True], "field": "description"}),
            dict(source_blank=True, reviewed_value=0),
            dict(source_blank=True, reviewed_value="No charge")]:
            with self.subTest(change=change):
                row = copy.deepcopy(self.reading)
                row["fields"][0].update(change)
                with self.assertRaises(ValueError):
                    self.build([row])

    def test_gap_must_name_an_existing_field_and_affected_claim(self):
        self.reading["gaps"] = [{"gap_id": "gap", "field_names": ["missing"],
            "issue": "cutoff", "visible_text": "for", "affected_claims": [],
            "locator": {"physical_pages": [7], "field": "missing"}}]
        with self.assertRaisesRegex(ValueError, "gap"):
            self.build()

    def test_multi_source_clarification_binds_each_named_source_without_rewriting_event(self):
        event = json.dumps({"source_hashes": {"first": self.source, "second": "b" * 64},
            "owner_statement": "These are reported origins; authority remains unknown."}).encode()
        self.events = {digest(event): event}
        self.reading["fields"][0].update(review_event_sha256=digest(event), decision="unresolved")
        result = self.build()
        self.assertEqual(result["review_events"][digest(event)], json.loads(event))
        self.assertEqual(result["coverage"]["field_decisions"]["unresolved"], 1)
        self.reading["source_sha256"] = "c" * 64
        self.sources["c" * 64] = b"not that hash"
        # Existing source integrity guards still apply before any event association.
        with self.assertRaisesRegex(ValueError, "digest"):
            self.build()

    def test_event_numbers_must_remain_finite_after_json_decoding(self):
        event = ('{"source_sha256":"'+self.source+'", "owner_statement":"Matches",'
            ' "metadata":1e999}').encode()
        self.events = {digest(event): event}
        self.reading['fields'][0]['review_event_sha256'] = digest(event)
        with self.assertRaisesRegex(ValueError, "finite"):
            self.build()

    def test_original_owner_correction_excerpts_are_usable_without_rewriting_event(self):
        event = json.dumps({"source_sha256": self.source,
            "owner_statement_excerpts": ["Restore complete step", "Link the roles"]}).encode()
        self.events = {digest(event): event}
        self.reading['fields'][0]['review_event_sha256'] = digest(event)
        self.assertEqual(self.build()['review_events'][digest(event)], json.loads(event))


if __name__ == "__main__":
    unittest.main()
