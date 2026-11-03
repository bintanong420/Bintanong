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
                                   aliases=list(aliases), source_ref='ver-a', review_ref='review-a', reviewed=True))


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
