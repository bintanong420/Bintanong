"""Offering clauses must be printed fields of this release, never arbitrary config text."""
import hashlib
import json

import pytest

from backend.bintanong_orchestration.contracts import DocumentResult, ReleasePin, DocumentPassage
from backend.bintanong_orchestration.plan_sources import check_route_sources, source_digest
from test_planning_recovery import ROUTES
from test_planning_check import SOURCE


def inputs(routes=ROUTES):
    passages = []
    for clause in routes.clauses:
        cid = hashlib.sha256(clause.text.encode()).hexdigest()
        passages.append(dict(chunk_id=cid, version_id=SOURCE.version_id,
            text=json.dumps(dict(fields=[dict(name='body',value=clause.text,source_blank=False,span_indexes=[0])],source_limits=[])),
            citations=[dict(version_id=SOURCE.version_id,byte_sha256=SOURCE.byte_sha256,page=clause.page,
                            locator=dict(kind='docling_ref',ref='printed-clause',table_index=None,cell_ids=[],item_ids=[]))]))
    pin = ReleasePin.parse(dict(release_id='release-synthetic-route',synthetic=True,rule_bundle_version=None,
        sources=[dict(version_id=SOURCE.version_id,byte_sha256=SOURCE.byte_sha256)],documents=[
            dict(chunk_id=p['chunk_id'],version_id=SOURCE.version_id,byte_sha256=SOURCE.byte_sha256,passage_sha256=source_digest(DocumentPassage.parse(p))) for p in passages]))
    routes = routes.model_copy(update=dict(source_chunk_ids=tuple(p['chunk_id'] for p in passages)))
    pin = pin.model_copy(update=dict(plan_routes_sha256=source_digest(routes)))
    documents = DocumentResult.parse(dict(release_id=pin.release_id,status='ok',passages=passages,gaps=[]))
    return pin,routes,documents


def test_exact_pinned_reviewed_field_is_accepted():
    check_route_sources(*inputs())


def test_track_a_clauses_pass_the_same_proof_and_cannot_be_forged():
    from test_planning_recovery_status import FULL
    pin, routes, documents = inputs(FULL)
    check_route_sources(pin, routes, documents)
    forged = routes.clauses[-1].model_copy(update=dict(text='An invented office approves everything.', conditions=()))
    with pytest.raises(ValueError):
        check_route_sources(pin, routes.model_copy(update=dict(clauses=(*routes.clauses[:-1], forged))), documents)


def test_runtime_uses_existing_source_chunks_without_retrieval():
    from backend.bintanong_runtime.research import plan_route_sources
    pin,routes,documents = inputs()
    chunks = []
    for passage in documents.passages:
        chunks.append(dict(chunk_id=passage.chunk_id, version_id=passage.version_id, text=passage.text,
            spans=[c.model_dump(mode='json') for c in passage.citations]))
    proof = plan_route_sources(pin,routes,chunks)
    check_route_sources(pin,routes,proof)
    assert proof == documents


def test_runtime_preserves_reviewed_field_span_links_from_chunk_metadata():
    from backend.bintanong_runtime.research import route_passage
    pin, routes, documents = inputs()
    original = documents.passages[0]
    record = json.loads(original.text)
    association = dict(record['fields'][0])
    record['fields'][0].pop('span_indexes')
    chunk = dict(chunk_id=original.chunk_id, version_id=original.version_id, text=json.dumps(record),
                 spans=[c.model_dump(mode='json') for c in original.citations],
                 type_fields=dict(field_associations=[association]))
    passage = route_passage(chunk)
    assert json.loads(passage.text)['fields'][0] == association
    check_route_sources(pin, routes, documents.model_copy(update=dict(passages=(passage, *documents.passages[1:]))))
    chunk['source_label'] = 'Fictional handbook.pdf'
    assert route_passage(chunk).citations[0].filename == 'Fictional handbook.pdf'
    chunk['type_fields']['field_associations'][0] = dict(association, value='Unrelated field text.')
    with pytest.raises(ValueError, match='plan_route_field_association_missing'):
        route_passage(chunk)


def test_coordinated_page_corruption_cannot_relabel_a_clause():
    pin,routes,documents = inputs()
    data = documents.model_dump(mode='json')
    data['passages'][0]['citations'][0]['page'] = 999
    documents = DocumentResult.parse(data)
    routes = routes.model_copy(update=dict(clauses=(routes.clauses[0].model_copy(update=dict(page=999)),
                                                   *routes.clauses[1:])))
    with pytest.raises(ValueError): check_route_sources(pin,routes,documents)


def test_reviewed_clause_conditions_cannot_be_shortened_away():
    pin,routes,documents = inputs()
    shortened = routes.clauses[0].model_copy(update=dict(text=routes.clauses[0].text[:10],conditions=()))
    routes = routes.model_copy(update=dict(clauses=(shortened,*routes.clauses[1:])))
    with pytest.raises(ValueError): check_route_sources(pin,routes,documents)


@pytest.mark.parametrize('defect', ['missing','unpinned','changed_text','metadata_only','wrong_page','held','forged_field_and_clause'])
def test_config_cannot_invent_a_clause_or_hide_source_limits(defect):
    pin,routes,documents = inputs()
    if defect == 'missing': documents = None
    elif defect == 'unpinned': pin = pin.model_copy(update=dict(documents=()))
    else:
        data = documents.model_dump(mode='json')
        record = json.loads(data['passages'][0]['text'])
        if defect == 'changed_text': record['fields'][0]['value'] = 'A different printed clause.'
        elif defect == 'forged_field_and_clause':
            record['fields'][0]['value'] = 'An invented office approves everything.'
            routes = routes.model_copy(update=dict(clauses=(routes.clauses[0].model_copy(
                update=dict(text=record['fields'][0]['value'])), *routes.clauses[1:])))
        elif defect == 'metadata_only':
            record['metadata'] = record['fields'][0]['value']
            record['fields'][0]['value'] = 'Unrelated printed text.'
        elif defect == 'wrong_page': data['passages'][0]['citations'][0]['page'] += 1
        elif defect == 'held': record['source_limits'] = [dict(issue='malformed_source_condition',resolution='unresolved')]
        data['passages'][0]['text'] = json.dumps(record)
        if defect in ('changed_text','metadata_only','held'):
            members = pin.model_dump(mode='json')['documents']
            members[0]['passage_sha256'] = source_digest(DocumentPassage.parse(data['passages'][0]))
            pin = ReleasePin.parse({**pin.model_dump(mode='json'), 'documents':members})
        documents = DocumentResult.parse(data)
    with pytest.raises(ValueError): check_route_sources(pin,routes,documents)
