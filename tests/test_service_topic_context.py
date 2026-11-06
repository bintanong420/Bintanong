"""Reviewed service labels reach the LLM menu without creating new answerable claims."""
from copy import deepcopy
import json

import pytest

from backend.bintanong_runtime.research import topic_menu
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.prompt import build_messages
from test_routing_validation import registry


def inputs():
    review = dict(subject_id='fictional_service', claim='visible service fields', finding='visible_fields',
        reviewed_chunk_ids=['chunk-a'], field_refs=[dict(reading_id='header-a', field_name=name)
                                                  for name in ('service_title', 'description')])
    register = dict(reviews=[review])
    catalogue = dict(assignments=[dict(reading_id='header-a', subject_id='fictional_service')])
    chunk = dict(chunk_id='chunk-a', type_fields=dict(reading_id='header-a'), text=json.dumps(dict(
        fields=[dict(name='service_title', value='ISSUANCE OF SLIP Q AND MARK EVALUATION', source_blank=False),
                dict(name='description', value='Fictional college assesses marks for registration.', source_blank=False),
                dict(name='requirement_1', value='Fictional card.', source_blank=False)], source_limits=[])))
    return register, catalogue, [chunk]


def menu_content(register, catalogue, chunks):
    topics = topic_menu(register, catalogue=catalogue, chunks=chunks)
    context = RequestContext(session_id='sess-a', request_id='req-a')
    system = build_messages('How do I get slip Q?', context, (), registry(), topics)[0]['content']
    return topics, system


def test_reviewed_service_purpose_is_available_to_the_model_as_topic_context():
    topics, system = menu_content(*inputs())
    assert 'ISSUANCE OF SLIP Q AND MARK EVALUATION' in system
    assert 'Fictional college assesses marks for registration.' in system
    assert 'Fictional card.' not in system
    assert topics[0].claims == ('visible service fields',) and not topics[0].not_stated


@pytest.mark.parametrize('mutation', ['missing_review', 'missing_field_ref', 'missing_membership',
    'other_topic', 'unassigned', 'not_stated', 'held', 'blank'])
def test_unreviewed_unassigned_or_held_description_never_enters_router_input(mutation):
    register, catalogue, chunks = inputs()
    if mutation == 'missing_review': register['reviews'] = []
    elif mutation == 'missing_field_ref': register['reviews'][0]['field_refs'] = []
    elif mutation == 'missing_membership': register['reviews'][0]['reviewed_chunk_ids'] = []
    elif mutation == 'other_topic': register['reviews'][0]['subject_id'] = 'other_service'
    elif mutation == 'unassigned': catalogue['assignments'] = []
    elif mutation == 'not_stated':
        register['reviews'][0]['finding'] = 'not_stated_in_selected_fields'
        register['reviews'].append(dict(subject_id='fictional_service',claim='other visible field',
                                       finding='visible_fields',field_refs=[],reviewed_chunk_ids=[]))
    else:
        fields = json.loads(chunks[0]['text'])
        if mutation == 'held': fields['source_limits'] = [dict(issue='source_cutoff', resolution='unresolved',
                                                             field_names=['description'], affected_claims=['end'])]
        else:
            for field in fields['fields']: field['source_blank'] = True
        chunks[0]['text'] = json.dumps(fields)
    topics, system = menu_content(register, catalogue, chunks)
    assert 'Fictional college assesses marks for registration.' not in system


def test_extra_unassigned_header_cannot_change_the_assigned_service_context():
    register, catalogue, chunks = inputs()
    extra = deepcopy(chunks[0])
    extra.update(chunk_id='chunk-b', type_fields=dict(reading_id='unassigned-header'))
    extra['text'] = extra['text'].replace('Fictional college', 'DO NOT USE this unrelated college')
    _, system = menu_content(register, catalogue, [*chunks, extra])
    assert 'Fictional college' in system and 'DO NOT USE' not in system


def test_inputs_are_detached_and_legacy_menu_without_context_keeps_its_display():
    register, catalogue, chunks = inputs()
    before = deepcopy((register, catalogue, chunks))
    _, system = menu_content(register, catalogue, chunks)
    assert (register, catalogue, chunks) == before
    register['reviews'][0]['field_refs'] = []
    _, plain = menu_content(register, catalogue, chunks)
    assert 'source_context' not in plain and 'visible service fields' in plain


def test_numbered_policy_clause_can_explain_topic_purpose_without_resolving_its_conflict():
    register,catalogue,chunks=inputs()
    register['reviews'][0]['field_refs']=[dict(reading_id='header-a',field_name='3.3')]
    chunks[0]['text']=json.dumps(dict(fields=[dict(name='3.3',value='Fictional conditional mark can be rechecked once.',source_blank=False)],
        source_limits=[dict(issue='conflicting_deadlines',resolution='unresolved',affected_claims=['applicable deadline'])]))
    topics,system=menu_content(register,catalogue,chunks)
    assert 'Fictional conditional mark can be rechecked once.' in system
    assert 'conflicting_deadlines' in system and 'applicable deadline' in system
    assert topics[0].claims==('visible service fields',)
    assert topics[0].not_stated==('applicable deadline',)


@pytest.mark.parametrize('issue',['malformed_source_condition','source_cutoff'])
def test_held_numbered_policy_clause_does_not_become_router_context(issue):
    register,catalogue,chunks=inputs()
    register['reviews'][0]['field_refs']=[dict(reading_id='header-a',field_name='3.3')]
    chunks[0]['text']=json.dumps(dict(fields=[dict(name='3.3',value='DO NOT ROUTE from this held clause.',source_blank=False)],
        source_limits=[dict(issue=issue,resolution='unresolved',affected_claims=['unknown continuation'])]))
    _,system=menu_content(register,catalogue,chunks)
    assert 'DO NOT ROUTE from this held clause.' not in system


def test_nontext_context_field_reference_cannot_crash_topic_construction():
    register,catalogue,chunks=inputs()
    register['reviews'][0]['field_refs'].append(dict(reading_id='header-a',field_name=None))
    topics,system=menu_content(register,catalogue,chunks)
    assert topics[0].claims==('visible service fields',)
    assert 'Fictional college assesses marks for registration.' in system


def test_router_receives_the_exact_reviewed_field_names_bound_to_each_selectable_claim():
    register,catalogue,chunks=inputs()
    topics,system=menu_content(register,catalogue,chunks)
    assert topics[0].claim_fields=={'visible service fields':('service_title','description')}
    assert '"fact_fields":[{"fact_indices":[0],"fields":["service_title","description"]}]' in system
    assert 'requirement_1' not in topics[0].claim_fields['visible service fields']


@pytest.mark.parametrize('mutation',['unassigned','unreviewed','blank','unknown_field','foreign_reading'])
def test_selector_field_names_require_the_same_reviewed_source_binding_as_context(mutation):
    register,catalogue,chunks=inputs()
    if mutation=='unassigned':catalogue['assignments']=[]
    elif mutation=='unreviewed':register['reviews'][0]['reviewed_chunk_ids']=[]
    elif mutation=='unknown_field':
        register['reviews'][0]['field_refs']=[dict(reading_id='header-a',field_name='NOT A SOURCE FIELD')]
    elif mutation=='foreign_reading':
        register['reviews'][0]['field_refs']=[dict(reading_id='other-reading',field_name='service_title')]
    else:
        value=json.loads(chunks[0]['text'])
        for field in value['fields']:field['source_blank']=True
        chunks[0]['text']=json.dumps(value)
    topics,_=menu_content(register,catalogue,chunks)
    assert topics[0].claim_fields=={}


def test_absent_field_metadata_does_not_add_an_empty_selection_payload():
    register,_,_=inputs()
    topics,system=menu_content(register,None,[])
    assert topics[0].claim_fields=={} and '"fact_fields":' not in system


def test_context_cannot_bind_fields_to_a_claim_that_is_not_selectable():
    from backend.bintanong_routing.contracts import DocumentTopic
    with pytest.raises(ValueError,match='context_requires_selectable_claim'):
        DocumentTopic(subject_id='fictional_service',claims=('known',),claim_fields={'other':('Cause',)})


@pytest.mark.parametrize('name',[[],{},None])
def test_malformed_extra_field_reference_cannot_crash_existing_valid_bindings(name):
    register,catalogue,chunks=inputs()
    register['reviews'][0]['field_refs'].append(dict(reading_id='header-a',field_name=name))
    topics,_=menu_content(register,catalogue,chunks)
    assert topics[0].claim_fields=={'visible service fields':('service_title','description')}


def test_repeated_field_sets_are_shown_once_with_complete_fact_positions():
    from backend.bintanong_routing.contracts import DocumentTopic
    claims=tuple(f'Fictional fact number {n}: action and consequences' for n in range(12))
    topic=DocumentTopic(subject_id='fictional_service',claims=claims,
        claim_fields={claim:('Cause','First consequence') for claim in claims})
    system=build_messages('What happens for fictional action Q?',
        RequestContext(session_id='sess-a',request_id='req-a'),(),registry(),(topic,))[0]['content']
    start=system.index('[{"fact_fields"')
    menu,_=json.JSONDecoder().raw_decode(system[start:])
    assert menu[0]['fact_fields']==[{'fields':['Cause','First consequence'],'fact_indices':list(range(12))}]
    assert menu[0]['facts']==list(claims)


def procedure_inputs():
    register, catalogue, chunks = inputs()
    register['reviews'][0]['field_refs'] = [dict(reading_id='header-a', field_name='application_fee_procedure')]
    chunks[0]['text'] = json.dumps(dict(fields=[dict(name='application_fee_procedure',
        value='Pay the fictional initial application charge.', source_blank=False),
        dict(name='application_form_office_context', value='Unbound office context must stay hidden.',
             source_blank=False)], source_limits=[]))
    return register, catalogue, chunks


def procedure_menu(register, catalogue, chunks):
    topics = topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)
    system = build_messages('How do I get slip Q?', RequestContext(session_id='sess-a', request_id='req-a'),
                            (), registry(), topics)[0]['content']
    return topics, system


def test_review_bound_partial_procedure_value_reaches_claim_context_without_new_claims_or_steps():
    topics, system = procedure_menu(*procedure_inputs())
    assert topics[0].claim_context == {'visible service fields': {
        'application_fee_procedure': 'Pay the fictional initial application charge.'}}
    assert 'Pay the fictional initial application charge.' in system
    assert 'Unbound office context must stay hidden.' not in system
    assert topics[0].claims == ('visible service fields',)
    assert 'step1_client_step' not in system


@pytest.mark.parametrize('mutation', ['unassigned', 'unreviewed', 'missing_membership', 'blank', 'held', 'wrong_suffix'])
def test_partial_procedure_context_keeps_existing_review_and_source_guards(mutation):
    register, catalogue, chunks = procedure_inputs()
    value = json.loads(chunks[0]['text'])
    if mutation == 'unassigned': catalogue['assignments'] = []
    elif mutation == 'unreviewed':
        register['reviews'][0]['finding'] = 'not_stated_in_selected_fields'
        register['reviews'].append(dict(subject_id='fictional_service', claim='other visible field',
                                       finding='visible_fields', field_refs=[], reviewed_chunk_ids=[]))
    elif mutation == 'missing_membership': register['reviews'][0]['reviewed_chunk_ids'] = []
    elif mutation == 'blank': value['fields'][0]['source_blank'] = True
    elif mutation == 'held':
        value['source_limits'] = [dict(issue='source_cutoff', resolution='unresolved',
                                      affected_claims=['missing continuation'])]
    else:
        value['fields'][0]['name'] = 'application_fee_procedure_note'
        register['reviews'][0]['field_refs'][0]['field_name'] = 'application_fee_procedure_note'
    chunks[0]['text'] = json.dumps(value)
    topics, system = procedure_menu(register, catalogue, chunks)
    assert not topics[0].claim_context
    assert 'Pay the fictional initial application charge.' not in system


def test_oversized_partial_procedure_context_is_not_silently_truncated():
    register, catalogue, chunks = procedure_inputs()
    value = json.loads(chunks[0]['text'])
    value['fields'][0]['value'] = 'x' * 1025
    chunks[0]['text'] = json.dumps(value)
    with pytest.raises(ValueError, match='routing_context_capacity'):
        topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)


def test_review_bound_client_step_location_reaches_both_routing_menus():
    from backend.bintanong_routing.topic_selection import build_messages as selection_messages
    register, catalogue, chunks = procedure_inputs()
    value = json.loads(chunks[0]['text'])
    value['fields'][0].update(name='step1_client_step', value='Obtain fictional form Q at Office Z.')
    register['reviews'][0]['field_refs'][0]['field_name'] = 'step1_client_step'
    chunks[0]['text'] = json.dumps(value)
    topics, system = procedure_menu(register, catalogue, chunks)
    assert topics[0].claim_context['visible service fields']['step1_client_step'] == 'Obtain fictional form Q at Office Z.'
    selector = selection_messages('Where do I get form Q?', topics)[0]['content']
    assert 'Obtain fictional form Q at Office Z.' in system
    assert 'Obtain fictional form Q at Office Z.' in selector


def test_large_aggregate_cannot_publish_unbound_client_step_hints():
    register, catalogue, chunks = procedure_inputs()
    names = ['step1_client_step', *(f'extra_field_{n}' for n in range(64))]
    chunks[0]['text'] = json.dumps(dict(fields=[dict(name=name, value='Fictional value.', source_blank=False)
        for name in names], source_limits=[]))
    register['reviews'][0]['field_refs'] = [dict(reading_id='header-a', field_name=name) for name in names]
    topics = topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)
    assert not topics[0].claim_fields and not topics[0].claim_context


@pytest.mark.parametrize('damage', ['held', 'oversized', 'many'])
def test_optional_client_step_hints_remain_bounded_and_do_not_launder_limits(damage):
    register, catalogue, chunks = procedure_inputs()
    count = 10 if damage == 'many' else 1
    fields = [dict(name=f'step{n}_client_step', value='x' * 1025 if damage=='oversized' else f'Fictional step {n}.',
                   source_blank=False) for n in range(1, count+1)]
    limits = [dict(issue='source_cutoff', resolution='unresolved')] if damage=='held' else []
    chunks[0]['text'] = json.dumps(dict(fields=fields, source_limits=limits))
    register['reviews'][0]['field_refs'] = [dict(reading_id='header-a', field_name=f['name']) for f in fields]
    topics = topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)
    context = topics[0].claim_context.get('visible service fields', {})
    assert len(context) == (8 if damage=='many' else 0)
