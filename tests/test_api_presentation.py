"""Phase 11 O4: students never see variable or function names. The canonical answer text (which the
validator checks byte for byte) stays unchanged; the student view is derived from it."""
import asyncio
import re
from types import SimpleNamespace

import pytest

from backend.bintanong_api.presentation import humanize_codes, student_text
from backend.bintanong_generation.render import _WORDS
from test_generation_loop import api as generation
from test_generation_pipeline import EchoEvidence
from test_orchestration_pipeline import api as orchestration, ports, resources, transport, ctx

_CODE = re.compile(r'\b[a-z]+(?:_[a-z]+)*:\S')


def answer_for(route):
    async def scenario():
        executor = orchestration().Orchestrator(transport(route),
                                                releases=ports().SyntheticReleaseProvider(resources()))
        pipeline = generation().AnswerPipeline(executor, generation().Generator(EchoEvidence(),
                                                                                explanation_profile='legacy'))
        return await pipeline.run('A1 policy', ctx())
    return asyncio.run(scenario())


@pytest.mark.parametrize('route', ['RAG', 'Symbolic', 'Hybrid'])
def test_student_text_has_no_ids_operations_or_codes(route):
    answer = answer_for(route)
    shown = student_text(answer)
    assert 'ev-' not in shown
    assert '_id=' not in shown and 'Check scope' not in shown
    if answer.structured_context is not None:
        assert answer.structured_context.operation not in shown
        assert (answer.structured_context.rule_bundle_version or 'never') not in shown
    assert not _CODE.search(shown), shown


@pytest.mark.parametrize('route', ['RAG', 'Symbolic', 'Hybrid'])
def test_student_text_keeps_the_claims_notice_and_decision(route):
    answer = answer_for(route)
    shown = student_text(answer)
    lines = answer.text.splitlines()
    assert lines[0] not in shown  # candidate-preview line left out (owner, 29 Oct 2026)
    for claim in answer.claims:
        assert claim.text in shown
    if answer.decision is not None:
        assert lines[lines.index(next(l for l in lines if l.startswith('You meet the reviewed') or
                                      l.startswith('Pasok ka sa reviewed') or l.startswith('Ayon sa')))] in shown


def test_canonical_text_is_left_unchanged():
    answer = answer_for('Hybrid')
    before = answer.text
    student_text(answer)
    assert answer.text == before and 'ev-' in before


def test_compound_legacy_text_projects_each_validated_child_without_internal_scope_or_source_markers():
    structured, document = answer_for('Symbolic'), answer_for('RAG')
    children = (SimpleNamespace(part_id='r1', evidence_need='structured', answer=structured),
                SimpleNamespace(part_id='r2', evidence_need='document', answer=document))
    raw = '\n\n'.join(f'Bahagi {n}\n{part.answer.text}' for n, part in enumerate(children, 1))
    citations = tuple({c.evidence_id: c for child in children for c in child.answer.citations}.values())
    parent = SimpleNamespace(**{**structured.__dict__, 'part_answers': children, 'structured_context': None,
        'decision': None, 'claims': document.claims, 'citations': citations, 'text': raw})
    shown = student_text(parent)
    assert shown == f'Bahagi 1\n{student_text(structured)}\n\nBahagi 2\n{student_text(document)}'
    assert 'Check scope' not in shown and 'Sakop ng check' not in shown
    assert structured.structured_context.operation not in shown
    assert 'ev-' not in shown and not _CODE.search(shown)
    assert all(claim.text in shown for claim in document.claims)
    assert parent.text == raw


def test_eligible_prerequisite_reply_does_not_repeat_explanation_and_rule():
    from dataclasses import replace
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.render import render_text
    from test_orchestration_research_evidence import research_integration

    pack = replace(prepare(research_integration(facts=(('course-1', 'passed'),))), language='en')
    canonical = render_text(pack, (), 'answered', explanation='You told me you passed course-1.')
    answer = type('Answer', (), dict(text=canonical, language='en', claims=(), citations=(),
        structured_context=pack.structured_context, decision=pack.decision,
        decision_explanation='You told me you passed course-1.'))()
    shown = student_text(answer)
    assert shown.splitlines()[0] == "Yes, you can take course-2! You've passed its prerequisite, course-1."
    assert 'Rule:' not in shown and 'You told me' not in shown
    assert 'Rule:' in canonical and 'You told me' in canonical


def test_course_clarification_invites_a_name_as_well_as_a_code():
    from backend.bintanong_generation.render import _COURSE_NOT_FOUND
    for language in ('en', 'taglish'):
        text = _COURSE_NOT_FOUND[language].lower()
        assert 'name' in text and 'code' in text


@pytest.mark.parametrize('language, expected', [
    ('en', 'Conditions: CC 4/L: passed, CC 3/L: not known yet whether you completed it'),
    ('fil', 'Conditions: CC 4/L: pasado, CC 3/L: hindi pa alam kung natapos mo na'),
    ('taglish', 'Conditions: CC 4/L: passed, CC 3/L: hindi pa alam kung na-complete mo na'),
])
def test_condition_codes_become_plain_phrases(language, expected):
    assert humanize_codes('Conditions: passed:CC 4/L, completion_unknown:CC 3/L', language) == expected


def test_every_runtime_condition_prefix_has_a_phrase_in_every_language():
    prefixes = ('verified_none', 'identity_unreviewed', 'enrollment_conflict', 'enrolled', 'not_enrolled',
                'enrollment_unknown', 'completion_conflict', 'passed', 'not_completed', 'completion_unknown',
                'rule_unresolved')
    for language in ('en', 'fil', 'taglish'):
        for prefix in prefixes:
            assert not _CODE.search(humanize_codes(f'{prefix}:CC 9', language)), (language, prefix)


def test_an_unrecognized_code_never_shows_its_prefix():
    assert humanize_codes('Conditions: brand_new_code:CC 9', 'en') == 'Conditions: CC 9'


@pytest.mark.parametrize('language, label, expected', [
    ('taglish', 'Conditions', 'Conditions: CC 4/L: passed'),
    ('fil', 'Mga kondisyon', 'Mga kondisyon: CC 4/L: pasado'),
])
def test_condition_line_of_a_real_answer_is_shown_in_plain_words(language, label, expected):
    answer = answer_for('Symbolic')
    text = answer.text.replace('Conditions: fictional-prereq-met', f'{label}: passed:CC 4/L')
    shown = student_text(answer.model_copy(update={'text': text, 'language': language}))
    assert expected in shown.splitlines()


@pytest.mark.parametrize('tag', [' (e2)', ' (e2, e3)', ' (e2 and e3)'])
def test_student_text_drops_short_evidence_aliases_the_model_wrote_into_a_claim(tag):
    answer = answer_for('RAG')
    claim = answer.claims[0]
    tagged = claim.model_copy(update=dict(text=claim.text + tag))
    text = answer.text.replace(f'{claim.text} [', f'{tagged.text} [', 1)
    answer = answer.model_copy(update=dict(claims=(tagged, *answer.claims[1:]), text=text))
    shown = student_text(answer)
    assert tag.strip() not in shown and claim.text in shown


def test_student_text_drops_evidence_ids_after_a_multi_line_claim():
    # Hosted query validation 30 Oct 2026: host-rendered Charter steps are claims spanning several lines; their
    # evidence IDs follow the last line, so line-by-line matching showed students the raw IDs.
    answer = answer_for('RAG')
    claim = answer.claims[0]
    multi = claim.model_copy(update=dict(text='Step 1: Fill out the form\n  Person responsible: Window In-Charge'))
    text = answer.text.replace(f'{claim.text} [', f'{multi.text} [', 1)
    answer = answer.model_copy(update=dict(claims=(multi, *answer.claims[1:]), text=text))
    shown = student_text(answer)
    assert 'ev-' not in shown
    assert multi.text in shown


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_student_text_leaves_out_the_candidate_preview_line(language):
    # Owner, 29 Oct 2026: no "candidate preview" line; the guidance notice is shown separately and subtly.
    answer = answer_for('RAG').model_copy(update=dict(language=language))
    shown = student_text(answer)
    assert not any(word in shown for word in ('Candidate preview', 'Preview ng kandidato'))
    for claim in answer.claims:
        assert claim.text in shown


@pytest.mark.parametrize('language, line', [('en', "Here's what I found:"),
                                            ('fil', 'Batay sa ibinigay na ebidensya:'),
                                            ('taglish', 'Ito yung nakita ko:')])
def test_student_text_leaves_out_the_supplied_evidence_lead_in(language, line):
    # Owner, 2 Nov 2026: the reply goes straight to the answer; the canonical text keeps the line.
    answer = answer_for('RAG')
    canonical = answer.text.replace(_WORDS[answer.language]['answered'], line)
    answer = answer.model_copy(update=dict(language=language, text=canonical))
    shown = student_text(answer)
    assert line not in shown and line in answer.text
    for claim in answer.claims:
        assert claim.text in shown
