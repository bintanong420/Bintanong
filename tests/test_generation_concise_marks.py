"""Concise mark replies retain source conditions, conflicts and exact citation binding."""
from dataclasses import replace
import json

from backend.bintanong_generation.part_answers import PartExplanation, to_draft
from backend.bintanong_generation.validation import validate_draft
from test_generation_condition_connectives import pack_with


METHOD = ('3.4 REMOVAL OF “INC”. A fictional mark is given for missing requirements. '
          'Removal of the INC must be done by passing a fictional examination or meeting all requirements, '
          'after which the student receives a final result based on overall performance.')
APPROVAL = ('3.5 EXAMINATION FOR REMOVAL OR COMPLETION. Seek Fictional Dean approval and pay the printed fee. '
            'For a prerequisite, finish before enrollment. 3.6 FORFEITURE OF RIGHT TO REMOVE OR COMPLETE. '
            'Repeating the subject forfeits the right to complete it.')


def fixture():
    texts = [json.dumps(dict(fields=[dict(name='body', value=value, source_blank=False)],
        source_limits=[dict(issue='conflicting_deadlines', resolution='unresolved',
                            affected_claims=['fictional deadline precedence is unresolved'])]))
        for value in (METHOD, APPROVAL)]
    pack = pack_with(*texts, language='en')
    part = pack.understanding.parts[0].model_copy(update=dict(text='How to complete INC?', start=0, end=20,
        subject_id='grade_completion', requested_claims=('INC method', 'approval'), detail='whole'))
    pack = replace(pack, understanding=pack.understanding.model_copy(update=dict(parts=(part,))),
        record_coverage=(('grade_completion', 'INC method', tuple(c.evidence_id for c in pack.cards)),))
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION, release_id=pack.release_id,
        language='en', answers={'r1': dict(status='answered', claims=[dict(
            text='Complete requirements.', evidence_ids=[pack.cards[0].evidence_id])])}))
    return pack, explanation


def test_mark_method_leads_and_shared_limit_is_printed_once_without_losing_conditions():
    pack, explanation = fixture()
    draft, _ = to_draft(explanation, pack)
    text = '\n'.join(c.text for c in draft.claims)
    assert text.startswith('The source states: "Removal of the INC must')
    assert 'missing requirements' not in text
    assert all(value in text for value in ('Fictional Dean approval', 'printed fee', 'before enrollment',
        'forfeits the right', 'overall performance'))
    assert text.count('fictional deadline precedence is unresolved') == 1
    assert 'conflict' in text.lower()
    assert {r for c in draft.claims for r in c.evidence_ids} == {c.evidence_id for c in pack.cards}
    assert validate_draft(draft, pack) == ()


def test_tampering_with_the_concise_condition_is_rejected_by_the_same_fidelity_check():
    pack, explanation = fixture()
    draft, _ = to_draft(explanation, pack)
    value = draft.model_dump(mode='json')
    value['claims'][0]['text'] += ' Approval is automatic.'
    assert 'malformed_source_fidelity' in validate_draft(type(draft).parse(value), pack)


def test_omitting_shared_conflict_notice_cannot_use_the_compact_fidelity_form():
    pack, explanation = fixture()
    draft, _ = to_draft(explanation, pack)
    value = draft.model_dump(mode='json')
    value['claims'] = value['claims'][:-1]
    assert 'malformed_source_fidelity' in validate_draft(type(draft).parse(value), pack)


def test_a_source_limit_message_with_additional_applicability_is_preserved():
    pack, explanation = fixture()
    cards = []
    message = 'This deadline belongs only to fictional Cohort Q; applicability is not stated.'
    for card in pack.cards:
        record = json.loads(card.text)
        record['source_limits'][0]['message'] = message
        cards.append(card.model_copy(update=dict(text=json.dumps(record))))
    pack = replace(pack, cards=tuple(cards))
    draft, _ = to_draft(explanation, pack)
    text = '\n'.join(c.text for c in draft.claims)
    assert text.count(message) == 1


def test_compact_source_warning_omits_only_redundant_machine_wrapper():
    pack, explanation = fixture()
    cards = []
    for card in pack.cards:
        record = json.loads(card.text)
        record['source_limits'][0]['message'] = ('Unavailable information: fictional deadline precedence. '
            'Source limitation remains unresolved (conflicting_deadlines).')
        cards.append(card.model_copy(update=dict(text=json.dumps(record))))
    pack = replace(pack, cards=tuple(cards))
    draft, _ = to_draft(explanation, pack)
    text = '\n'.join(c.text for c in draft.claims)
    assert text.count('fictional deadline precedence') == 1
    assert 'conflicting_deadlines' not in text and 'Completion deadlines conflict' in text


def test_grade_four_method_does_not_quote_a_separate_unasked_improvement_section():
    pack, _ = fixture()
    body = ('3.3 REMOVAL OF ‘4’. Complete fictional removal examination or repeat the activity. '
            'Only one removal examination is allowed. 3.7 NO IMPROVEMENT OF GRADE. Separate fictional timing rule.')
    record = json.loads(pack.cards[0].text)
    record['fields'][0]['value'] = body
    part = pack.understanding.parts[0].model_copy(update=dict(text='How to remove grade 4?', end=22))
    pack = replace(pack, cards=(pack.cards[0].model_copy(update=dict(text=json.dumps(record))), pack.cards[1]),
        understanding=pack.understanding.model_copy(update=dict(parts=(part,))))
    from backend.bintanong_generation.grade_completion_reply import concise_mark_reply
    reply = concise_mark_reply(pack, part, {c.evidence_id for c in pack.cards})
    text = '\n'.join(c['text'] for c in reply)
    assert 'Only one removal examination' in text and 'Separate fictional timing' not in text
    assert 'conflict' in text.lower() and 'Fictional Dean approval' in text
