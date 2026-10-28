"""Synthetic printed openings and owner-approved topic families; no institutional policy is asserted."""
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from backend.bintanong_routing.prompt import build_messages
from backend.bintanong_routing import topic_selection
from backend.bintanong_runtime import research
from backend.bintanong_runtime.research import topic_menu
from test_routing_validation import registry

LONG_BODY = ('7. How to file fictional slips? A. Students shall secure a fictional slip at the '
             'Fictional Office upon payment at the Fictional Cashier. B. The slip is signed.')


def body_inputs(body=LONG_BODY, limits=(), subject='fictional_policy'):
    review = dict(subject_id=subject, claim='printed fictional fields', finding='visible_fields',
        reviewed_chunk_ids=['chunk-a'], field_refs=[dict(reading_id='body-a', field_name='body')])
    catalogue = dict(assignments=[dict(reading_id='body-a', subject_id=subject)])
    chunk = dict(chunk_id='chunk-a', type_fields=dict(reading_id='body-a'), text=json.dumps(dict(
        fields=[dict(name='body', value=body, source_blank=False)], source_limits=list(limits))))
    return dict(reviews=[review]), catalogue, [chunk]


def candidate(register, catalogue, chunks):
    return topic_menu(register, catalogue=catalogue, chunks=chunks, routing_context=True)


def test_long_reviewed_body_supplies_a_verbatim_opening_cut_at_a_word():
    topic, = candidate(*body_inputs())
    assert topic.source_opening == ('7. How to file fictional slips? A. Students shall secure a fictional '
                                    'slip at the Fictional Office…')
    assert LONG_BODY.startswith(topic.source_opening[:-1])


def test_short_reviewed_body_is_its_own_complete_opening():
    topic, = candidate(*body_inputs('FICTIONAL RESIDENCE. Residence means years enrolled.'))
    assert topic.source_opening == 'FICTIONAL RESIDENCE. Residence means years enrolled.'


def test_a_not_stated_limit_keeps_the_opening_but_a_source_defect_withholds_it():
    not_stated = dict(resolution='unresolved', issue='claim_not_stated', affected_claims=['fee'])
    topic, = candidate(*body_inputs(limits=[not_stated]))
    assert topic.source_opening is not None
    defect = dict(resolution='unresolved', issue='source_cutoff')
    topic, = candidate(*body_inputs(limits=[defect]))
    assert topic.source_opening is None


def test_default_menu_and_serialization_carry_no_opening_or_family():
    register, catalogue, chunks = body_inputs()
    topic, = topic_menu(register, catalogue=catalogue, chunks=chunks)
    assert topic.source_opening is None and topic.family is None
    dumped = topic.model_dump(mode='json')
    assert 'source_opening' not in dumped and 'family' not in dumped


def test_opening_reaches_both_the_selector_menu_and_the_router_menu():
    topic, = candidate(*body_inputs())
    selector = topic_selection.build_messages('How do I file a slip?', (topic,))[0]['content']
    assert topic.source_opening in selector
    context = RequestContext(session_id='sess-a', request_id='req-a')
    router = build_messages('How do I file a slip?', context, (), registry(), (topic,))[0]['content']
    assert topic.source_opening in router


def test_approved_family_is_attached_to_its_member_topics(monkeypatch):
    monkeypatch.setattr(research, 'TOPIC_FAMILIES', {'fictional_policy': 'fictional_slips'})
    topic, = candidate(*body_inputs())
    assert topic.family == 'fictional_slips'


def menu(*families):
    return tuple(DocumentTopic(subject_id=f'topic_{i}', claims=(f'printed clause {i}',), family=family)
                 for i, family in enumerate(families))


def selection(*ids):
    return dict(schema_version=topic_selection.VERSION, subject_ids=list(ids), ambiguous=False)


def test_selected_topics_keep_their_order_and_family_siblings_follow_in_menu_order():
    topics = menu('slips', None, 'slips', 'other', 'slips')
    chosen = topic_selection.selected_topics(selection('topic_2', 'topic_1'), topics)
    assert [t.subject_id for t in chosen] == ['topic_2', 'topic_1', 'topic_0', 'topic_4']


def test_family_expansion_beyond_the_selection_bound_is_unavailable_not_truncated():
    topics = menu(*(['slips'] * 9))
    with pytest.raises(ValueError, match='topic_selection_unavailable'):
        topic_selection.selected_topics(selection('topic_0'), topics)


def test_owner_approved_batch_one_families():
    families = {}
    for subject, family in research.TOPIC_FAMILIES.items():
        families.setdefault(family, set()).add(subject)
    assert families == {
        'drop_add_change_subjects': {'charter_dac', 'handbook_drop_shift_faq', 'handbook_dac_policy',
                                     'handbook_change_sections'},
        'refund_of_school_fees': {'charter_refund', 'handbook_school_fees_refund'},
        'leaving_palsu_transfer_credentials': {'charter_transfer', 'handbook_transfer_clearance'},
        'transferring_into_palsu': {'handbook_transfer', 'handbook_transfer_credentials',
                                    'handbook_transfer_load'},
    }
