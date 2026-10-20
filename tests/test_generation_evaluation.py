import asyncio
import importlib

import pytest

from backend.bintanong_generation.generator import Generator
from test_generation_evidence import integrated
from test_generation_pipeline import EchoEvidence


def api():
    return importlib.import_module('backend.bintanong_generation.evaluation')


def case(**updates):
    value=dict(case_id='synthetic-dev-1',family_id='fictional-policy',split='dev',synthetic=True,
        question='Fictional policy?',integration=integrated('RAG').model_dump(mode='json'))
    value.update(updates)
    return value


def test_mock_observations_do_not_claim_language_or_support_accuracy():
    async def scenario():
        cases=api().load_cases([case()])
        result=await api().observe(cases,Generator(EchoEvidence(),explanation_profile='legacy'),evaluation_kind='mock')
        assert result['evaluation_kind']=='mock' and result['actual_model_accuracy']=='unmeasured'
        row=result['observations'][0]
        assert row['answer']['status']=='answered'
        assert row['human_language_review']=='pending' and row['human_claim_support_review']=='pending'
        assert row['canonical_decision_preserved'] is True
    asyncio.run(scenario())


@pytest.mark.parametrize('values', [[case(split='final')],[case(synthetic=False)],
    [case(),case()],[case(question='')]])
def test_final_duplicate_and_nonsynthetic_cases_are_rejected(values):
    with pytest.raises(ValueError): api().load_cases(values)


def test_report_must_stay_under_explicit_ignored_evidence_root(tmp_path):
    with pytest.raises(ValueError):
        api().write_report({},tmp_path.parent/'outside.json',tmp_path)
    path=tmp_path/'report.json'
    api().write_report({'candidate_only':True},path,tmp_path)
    assert path.exists()


@pytest.mark.parametrize('profile,refs',[('scoped','canonical'),('legacy','canonical'),('legacy','short')])
def test_report_identifies_effective_profile_and_prompt_hashes(profile,refs):
    import json
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation import prompt,scope
    from backend.bintanong_generation.references import EvidenceReferences
    from test_generation_loop import Fake,supported
    from test_generation_validation import draft
    from test_generation_scope import document_draft
    async def run():
        pack=prepare(integrated('RAG'))
        if profile=='scoped':
            raw=document_draft(pack)
            expected=(scope.DOCUMENT_PROMPT_SHA256,scope.DOCUMENT_SUPPORT_PROMPT_SHA256)
        elif refs=='short':
            raw=json.dumps(EvidenceReferences(pack).encode(draft(pack)))
            expected=(prompt.SHORT_PROMPT_SHA256,prompt.SHORT_SUPPORT_PROMPT_SHA256)
        else:
            raw=draft(pack).model_dump_json()
            expected=(prompt.PROMPT_SHA256,prompt.SUPPORT_PROMPT_SHA256)
        generator=Generator(Fake(raw,supported()),explanation_profile=profile,reference_profile=refs)
        result=await api().observe(api().load_cases([case()]),generator,evaluation_kind='mock')
        assert result['observations'][0]['answer']['status']=='answered'
        assert (result['prompt_sha256'],result['support_prompt_sha256'])==expected
        assert result['explanation_profile']==profile and result['reference_profile']==refs
    asyncio.run(run())


def test_observation_distinguishes_host_only_structured_answers_from_model_generation():
    from test_generation_loop import Fake
    async def run():
        cases=api().load_cases([case(integration=integrated('Symbolic').model_dump(mode='json'))])
        result=await api().observe(cases,Generator(Fake()),evaluation_kind='mock')
        row=result['observations'][0]
        assert row['answer']['status']=='answered' and row['answer']['draft_attempts']==0
        assert row['generation_mode']=='host_only'
    asyncio.run(run())
