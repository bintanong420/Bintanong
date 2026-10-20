"""Synthetic wire-boundary tests; model semantics are evaluated separately."""
import asyncio
import importlib
import json

import pytest

from backend.bintanong_generation.contracts import AnswerDraft
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from test_generation_evidence import integrated
from test_generation_loop import Fake, supported
from test_generation_validation import draft


def refs(pack):
    return importlib.import_module('backend.bintanong_generation.references').EvidenceReferences(pack)


def short_draft(pack, **updates):
    value=refs(pack).encode(draft(pack))
    value.update(updates)
    return json.dumps(value)


@pytest.mark.parametrize('route', ['RAG','Symbolic','Hybrid'])
def test_short_payload_preserves_every_source_field_and_round_trips_exact_claims(route):
    pack=prepare(integrated(route))
    before=pack.model_payload()
    codec=refs(pack)
    payload=codec.payload()
    assert [c['evidence_id'] for c in payload['sources']]==[f'e{i+1}' for i in range(len(pack.cards))]
    for old,new in zip(before['sources'],payload['sources'],strict=True):
        assert {k:v for k,v in old.items() if k!='evidence_id'}=={k:v for k,v in new.items() if k!='evidence_id'}
    assert {k:v for k,v in payload.items() if k!='sources'}=={k:v for k,v in before.items() if k!='sources'}
    original=draft(pack)
    encoded=codec.encode(original)
    wire=importlib.import_module('backend.bintanong_generation.references').ShortAnswerDraft.parse(encoded)
    assert codec.decode(wire)==original
    assert pack.model_payload()==before


def test_full_32_card_map_preserves_order_multiple_refs_and_prose_verbatim():
    from dataclasses import replace
    pack=prepare(integrated())
    cards=tuple(pack.cards[0].model_copy(update={'evidence_id':'ev-'+f'{i:064x}'}) for i in range(32))
    pack=replace(pack,cards=cards)
    original=draft(pack,claims=[dict(claim_id='c1',text='e1 and ev-'+'a'*64,
        evidence_ids=[cards[31].evidence_id,cards[0].evidence_id])])
    codec=refs(pack)
    encoded=codec.encode(original)
    assert encoded['claims'][0]['evidence_ids']==['e32','e1']
    assert encoded['claims'][0]['text']==original.claims[0].text
    wire=importlib.import_module('backend.bintanong_generation.references').ShortAnswerDraft.parse(encoded)
    assert codec.decode(wire)==original


@pytest.mark.parametrize('bad', ['e0','e33','e01','E1','ev-'+'a'*64,'sess-other-1',1])
def test_invalid_short_reference_rejected_by_wire_contract(bad):
    pack=prepare(integrated())
    value=refs(pack).encode(draft(pack))
    value['claims'][0]['evidence_ids']=[bad]
    with pytest.raises(ValueError):
        importlib.import_module('backend.bintanong_generation.references').ShortAnswerDraft.parse(value)


@pytest.mark.parametrize('change',['unknown','duplicate_ref','duplicate_claim','extra'])
def test_nonconforming_wire_never_reaches_checker_or_final_answer(change):
    async def run():
        pack=prepare(integrated())
        value=refs(pack).encode(draft(pack))
        if change=='unknown': value['claims'][0]['evidence_ids']=['e32']
        elif change=='duplicate_ref': value['claims'][0]['evidence_ids']=['e1','e1']
        elif change=='duplicate_claim': value['claims']*=2
        else: value['claims'][0]['office']='invented'
        model=Fake(json.dumps(value),json.dumps(value))
        answer=await Generator(model,reference_profile='short',explanation_profile='legacy').generate('Fictional?',integrated())
        assert answer.validation=='repair_exhausted' and not answer.claims
        assert answer.check_attempts==0 and answer.answer_repairs==1
    asyncio.run(run())


def test_short_generator_restores_canonical_ids_before_host_validation_and_checker_encoding():
    async def run():
        pack=prepare(integrated())
        model=Fake(short_draft(pack),supported())
        answer=await Generator(model,reference_profile='short',explanation_profile='legacy').generate('Fictional?',integrated())
        assert answer.status=='answered' and answer.claims==draft(pack).claims
        # Canonical decision rendering also retains its rule citation.
        assert answer.citations==pack.cards
        assert pack.cards[0].evidence_id in answer.text
        checker=json.loads(model.calls[1][0][1]['content'])
        assert checker['untrusted_draft']['claims'][0]['evidence_ids']==['e1']
        assert checker['evidence']==json.loads(model.calls[0][0][1]['content'])['evidence']
    asyncio.run(run())


def test_short_schema_matches_payload_and_does_not_mutate_canonical_schema():
    from backend.bintanong_generation.prompt import draft_messages,draft_schema,output_schema
    pack=prepare(integrated())
    before=output_schema(AnswerDraft)
    codec=refs(pack)
    schema=draft_schema(pack,references=codec)
    item=schema['$defs']['ShortProseClaim']['properties']['evidence_ids']['items']
    assert item=={'type':'string','enum':['e1','e2']}
    messages=draft_messages('Fictional?',pack,references=codec)
    from backend.bintanong_contracts.schema_display import compact_for_prompt
    assert json.loads(messages[0]['content'].split('\nOutput schema:\n')[1])==compact_for_prompt(schema)
    assert output_schema(AnswerDraft)==before


def test_repair_reuses_same_map_and_preserves_canonical_checks():
    async def run():
        pack=prepare(integrated())
        model=Fake(short_draft(pack,release_id='release-wrong'),short_draft(pack),supported())
        answer=await Generator(model,reference_profile='short',explanation_profile='legacy').generate('Fictional?',integrated())
        assert answer.status=='answered' and answer.answer_repairs==1
        calls=[json.loads(m[1]['content']) for m,s in model.calls[:2]]
        assert calls[0]['evidence']==calls[1]['evidence']
        assert 'wrong_release' in calls[1]['validation_errors']
        assert answer.claims==draft(pack).claims
    asyncio.run(run())


def test_concurrent_requests_do_not_share_short_reference_maps():
    from dataclasses import replace
    async def run():
        first=prepare(integrated('RAG'))
        second=replace(first,cards=(first.cards[0].model_copy(update={'evidence_id':'ev-'+'b'*64}),))
        async def decode(pack):
            codec=refs(pack)
            encoded=codec.encode(draft(pack))
            await asyncio.sleep(0)
            wire=importlib.import_module('backend.bintanong_generation.references').ShortAnswerDraft.parse(encoded)
            return codec.decode(wire)
        a,b=await asyncio.gather(decode(first),decode(second))
        assert a.claims[0].evidence_ids==(first.cards[0].evidence_id,)
        assert b.claims[0].evidence_ids==(second.cards[0].evidence_id,)
    asyncio.run(run())


@pytest.mark.parametrize('bad', [None,'combined',True,[],1])
def test_invalid_profile_rejected(bad):
    with pytest.raises(ValueError,match='invalid_generation_reference_profile'):
        Generator(Fake(),reference_profile=bad,explanation_profile='legacy')


def test_runtime_reference_profile_is_explicit_and_canonical_by_default():
    from backend.bintanong_runtime.application import RuntimeSettings,RuntimeRun
    assert RuntimeSettings().generation_reference_profile=='canonical'
    assert RuntimeSettings(generation_reference_profile='short',explanation_profile='legacy').generation_reference_profile=='short'
    with pytest.raises(ValueError,match='invalid_generation_reference_profile'):
        RuntimeSettings(generation_reference_profile='other')
    assert RuntimeRun.model_fields['generation_reference_profile'].default=='canonical'


def test_runtime_forwards_short_profile_and_reports_it_without_changing_routing(monkeypatch):
    import backend.bintanong_runtime.application as module
    from backend.bintanong_routing.contracts import RequestContext
    from test_runtime_composition import spec,Database
    data=spec()
    class Held(Database):
        def select(self,*args,**kwargs): return []
    seen=[]
    original=module.Generator
    def observe(*args,**kwargs):
        seen.append(kwargs['reference_profile'])
        return original(*args,**kwargs)
    monkeypatch.setattr(module,'Generator',observe)
    app=module.build_application(module.RuntimeSpec.parse(data),client=Held(data),
        settings=module.RuntimeSettings(generation_reference_profile='short',explanation_profile='legacy'))
    result=asyncio.run(app.run('Fictional?',RequestContext(session_id='sess-a',request_id='req-a')))
    assert seen==['short'] and result.generation_reference_profile=='short'
    assert result.routing_profile=='separate' and not result.model_calls


@pytest.mark.parametrize('field,value,error',[
    ('language','fil','wrong_language'),('decision_outcome','ineligible','wrong_outcome')])
def test_short_profile_preserves_language_and_canonical_decision_validation(field,value,error):
    async def run():
        pack=prepare(integrated())
        invalid=short_draft(pack,**{field:value})
        model=Fake(invalid,invalid)
        answer=await Generator(model,reference_profile='short',explanation_profile='legacy').generate('Fictional?',integrated())
        assert answer.validation=='repair_exhausted' and not answer.claims
        repair=json.loads(model.calls[1][0][1]['content'])
        assert error in repair['validation_errors']
        assert answer.decision==pack.decision and answer.check_attempts==0
    asyncio.run(run())


def test_short_profile_retains_independent_support_rejection():
    from test_generation_validation import report
    async def run():
        pack=prepare(integrated())
        model=Fake(short_draft(pack),report('unsupported').model_dump_json(),
                   short_draft(pack),report('contradiction').model_dump_json())
        answer=await Generator(model,reference_profile='short',explanation_profile='legacy').generate('Fictional?',integrated())
        assert answer.validation=='repair_exhausted' and not answer.claims
        assert (answer.draft_attempts,answer.check_attempts,answer.answer_repairs)==(2,2,1)
    asyncio.run(run())
