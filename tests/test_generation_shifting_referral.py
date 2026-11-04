"""Thesis leader, 4 Nov 2026: a shifting answer ends with a referral to the offices the retrieved text prints.
Fictional wording with the printed role names only."""
import json

import pytest

import test_generation_shifting_companion as companion
from backend.bintanong_generation.render import render_text
from backend.bintanong_generation.shifting_reply import shifting_referral

CROSS = ('4.1 Request to shift to another college: approved by the Dean of the College where he is enrolled and the '
         'Dean of the College where he intends to shift. 4.3 Approved requests are submitted to the Office of the '
         'University Registrar.')
FAQ = ('The Shifting forms shall be approved by the College Dean and by the College Guidance Practitioner. The approved '
       "shifting forms shall be submitted to the registrar's office.")


def pack(rule, faq, language='en'):
    companion.RULE = json.dumps(dict(fields=[dict(name='body', value=rule, source_blank=False)], source_limits=[]))
    companion.FAQ = json.dumps(dict(fields=[dict(name='body', value=faq, source_blank=False)], source_limits=[]))
    from dataclasses import replace
    return replace(companion.integration(), language=language)


def test_the_referral_names_each_printed_office_and_never_approves_a_shift():
    line = shifting_referral(pack(CROSS, FAQ))
    assert ('the Deans of your current college and the college you want to shift to, the College Guidance Practitioner '
            'and the Office of the University Registrar') in line
    assert 'Department Head' not in line and 'OSAS' not in line  # not printed in this text
    assert 'cannot evaluate your credits or approve a shift' in line


def test_a_same_college_rule_names_the_department_head_and_dean():
    line = shifting_referral(pack('4.2 A request to shift within the same college is endorsed by the Department Head '
                                  'and approved by the Dean.', 'Fictional steps with no office.'))
    assert 'the Department Head of your course' in line and 'your College Dean' in line and 'Registrar' not in line


def test_taglish_referral_keeps_the_printed_role_names():
    line = shifting_referral(pack(CROSS, FAQ, 'taglish'))
    assert line.startswith('Para mag-shift') and 'College Guidance Practitioner' in line and 'Hindi kayang' in line


def test_no_printed_office_means_no_referral_and_other_topics_get_none():
    assert shifting_referral(pack('4.1 Fictional rule.', 'Fictional steps.')) is None
    other = pack(CROSS, FAQ)
    from dataclasses import replace
    parts = tuple(p.model_copy(update=dict(subject_id='other_subject', requested_claims=('printed other fields',)))
                  for p in other.understanding.parts)
    assert shifting_referral(replace(other, understanding=other.understanding.model_copy(update=dict(parts=parts)))) is None


def test_an_answered_reply_ends_with_the_referral_before_the_citations():
    source = pack(CROSS, FAQ)
    text = render_text(source, (), 'answered')
    lines = text.splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith('To shift, take your request'))
    assert all(line.startswith('[') for line in lines[index + 1:])  # only citations follow


@pytest.mark.parametrize('status', ('insufficient_evidence', 'abstained'))
def test_an_unstated_shifting_detail_still_ends_with_the_printed_office_referral(status):
    source = pack(CROSS, FAQ, 'taglish')
    text = render_text(source, (), status, question_uncovered=(status == 'insufficient_evidence'))
    assert 'Para mag-shift, dalhin ang request mo sa' in text
    assert 'Office of the University Registrar' in text
    assert 'Deans ng current college mo' in text
