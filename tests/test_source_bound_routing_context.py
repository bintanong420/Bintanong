"""Synthetic reviewed label/column context; no institutional policy is asserted."""
from copy import deepcopy
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.prompt import build_messages, output_schema
from backend.bintanong_routing import topic_selection
from backend.bintanong_runtime.research import topic_menu
from test_service_topic_context import inputs
from test_routing_validation import registry


def candidate(register, catalogue, chunks):
    return topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)


def fixture(name='service_title_and_description', value='BORROWING FICTIONAL ITEMS. Students request items.'):
    register, catalogue, chunks = inputs()
    register['reviews'][0]['field_refs'] = [dict(reading_id='header-a', field_name=name)]
    chunks[0]['text'] = json.dumps(dict(fields=[dict(name=name, value=value, source_blank=False)], source_limits=[]))
    return register, catalogue, chunks


@pytest.mark.parametrize('name', ['service_title', 'service_title_and_description', 'service_context'])
def test_complete_review_bound_legacy_service_labels_reach_candidate_topics(name):
    args = fixture(name)
    before = deepcopy(args)
    topic, = candidate(*args)
    assert topic.source_labels == ('BORROWING FICTIONAL ITEMS. Students request items.',)
    assert topic.claims == ('visible service fields',)
    assert args == before


def test_default_topic_construction_and_serialization_preserve_the_old_metadata():
    args = fixture()
    topic, = topic_menu(args[0], catalogue=args[1], chunks=args[2])
    assert topic.model_dump(mode='json') == dict(subject_id='fictional_service',
        claims=['visible service fields'], claim_fields={'visible service fields':['service_title_and_description']},
        source_context=[], not_stated=[], cues=[])


@pytest.mark.parametrize('damage', ['missing_ref', 'missing_review', 'missing_member', 'foreign_subject',
    'unassigned', 'blank', 'not_stated', 'held', 'malformed_limit', 'malformed_field', 'duplicate_name'])
def test_unbound_held_or_malformed_records_supply_no_new_routing_labels(damage):
    register, catalogue, chunks = fixture()
    fields = json.loads(chunks[0]['text'])
    if damage == 'missing_ref': register['reviews'][0]['field_refs'] = []
    elif damage == 'missing_review': register['reviews'] = []
    elif damage == 'missing_member': register['reviews'][0]['reviewed_chunk_ids'] = []
    elif damage == 'foreign_subject': register['reviews'][0]['subject_id'] = 'other_service'
    elif damage == 'unassigned': catalogue['assignments'] = []
    elif damage == 'blank': fields['fields'][0]['source_blank'] = True
    elif damage == 'not_stated':
        register['reviews'][0]['finding'] = 'not_stated_in_selected_fields'
        register['reviews'].append(dict(subject_id='fictional_service', claim='other visible fields',
            finding='visible_fields', reviewed_chunk_ids=[], field_refs=[]))
    elif damage == 'held': fields['source_limits'] = [dict(resolution='unresolved', issue='source_cutoff')]
    elif damage == 'malformed_limit':
        fields['source_limits'] = [None, dict(resolution='unresolved', issue='malformed_source_condition')]
    elif damage == 'malformed_field': fields['fields'].insert(0, None)
    elif damage == 'duplicate_name': fields['fields'].append(deepcopy(fields['fields'][0]))
    chunks[0]['text'] = json.dumps(fields)
    if damage in ('malformed_limit', 'malformed_field', 'duplicate_name'):
        with pytest.raises(ValueError, match='invalid_routing_context'):
            candidate(register, catalogue, chunks)
        return
    topics = candidate(register, catalogue, chunks)
    assert all(not t.source_labels for t in topics)


def test_column_values_remain_bound_to_their_own_reviewed_claim():
    register, catalogue, chunks = fixture('descriptive_rating', 'Fictional satisfactory')
    register['reviews'].append(dict(subject_id='fictional_service', claim='different row',
        finding='visible_fields', reviewed_chunk_ids=['chunk-b'], field_refs=[]))
    topic, = candidate(register, catalogue, chunks)
    assert topic.claim_context == {'visible service fields': {'descriptive_rating': 'Fictional satisfactory'}}
    assert 'different row' not in topic.claim_context
    assert not topic.source_labels


def test_longer_candidate_field_sets_are_complete_while_default_remains_unchanged():
    register, catalogue, chunks = fixture()
    names = ['service_title_and_description'] + [f'row_{i}_client_step' for i in range(40)]
    register['reviews'][0]['field_refs'] = [dict(reading_id='header-a', field_name=n) for n in names]
    chunks[0]['text'] = json.dumps(dict(fields=[dict(name=n, value='Fictional value',
        source_blank=False) for n in names], source_limits=[]))
    default, = topic_menu(register, catalogue=catalogue, chunks=chunks)
    enhanced, = candidate(register, catalogue, chunks)
    assert default.claim_fields == {}
    assert enhanced.claim_fields == {'visible service fields': tuple(names)}


def test_column_context_requires_selectable_claim_and_bound_field_names():
    with pytest.raises(ValueError):
        DocumentTopic(subject_id='fictional_service', claims=('one',),
            claim_context={'other': {'grade':'Q'}})
    with pytest.raises(ValueError):
        DocumentTopic(subject_id='fictional_service', claims=('one',),
            claim_context={'one': {'grade':'Q'}})


def test_overlong_label_fails_preparation_instead_of_silently_truncating():
    with pytest.raises(ValueError, match='routing_context_capacity'):
        candidate(*fixture(value='L' * 1025))


def test_empty_new_fields_do_not_change_serialized_existing_topics():
    topic = DocumentTopic(subject_id='fictional_service', claims=('one',))
    assert 'source_labels' not in topic.model_dump(mode='json')
    assert 'claim_context' not in topic.model_dump(mode='json')


def test_missing_limitation_inventory_cannot_be_treated_as_no_source_limits():
    register, catalogue, chunks = fixture()
    record = json.loads(chunks[0]['text'])
    del record['source_limits']
    chunks[0]['text'] = json.dumps(record)
    with pytest.raises(ValueError, match='invalid_routing_context'):
        candidate(register, catalogue, chunks)


def test_compact_selection_shows_complete_bound_labels_without_turning_them_into_claims():
    topic, = candidate(*fixture())
    messages = topic_selection.build_messages('How do I borrow a fictional item?', (topic,))
    menu = json.loads(messages[0]['content'].split('\nMenu:', 1)[1])
    assert menu[0]['source_labels'] == ['BORROWING FICTIONAL ITEMS. Students request items.']
    assert menu[0]['subject_id'] == 'fictional_service'
    assert topic_selection.output_schema((topic,))['properties']['subject_ids']['items']['enum'] == ['fictional_service']
    assert topic.claims == ('visible service fields',)


def test_detailed_claim_values_keep_their_fact_index_and_not_stated_limits():
    topic = DocumentTopic(subject_id='fictional_marks', claims=('row Q', 'row Z'),
        claim_fields={'row Q':('grade','descriptive_rating'), 'row Z':('grade',)},
        claim_context={'row Q':{'grade':'Q','descriptive_rating':'Fictional satisfactory'},
                       'row Z':{'grade':'Z'}}, not_stated=('unprinted conversion',))
    context = RequestContext(session_id='sess-a', request_id='req-a')
    system = build_messages('What does mark Q mean?', context, (), registry(), (topic,))[0]['content']
    start = system.index('[{"fact_fields"')
    menu, _ = json.JSONDecoder().raw_decode(system[start:])
    assert menu[0]['fact_values'] == [
        {'fact_indices':[0], 'fields':{'grade':'Q','descriptive_rating':'Fictional satisfactory'}},
        {'fact_indices':[1], 'fields':{'grade':'Z'}}]
    assert menu[0]['not_stated'] == ['unprinted conversion']
    branches = output_schema((topic,))['$defs']['WirePart']['anyOf']
    assert branches[0]['properties']['requested_claims']['maxItems'] == 3  # three offered facts, below the cap
    assert branches[0]['properties']['requested_claims']['items']['enum'] == ['row Q','row Z','unprinted conversion']


def test_detailed_menu_receives_the_same_source_labels_as_the_compact_menu():
    topic, = candidate(*fixture('service_context', 'FICTIONAL ITEM SERVICE. Office Q;steps follow.'))
    system = build_messages('What is step one?', RequestContext(session_id='sess-a', request_id='req-a'),
        (), registry(), (topic,))[0]['content']
    assert '"source_labels":["FICTIONAL ITEM SERVICE. Office Q;steps follow."]' in system
