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
        result=await api().observe(cases,Generator(EchoEvidence()),evaluation_kind='mock')
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
