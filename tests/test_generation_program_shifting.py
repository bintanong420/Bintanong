"""A generic program change must not assume a move to another college."""
from dataclasses import replace
import json

import pytest

from backend.bintanong_generation.part_answers import PartExplanation, to_draft
from backend.bintanong_generation.shifting_reply import shifting_referral
from test_generation_condition_connectives import pack_with


RULE = ('4. CHANGE OF COURSE 4.1 REQUEST TO SHIFT TO ANOTHER COLLEGE. '
        'A fictional request needs the Dean of the College where he is enrolled and the '
        'Dean of the College where he intends to shift. '
        '4.2 REQUEST TO SHIFT WITHIN THE SAME COLLEGE. A fictional request needs Department Head '
        'endorsement and Dean approval. 4.3 Approved requests go to the Office of the University Registrar.')
FAQ = '8. How to shift? A. Obtain the fictional form. B. Submit the approved form to the registrar.'


def fixture(question='Pano po lumipat ng kurso?', *, limits=()):
    records = [json.dumps(dict(fields=[dict(name='body', value=body, source_blank=False)],
                               source_limits=list(limits))) for body in (RULE, FAQ)]
    pack = pack_with(*records, language='taglish')
    part = pack.understanding.parts[0].model_copy(update=dict(text=question, start=0, end=len(question),
        subject_id='handbook_shifting', requested_claims=('printed shifting fields',), detail='whole'))
    refs = tuple(c.evidence_id for c in pack.cards)
    pack = replace(pack, understanding=pack.understanding.model_copy(update=dict(parts=(part,))),
        record_coverage=(('handbook_shifting', 'printed shifting fields', refs[:1]),
                         ('handbook_drop_shift_faq', 'printed FAQ 8 shifting steps', refs[1:])))
    explanation = PartExplanation.parse(dict(schema_version=PartExplanation.SCHEMA_VERSION,
        release_id=pack.release_id, language='taglish', answers={'r1': dict(status='answered', claims=[dict(
            text='Kung lilipat ka ng college, kailangan ang dalawang Dean.', evidence_ids=[refs[0]])])}))
    return pack, explanation


@pytest.mark.parametrize('question', ['Pano po lumipat ng kurso?', 'Paano po lumipat ng kurso?',
                                    'How can I change programs?'])
def test_generic_program_change_preserves_both_source_branches_and_faq_steps(question):
    pack, explanation = fixture(question)
    draft, _ = to_draft(explanation, pack)
    assert all(any(body in c.text for c in draft.claims) for body in (RULE, FAQ))
    assert {r for c in draft.claims for r in c.evidence_ids} == {c.evidence_id for c in pack.cards}


def test_explicit_cross_college_question_keeps_its_narrow_answer():
    pack, explanation = fixture('How can I shift to another college?')
    draft, _ = to_draft(explanation, pack)
    assert RULE not in '\n'.join(c.text for c in draft.claims)


def test_unresolved_source_limit_does_not_get_a_clean_whole_policy_reply():
    pack, explanation = fixture(limits=[dict(issue='claim_not_stated', resolution='unresolved',
                                           affected_claims=['fictional application deadline'])])
    from backend.bintanong_generation.shifting_reply import complete_program_shifting_reply
    assert complete_program_shifting_reply(pack, pack.understanding.parts[0],
                                           {c.evidence_id for c in pack.cards}) is None


def test_generic_referral_keeps_college_branches_conditional():
    pack, _ = fixture()
    line = shifting_referral(pack)
    assert 'kung ibang college' in line
    assert 'kung same college' in line


def test_cross_college_referral_does_not_add_same_college_instructions():
    pack, _ = fixture('How can I shift to another college?')
    assert 'kung same college' not in shifting_referral(pack)
