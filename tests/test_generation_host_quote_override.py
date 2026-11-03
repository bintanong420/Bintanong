"""Owner 2 Nov 2026 ("ok host quotes"): for the owner-approved exact host quotes (#2 residence, #5 honours, leave length,
#10 overdue fine), a flipped "answers" verdict is not decisive when every claim is supported; the skip is recorded on
the answer. Drafts keep the full check. Fictional card wrappers around printed-style text."""
import json
from types import SimpleNamespace

from backend.bintanong_generation.part_answers import host_quote_override

RULE = ('Leave of absence shall be applied for in writing before the start of the semester. The application indicating '
        'the reason for the leave and the period which must not exceed one (1) academic year, shall be submitted to '
        'the Department Chair concerned for appropriate action and shall be subject to approval by the Dean.')
CARD = SimpleNamespace(evidence_id='ev-l', kind='document', citations=(),
                       text=json.dumps(dict(fields=[dict(name='body', source_blank=False, value=RULE)])))


def pack(text):
    part = SimpleNamespace(part_id='r1', subject_id='handbook_leave', text=text, requested_claims=('printed leave fields',))
    return SimpleNamespace(language='en', cards=(CARD,), understanding=SimpleNamespace(parts=(part,)))


def review(verdict, support='supported'):
    return SimpleNamespace(parts={'r1': verdict}, support=SimpleNamespace(verdicts=(SimpleNamespace(verdict=support),)))


def test_a_supported_host_quote_is_not_withheld_by_a_flipped_answers_verdict():
    assert host_quote_override(pack('How long can a leave of absence be?'), review('does_not_answer')) == ('r1',)


def test_an_unsupported_quote_or_a_draft_part_keeps_the_verdict():
    assert host_quote_override(pack('How long can a leave of absence be?'), review('does_not_answer', 'unsupported')) == ()
    assert host_quote_override(pack('How do I apply for a leave of absence?'), review('does_not_answer')) == ()
    assert host_quote_override(pack('How long can a leave of absence be?'), review('answers')) == ()


def test_the_override_is_recorded_only_when_used():
    from backend.bintanong_generation.contracts import CandidateAnswer
    assert 'host_quote_override' in CandidateAnswer.model_fields
    assert CandidateAnswer.model_fields['host_quote_override'].default == ()
