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
