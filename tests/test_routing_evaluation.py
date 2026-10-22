import asyncio
import importlib
import json

import pytest

from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_routing.router import Router
from test_routing_contracts import context
from test_routing_router import FakeTransport, proposal
from test_routing_validation import catalog, registry


def api():
    return importlib.import_module('backend.bintanong_routing.evaluation')


def case(case_id='case-en', language='en', **kw):
    data = dict(case_id=case_id, family_id='family-1', split='dev', synthetic=True,
        synthetic_policy='Fictional A1 catalog; no university rule is asserted.', text='A1',
        language=language, context=context(), expected='Symbolic',
        expected_operations=['check_prerequisite_eligibility:curriculum-a:course-a'],
        expected_entities=['course-a'], expected_claims=[], expected_style=language)
    data.update(kw)
    return data


def metadata():
    return dict(model_sha256='a'*64, runtime_image_digest='b'*64,
                code_commit='c'*40, evaluation_kind='mock')


def evaluate(cases, *outputs):
    router = Router(FakeTransport(*[json.dumps(o) for o in outputs]), catalog=catalog(),
        registry=registry(), documents_available=True, synthetic=True)
    return asyncio.run(api().evaluate_cases(router, cases, metadata()))


def test_report_keeps_wrong_proposal_visible_behind_safe_effective_control():
    report = evaluate([case()], proposal(language='en', route='RAG'))
    assert report['total'] == 1 and report['proposal_correct'] == 0
    assert report['proposal_matrix'] == {'Symbolic': {'RAG': 1}}
    assert report['effective_matrix'] == {'Symbolic': {'evidence_unavailable': 1}}
    assert report['diagnostics'] == {'inconsistent_proposal': 1}
    assert report['per_language']['en']['total'] == 1


def test_equivalent_languages_and_entities_are_measured_separately():
    report = evaluate([case(), case('case-fil', 'fil'), case('case-taglish', 'taglish')],
                      proposal(language='en'), proposal(language='fil'), proposal(language='taglish'))
    assert report['proposal_correct'] == 3 and report['family_consistent'] == 1
    assert report['entity_correct'] == 3 and report['style_correct'] == 3
    assert set(report['per_language']) == {'en','fil','taglish'}
    assert len(report['case_set_sha256']) == 64
    assert len(report['schema_sha256']) == 64 and report['metadata']['evaluation_kind'] == 'mock'


def test_fact_or_style_errors_cannot_hide_behind_a_correct_route():
    report = evaluate([case(expected_claims=['course-a:failed:asserted'])], proposal(language='fil'))
    assert report['proposal_correct'] == 1
    assert report['claim_correct'] == 0 and report['style_correct'] == 0


@pytest.mark.parametrize('cases', [[], [case(), case()], [case(split='final')],
    [case(), case('case-fil','fil',expected='RAG')]])
def test_empty_duplicate_final_or_inconsistent_families_are_rejected(cases):
    with pytest.raises(ValueError):
        evaluate(cases, proposal())


def test_invalid_output_stays_in_the_denominator():
    router = Router(FakeTransport('invalid','invalid'))
    report = asyncio.run(api().evaluate_cases(router, [case()], metadata()))
    assert report['total'] == 1 and report['proposal_matrix'] == {'Symbolic': {'invalid': 1}}
    assert report['repair_attempts'] == 1 and report['diagnostics'] == {'invalid_model_output': 1}


def test_expected_effective_hold_is_separate_from_the_required_evidence_path():
    router = Router(FakeTransport(json.dumps(proposal(language='en'))), catalog=catalog())
    report = asyncio.run(api().evaluate_cases(router,
        [case(expected_effective='evidence_unavailable')], metadata()))
    assert report['proposal_correct'] == 1 and report['effective_correct'] == 1
    assert report['effective_matrix'] == {'evidence_unavailable': {'evidence_unavailable': 1}}


def test_wrong_operation_target_fails_meaning_even_when_all_mentions_are_correct():
    value = proposal(language='en', mentions=[dict(kind='course',text='A1',start=0,end=2),
        dict(kind='course',text='B1',start=3,end=5)],
        operations=[dict(name='check_prerequisite_eligibility',target=1)])
    report = evaluate([case(text='A1 B1',expected_entities=['course-a','course-b'],
        expected_operations=['check_prerequisite_eligibility:curriculum-a:course-a'])], value)
    assert report['proposal_correct'] == 1 and report['entity_correct'] == 1
    assert report['operation_correct'] == 0 and report['records'][0]['operation_correct'] is False


def test_report_retains_style_evidence_without_turning_it_into_a_fact():
    report = evaluate([case()], proposal(language='en'), proposal(language='en'))
    row = report['records'][0]
    assert row.get('style_evidence') is not None
    assert row['style_evidence']['english_fragments'] == ['A1']
    assert row['claims'] == () and row['style_correct']
