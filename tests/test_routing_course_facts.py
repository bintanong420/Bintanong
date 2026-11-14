"""Course-fact operations: a term listing targets a year/semester mention, a fact lookup a course."""
import importlib
import json

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_routing.contracts import Interpretation, RequestContext
from test_routing_contracts import context, proposal
from test_routing_validation import catalog
from test_routing_wire import quote


def registry():
    return CapabilityRegistry({
        'list_term_courses': Capability('synthetic_term_courses', ('curriculum_id', 'year_level', 'semester')),
        'course_facts': Capability('synthetic_course_facts', ('curriculum_id', 'course_id'))})


def term_proposal(text='Subjects in first year second sem?', term='first year second sem', name='list_term_courses',
                  kind='term'):
    start = text.find(term)
    return proposal(text=text, intent='term_courses', mentions=[dict(kind=kind, text=term, start=start,
                    end=start + len(term))], operations=[dict(name=name, target=0)])


def validate(text, value):
    return importlib.import_module('backend.bintanong_routing.validation').validate_interpretation(
        text, RequestContext.parse(context()), Interpretation.parse(value), catalog=catalog(),
        registry=registry(), documents_available=True, synthetic=True)


def inputs(result):
    return {i.name: i.value for i in result.decision.predicate_request.inputs}


def test_term_listing_binds_the_parsed_year_and_semester():
    text = 'Subjects in first year second sem?'
    result = validate(text, term_proposal(text))
    assert result.decision.route == 'Symbolic' and result.diagnostic == 'validated'
    assert result.decision.predicate_request.predicate == 'list_term_courses'
    assert inputs(result) == {'curriculum_id': 'curriculum-a', 'year_level': '1', 'semester': 'second_semester'}


def test_course_fact_lookup_binds_the_course():
    result = validate('Units of A1?', proposal(text='Units of A1?', intent='course_facts',
        mentions=[dict(kind='course', text='A1', start=9, end=11)], operations=[dict(name='course_facts', target=0)]))
    assert result.diagnostic == 'validated'
    assert inputs(result) == {'curriculum_id': 'curriculum-a', 'course_id': 'course-a'}


@pytest.mark.parametrize('name,kind', [('list_term_courses', 'course'), ('check_prerequisite_eligibility', 'term'),
                                       ('course_facts', 'term')])
def test_operation_targets_only_its_own_mention_kind(name, kind):
    with pytest.raises(ValueError, match='mention_reference'):
        Interpretation.parse(term_proposal(name=name, kind=kind))


def test_term_without_a_stated_year_asks_instead_of_guessing():
    text = 'Subjects in first sem?'
    result = validate(text, term_proposal(text, term='first sem'))
    assert result.decision.control == 'clarify' and result.diagnostic == 'unresolved_entity'
    assert result.decision.missing_facts == ()


def test_wire_term_mention_becomes_the_listing_target():
    api = importlib.import_module('backend.bintanong_routing.wire')
    text = 'What subjects are in first year?'
    wire = dict(schema_version='bintanong-interpretation-wire-v4', language='en', part_count=1,
        audience='undergraduate', intent='term courses', mentions=[dict(kind='term', quote=quote('first year'))],
        claims=[], operations=[dict(name='list_term_courses', target=quote('first year'))],
        parts=[dict(part_id='r1', quote=quote(text), evidence_need='structured', operation_indices=[0])],
        route='Symbolic', control=None, ambiguities=[])
    result = api.normalize_interpretation(text, api.WireInterpretation.parse(wire))
    assert result.mentions[result.operations[0].target].kind == 'term'


def test_router_prompt_describes_the_course_fact_operations_and_term_mentions():
    prompt = importlib.import_module('backend.bintanong_routing.prompt')
    text = prompt.SYSTEM_PROMPT
    assert 'course_facts' in text and 'list_term_courses' in text
    assert 'term mention' in text
    assert prompt.PROMPT_VERSION == 'bintanong-router-p11-v25'
    assert 'a school year is never a term mention' in text
    kinds = prompt.output_schema()
    assert '"term"' in json.dumps(kinds)


def year_wire(kind, text='What subjects are in second year BSIT?', term='second year'):
    program = [dict(kind='program', quote=quote('BSIT'))] if term != 'BSIT' else []
    return dict(schema_version='bintanong-interpretation-wire-v4', language='en', part_count=1,
        audience='undergraduate', intent='term courses',
        mentions=[*program, dict(kind=kind, quote=quote(term))],
        claims=[], operations=[dict(name='list_term_courses', target=quote(term))],
        parts=[dict(part_id='r1', quote=quote(text), evidence_need='structured', operation_indices=[0])],
        route='Symbolic', control=None, ambiguities=[])


def test_a_listing_target_labelled_as_another_kind_becomes_a_term_when_it_reads_as_one():
    # Live 25 Oct 2026: the model listed "second year" as a curriculum mention and targeted it.
    api = importlib.import_module('backend.bintanong_routing.wire')
    result = api.normalize_interpretation('What subjects are in second year BSIT?',
                                          api.WireInterpretation.parse(year_wire('curriculum')))
    assert result.mentions[result.operations[0].target].kind == 'term'


def test_a_listing_target_that_is_not_a_year_is_still_rejected():
    api = importlib.import_module('backend.bintanong_routing.wire')
    with pytest.raises(ValueError, match='invalid_term_quote_reference'):
        api.normalize_interpretation('What subjects are in BSIT?', api.WireInterpretation.parse(
            year_wire('curriculum', text='What subjects are in BSIT?', term='BSIT')))


def test_a_scope_mention_that_reads_as_a_year_level_becomes_a_term():
    # Live 25 Oct 2026: "second year" listed as a curriculum beside a "second year BSIT" listing target.
    api = importlib.import_module('backend.bintanong_routing.wire')
    wire = year_wire('curriculum')
    wire['operations'][0]['target'] = quote('second year BSIT')
    result = api.normalize_interpretation('What subjects are in second year BSIT?', api.WireInterpretation.parse(wire))
    assert [m.kind for m in result.mentions if m.text == 'second year'] == ['term']
    assert all(m.kind != 'curriculum' for m in result.mentions)
