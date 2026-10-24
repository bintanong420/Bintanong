"""Owner, 25 Oct 2026 (step 2 item g, "host-written"): a grading-scale question gets a host-written reply
from the owner-approved printed undergraduate grading table, bound to the reviewed Handbook page that a
retrieved card cites. No model call. Rows and the anchor here are fictional (patched in)."""
import asyncio
import hashlib
import json

import pytest

from backend.bintanong_generation import grade_reply
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_evidence import integrated
from test_generation_fee_reply import DraftModel, NoModel

ROWS = (('1.0', '90-100', 'Top'), ('2.0', '80-89', 'Good'), ('3.0', '70-79', 'Passed'), ('4.0', None, 'Condition'),
        ('Inc.', None, 'Incomplete'), ('5.0', None, 'Failed'), ('NC', None, 'No credit'))
CARD = dict(fields=[dict(name='grade', source_blank=False, value='1.0')], source_limits=[])


def grade_integration(text, *, language='en', subject='grading_scale'):
    value = integrated('RAG', text=text).model_dump(mode='json')
    passage = value['evidence']['documents']['passages'][0]
    passage['text'] = json.dumps(CARD)
    value['response_style'] = language
    value['understanding']['parts'][0].update(subject_id=subject, requested_claims=['printed grade meaning'])
    assert value['understanding']['question_sha256'] == hashlib.sha256(text.encode()).hexdigest()
    return IntegrationResult.parse(value)


@pytest.fixture
def table(monkeypatch):
    citation = grade_integration('x').evidence.documents.passages[0].citations[0]
    monkeypatch.setattr(grade_reply, 'ROWS', ROWS)
    monkeypatch.setattr(grade_reply, 'TABLE_PAGE', (citation.version_id, citation.page))


def generate(text, model, **kwargs):
    return asyncio.run(Generator(model).generate(text, grade_integration(text, **kwargs)))


PASSING = {
    'en': ('What is the passing grade?',
           ['The printed passing grade is 3.0 (70-79), rated "Passed".', '4.0 is "Condition" and 5.0 is "Failed".']),
    'fil': ('Ano ang pasadong grade?',
            ['Ang naka-print na passing grade ay 3.0 (70-79), na "Passed".',
             'Ang 4.0 ay "Condition" at ang 5.0 ay "Failed".']),
    'taglish': ('Ano yung passing grade?',
                ['Ang printed passing grade ay 3.0 (70-79), na "Passed".',
                 'Ang 4.0 ay "Condition" at ang 5.0 ay "Failed".'])}


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_passing_grade_question_gets_the_printed_passing_row_without_a_model_call(language, table):
    text, expected = PASSING[language]
    model = NoModel()
    answer = generate(text, model, language=language)
    assert model.calls == [] and answer.status == 'answered' and answer.validation == 'validated'
    assert [c.text for c in answer.claims] == expected
    card = prepare(grade_integration(text)).cards[0].evidence_id
    assert {c.evidence_ids for c in answer.claims} == {(card,)}
    assert [(e.part_id, e.claim_ids) for e in answer.part_ledger.entries] == [('r1', ('c1', 'c2'))]


@pytest.mark.parametrize('text, expected', [
    ('What does 4.0 mean?', ['4.0 is "Condition" in the printed undergraduate grading system.']),
    ('Is 3.0 passing?', ['3.0 (70-79) is "Passed" in the printed undergraduate grading system.']),
    ('What is INC and NC?', ['Inc. is "Incomplete" in the printed undergraduate grading system.',
                             'NC is "No credit" in the printed undergraduate grading system.']),
    ('What grade is 85?', ['2.0 (80-89) is "Good" in the printed undergraduate grading system.']),
    ('I got 1.00, what is that?', ['1.0 (90-100) is "Top" in the printed undergraduate grading system.'])])
def test_a_named_grade_mark_or_percentage_gets_its_printed_row(text, expected, table):
    answer = generate(text, NoModel())
    assert answer.status == 'answered' and [c.text for c in answer.claims] == expected


def test_a_named_row_in_filipino_and_taglish(table):
    assert [c.text for c in generate('Ano ang 5.0?', NoModel(), language='fil').claims] == [
        'Sa naka-print na undergraduate grading system, ang 5.0 ay "Failed".']
    assert [c.text for c in generate('Ano meaning ng 2.0?', NoModel(), language='taglish').claims] == [
        'Sa printed undergraduate grading system, ang 2.0 (80-89) ay "Good".']


def test_a_percentage_outside_the_printed_ranges_is_not_mapped(table):
    answer = generate('Is 65 a passing grade?', NoModel())
    assert [c.text for c in answer.claims] == PASSING['en'][1]  # passing reply; 65 is never given a grade


@pytest.mark.parametrize('text', ['What does 2.05 mean?', 'What does 12.0 mean?'])
def test_a_longer_number_is_not_read_as_a_printed_grade(text, table):
    answer = generate(text, NoModel())
    assert not any(c.text.startswith('2.0 ') for c in answer.claims)


def test_a_general_grading_question_gets_the_whole_printed_table(table):
    answer = generate('How does the grading system work?', NoModel())
    assert [c.text for c in answer.claims] == [
        'The printed undergraduate grades are: 1.0 (90-100) Top; 2.0 (80-89) Good; 3.0 (70-79) Passed.',
        'Other printed marks: 4.0 Condition; Inc. Incomplete; 5.0 Failed; NC No credit.']


@pytest.mark.parametrize('anchor', [('ver-' + 'f' * 64, 1), (None, 99)])
def test_without_a_retrieved_card_from_the_reviewed_table_page_the_model_explains(anchor, table, monkeypatch):
    version, page = grade_reply.TABLE_PAGE
    monkeypatch.setattr(grade_reply, 'TABLE_PAGE', (anchor[0] or version, anchor[1]))
    model = DraftModel()
    answer = generate('What is the passing grade?', model)
    assert model.calls and answer.status == 'insufficient_evidence'


def test_another_topic_is_not_answered_from_the_table(table):
    model = DraftModel()
    answer = generate('What is the passing grade?', model, subject='overload')
    assert model.calls and answer.status == 'insufficient_evidence'


def test_shipped_table_is_the_owner_approved_page_46_reading():
    """Owner, 25 Oct 2026: 2021 Student Handbook physical p.46, 2.2 Undergraduate Level, every row."""
    assert grade_reply.TABLE_PAGE == ('ver-4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8', 46)
    assert len(grade_reply.ROWS) == 18 and [r for r in grade_reply.ROWS if r[2] == 'Passed'] == [('3.0', '75-76', 'Passed')]
