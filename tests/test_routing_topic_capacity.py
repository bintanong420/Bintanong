"""A larger reviewed source menu must not expand model-request output limits."""
import pytest

from backend.bintanong_routing.contracts import DocumentTopic, RequestPart
from backend.bintanong_routing.prompt import output_schema


@pytest.mark.parametrize('count',[39,64])
def test_reviewed_row_claims_fit_one_release_supplied_topic(count):
    claims = tuple('printed synthetic row '+str(i) for i in range(count))
    topic = DocumentTopic(subject_id='synthetic_policies',claims=claims)
    assert topic.claims == claims


@pytest.mark.parametrize('count',[39,64])
def test_larger_topic_choices_do_not_expand_the_model_claim_selection_limit(count):
    topic = DocumentTopic(subject_id='synthetic_policies',claims=tuple(
        'printed synthetic row '+str(i) for i in range(count)))
    schema = output_schema(topics=(topic,))
    constraints = []
    def visit(value):
        if isinstance(value,dict):
            if 'requested_claims' in value:
                choice = value['requested_claims']
                if isinstance(choice,dict) and choice.get('items',{}).get('enum'):
                    constraints.append(choice)
            for item in value.values():
                visit(item)
        elif isinstance(value,list):
            for item in value:
                visit(item)
    visit(schema)
    assert constraints
    assert all(c['maxItems'] == 8 for c in constraints)
    assert all(len(c['items']['enum']) == count for c in constraints)


def test_topic_capacity_and_requested_claim_count_remain_bounded():
    with pytest.raises(ValueError):
        DocumentTopic(subject_id='synthetic_policies',
            claims=tuple('printed synthetic row '+str(i) for i in range(65)))
    fields = dict(part_id='r1',text='synthetic question',start=0,end=18,evidence_need='document',
        operation_indices=(),subject_id='synthetic_policies')
    assert len(RequestPart(**fields,requested_claims=tuple(
        'printed synthetic row '+str(i) for i in range(8))).requested_claims) == 8
    with pytest.raises(ValueError):
        RequestPart(**fields,requested_claims=tuple('printed synthetic row '+str(i) for i in range(9)))
