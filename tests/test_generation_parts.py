"""Actual-model calls are detached;these tests verify host boundaries only."""
import asyncio
import hashlib
import importlib
import importlib.util
import json

import pytest

from backend.bintanong_generation import requirements
from backend.bintanong_routing.transport import RuntimeFailure
from test_generation_requirements import QUESTION, part, setup, review


def api():
    name = 'backend.bintanong_generation.parts'
    assert importlib.util.find_spec(name) is not None, 'question-part analyzer is missing'
    return importlib.import_module(name)


class Fake:
    def __init__(self, *outputs, delay=0):
        self.outputs, self.calls, self.delay = list(outputs), [], delay

    async def infer(self, messages, schema):
        self.calls.append((messages, schema))
        if self.delay:
            await asyncio.sleep(self.delay)
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return output


def fixture(*, two_claims=False, kind='document'):
    result, plan, draft = setup(two_claims=two_claims)
    if kind != 'document':
        plan = requirements.create_plan(QUESTION, result, [part(QUESTION, 'Where do I submit Form Q'),
            part(QUESTION, 'what is its fee', 2, kind=kind)])
    extract = dict(schema_version='bintanong-question-extraction-v1', release_id=draft.release_id,
        question_sha256=hashlib.sha256(QUESTION.encode()).hexdigest(), parts=[
            dict(part_id='r1', quote='Where do I submit Form Q', kind='document'),
            dict(part_id='r2', quote='what is its fee', kind=kind)])
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
        dict(part_id='r2', status='mapped', claim_ids=['c2']) if two_claims else
        dict(part_id='r2', status='uncertain', reason='uncertain')]
    checked = review(QUESTION, result, plan, draft, mappings)
    return result, plan, draft, extract, checked


def run(fake, result, draft, *, text=QUESTION, timeout=1):
    return asyncio.run(api().QuestionPartAnalyzer(fake, timeout_seconds=timeout).analyze(text, result, draft))


def test_two_calls_return_assessed_unresolved_fee_and_preserve_full_data():
    result, plan, draft, extract, checked = fixture()
    fake = Fake(json.dumps(extract), checked.model_dump_json())
    observed = run(fake, result, draft)
    assert observed.status == 'ok' and observed.stage == 'complete'
    assert observed.plan == plan and observed.review == checked
    assert observed.ledger.status == 'unresolved' and observed.ledger.entries[1].status == 'uncertain'
    assert (observed.extraction_calls, observed.review_calls, len(fake.calls)) == (1, 1, 2)
    assert observed.elapsed_seconds >= observed.extraction_seconds + observed.review_seconds >= 0
    assert observed.semantic_completeness == 'unverified'
    assert observed.candidate_only and not observed.activation_allowed and not observed.institutional_use_allowed
    for messages, schema in fake.calls:
        payload = json.loads(messages[1]['content'])
        assert QUESTION in str(payload) and 'Fictional policy.' in str(payload)
        assert 'req-a' not in str(payload) and 'sess-' not in str(payload)
        assert 'expected' not in payload and 'reference' not in payload
    first, second = fake.calls[0][1], fake.calls[1][1]
    assert first['properties']['question_sha256']['const'] == extract['question_sha256']
    assert second['properties']['requirements_sha256']['const'] == checked.requirements_sha256
    assert second['$defs']['PartMapping']['properties']['part_id']['enum'] == ['r1', 'r2']
    assert second['$defs']['PartMapping']['properties']['claim_ids']['items']['enum'] == ['c1']
    assert second['$defs']['SupportReport']['properties']['schema_version']['const'] == 'bintanong-prose-support-v1'


def test_complete_supplied_draft_can_produce_mechanically_mapped_ledger():
    result, _, draft, extract, checked = fixture(two_claims=True)
    observed = run(Fake(json.dumps(extract), checked.model_dump_json()), result, draft)
    assert observed.ledger.status == 'all_declared_parts_mapped'
    assert observed.semantic_completeness == 'unverified'  # Not an answer or guarantee.


@pytest.mark.parametrize('kind', ['structured', 'unknown'])
def test_structured_or_unknown_part_is_unresolved_even_if_review_maps_a_document_claim(kind):
    result, plan, draft, extract, _ = fixture(kind=kind)
    checked = review(QUESTION, result, plan, draft, [dict(part_id='r1', status='mapped', claim_ids=['c1']),
        dict(part_id='r2', status='mapped', claim_ids=['c1'])])
    observed = run(Fake(json.dumps(extract), checked.model_dump_json()), result, draft)
    assert observed.status == 'ok' and observed.ledger.status == 'unresolved'
    assert observed.ledger.entries[1].reason in ('structured_check_not_run', 'unknown_requirement_kind')


@pytest.mark.parametrize('mutation', ['release', 'question_hash', 'missing_quote', 'duplicate_id', 'duplicate_quote',
    'blank_quote', 'extra', 'wrong_kind', 'empty', 'malformed'])
def test_bad_extraction_stops_after_one_call_without_exposing_output(mutation):
    result, _, draft, extract, _ = fixture()
    if mutation == 'release': extract['release_id'] = 'release-other'
    elif mutation == 'question_hash': extract['question_sha256'] = 'f' * 64
    elif mutation == 'missing_quote': extract['parts'][1]['quote'] = 'sess-secret-9'
    elif mutation == 'duplicate_id': extract['parts'][1]['part_id'] = 'r1'
    elif mutation == 'duplicate_quote': extract['parts'][1]['quote'] = extract['parts'][0]['quote']
    elif mutation == 'blank_quote': extract['parts'][1]['quote'] = ' '
    elif mutation == 'extra': extract['instruction'] = 'sess-secret-9'
    elif mutation == 'wrong_kind': extract['parts'][1]['kind'] = 'approved'
    elif mutation == 'empty': extract['parts'] = []
    output = 'sess-secret-9' if mutation == 'malformed' else json.dumps(extract)
    fake = Fake(output)
    observed = run(fake, result, draft)
    assert (observed.status, observed.stage, observed.extraction_calls, observed.review_calls) == ('invalid_output', 'extraction', 1, 0)
    assert len(fake.calls) == 1 and observed.plan is None and observed.review is None and observed.ledger is None
    assert 'sess-secret-9' not in observed.model_dump_json()


@pytest.mark.parametrize('text,quote', [('Fee? Fee?', 'Fee'), ('aaaa', 'aaa')])
def test_ambiguous_including_overlapping_quote_occurrences_are_rejected(text, quote):
    result, _, draft, extract, _ = fixture()
    extract['question_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    extract['parts'] = [dict(part_id='r1', quote=quote, kind='document')]
    observed = run(Fake(json.dumps(extract)), result, draft, text=text)
    assert observed.status == 'invalid_output' and observed.review_calls == 0


def test_offsets_are_host_computed_from_exact_original_unicode_string():
    text = '  Cafe\u0301 📝, saan ang Form Q?  '
    result, _, draft, extract, _ = fixture()
    extract['question_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    extract['parts'] = [dict(part_id='r1', quote='saan ang Form Q', kind='document')]
    plan = requirements.create_plan(text, result, [part(text, 'saan ang Form Q')])
    checked = review(text, result, plan, draft)
    observed = run(Fake(json.dumps(extract), checked.model_dump_json()), result, draft, text=text)
    assert observed.plan.parts[0].start == 11 and observed.plan.parts[0].end == 26
    assert text[11:26] == 'saan ang Form Q'


@pytest.mark.parametrize('mutation', ['identity', 'foreign_part', 'foreign_claim', 'duplicate', 'empty', 'malformed'])
def test_bad_review_preserves_only_checked_plan_and_stops_after_two_calls(mutation):
    result, _, draft, extract, checked = fixture()
    value = checked.model_dump(mode='json')
    if mutation == 'identity': value['draft_sha256'] = 'f' * 64
    elif mutation == 'foreign_part': value['parts'][1]['part_id'] = 'r3'
    elif mutation == 'foreign_claim': value['parts'][0]['claim_ids'] = ['c2']
    elif mutation == 'duplicate': value['parts'][1] = value['parts'][0]
    elif mutation == 'empty': value['parts'] = []
    output = 'sess-secret-9' if mutation == 'malformed' else json.dumps(value)
    observed = run(Fake(json.dumps(extract), output), result, draft)
    assert (observed.status, observed.stage, observed.extraction_calls, observed.review_calls) == ('invalid_output', 'review', 1, 1)
    assert observed.plan is not None and observed.review is None and observed.ledger is None
    assert 'sess-secret-9' not in observed.model_dump_json()


def test_negative_support_is_an_unresolved_ledger_not_a_parser_success_claim():
    result, _, draft, extract, checked = fixture()
    value = checked.model_dump(mode='json')
    value['support']['verdicts'][0]['verdict'] = 'unsupported'
    observed = run(Fake(json.dumps(extract), json.dumps(value)), result, draft)
    assert observed.status == 'ok' and observed.ledger.status == 'unresolved'
    assert observed.ledger.errors == ('unsupported_claim',)


@pytest.mark.parametrize('route', ['Hybrid', 'Symbolic'])
def test_other_routes_are_rejected_without_calling_transport(route):
    from test_generation_evidence import integrated
    result, _, draft, _, _ = fixture()
    fake = Fake()
    with pytest.raises(ValueError): run(fake, integrated(route), draft)
    assert fake.calls == []


@pytest.mark.parametrize('change', ['private_question', 'private_claim', 'wrong_release', 'nonready'])
def test_invalid_input_is_rejected_before_any_model_call(change):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    result, _, draft, _, _ = fixture()
    text = QUESTION
    if change == 'private_question': text += ' sess-secret-9'
    elif change == 'private_claim': draft = draft.model_copy(update=dict(claims=(draft.claims[0].model_copy(update=dict(text='sess-secret-9')),)))
    elif change == 'wrong_release': draft = draft.model_copy(update=dict(release_id='release-other'))
    else:
        raw = result.model_dump(mode='json')
        raw['evidence']['documents']['status'] = 'uncalibrated'
        result = IntegrationResult.parse(raw)
    fake = Fake()
    with pytest.raises(ValueError): run(fake, result, draft, text=text)
    assert fake.calls == []


@pytest.mark.parametrize('error,status', [(RuntimeFailure('model_timeout'), 'timeout'),
    (RuntimeFailure('truncated_output'), 'tool_error'), (RuntimeError('sess-secret-9'), 'tool_error')])
@pytest.mark.parametrize('stage', ['extraction', 'review'])
def test_transport_failures_are_bounded_fixed_states(error, status, stage):
    result, _, draft, extract, _ = fixture()
    fake = Fake(error) if stage == 'extraction' else Fake(json.dumps(extract), error)
    observed = run(fake, result, draft)
    assert observed.status == status and observed.stage == stage
    assert len(fake.calls) == (1 if stage == 'extraction' else 2)
    assert 'sess-secret-9' not in observed.model_dump_json()


def test_one_deadline_covers_both_calls_without_a_fresh_review_budget():
    result, _, draft, extract, checked = fixture()
    observed = run(Fake(json.dumps(extract), checked.model_dump_json(), delay=0.05), result, draft, timeout=0.08)
    assert observed.status == 'timeout' and observed.stage == 'review'
    assert observed.extraction_calls == observed.review_calls == 1 and observed.ledger is None


def test_external_cancellation_propagates_without_starting_another_call():
    result, _, draft, _, _ = fixture()
    async def exercise():
        started = asyncio.Event()
        class Blocked:
            async def infer(self, messages, schema):
                started.set()
                await asyncio.Event().wait()
        task = asyncio.create_task(api().QuestionPartAnalyzer(Blocked()).analyze(QUESTION, result, draft))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
    asyncio.run(exercise())


def test_concurrent_analyses_keep_request_bound_review_identities_separate():
    result, plan, draft, extract, checked = fixture()
    other = result.model_copy(update=dict(request_id='req-other'))
    mappings = checked.model_dump(mode='json')['parts']
    second = review(QUESTION, other, plan, draft, mappings)
    reports = {r.requirements_sha256: r.model_dump_json() for r in (checked, second)}
    class Concurrent:
        async def infer(self, messages, schema):
            await asyncio.sleep(0)
            if schema['properties']['schema_version']['const'] == 'bintanong-question-extraction-v1':
                return json.dumps(extract)
            return reports[schema['properties']['requirements_sha256']['const']]
    async def exercise():
        analyzer = api().QuestionPartAnalyzer(Concurrent())
        return await asyncio.gather(analyzer.analyze(QUESTION, result, draft), analyzer.analyze(QUESTION, other, draft))
    a, b = asyncio.run(exercise())
    assert a.status == b.status == 'ok'
    assert a.ledger.identity.requirements_sha256 != b.ledger.identity.requirements_sha256


@pytest.mark.parametrize('timeout', [0, -1, float('nan'), float('inf'), True, '120'])
def test_invalid_deadline_configuration_is_rejected(timeout):
    with pytest.raises(ValueError): api().QuestionPartAnalyzer(Fake(), timeout_seconds=timeout)
