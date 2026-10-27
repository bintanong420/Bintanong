"""Host-written course-fact replies (printed title, units, year/semester); fictional data, no model call."""
import asyncio

import pytest

from backend.bintanong_api.presentation import student_text
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import IntegrationResult, RequestUnderstanding
from backend.bintanong_orchestration.integration import assemble
from backend.bintanong_symbolic.course_facts import CourseFactsResult
from test_generation_evidence import integrated
from test_generation_loop import Fake
from test_orchestration_integration import pin, symbolic

VERSION = 'ver-synth-handbook-1'


def course(code, title, units, year=1, term='first_semester', page=3):
    return dict(course_id='course-' + code.replace(' ', '').lower(), code=code, title=title, units=units,
                year=year, term=term, page=page, version_id=VERSION)


def result(predicate, inputs, courses=(), status='complete'):
    return CourseFactsResult.parse(dict(schema_version=CourseFactsResult.SCHEMA_VERSION, synthetic=True,
        predicate=predicate, inputs=inputs, status=status, courses=list(courses),
        scope=symbolic().scope.model_dump(mode='json') if status == 'complete' else None))


def source(facts, language='en'):
    evidence = assemble(pin(), 'Symbolic', course_facts=facts)
    plan = integrated('Symbolic').understanding.model_dump(mode='json')
    plan['operations'][0]['name'] = facts.predicate
    plan['predicate_request'] = dict(predicate=facts.predicate, inputs=[i.model_dump(mode='json') for i in facts.inputs])
    return IntegrationResult(understanding=RequestUnderstanding.parse(plan), schema_version=IntegrationResult.SCHEMA_VERSION,
        request_id='req-a', route='Symbolic', response_style=language, status=evidence.status, evidence=evidence, events=())


def term_inputs(year='1', semester='first_semester'):
    return [dict(name='curriculum_id', value='curriculum-a', fact_ref=None),
            dict(name='year_level', value=year, fact_ref=None), dict(name='semester', value=semester, fact_ref=None)]


COURSE_INPUTS = [dict(name='curriculum_id', value='curriculum-a', fact_ref=None),
                 dict(name='course_id', value='course-fict101', fact_ref=None)]


def answer(facts, language='en'):
    model = Fake()
    reply = asyncio.run(Generator(model, explanation_profile='parts').generate('Fictional check; fictional policy?', source(facts, language)))
    assert not model.calls
    return reply


def test_term_listing_names_each_printed_course_with_its_printed_units_and_page():
    reply = answer(result('list_term_courses', term_inputs(), [
        course('FICT 101', 'Fictional Computing', (('units.printed', '2/1'),)),
        course('FICT 102', 'Fictional Writing', (('units.printed', '3'),)),
        course('FICT 103', 'Fictional Thesis', ())]))
    assert reply.status == 'answered'
    text = student_text(reply)
    assert 'First year, first semester courses (prospectus p. 3):' in text
    assert 'FICT 101 Fictional Computing: 2/1 units' in text
    assert 'FICT 102 Fictional Writing: 3 units' in text
    assert 'FICT 103 Fictional Thesis: units not printed' in text
    assert '5 units' not in text and '6 units' not in text  # nothing is added up


def test_year_without_semester_groups_courses_under_each_printed_term():
    text = student_text(answer(result('list_term_courses', term_inputs(semester='any'), [
        course('FICT 101', 'Fictional Computing', (('units.printed', '3'),)),
        course('FICT 201', 'Fictional Practicum', (('units.lecture', '2'), ('units.rle', '1')), term='summer', page=4)])))
    assert 'First year, first semester courses (prospectus p. 3):' in text
    assert 'First year, summer courses (prospectus p. 4):' in text
    assert 'FICT 201 Fictional Practicum: LEC 2, RLE 1' in text


def test_term_with_no_printed_courses_says_so():
    text = student_text(answer(result('list_term_courses', term_inputs(year='5', semester='summer'))))
    assert 'The prospectus lists no courses for fifth year, summer.' in text


def test_course_lookup_gives_printed_units_and_placement():
    text = student_text(answer(result('course_facts', COURSE_INPUTS, [
        course('FICT 101', 'Fictional Computing', (('units.printed', '2/1'),), year=2, term='second_semester')])))
    assert 'FICT 101 Fictional Computing: 2/1 units; second year, second semester (prospectus p. 3).' in text


@pytest.mark.parametrize('language,heading,line', [
    ('fil', 'Ito ang subjects sa first year, first semester (prospectus p. 3):', 'FICT 101 Fictional Thesis: walang naka-print na units'),
    ('taglish', 'Ito ang subjects sa first year, first semester (prospectus p. 3):', 'FICT 101 Fictional Thesis: walang naka-print na units')])
def test_listing_follows_the_reply_language(language, heading, line):
    text = student_text(answer(result('list_term_courses', term_inputs(), [course('FICT 101', 'Fictional Thesis', ())]),
                               language))
    assert heading in text and line in text


def test_unreviewed_curriculum_gets_the_reviewed_sources_referral():
    reply = answer(result('list_term_courses', term_inputs(), status='not_reviewed'))
    assert reply.status == 'insufficient_evidence'
    assert "not in Bintanong's reviewed sources yet" in student_text(reply)


def test_research_release_refuses_synthetic_course_facts():
    from backend.bintanong_orchestration.contracts import ReleasePin
    research = ReleasePin.parse(dict(pin().model_dump(mode='json'), synthetic=False, research_ref='research-fictional'))
    with pytest.raises(ValueError, match='research_results_must_match_pin'):
        assemble(research, 'Symbolic', course_facts=result('course_facts', COURSE_INPUTS, [
            course('FICT 101', 'Fictional Computing', (('units.printed', '3'),))]))


def test_course_from_a_source_outside_the_pin_is_a_release_mismatch():
    foreign = dict(course('FICT 101', 'Fictional Computing', (('units.printed', '3'),)), version_id='ver-other-edition')
    evidence = assemble(pin(), 'Symbolic', course_facts=result('course_facts', COURSE_INPUTS, [foreign]))
    assert evidence.status == 'release_mismatch'
