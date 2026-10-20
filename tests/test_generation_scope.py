"""Synthetic boundaries for host-owned decisions and documentary explanations."""
import asyncio
from dataclasses import replace
import importlib
import json

import pytest

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from test_generation_evidence import integrated
from test_generation_loop import Fake,supported
from test_generation_validation import report


def api(): return importlib.import_module('backend.bintanong_generation.scope')


def document_draft(pack,**updates):
    card=next(c for c in pack.cards if c.kind=='document')
    value=dict(schema_version='bintanong-document-explanation-v1',
        release_id=pack.release_id,language=pack.language,
        claims=[dict(claim_id='c1',text=card.text,evidence_ids=[card.evidence_id])])
    value.update(updates)
    return json.dumps(value)


@pytest.mark.parametrize('language',['en','fil','taglish'])
@pytest.mark.parametrize('outcome',['eligible','ineligible'])
def test_ready_symbolic_has_only_canonical_wording_and_no_generated_decision(language,outcome):
    async def run():
        source=integrated('Symbolic',outcome=outcome,response_style=language)
        model=Fake()
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',source)
        assert answer.status=='answered' and answer.validation=='validated'
        assert answer.decision==source.evidence.symbolic.decision
        assert answer.claims==() and answer.citations==prepare(source).cards
        assert (answer.draft_attempts,answer.check_attempts,answer.answer_repairs)==(0,0,0)
        assert not model.calls
        assert 'fictional-prereq' in answer.text and 'FICTIONAL-101' in answer.text
        assert 'Eligible ang enrollment' not in answer.text
    asyncio.run(run())


@pytest.mark.parametrize('status',['unknown','conflict','held'])
def test_scoped_controls_keep_unknown_or_conflicting_conclusions_withheld(status):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    async def run():
        source=integrated('Symbolic',outcome='unknown') if status=='unknown' else IntegrationResult(understanding=None,
            schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',route=None,
            response_style='en',status=status,evidence=None,events=())
        model=Fake()
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',source)
        assert answer.status!='answered' and not model.calls
        assert 'conditions satisfied' not in answer.text
    asyncio.run(run())


def test_document_payload_preserves_all_passages_and_scope_without_structured_decision_basis():
    pack=prepare(integrated())
    payload=api().document_payload(pack)
    assert payload['sources']==[c.model_dump(mode='json') for c in pack.cards if c.kind=='document']
    assert payload['subject_scope']['scope']==pack.structured_context.scope.model_dump(mode='json')
    assert payload['subject_scope']['inputs']=={'course':'FICTIONAL-101'}
    assert all(k not in payload for k in ('decision','dependencies','structured_context'))
    assert 'can_enroll_fictional' not in json.dumps(payload)
    assert 'fact-synth' not in json.dumps(payload) and 'req-a' not in json.dumps(payload)
    assert any(c.kind=='rule' for c in pack.cards)


@pytest.mark.parametrize('route',['RAG','Hybrid'])
def test_document_schema_is_strict_and_does_not_allow_rule_or_decision_fields(route):
    pack=prepare(integrated(route))
    schema=api().document_schema(pack)
    assert 'decision_outcome' not in schema['properties']
    refs=schema['$defs']['ProseClaim']['properties']['evidence_ids']['items']['enum']
    assert refs==[c.evidence_id for c in pack.cards if c.kind=='document']
    with pytest.raises(ValueError):
        api().DocumentExplanation.parse(json.loads(document_draft(pack,decision_outcome='eligible')))


@pytest.mark.parametrize('bad',['rule_only','mixed','unknown','empty'])
def test_host_rejects_every_non_document_reference_even_with_a_document_also_present(bad):
    async def run():
        pack=prepare(integrated())
        doc=next(c for c in pack.cards if c.kind=='document')
        rule=next(c for c in pack.cards if c.kind=='rule')
        ids={'rule_only':[rule.evidence_id],'mixed':[doc.evidence_id,rule.evidence_id],
             'unknown':['ev-'+'f'*64]}
        claims=[] if bad=='empty' else [dict(claim_id='c1',text='Fictional.',evidence_ids=ids[bad])]
        raw=document_draft(pack,claims=claims)
        model=Fake(raw,raw)
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',integrated())
        assert answer.validation=='repair_exhausted' and not answer.claims
        assert answer.check_attempts==0 and answer.answer_repairs==1
    asyncio.run(run())


def test_scoped_hybrid_keeps_canonical_decision_and_checks_only_cited_documentary_basis():
    async def run():
        pack=prepare(integrated())
        model=Fake(document_draft(pack),supported())
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',integrated())
        assert answer.status=='answered' and answer.decision==pack.decision
        assert answer.citations==pack.cards
        generation=json.loads(model.calls[0][0][1]['content'])
        check=json.loads(model.calls[1][0][1]['content'])
        assert 'decision' not in generation['evidence']
        assert 'decision' not in check and 'evidence' not in check
        assert check['claim_evidence'][0]['sources']==generation['evidence']['sources']
        assert check['claim_evidence'][0]['claim']==answer.claims[0].model_dump(mode='json')
        assert 'can_enroll_fictional' not in json.dumps(check)
    asyncio.run(run())


@pytest.mark.parametrize('verdict',['unsupported','contradiction','unknown'])
def test_documentary_checker_rejection_cannot_be_overridden_by_correct_canonical_decision(verdict):
    async def run():
        pack=prepare(integrated())
        model=Fake(document_draft(pack),report(verdict).model_dump_json(),
                   document_draft(pack),report(verdict).model_dump_json())
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',integrated())
        assert answer.status=='abstained' and not answer.claims
        assert answer.decision==pack.decision and answer.check_attempts==2
        assert 'conditions satisfied' not in answer.text
    asyncio.run(run())


@pytest.mark.parametrize('field,value,error',[
    ('release_id','release-wrong','wrong_release'),('language','fil','wrong_language')])
def test_documentary_repair_reuses_evidence_and_preserves_identity_guards(field,value,error):
    async def run():
        pack=prepare(integrated())
        model=Fake(document_draft(pack,**{field:value}),document_draft(pack),supported())
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',integrated())
        assert answer.status=='answered' and answer.answer_repairs==1
        payloads=[json.loads(m[1]['content']) for m,s in model.calls[:2]]
        assert payloads[0]['evidence']==payloads[1]['evidence']
        assert error in payloads[1]['validation_errors']
    asyncio.run(run())


def test_symbolic_host_only_still_respects_exhausted_request_budget():
    async def run():
        answer=await Generator(Fake(),explanation_profile='scoped').generate(
            'Fictional check; fictional policy?',integrated('Symbolic'),remaining_seconds=0)
        assert answer.validation=='timeout' and answer.status=='temporarily_unavailable'
        assert 'conditions satisfied' not in answer.text
    asyncio.run(run())


def test_host_dependency_listing_retains_exact_scope_and_rule_provenance():
    from backend.bintanong_orchestration.contracts import IntegrationResult
    from backend.bintanong_orchestration.integration import assemble
    from backend.bintanong_symbolic.runtime import DependencyResult
    from test_orchestration_integration import pin,symbolic
    sym=symbolic()
    dependencies=DependencyResult(schema_version=DependencyResult.SCHEMA_VERSION,
        synthetic=True,activation_allowed=False,eligibility_executable=False,
        relation='potential_prior_completion_dependency',coverage_scope='supplied_bundle',
        status='complete',inputs=sym.inputs,course_ids=('fictional-dependent',),
        unknown_conditions=(),rule_bundle_version=sym.rule_bundle_version,scope=sym.scope,
        rule_ids=sym.rule_ids,rule_spans=sym.rule_spans,error_code=None)
    evidence=assemble(pin(),'Symbolic',dependencies=dependencies)
    plan=integrated('Symbolic').understanding.model_dump(mode='json')
    plan['operations'][0]['name']='list_affected_courses'
    plan['predicate_request']['predicate']='list_affected_courses'
    from backend.bintanong_orchestration.contracts import RequestUnderstanding
    source=IntegrationResult(understanding=RequestUnderstanding.parse(plan),schema_version=IntegrationResult.SCHEMA_VERSION,request_id='req-a',
        route='Symbolic',response_style='en',status=evidence.status,evidence=evidence,events=())
    async def run():
        model=Fake()
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',source)
        assert answer.status=='answered' and answer.dependencies==dependencies
        assert answer.decision is None and not model.calls and not answer.claims
        assert 'within the supplied bundle: fictional-dependent' in answer.text
        assert answer.citations==prepare(source).cards
    asyncio.run(run())


def test_checker_basis_does_not_include_an_uncited_document_or_rule_card():
    pack=prepare(integrated())
    doc=next(c for c in pack.cards if c.kind=='document')
    extra=doc.model_copy(update={'evidence_id':'ev-'+'b'*64,'text':'An unrelated service.'})
    pack=replace(pack,cards=(*pack.cards,extra))
    wire=api().DocumentExplanation.parse(json.loads(document_draft(pack)))
    proposal=api().canonical_draft(wire,pack)
    payload=json.loads(api().document_support_messages('Fictional check; fictional policy?',pack,proposal)[1]['content'])
    assert payload['claim_evidence'][0]['sources']==[doc.model_dump(mode='json')]
    assert 'An unrelated service.' not in json.dumps(payload)


def test_scoped_checker_timeout_withholds_unchecked_documentary_prose():
    async def run():
        pack=prepare(integrated())
        class Wait(Fake):
            async def infer(self,messages,schema):
                if self.outputs: return await super().infer(messages,schema)
                await asyncio.Event().wait()
        answer=await Generator(Wait(document_draft(pack)),explanation_profile='scoped',
            timeout_seconds=0.03).generate('Fictional check; fictional policy?',integrated())
        assert answer.validation=='timeout' and not answer.claims
        assert answer.check_attempts==1 and answer.status=='temporarily_unavailable'
        assert 'conditions satisfied' not in answer.text
    asyncio.run(run())


def test_source_text_that_explicitly_describes_enrollment_is_not_keyword_filtered():
    # Scope comes from reviewed evidence, not a blanket ban on a word.
    pack=prepare(integrated('RAG'))
    card=pack.cards[0].model_copy(update={'text':'Fictional enrollment service: submit Form Q.'})
    pack=replace(pack,cards=(card,))
    wire=api().DocumentExplanation.parse(json.loads(document_draft(pack)))
    proposal=api().canonical_draft(wire,pack)
    assert proposal.claims[0].text==card.text
    assert proposal.decision_outcome is None


def test_scoped_documentary_text_keeps_existing_private_reference_guard():
    async def run():
        pack=prepare(integrated())
        bad=document_draft(pack,claims=[dict(claim_id='c1',text='sess-other-1 fact-private-1',
            evidence_ids=[pack.cards[0].evidence_id])])
        model=Fake(bad,bad)
        answer=await Generator(model,explanation_profile='scoped').generate('Fictional check; fictional policy?',integrated())
        assert answer.validation=='repair_exhausted' and not answer.claims
        assert 'private_reference' in json.loads(model.calls[1][0][1]['content'])['validation_errors']
    asyncio.run(run())


@pytest.mark.parametrize('bad',[None,True,'other',[],1])
def test_invalid_explanation_profile_rejected(bad):
    with pytest.raises(ValueError,match='invalid_explanation_profile'):
        Generator(Fake(),explanation_profile=bad)


def test_unverified_profile_composition_rejected():
    with pytest.raises(ValueError,match='scoped_requires_canonical_references'):
        Generator(Fake(),explanation_profile='scoped',reference_profile='short')


@pytest.mark.parametrize('profile',['scoped','guarded','covered'])
def test_runtime_profile_is_forwarded_and_reported(monkeypatch,profile):
    import backend.bintanong_runtime.application as module
    from backend.bintanong_routing.contracts import RequestContext
    from test_runtime_composition import spec,Database
    seen=[]
    original=module.Generator
    def observe(*args,**kwargs):
        seen.append(kwargs['explanation_profile'])
        return original(*args,**kwargs)
    monkeypatch.setattr(module,'Generator',observe)
    class Held(Database):
        def select(self,*args,**kwargs): return []
    data=spec()
    app=module.build_application(module.RuntimeSpec.parse(data),client=Held(data),
        settings=module.RuntimeSettings(explanation_profile=profile))
    result=asyncio.run(app.run('Fictional check; fictional policy?',RequestContext(session_id='sess-a',request_id='req-a')))
    assert seen==[profile] and result.explanation_profile==profile
    assert result.routing_profile=='separate' and not result.model_calls


def test_selected_defaults_use_scoped_explanations_with_separate_routing_and_canonical_ids():
    from backend.bintanong_runtime.application import RuntimeSettings,RuntimeRun
    generator=Generator(Fake())
    assert generator.explanation_profile=='scoped'
    assert generator.reference_profile=='canonical'
    settings=RuntimeSettings()
    assert settings.explanation_profile=='scoped' and settings.routing_profile=='separate'
    # Missing fields in historical reports must retain their historical meaning.
    assert RuntimeRun.model_fields['explanation_profile'].default=='legacy'


def test_selected_default_symbolic_retains_narrow_canonical_result_without_paraphrase():
    async def run():
        model=Fake()
        answer=await Generator(model).generate('Fictional check; fictional policy?',integrated('Symbolic',response_style='taglish'))
        assert answer.status=='answered' and not answer.claims and not model.calls
        assert 'Sa supported prerequisite check, satisfied ang conditions.' in answer.text
    asyncio.run(run())


def test_selected_cli_help_identifies_scoped_default(capsys):
    from backend.bintanong_runtime.cli import main
    with pytest.raises(SystemExit) as exc: main(['--help'])
    assert exc.value.code==0
    assert 'default: scoped' in capsys.readouterr().out
