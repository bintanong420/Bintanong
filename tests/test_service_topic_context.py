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
