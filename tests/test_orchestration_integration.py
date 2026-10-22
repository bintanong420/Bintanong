"""Synthetic integration boundaries; none of these examples is university policy."""
import importlib

import pytest

from backend.bintanong_contracts.symbolic import SymbolicResult
from test_contracts_answer import symbolic as symbolic_payload


def api():
    return importlib.import_module('backend.bintanong_orchestration.integration')


def contracts():
    return importlib.import_module('backend.bintanong_orchestration.contracts')


def pin():
    return contracts().ReleasePin.parse(dict(
        release_id='release-synth-1', synthetic=True,
        rule_bundle_version='bundle-synth-1',
        sources=[dict(version_id='ver-synth-handbook-1', byte_sha256='1'*64)],
        documents=[dict(chunk_id='0'*63+'1', version_id='ver-synth-handbook-1', byte_sha256='1'*64)]))


def documents(status='ok', **updates):
    value = dict(release_id='release-synth-1', status=status, gaps=[], passages=[dict(
        chunk_id='0'*63+'1', version_id='ver-synth-handbook-1', text='Fictional policy.',
        citations=[dict(version_id='ver-synth-handbook-1', byte_sha256='1'*64,
                        page=1, locator={'kind':'docling_ref', 'ref':'fictional/1',
                                         'table_index':None, 'cell_ids':[], 'item_ids':[]})])])
    value.update(updates)
    return contracts().DocumentResult.parse(value)


def symbolic(outcome='eligible'):
    return SymbolicResult.parse(symbolic_payload(outcome, synthetic=True))


@pytest.mark.parametrize('route', ['RAG', 'Symbolic', 'Hybrid'])
def test_common_candidate_package_for_each_route(route):
    result = api().assemble(pin(), route,
        documents=documents() if route != 'Symbolic' else None,
        symbolic=symbolic() if route != 'RAG' else None)
    assert result.status == 'ready'
    assert result.route == route
    assert result.candidate_only and not result.institutional_use_allowed
    assert not result.activation_allowed
    assert result.permitted_scope == {'RAG':'document_explanation',
        'Symbolic':'scoped_prerequisite_check', 'Hybrid':'combined_explanation'}[route]
    assert type(result).parse(result.model_dump(mode='json')) == result


@pytest.mark.parametrize('status', ['uncalibrated', 'insufficient_evidence', 'conflicting_sources',
    'release_changed', 'storage_error', 'needs_scope'])
def test_retrieval_holds_cannot_become_a_ready_hybrid_decision(status):
    result = api().assemble(pin(), 'Hybrid', documents=documents(status), symbolic=symbolic())
    assert result.status != 'ready' and result.permitted_scope == 'none'
    assert result.symbolic.decision.outcome == 'eligible'  # observation kept, never a fallback decision


@pytest.mark.parametrize('updates', [dict(release_id='release-other'),
    dict(passages=[]), dict(gaps=['missing_required_neighbor'])])
def test_missing_or_incomplete_document_evidence_withholds_scope(updates):
    result = api().assemble(pin(), 'RAG', documents=documents(**updates))
    assert result.status != 'ready' and result.permitted_scope == 'none'


def test_unlisted_chunk_or_changed_source_bytes_refuse_release_membership():
    doc = documents().model_dump(mode='json')
    doc['passages'][0]['chunk_id'] = 'f'*64
    result = api().assemble(pin(), 'RAG', documents=contracts().DocumentResult.parse(doc))
    assert result.status == 'release_mismatch'
    doc['passages'][0]['chunk_id'] = '0'*63+'1'
    doc['passages'][0]['citations'][0]['byte_sha256'] = 'f'*64
    result = api().assemble(pin(), 'RAG', documents=contracts().DocumentResult.parse(doc))
    assert result.status == 'release_mismatch'


@pytest.mark.parametrize('outcome', ['unknown', 'unsupported', 'error'])
def test_symbolic_nondecisions_remain_distinct(outcome):
    result = api().assemble(pin(), 'Symbolic', symbolic=symbolic(outcome))
    assert result.status == outcome and result.permitted_scope == 'none'
    if outcome == 'unknown':
        assert result.missing_facts or result.symbolic.decision.unknown_conditions


def test_bundle_version_and_rule_source_membership_are_checked():
    result = api().assemble(pin().model_copy(update={'rule_bundle_version':'other'}),
                            'Symbolic', symbolic=symbolic())
    assert result.status == 'release_mismatch'


def test_real_decision_and_institutional_pin_are_not_admitted():
    with pytest.raises(ValueError):
        pin().model_copy(update={'synthetic':False})
    with pytest.raises(ValueError, match='synthetic'):
        api().assemble(pin(), 'Symbolic', symbolic=SymbolicResult.parse(symbolic_payload()))


def test_empty_components_and_cross_route_components_are_invalid():
    with pytest.raises(ValueError):
        api().assemble(pin(), 'Hybrid', documents=documents())
    with pytest.raises(ValueError):
        api().assemble(pin(), 'RAG', documents=documents(), symbolic=symbolic())


@pytest.mark.parametrize('doc', ['uncalibrated','insufficient_evidence','empty'])
@pytest.mark.parametrize('outcome', ['conflict','error','unknown'])
def test_hybrid_preserves_symbolic_failure_ahead_of_document_availability(doc,outcome):
    sym = symbolic('unknown' if outcome == 'conflict' else outcome)
    if outcome == 'conflict':
        sym = sym.model_copy(update={'decision':sym.decision.model_copy(update={
            'unresolved_conflicts':('conflicting completion assertions',)})})
    result = api().assemble(pin(),'Hybrid',symbolic=sym,
        documents=documents(passages=[]) if doc == 'empty' else documents(doc))
    assert result.status == outcome and result.permitted_scope == 'none'
    assert result.documents is not None and result.symbolic == sym


def test_document_conflict_and_release_mismatch_take_priority_over_unknown_facts():
    for document_status,expected in [('conflicting_sources','conflict'),('release_changed','release_mismatch')]:
        result = api().assemble(pin(),'Hybrid',symbolic=symbolic('unknown'),documents=documents(document_status))
        assert result.status == expected
