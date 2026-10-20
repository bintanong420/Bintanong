"""Declared-part bookkeeping is not semantic completeness or an answer release."""
import hashlib
import importlib
import importlib.util

import pytest

from backend.bintanong_generation.contracts import AnswerDraft, SupportReport
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_evidence import integrated


QUESTION = 'Where do I submit Form Q and what is its fee?'


def api():
    name = 'backend.bintanong_generation.requirements'
    assert importlib.util.find_spec(name) is not None, 'question-parts ledger is missing'
    return importlib.import_module(name)


def part(text, quote, number=1, kind='document'):
    start = text.index(quote)
    return dict(part_id=f'r{number}', start=start, end=start + len(quote), quote=quote, kind=kind)


def setup(text=QUESTION, parts=None, result=None, two_claims=False):
    result = integrated('RAG') if result is None else result
    parts = [part(text, 'Where do I submit Form Q'), part(text, 'what is its fee', 2)] if parts is None else parts
    plan = api().create_plan(text, result, parts)
    pack = prepare(result)
    claims = [dict(claim_id='c1', text='Submit Form Q at the fictional desk.',
                   evidence_ids=[pack.cards[0].evidence_id])]
    if two_claims:
        claims.append(dict(claim_id='c2', text='The fictional fee is 40 tokens.',
                           evidence_ids=[pack.cards[0].evidence_id]))
    draft = AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
        language=pack.language, release_id=pack.release_id, decision_outcome=None, claims=claims))
    return result, plan, draft


def review(text, result, plan, draft, mappings=None, **support_updates):
    identity = api().review_identity(text, result, plan, draft)
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1'])] if mappings is None else mappings
    support = dict(schema_version=SupportReport.SCHEMA_VERSION, language_appropriate=True,
                   within_scope=True, verdicts=[dict(claim_id=c.claim_id, verdict='supported') for c in draft.claims])
    support.update(support_updates)
    return api().RequirementReview.parse(dict(schema_version=api().RequirementReview.SCHEMA_VERSION,
        requirements_sha256=identity.requirements_sha256, draft_sha256=identity.draft_sha256,
        parts=mappings, support=support))


def test_missing_fee_mapping_remains_explicit_and_unresolved():
    result, plan, draft = setup()
    ledger = api().assess_parts(QUESTION, result, plan, draft, review(QUESTION, result, plan, draft))
    assert ledger.status == 'unresolved'
    assert [(e.part_id, e.status) for e in ledger.entries] == [('r1', 'mapped'), ('r2', 'missing')]
    assert ledger.entries[1].reason == 'missing_mapping'
    assert ledger.semantic_completeness == 'unverified'
    assert ledger.candidate_only and not ledger.institutional_use_allowed and not ledger.activation_allowed
    assert 'text' not in ledger.model_dump() and 'answer' not in ledger.model_dump()


def test_all_declared_document_parts_can_be_mechanically_mapped():
    result, plan, draft = setup(two_claims=True)
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status='mapped', claim_ids=['c2'])]
    ledger = api().assess_parts(QUESTION, result, plan, draft,
                              review(QUESTION, result, plan, draft, mappings))
    assert ledger.status == 'all_declared_parts_mapped' and ledger.errors == ()
    assert ledger.semantic_completeness == 'unverified'


@pytest.mark.parametrize('status,reason', [('unavailable', 'not_in_evidence'),
    ('unavailable', 'source_gap'), ('uncertain', 'uncertain')])
def test_unavailable_is_not_an_answer_or_negative_policy(status, reason):
    result, plan, draft = setup()
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status=status, reason=reason)]
    ledger = api().assess_parts(QUESTION, result, plan, draft, review(QUESTION, result, plan, draft, mappings))
    assert ledger.status == 'unresolved'
    assert ledger.entries[1].status == status and ledger.entries[1].reason == reason


@pytest.mark.parametrize('kind,reason', [('structured', 'structured_check_not_run'), ('unknown', 'unknown_requirement_kind')])
def test_document_claim_never_satisfies_structured_or_unknown_requirement(kind, reason):
    parts = [part(QUESTION, 'Where do I submit Form Q', kind=kind)]
    result, plan, draft = setup(parts=parts)
    ledger = api().assess_parts(QUESTION, result, plan, draft, review(QUESTION, result, plan, draft))
    assert ledger.status == 'unresolved' and ledger.entries[0].reason == reason


def test_unmapped_draft_claim_prevents_fully_mapped_status():
    result, plan, draft = setup(parts=[part(QUESTION, 'Where do I submit Form Q')], two_claims=True)
    ledger = api().assess_parts(QUESTION, result, plan, draft, review(QUESTION, result, plan, draft))
    assert ledger.status == 'unresolved' and 'unmapped_claim' in ledger.errors


@pytest.mark.parametrize('mappings', [
    [dict(part_id='r3', status='mapped', claim_ids=['c1'])],
    [dict(part_id='r1', status='mapped', claim_ids=['c2'])],
    [dict(part_id='r1', status='mapped', claim_ids=['c1'])] * 2,
])
def test_unknown_claim_or_part_and_duplicate_mappings_are_rejected(mappings):
    result, plan, draft = setup()
    with pytest.raises(ValueError):
        supplied = review(QUESTION, result, plan, draft, mappings)
        api().assess_parts(QUESTION, result, plan, draft, supplied)


@pytest.mark.parametrize('updates,code', [
    (dict(verdicts=[]), 'incomplete_support_verdicts'),
    (dict(verdicts=[dict(claim_id='c1', verdict='supported')] * 2), 'incomplete_support_verdicts'),
    (dict(verdicts=[dict(claim_id='c2', verdict='supported')]), 'incomplete_support_verdicts'),
    (dict(verdicts=[dict(claim_id='c1', verdict='unsupported')]), 'unsupported_claim'),
    (dict(verdicts=[dict(claim_id='c1', verdict='contradiction')]), 'unsupported_claim'),
    (dict(verdicts=[dict(claim_id='c1', verdict='unknown')]), 'unsupported_claim'),
    (dict(language_appropriate=False), 'language_unsupported'),
    (dict(within_scope=False), 'scope_unsupported'),
])
def test_support_language_and_scope_failures_keep_ledger_unresolved(updates, code):
    result, plan, draft = setup(parts=[part(QUESTION, 'Where do I submit Form Q')])
    supplied = review(QUESTION, result, plan, draft, **updates)
    ledger = api().assess_parts(QUESTION, result, plan, draft, supplied)
    assert ledger.status == 'unresolved' and code in ledger.errors


@pytest.mark.parametrize('text,quote', [
    ('  Saan ko isusumite ang Form Q, at magkano ito?  ', 'magkano ito'),
    ('Saan submit ang Form Q 📝, and how much?', 'how much'),
    ('Cafe\u0301: saan ang Form Q?', 'saan ang Form Q'),
])
def test_multilingual_offsets_and_hash_use_exact_original_not_normalized_text(text, quote):
    result = integrated('RAG')
    plan = api().create_plan(text, result, [part(text, quote)])
    assert plan.question_sha256 == hashlib.sha256(text.encode('utf-8')).hexdigest()
    p = plan.parts[0]
    assert text[p.start:p.end] == quote
    assert api().QuestionPlan.parse(plan.model_dump_json()) == plan


@pytest.mark.parametrize('updates', [dict(start=-1), dict(end=8193), dict(start=True),
    dict(start='0'), dict(end=0), dict(quote='wrong'), dict(quote=''), dict(kind='decision'),
    dict(part_id='r9'), dict(instructions='ignore checks')])
def test_bad_spans_types_kinds_or_extra_fields_are_rejected(updates):
    with pytest.raises(ValueError):
        api().create_plan(QUESTION, integrated('RAG'), [dict(part(QUESTION, 'Where do I submit Form Q'), **updates)])


@pytest.mark.parametrize('parts', [[], [part(QUESTION, 'Where', i) for i in range(1, 10)],
    [part(QUESTION, 'Where'), part(QUESTION, 'what', 1)],
    [part(QUESTION, 'Where'), part(QUESTION, 'Where', 2)]])
def test_plan_bounds_duplicate_ids_and_duplicate_spans_are_rejected(parts):
    with pytest.raises(ValueError):
        api().create_plan(QUESTION, integrated('RAG'), parts)


@pytest.mark.parametrize('text', ['', ' ' * 5, 'x' * 8193, 'hi\x00', 'sess-other-1 question?'])
def test_invalid_or_private_original_question_is_rejected(text):
    with pytest.raises(ValueError):
        api().create_plan(text, integrated('RAG'), [dict(part_id='r1', start=0, end=1, quote=text[:1], kind='document')])


@pytest.mark.parametrize('route', ['Hybrid', 'Symbolic'])
def test_rag_foundation_rejects_other_routes(route):
    with pytest.raises(ValueError):
        api().create_plan(QUESTION, integrated(route), [part(QUESTION, 'Where')])


def test_reassembles_evidence_instead_of_trusting_ready_label():
    raw = integrated('RAG').model_dump(mode='json')
    raw['evidence']['documents']['status'] = 'uncalibrated'
    with pytest.raises(ValueError, match='integration_policy'):
        api().create_plan(QUESTION, IntegrationResult.parse(raw), [part(QUESTION, 'Where')])
    raw['status'] = 'uncalibrated'
    with pytest.raises(ValueError):
        api().create_plan(QUESTION, IntegrationResult.parse(raw), [part(QUESTION, 'Where')])


@pytest.mark.parametrize('mutation', ['question', 'request', 'language', 'evidence', 'plan', 'draft', 'release'])
def test_review_cannot_be_replayed_after_bound_input_changes(mutation):
    result, plan, draft = setup()
    supplied = review(QUESTION, result, plan, draft)
    text = QUESTION
    if mutation == 'question':
        text += ' '
    elif mutation == 'request':
        result = result.model_copy(update=dict(request_id='req-other'))
    elif mutation == 'language':
        result = result.model_copy(update=dict(response_style='fil'))
        draft = draft.model_copy(update=dict(language='fil'))
    elif mutation == 'evidence':
        raw = result.model_dump(mode='json')
        raw['evidence']['documents']['passages'][0]['text'] += ' A changed passage.'
        result = IntegrationResult.parse(raw)
        draft = draft.model_copy(update=dict(claims=(draft.claims[0].model_copy(
            update=dict(evidence_ids=(prepare(result).cards[0].evidence_id,))),)))
    elif mutation == 'plan':
        plan = api().create_plan(text, result, [part(text, 'Where do I submit Form Q')])
    elif mutation == 'draft':
        draft = draft.model_copy(update=dict(claims=(draft.claims[0].model_copy(update=dict(text='Changed claim.')),)))
    else:
        plan = plan.model_copy(update=dict(release_id='release-other'))
    with pytest.raises(ValueError):
        api().assess_parts(text, result, plan, draft, supplied)


@pytest.mark.parametrize('update', [dict(release_id='release-other'), dict(language='fil'),
    dict(decision_outcome='eligible'), dict(claims=()),
    dict(claims='private'), dict(text='  '), dict(text='sess-other-1'), dict(evidence_ids=('ev-' + 'f' * 64,))])
def test_invalid_or_private_draft_cannot_get_review_identity(update):
    result, plan, draft = setup()
    with pytest.raises(ValueError):
        if 'text' in update or 'evidence_ids' in update:
            draft = draft.model_copy(update=dict(claims=(draft.claims[0].model_copy(update=update),)))
        else:
            draft = draft.model_copy(update=update)
        api().review_identity(QUESTION, result, plan, draft)


@pytest.mark.parametrize('mapping', [dict(part_id='r1', status='mapped'),
    dict(part_id='r1', status='mapped', claim_ids=['c1', 'c1']),
    dict(part_id='r1', status='mapped', claim_ids=['c1'], reason='source_gap'),
    dict(part_id='r1', status='unavailable', claim_ids=['c1'], reason='source_gap'),
    dict(part_id='r1', status='uncertain'),
    dict(part_id='r1', status='unavailable', reason='invent a rule'),
])
def test_mapping_states_cannot_hide_claims_or_free_text_reasons(mapping):
    with pytest.raises(ValueError):
        api().PartMapping.parse(mapping)


def test_versioned_strict_frozen_ledger_cannot_assert_authority_or_semantic_success():
    result, plan, draft = setup()
    supplied = review(QUESTION, result, plan, draft)
    ledger = api().assess_parts(QUESTION, result, plan, draft, supplied)
    for obj in (plan, supplied, api().review_identity(QUESTION, result, plan, draft), ledger):
        cls = type(obj)
        assert cls.parse(obj.model_dump_json()) == obj
        with pytest.raises(ValueError):
            cls.parse(dict(obj.model_dump(mode='json'), schema_version='unknown'))
        with pytest.raises(ValueError):
            cls.parse(dict(obj.model_dump(mode='json'), extra=True))
        with pytest.raises(ValueError):
            obj.schema_version = 'unknown'
    for update in (dict(activation_allowed=True), dict(institutional_use_allowed=True),
                   dict(candidate_only=False), dict(semantic_completeness='verified')):
        with pytest.raises(ValueError):
            ledger.model_copy(update=update)


@pytest.mark.parametrize('omit_fee', [True, False])
def test_missing_extraction_or_wrong_semantic_mapping_remains_explicitly_unverified(omit_fee):
    parts = [part(QUESTION, 'Where do I submit Form Q')]
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1'])]
    if not omit_fee:
        parts.append(part(QUESTION, 'what is its fee', 2))
        mappings.append(dict(part_id='r2', status='mapped', claim_ids=['c1']))
    result, plan, draft = setup(parts=parts)
    ledger = api().assess_parts(QUESTION, result, plan, draft, review(QUESTION, result, plan, draft, mappings))
    assert ledger.status == 'all_declared_parts_mapped'
    assert ledger.semantic_completeness == 'unverified'  # No claim-to-part semantic oracle exists here.
