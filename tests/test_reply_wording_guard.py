"""Owner-approved conversational host replies, using synthetic decisions and source text."""
from dataclasses import replace

import pytest

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.render import fallback_status, render_text
from backend.bintanong_generation.required_context import _quote, _WORDS
from backend.bintanong_contracts.symbolic import RequirementView
from test_orchestration_research_evidence import research_integration


FORBIDDEN = ('Supported prerequisite check', 'conditions satisfied', 'a documented condition is unmet',
             'Please clarify the missing information before a conclusion can be given',
             'Paki-clarify muna ang missing information', 'Reviewed source fields (quoted)',
             'Based on the supplied evidence', 'Based sa supplied evidence')


@pytest.mark.parametrize('language', ['en', 'taglish'])
@pytest.mark.parametrize('facts,status', [((('course-1', 'passed'),), 'answered'),
                                        ((('course-1', 'failed'),), 'answered'),
                                        ((), 'clarification_needed')])
def test_checked_replies_use_conversational_words(language, facts, status):
    pack = replace(prepare(research_integration(facts=facts)), language=language)
    text = render_text(pack, (), status)
    assert not any(s.lower() in text.lower() for s in FORBIDDEN)
    if not facts:
        assert '?' in text and 'course-1' in text
    elif facts[0][1] == 'passed':
        assert ('Yes, you can take course-2!' if language == 'en' else
                'Oo, pwede mo nang i-take ang course-2!') in text


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_empty_clarify_asks_a_question_without_inventing_a_missing_field(language):
    pack = replace(prepare(research_integration()), language=language, decision=None,
                   requirement=None, missing_facts=(), structured_context=None)
    text = render_text(pack, (), 'clarification_needed')
    assert not any(s.lower() in text.lower() for s in FORBIDDEN)
    assert ('which subject or topic' if language == 'en' else 'subject o topic') in text
    assert '?' in text


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_quoted_procedure_uses_printed_steps_and_keeps_its_limitation(language):
    body = '7. How to submit a fictional form? A. Get Form Q. B. Submit Form Q.'
    record = dict(fields=[dict(name='body', value=body, source_blank=False)], source_limits=[
        dict(issue='claim_not_stated', resolution='unresolved', message='The final step is not printed.')])
    text = _quote(record, _WORDS[language])
    assert not any(s.lower() in text.lower() for s in FORBIDDEN)
    assert '\nA. Get Form Q.\nB. Submit Form Q.' in text
    assert ' '.join(body.split()) in ' '.join(text.replace('"', '').split())
    assert 'The final step is not printed.' in text


@pytest.mark.parametrize('status', ['held', 'evidence_unavailable', 'release_mismatch', 'invalid_output'])
def test_missing_or_held_information_is_not_an_outage(status):
    assert fallback_status(status) != 'temporarily_unavailable'


@pytest.mark.parametrize('status', ['error', 'timeout', 'busy', 'tool_error'])
def test_actual_tool_failures_stay_outages(status):
    assert fallback_status(status) == 'temporarily_unavailable'


@pytest.mark.parametrize('language', ['en', 'taglish'])
@pytest.mark.parametrize('kind', ['all_of', 'any_of'])
def test_prerequisite_list_keeps_alternatives_and_same_term_options(language, kind):
    pack = prepare(research_integration())
    tree = RequirementView(kind=kind, items=(RequirementView(kind='course', course_id='course-1'),
        RequirementView(kind='co_requisite', course_id='course-3')))
    missing = ('completion_unknown:course-1', 'completion_unknown:course-3')
    decision = pack.decision.model_copy(update=dict(missing_facts=missing,
        unknown_conditions=('enrollment_unknown:course-3',)))
    pack = replace(pack, language=language, requirement=tree, decision=decision, missing_facts=missing)
    text = render_text(pack, (), 'clarification_needed')
    assert not any(s.lower() in text.lower() for s in FORBIDDEN)
    connective = {('en', 'all_of'): 'both ', ('en', 'any_of'): 'either ',
                  ('taglish', 'all_of'): 'parehong ', ('taglish', 'any_of'): 'alinman sa '}[language, kind]
    assert connective in text
    assert ('taken in the same term' if language == 'en' else 'kinukuha nang sabay') in text
    assert 'course-1' in text and 'course-3' in text and '?' in text


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_unmet_alternatives_do_not_tell_the_student_to_pass_both(language):
    pack = prepare(research_integration(facts=(('course-1', 'failed'),)))
    tree = RequirementView(kind='any_of', items=(RequirementView(kind='course', course_id='course-1'),
        RequirementView(kind='course', course_id='course-3')))
    decision = pack.decision.model_copy(update=dict(violated_conditions=(
        'not_completed:course-1', 'not_completed:course-3')))
    pack = replace(pack, language=language, requirement=tree, decision=decision)
    text = render_text(pack, (), 'answered')
    from backend.bintanong_generation.decision_reply import decision_lines
    first = decision_lines(pack)[0]
    assert ('either course-1 or course-3' if language == 'en' else 'alinman sa course-1 o course-3') in first
    assert 'pass course-1 and course-3' not in text
    assert 'maipasa ang course-1 at course-3' not in text
