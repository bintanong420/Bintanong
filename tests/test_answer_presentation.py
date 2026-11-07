"""Presentation is a bounded projection of validated part witnesses."""
import pytest
from types import SimpleNamespace
from backend.bintanong_api.answer_presentation import build_answer_presentation, AnswerPresentationV2
from test_api_presentation import answer_for


@pytest.mark.parametrize('route', ['RAG', 'Symbolic', 'Hybrid'])
def test_presentation_preserves_mapped_parts_and_released_sources(route):
    answer = answer_for(route)
    view = build_answer_presentation(answer)
    assert view['schemaVersion'] == 'bintanong-answer-presentation-v2'
    assert view['coverageState'] == 'complete'
    assert [p['partId'] for p in view['parts']] == [e.part_id for e in answer.part_ledger.entries]
    assert all(p['state'] == 'answered' for p in view['parts'])
    released = {c.evidence_id for c in answer.citations}
    assert all(set(p['sourceIds']) <= released for p in view['parts'])
    AnswerPresentationV2.model_validate(view)


def test_unvalidated_control_uses_legacy_text_fallback():
    answer = answer_for('Hybrid').model_copy(update={'status': 'insufficient_evidence', 'validation': 'control_fallback'})
    assert build_answer_presentation(answer) is None


def test_partial_has_visible_unavailable_part_without_borrowing_sources():
    answer = answer_for('RAG')
    ledger = answer.part_ledger
    entry = ledger.entries[0].model_copy(update={'part_id': 'r8', 'status': 'unavailable', 'claim_ids': (), 'reason': 'source_gap'})
    answer = answer.model_copy(update={'part_ledger': ledger.model_copy(update={
        'entries': ledger.entries + (entry,), 'status': 'some_parts_unavailable'})})
    view = build_answer_presentation(answer)
    assert view['coverageState'] == 'partial'
    assert view['parts'][-1]['state'] == 'unavailable'
    assert view['parts'][-1]['sourceIds'] == []


def test_unreleased_claim_reference_falls_back_instead_of_displaying_it():
    answer = answer_for('RAG')
    assert build_answer_presentation(answer.model_copy(update={'citations': ()})) is None


def test_compound_children_keep_their_own_result_and_conditional_qualifier():
    child = answer_for('Symbolic')
    parent = SimpleNamespace(**{**child.__dict__, 'part_answers': (
        SimpleNamespace(part_id='r1', evidence_need='structured', answer=child),
        SimpleNamespace(part_id='r2', evidence_need='structured', answer=child))})
    view = build_answer_presentation(parent)
    assert [part['partId'] for part in view['parts']] == ['r1', 'r2']
    assert all(part['conditional'] for part in view['parts'])


def test_recorded_source_limits_remain_adjacent_to_the_supported_part():
    answer = answer_for('RAG')
    limited = tuple(card.model_copy(update={'text': '{"fields":[],"source_limits":["missing field"]}'})
                    for card in answer.citations)
    view = build_answer_presentation(answer.model_copy(update={'citations': limited}))
    assert any(block['type'] == 'source_notice' for part in view['parts'] for block in part['blocks'])


def test_source_gap_is_not_presented_as_absent_reviewed_information():
    answer = answer_for('RAG').model_copy(update={'language': 'en'})
    notices = {}
    for reason in ('source_gap', 'not_in_evidence'):
        entry = answer.part_ledger.entries[0].model_copy(update={
            'part_id': 'r8', 'status': 'unavailable', 'claim_ids': (), 'reason': reason})
        ledger = answer.part_ledger.model_copy(update={
            'entries': answer.part_ledger.entries + (entry,), 'status': 'some_parts_unavailable'})
        view = build_answer_presentation(answer.model_copy(update={'part_ledger': ledger}))
        notices[reason] = view['parts'][-1]['blocks'][0]['text']
    assert 'incomplete or unclear' in notices['source_gap']
    assert notices['source_gap'] != notices['not_in_evidence']
