"""Distinct failures in pre-evidence question understanding;fictional inputs only."""
from copy import deepcopy

import pytest

from backend.bintanong_routing.contracts import Interpretation, RequestContext
from backend.bintanong_routing.validation import anchor_unique_quotes, validate_interpretation
from test_routing_contracts import context
from test_routing_validation import catalog, registry


TEXT = 'Can I take A1 and where do I file Form Q?'


def part(quote, need='document', operations=(), *, text=TEXT, ident='r1'):
    start = text.index(quote)
    return dict(part_id=ident, text=quote, start=start, end=start+len(quote),
                evidence_need=need, operation_indices=list(operations))


def proposal(**updates):
    value = dict(schema_version=Interpretation.SCHEMA_VERSION, language='en',
        audience='undergraduate', intent='Fictional check and procedure',
        mentions=[dict(kind='course', text='A1', start=11, end=13)], claims=[],
        operations=[dict(name='check_prerequisite_eligibility', target=0)],
        parts=[part('Can I take A1', 'structured', (0,)),
               part('where do I file Form Q?', ident='r2')],
        route='Hybrid', control=None, ambiguities=[], reason='Both requested paths')
    value.update(updates)
    return value


def validate(value):
    return validate_interpretation(TEXT, RequestContext.parse(context()),
        Interpretation.parse(value), catalog=catalog(), registry=registry(),
        documents_available=True, synthetic=True)


def test_hybrid_retains_distinct_structured_and_document_parts_before_evidence():
    result = validate(proposal())
    assert result.decision.route == 'Hybrid'
    assert [p.evidence_need for p in result.proposed.parts] == ['structured', 'document']
    assert result.proposed.parts[0].operation_indices == (0,)


@pytest.mark.parametrize('damage', ['missing', 'empty', 'duplicate_id', 'duplicate_span', 'foreign_operation'])
def test_missing_duplicated_or_misbound_parts_cannot_enter_runtime(damage):
    value = proposal()
    if damage == 'missing': value.pop('parts')
    elif damage == 'empty': value['parts'] = []
    elif damage == 'duplicate_id': value['parts'][1]['part_id'] = 'r1'
    elif damage == 'duplicate_span': value['parts'][1] = dict(value['parts'][0], part_id='r2')
    else: value['parts'][0]['operation_indices'] = [1]
    with pytest.raises(ValueError):
        Interpretation.parse(value)


def test_parts_reuse_unique_quote_anchoring_and_reject_source_sentence_substitution():
    value = proposal()
    value['parts'][1].update(start=0, end=22)
    anchored, corrections = anchor_unique_quotes(value, TEXT)
    assert corrections == 1 and anchored['parts'][1]['start'] == 18
    assert value['parts'][1]['start'] == 0
    value = deepcopy(anchored)
    value['parts'][1].update(text='Submit Form Q at Office V.', start=0, end=26)
    with pytest.raises(ValueError, match='ungrounded_part'):
        validate(value)


@pytest.mark.parametrize('need,indices,route,expected', [
    ('structured', (), 'RAG', 'unsupported_requirement'),
    ('unknown', (), 'RAG', 'unknown_requirement'),
    ('document', (), 'Symbolic', 'inconsistent_requirements'),
])
def test_declared_needs_cannot_be_silently_downgraded_or_ignored(need, indices, route, expected):
    operations = [] if route == 'RAG' else proposal()['operations']
    result = validate(proposal(parts=[part('Can I take A1', need, indices)],
                               operations=operations, route=route))
    assert result.decision.route is None and result.diagnostic == expected


def test_document_parts_cannot_claim_a_symbolic_operation():
    value = proposal()
    value['parts'][1]['operation_indices'] = [0]
    with pytest.raises(ValueError):
        Interpretation.parse(value)


def test_old_interpretation_version_is_rejected_even_with_parts():
    with pytest.raises(ValueError):
        Interpretation.parse(proposal(schema_version='bintanong-interpretation-v1'))


@pytest.mark.parametrize('parts,route,repaired', [
    ([part('Can I take A1', 'structured', (0,))], 'Hybrid', 'Symbolic'),
    ([part('Can I take A1', 'structured', (0,)), part('where do I file Form Q?', ident='r2')], 'Symbolic', 'Hybrid')])
def test_a_route_that_disagrees_with_consistent_declared_parts_follows_the_parts(parts, route, repaired):
    # Owner, 25 Oct 2026 (roster 18 slip: one structured part with route Hybrid): repair from the parts.
    result = validate(proposal(parts=parts, route=route))
    assert result.diagnostic == 'validated' and result.decision.route == repaired
