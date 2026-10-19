"""Composition boundaries; fictional data, no live inference in unit tests."""
import asyncio
import copy

import pytest

from backend.bintanong_runtime.application import RuntimeSpec, build_application
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_routing.contracts import CatalogEntry
from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_symbolic_authoring import fixture, run


def spec():
    bundle = prepare_runtime_bundle(run(fixture()))
    runtime = CurriculumRuntime.from_bundle(bundle)
    source = bundle['ledger']['sources'][0]
    return dict(schema_version='bintanong-runtime-spec-v1', synthetic=True,
        bundle=bundle, embedding_assets={'model.safetensors':'a'*64},
        pin=ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True,
            rule_bundle_version=runtime.rule_bundle_version,
            sources=[dict(version_id=source['version_id'],byte_sha256=source['byte_sha256'])],
            documents=[dict(chunk_id='b'*64,version_id=source['version_id'],
                byte_sha256=source['byte_sha256'])])).model_dump(mode='json'),
        catalog=[CatalogEntry.parse(dict(kind='course', entity_id='course-2',
            program_id='program-synthetic',curriculum_id='curriculum-synthetic-1',
            aliases=['SYN201'], source_ref=source['version_id'], review_ref='fictional-review',
            reviewed=True)).model_dump(mode='json')])


class Database:
    def __init__(self, data):
        self.data, self.calls = data, []

    def select(self, table, *, filters=None, role='runtime', **kwargs):
        self.calls.append((table, role))
        p = self.data['pin']
        return {'knowledge_releases':[dict(release_id=p['release_id'],status='active')],
            'release_document_versions':[dict(version_id=s['version_id']) for s in p['sources']],
            'release_chunks':[dict(chunk_id=d['chunk_id']) for d in p['documents']],
            'document_versions':[dict(version_id=s['version_id'],byte_sha256=s['byte_sha256'],
                document_id='doc-fictional') for s in p['sources']],
            'documents':[dict(document_id='doc-fictional',synthetic=True)]}[table]


def test_builder_uses_actual_components_and_read_only_verified_provider():
    from backend.bintanong_orchestration.adapters import RetrievalAdapter, SymbolicAdapter
    from backend.bintanong_retrieval.query import QueryEncoder
    data=spec()
    db=Database(data)
    app=build_application(RuntimeSpec.parse(data),client=db)
    resources=asyncio.run(app.releases.pin())
    assert type(resources.retrieval) is RetrievalAdapter
    assert type(resources.symbolic) is SymbolicAdapter
    assert type(app.encoder) is QueryEncoder
    assert all(role=='runtime' for _,role in db.calls)
    assert resources.registry.supports('check_prerequisite_eligibility')


@pytest.mark.parametrize('change', ['source_hash','non_synthetic','membership','inactive'])
def test_provider_holds_mismatched_or_institutional_database_sources(change):
    from backend.bintanong_orchestration.ports import ReleaseUnavailable
    data=spec()
    class Changed(Database):
        def select(self,table,**kwargs):
            rows=copy.deepcopy(super().select(table,**kwargs))
            if change=='source_hash' and table=='document_versions': rows[0]['byte_sha256']='c'*64
            if change=='non_synthetic' and table=='documents': rows[0]['synthetic']=False
            if change=='membership' and table=='release_chunks': rows=[]
            if change=='inactive' and table=='knowledge_releases': rows[0]['status']='draft'
            return rows
    app=build_application(RuntimeSpec.parse(data),client=Changed(data))
    with pytest.raises(ReleaseUnavailable): asyncio.run(app.releases.pin())


def test_bundle_pin_mismatch_rejected_before_database_or_model_calls():
    data=spec()
    data['pin']['release_id']='release-other'
    db=Database(data)
    with pytest.raises(ValueError): build_application(RuntimeSpec.parse(data),client=db)
    assert db.calls==[]


def test_non_synthetic_spec_rejected():
    data=spec(); data['synthetic']=False
    with pytest.raises(ValueError): RuntimeSpec.parse(data)
