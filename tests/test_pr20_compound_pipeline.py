"""Bounded opt-in composition; synthetic fixtures never activate a real release."""
import asyncio
import json

from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_generation.generator import Generator
from test_compound_symbolic import QUESTION, compound_data
from test_orchestration_pipeline import ctx, ports, resources, Symbolic
from test_routing_router import FakeTransport


def run(*, enabled=False, sym=None, mixed=False, doc=None, mutate=None):
    text = QUESTION + (' What is the policy?' if mixed else '')
    data = compound_data()
    if mixed:
        data['route'] = 'Hybrid'
        start = text.index('What is')
        data['parts'].append(dict(part_id='r3', text=text[start:], start=start, end=len(text),
                                  evidence_need='document', operation_indices=[]))
    if mutate:
        mutate(data)
    release = resources(sym=sym, doc=doc)
    result = asyncio.run(Orchestrator(FakeTransport(json.dumps(data)),
        releases=ports().SyntheticReleaseProvider(release), compound_checks=enabled).run(text, ctx()))
    return text, result, release


def test_default_retains_compound_clarification_without_tool_calls():
    _, result, release = run()
    assert result.status == 'clarify' and not release.symbolic.calls
    assert result.execution_plan is None


def test_opt_in_keeps_two_validated_results_and_one_release():
    text, result, release = run(enabled=True)
    assert result.status == 'ready' and len(release.symbolic.calls) == 2
    assert result.execution_plan.schema_version == 'bintanong-execution-plan-v1'
    assert [p.understanding.parts[0].part_id for p in result.execution_parts] == ['r1', 'r2']
    assert all(p.evidence.pin == release.pin for p in result.execution_parts)
    answer = asyncio.run(Generator(FakeTransport()).generate(text, result))
    assert answer.status == 'answered' and answer.decision is None
    assert [p.answer.decision.outcome for p in answer.part_answers] == ['eligible', 'eligible']
    assert answer.part_ledger.canonical_parts == ('r1', 'r2')


def test_unknown_check_preserves_independent_answer_without_guessing():
    class UnknownFirst(Symbolic):
        async def execute(self, request, context):
            if any(i.name == 'course_id' and i.value == 'course-a' for i in request.inputs):
                context = context.model_copy(update={'facts': ()})
            return await super().execute(request, context)
    text, result, _ = run(enabled=True, sym=UnknownFirst())
    answer = asyncio.run(Generator(FakeTransport()).generate(text, result))
    assert answer.status == 'answered'
    assert answer.part_ledger.status == 'some_parts_unavailable'
    assert [p.answer.decision.outcome for p in answer.part_answers] == ['unknown', 'eligible']
    assert answer.part_ledger.canonical_parts == ('r2',)
    import pytest
    from backend.bintanong_generation.contracts import CandidateAnswer
    value = answer.model_dump(mode='json')
    assert value['missing_facts']
    value['missing_facts'] = []
    with pytest.raises(ValueError, match='compound_answer_provenance'):
        CandidateAnswer.parse(value)


def test_two_checks_survive_missing_document_without_claiming_policy():
    from test_orchestration_integration import documents
    from test_orchestration_pipeline import Documents
    text, result, _ = run(enabled=True, mixed=True,
        doc=Documents(documents(status='insufficient_evidence', passages=[])))
    answer = asyncio.run(Generator(FakeTransport()).generate(text, result))
    assert result.route == 'Hybrid' and len(answer.part_answers) == 3
    assert answer.part_ledger.status == 'some_parts_unavailable'
    assert answer.part_answers[2].answer.status == 'insufficient_evidence'
    assert not answer.part_answers[2].answer.claims


def test_document_uses_only_its_own_question_span():
    from test_orchestration_integration import documents
    from test_orchestration_pipeline import Documents
    doc = Documents(documents(status='insufficient_evidence', passages=[]))
    run(enabled=True, mixed=True, doc=doc)
    assert doc.calls[0].query == 'What is the policy?'


def test_document_conflict_holds_all_claims_without_fabricated_tie_breaker():
    from test_orchestration_integration import documents
    from test_orchestration_pipeline import Documents
    _, result, _ = run(enabled=True, mixed=True,
        doc=Documents(documents(status='conflicting_sources', passages=[])))
    assert result.status == 'clarify' and not result.execution_parts


def test_wrong_symbolic_release_never_survives_partial_composition():
    class WrongRelease(Symbolic):
        async def execute(self, request, context):
            value = (await super().execute(request, context)).model_dump(mode='json')
            value['scope']['knowledge_release_id'] = 'release-other'
            from backend.bintanong_contracts.symbolic import SymbolicResult
            return SymbolicResult.parse(value)
    _, result, _ = run(enabled=True, sym=WrongRelease())
    assert result.status == 'clarify' and not result.execution_parts


def test_duplicate_targets_and_unsupported_operations_remain_clarifications():
    from test_compound_symbolic import plan
    from backend.bintanong_orchestration.compound import CompoundNotSupported
    import pytest
    for mutate in (
        lambda data: data['operations'][1].update(target=0),
        lambda data: data['operations'][1].update(name='list_course_prerequisites'),
        lambda data: data['operations'].append(dict(data['operations'][0])),
    ):
        data = compound_data()
        mutate(data)
        release = resources()
        with pytest.raises(CompoundNotSupported):
            plan(data, release=release)
        assert not release.symbolic.calls


def test_document_tool_failure_retains_successful_checks():
    from backend.bintanong_orchestration.adapters import AdapterFailure
    from test_orchestration_pipeline import Documents
    for failure in (TimeoutError(), AdapterFailure('busy'), RuntimeError('PRIVATE FAILURE')):
        class Broken(Documents):
            async def retrieve(self, request):
                raise failure
        text, result, _ = run(enabled=True, mixed=True, doc=Broken())
        answer = asyncio.run(Generator(FakeTransport()).generate(text, result))
        assert answer.part_ledger.status == 'some_parts_unavailable'
        assert answer.part_answers[-1].answer.status == 'temporarily_unavailable'
        assert 'PRIVATE FAILURE' not in repr(answer)


def test_overlapping_parts_cannot_claim_independent_checks():
    from test_compound_symbolic import plan
    from backend.bintanong_orchestration.compound import CompoundNotSupported
    import pytest
    data = compound_data()
    data['parts'][1].update(text=QUESTION, start=0, end=len(QUESTION))
    with pytest.raises(CompoundNotSupported):
        plan(data)


def test_composition_rejects_part_swap_or_duplicate_proof_binding():
    import pytest
    from backend.bintanong_orchestration.contracts import IntegrationResult
    _, result, _ = run(enabled=True)
    value = result.model_dump(mode='json')
    value['execution_parts'][1] = value['execution_parts'][0]
    with pytest.raises(ValueError, match='execution_part_binding'):
        IntegrationResult.parse(value)


def test_research_api_flag_is_strict_and_default_off():
    import pytest
    from backend.bintanong_api.research_app import ResearchApiConfig
    field = ResearchApiConfig.model_fields['compound_checks']
    assert field.default is False
    with pytest.raises(ValueError):
        Orchestrator(FakeTransport(), compound_checks='true')


def test_authorized_research_executor_retains_authorization_and_never_activates():
    from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
    from backend.bintanong_orchestration.adapters import SymbolicAdapter
    from backend.bintanong_orchestration.ports import ReleaseResources
    from backend.bintanong_routing.contracts import RequestContext
    from test_orchestration_research_evidence import research_case
    from test_symbolic_offline_research import research
    from test_routing_validation import entry
    from test_routing_contracts import context
    pin, _ = research_case()
    runtime = research()
    catalog = tuple(entry(entity=cid, alias=alias, curriculum='curriculum-synthetic-1').model_copy(
        update={'source_ref': pin.sources[0].version_id}) for cid, alias in [('course-2', 'A1'), ('course-1', 'B1')])
    registry = CapabilityRegistry({'check_prerequisite_eligibility': Capability(
        'offline_research_prerequisite_check', ('curriculum_id', 'course_id'))})
    release = ReleaseResources(pin, catalog, registry, None, SymbolicAdapter(runtime, research=True))
    scoped = RequestContext.parse(context(curriculum_id='curriculum-synthetic-1', facts=[]))
    result = asyncio.run(Orchestrator(FakeTransport(json.dumps(compound_data())),
        releases=ports().SyntheticReleaseProvider(release), compound_checks=True).run(QUESTION, scoped))
    assert result.execution_plan is not None
    assert [p.evidence.symbolic.decision.outcome for p in result.execution_parts] == ['unknown', 'eligible']
    answer = asyncio.run(Generator(FakeTransport()).generate(QUESTION, result))
    assert answer.status == 'answered' and answer.research_ref == 'research-fictional-test'
    assert all(not p.answer.activation_allowed and not p.answer.institutional_use_allowed for p in answer.part_answers)


def test_serialized_compound_proof_cannot_relabel_or_replace_citations():
    import copy
    import pytest
    from backend.bintanong_generation.contracts import CandidateAnswer
    from backend.bintanong_orchestration.contracts import IntegrationResult
    text, result, _ = run(enabled=True)
    value = result.model_dump(mode='json')
    value['execution_parts'][0]['understanding']['parts'][0]['text'] = 'Can I take C1?'
    with pytest.raises(ValueError, match='execution_part_binding'):
        IntegrationResult.parse(value)
    answer = asyncio.run(Generator(FakeTransport()).generate(text, result))
    value = answer.model_dump(mode='json')
    swapped = copy.deepcopy(value)
    swapped['part_answers'][0]['evidence_need'] = 'document'
    with pytest.raises(ValueError, match='document_part_has_symbolic'):
        CandidateAnswer.parse(swapped)
    value['citations'][0]['text'] = 'Forged text retaining an old evidence ID'
    with pytest.raises(ValueError, match='compound_answer_provenance'):
        CandidateAnswer.parse(value)


def test_generator_rejects_untyped_integration_before_compound_dispatch():
    import pytest
    for value in ({'execution_plan': {}}, object()):
        with pytest.raises(ValueError, match='candidate_integration_required'):
            asyncio.run(Generator(FakeTransport()).generate(QUESTION, value))


def test_compound_hypothesis_remains_explicit_in_each_checked_part():
    from dataclasses import replace
    from test_routing_validation import entry
    prefix = 'If I pass P1, '
    text = prefix + QUESTION
    data = compound_data()
    for quoted in (*data['mentions'], *data['parts']):
        quoted['start'] += len(prefix)
        quoted['end'] += len(prefix)
    data['mentions'].append(dict(kind='course', text='P1', start=text.index('P1'), end=text.index('P1')+2))
    data['claims'] = [dict(entity=2, text=prefix.rstrip(', '), start=0, end=len(prefix.rstrip(', ')),
                           state='passed', mode='hypothetical')]
    release = resources()
    release = replace(release, catalog=(*release.catalog, entry(entity='course-pre', alias='P1').model_copy(
        update={'source_ref': release.pin.sources[0].version_id})))
    result = asyncio.run(Orchestrator(FakeTransport(json.dumps(data)),
        releases=ports().SyntheticReleaseProvider(release), compound_checks=True).run(text, ctx(state=None)))
    assert result.execution_plan is not None
    assert all(part.assumed_facts == ('passed:course-pre',) for part in result.execution_parts)
    answer = asyncio.run(Generator(FakeTransport()).generate(text, result))
    assert all('what-if' in part.answer.text.casefold() or 'assum' in part.answer.text.casefold()
               for part in answer.part_answers)
