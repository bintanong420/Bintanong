"""Thesis leader, 4 Nov 2026: after a term listing, "how about the hotel track?" re-asks it for the named track of the
same program-name family. Fictional programs; track words come from the catalog's own names."""
import asyncio
import json

import pytest

from backend.bintanong_routing.contracts import CatalogEntry, RequestContext
from backend.bintanong_routing.router import Router
from test_routing_contracts import context, proposal
from test_routing_course_facts import registry
from test_routing_router import FakeTransport, style_proposal


def entry(kind, entity, program, curriculum, *aliases):
    return CatalogEntry.parse(dict(kind=kind, entity_id=entity, program_id=program, curriculum_id=curriculum,
                                   aliases=list(aliases), course_code=aliases[0] if kind == 'course' else None,
                                   source_ref='ver-a', review_ref='review-a', reviewed=True))


def catalog(third=False):
    items = [entry('program', 'program-hotel', 'program-hotel', None, 'Hospitality Management',
                   'Hospitality Management (Hotel Track)'),
             entry('curriculum', 'curriculum-hotel', 'program-hotel', 'curriculum-hotel', 'Hotel Edition'),
             entry('program', 'program-culinary', 'program-culinary', None, 'Hospitality Management',
                   'Hospitality Management (Culinary Track)'),
             entry('curriculum', 'curriculum-culinary', 'program-culinary', 'curriculum-culinary', 'Culinary Edition')]
    if third:  # a second culinary track, so the word alone fits two programs
        items += [entry('program', 'program-kitchen', 'program-kitchen', None, 'Hospitality Management',
                        'Hospitality Management (Culinary Kitchen Track)'),
                  entry('curriculum', 'curriculum-kitchen', 'program-kitchen', 'curriculum-kitchen', 'Kitchen Edition')]
    return tuple(items)


MEMORY = dict(program_id='program-hotel', curriculum_id='curriculum-hotel', operation='list_term_courses',
              year_level=1, semester='first_semester')


def route(text, memory=MEMORY, third=False):
    # the model's reading of a message with no question in it: a bare clarification
    value = proposal(text=text, mentions=[], operations=[], route=None, control='clarify', parts=[])
    styles = [json.dumps(style_proposal('en', english=[text.split()[0]]))]
    ctx = context(program_id='program-hotel', curriculum_id='curriculum-hotel', conversation=memory)
    router = Router(FakeTransport(json.dumps(value), style_outputs=styles), catalog=catalog(third), registry=registry(),
                    documents_available=True, synthetic=True)
    return asyncio.run(router.route(text, RequestContext.parse(ctx)))


def inputs(result):
    return {i.name: i.value for i in result.decision.predicate_request.inputs}


@pytest.mark.parametrize('text', ['how about the culinary track?', 'what about culinary?'])
def test_a_named_track_re_runs_the_previous_term_listing_for_its_curriculum(text):
    result = route(text)
    assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert result.decision.predicate_request.predicate == 'list_term_courses'
    assert inputs(result) == {'curriculum_id': 'curriculum-culinary', 'year_level': '1', 'semester': 'first_semester'}
    assert (result.program_id, result.curriculum_id) == ('program-culinary', 'curriculum-culinary')


def test_a_word_fitting_two_tracks_asks_which_one():
    result = route('how about the culinary track?', third=True)
    assert result.decision.control == 'clarify' and result.diagnostic == 'program_switch_ambiguous'
    assert result.decision.missing_facts == ('program_choice:program-culinary', 'program_choice:program-kitchen')


@pytest.mark.parametrize('text,memory', [
    ('how about the hotel track?', MEMORY),  # the program already in use
    ('how about the nursing track?', MEMORY),  # no such track in the catalog
    ('how about the culinary track?', dict(MEMORY, operation='course_facts')),  # the previous turn was no term listing
    ('how about the culinary track for first year second sem?', MEMORY)])  # the message names its own term
def test_other_messages_are_not_a_track_switch(text, memory):
    result = route(text, memory)
    assert result.proposed.reason != 'program_switch_follow_up'


CHECK_MEMORY = dict(program_id='program-hotel', curriculum_id='curriculum-hotel',
                    course_id='course-hotel', operation='check_prerequisite_eligibility')


def check_route(*, missing=False, third=False, repeated=False):
    from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
    text = 'how about the culinary track?'
    value = proposal(text=text, mentions=[], operations=[], route=None, control='clarify', parts=[])
    items = [*catalog(third), entry('course', 'course-hotel', 'program-hotel', 'curriculum-hotel', 'H 1', 'Shared Title')]
    if not missing:
        items.append(entry('course', 'course-culinary', 'program-culinary', 'curriculum-culinary', 'H 1', 'Shared Title'))
    else:  # the same title with a different code must never count as the same course
        items.append(entry('course', 'course-other', 'program-culinary', 'curriculum-culinary', 'X 2', 'Shared Title'))
    if repeated:
        items.append(entry('course', 'course-repeat', 'program-culinary', 'curriculum-culinary', 'H 1'))
    capabilities = CapabilityRegistry({'check_prerequisite_eligibility': Capability(
        'synthetic_prerequisite_check', ('curriculum_id', 'course_id'))})
    ctx = RequestContext.parse(context(program_id='program-hotel', curriculum_id='curriculum-hotel',
        conversation=CHECK_MEMORY, facts=[dict(fact_id='fact-old', session_id='sess-a', program_id='program-hotel',
        curriculum_id='curriculum-hotel', course_id='course-hotel', state='passed', source='user_statement')]))
    router = Router(FakeTransport(json.dumps(value), style_outputs=[json.dumps(style_proposal('en', english=['how']))]),
                    catalog=items, registry=capabilities, documents_available=True, synthetic=True)
    return asyncio.run(router.route(text, ctx))


def test_eligibility_track_switch_repeats_the_check_using_the_new_curriculums_course_id():
    result = check_route()
    assert result.diagnostic == 'validated'
    assert result.decision.predicate_request.predicate == 'check_prerequisite_eligibility'
    assert inputs(result) == {'curriculum_id': 'curriculum-culinary', 'course_id': 'course-culinary'}
    assert result.query.session_fact_refs == () and result.claims == ()


def test_eligibility_track_switch_reports_a_course_missing_from_that_curriculum():
    result = check_route(missing=True)
    assert result.diagnostic == 'course_not_in_curriculum'
    assert result.decision.predicate_request is None
    assert result.decision.missing_facts == ('course_id',)


def test_eligibility_track_switch_with_two_matching_tracks_asks_which_program():
    result = check_route(third=True)
    assert result.diagnostic == 'program_switch_ambiguous'
    assert result.decision.missing_facts == ('program_choice:program-culinary', 'program_choice:program-kitchen')


def test_a_repeated_code_in_the_new_track_never_picks_a_course_by_title():
    result = check_route(repeated=True)
    assert result.decision.control == 'clarify'
    assert result.decision.predicate_request is None
    assert result.decision.missing_facts == ('course_choice:course-culinary', 'course_choice:course-repeat')


def test_orchestration_executes_the_switched_check_without_old_curriculum_facts():
    from test_orchestration_pipeline import api, ports, resources
    base = resources()
    items = (*catalog(), entry('course', 'course-hotel', 'program-hotel', 'curriculum-hotel', 'H 1'),
             entry('course', 'course-culinary', 'program-culinary', 'curriculum-culinary', 'H 1'))
    items = tuple(c.model_copy(update=dict(source_ref='ver-synth-handbook-1')) for c in items)
    release = ports().ReleaseResources(base.pin, items, base.registry, base.retrieval, base.symbolic)
    text = 'how about the culinary track?'
    value = proposal(text=text, mentions=[], operations=[], route=None, control='clarify', parts=[])
    ctx = RequestContext.parse(context(program_id='program-hotel', curriculum_id='curriculum-hotel',
        conversation=CHECK_MEMORY, facts=[dict(fact_id='fact-old', session_id='sess-a', program_id='program-hotel',
        curriculum_id='curriculum-hotel', course_id='course-hotel', state='passed', source='user_statement')]))
    transport = FakeTransport(json.dumps(value), style_outputs=[json.dumps(style_proposal('en', english=['how']))])
    asyncio.run(api().Orchestrator(transport, releases=ports().SyntheticReleaseProvider(release)).run(text, ctx))
    assert len(base.symbolic.calls) == 1
    request, switched = base.symbolic.calls[0]
    assert (switched.program_id, switched.curriculum_id, switched.facts) == (
        'program-culinary', 'curriculum-culinary', ())
    assert {i.name: i.value for i in request.inputs} == {
        'course_id': 'course-culinary', 'curriculum_id': 'curriculum-culinary'}
