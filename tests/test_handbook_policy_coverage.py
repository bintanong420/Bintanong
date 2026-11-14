"""Owner 29 Oct 2026 option A: a whole-section question on a Handbook policy section is answered from the clause
it cites; Charter or other sources, and reviewed step sequences, keep complete record coverage."""
from dataclasses import replace

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.grade_reply import HANDBOOK_VERSION
from backend.bintanong_generation.part_answers import PartExplanation, record_coverage_errors, to_draft
from test_service_record_coverage import CLAIM, SUBJECT, covered_integration


def cite_version(pack, version_id):
    cards = tuple(card.model_copy(update=dict(citations=tuple(
        c.model_copy(update=dict(version_id=version_id)) for c in card.citations))) for card in pack.cards)
    return replace(pack, cards=cards)


def first_record_draft(pack):
    card = pack.cards[0]
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id, language='en', answers=dict(r1=dict(status='answered', claims=[
            dict(text=card.text, evidence_ids=[card.evidence_id])]))))
    draft, slots = to_draft(explanation, pack)
    return draft.claims, slots


def test_handbook_policy_section_accepts_the_clause_it_cites():
    pack = cite_version(prepare(covered_integration()), HANDBOOK_VERSION)
    assert len(pack.cards) > 1
    assert record_coverage_errors(pack, *first_record_draft(pack)) == ()


def test_other_sources_still_need_every_record():
    pack = prepare(covered_integration())
    assert record_coverage_errors(pack, *first_record_draft(pack)) == ('missing_procedure_record_coverage',)


def test_handbook_reviewed_step_sequence_still_needs_every_record():
    pack = cite_version(prepare(covered_integration()), HANDBOOK_VERSION)
    ordered = replace(pack, record_order=((SUBJECT, CLAIM, tuple(c.evidence_id for c in pack.cards)),))
    assert record_coverage_errors(ordered, *first_record_draft(ordered)) == ('missing_procedure_record_coverage',)


def test_handbook_section_answer_must_cite_one_of_its_records():
    pack = cite_version(prepare(covered_integration()), HANDBOOK_VERSION)
    claims, slots = first_record_draft(pack)
    assert record_coverage_errors(pack, claims, dict(r1=('answered', ()))) == ('missing_procedure_record_coverage',)
