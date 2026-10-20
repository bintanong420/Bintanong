"""Reference labels expose ledger false positives without pretending to run extraction."""
import importlib
import importlib.util

import pytest

from backend.bintanong_generation import requirements as ledger_api
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_requirements import QUESTION, part, setup, review


def api():
    name = 'evaluation.question_parts'
    assert importlib.util.find_spec(name) is not None, 'reference evaluator is missing'
    return importlib.import_module(name)


def reference(result, plan, draft, expected=None):
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status='uncertain', reason='uncertain')] if expected is None else expected
    identity = ledger_api.review_identity(QUESTION, result, plan, draft)
    return api().QuestionPartsReference.parse(dict(schema_version=api().QuestionPartsReference.SCHEMA_VERSION,
        case_id='fictional-location-fee', plan=plan.model_dump(mode='json'),
        identity=identity.model_dump(mode='json'), expected=expected))


def assess(result, plan, draft, supplied, gold, text=QUESTION):
    return api().evaluate_parts(text, result, plan, draft, supplied, gold)


def test_omitted_extraction_is_counted_against_the_full_reference():
    result, full, draft = setup()
    gold = reference(result, full, draft)
    plan = ledger_api.create_plan(QUESTION, result, [part(QUESTION, 'Where do I submit Form Q')])
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft), gold)
    assert (score.expected_count, score.predicted_count, score.matched_count) == (2, 1, 1)
    assert score.exact_span_and_kind_precision == 1.0 and score.exact_span_and_kind_recall == 0.5
    assert score.correct_mapping_count == 1 and score.mapping_recall == 0.5
    assert score.missing_reference_parts == ('r2',)
    assert score.incorrect_mapping_parts == ('r2',)
    assert not score.agrees_with_reference and score.false_complete_against_reference


def test_wrong_semantic_mapping_is_a_false_completion_against_frozen_labels():
    result, plan, draft = setup()
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status='mapped', claim_ids=['c1'])]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, mappings), reference(result, plan, draft))
    assert score.matched_count == 2 and score.exact_span_and_kind_recall == 1.0
    assert score.correct_mapping_count == 1 and score.incorrect_mapping_parts == ('r2',)
    assert not score.agrees_with_reference and score.false_complete_against_reference


def test_missing_mapping_fails_reference_without_claiming_a_released_false_completion():
    result, plan, draft = setup()
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft), reference(result, plan, draft))
    assert score.correct_mapping_count == 1 and score.mapping_recall == 0.5
    assert score.ledger_status == 'unresolved' and not score.false_complete_against_reference
    assert not score.agrees_with_reference


@pytest.mark.parametrize('status,reason', [('uncertain', 'uncertain'), ('unavailable', 'source_gap')])
def test_correct_unresolved_mapping_can_agree_without_becoming_complete(status, reason):
    result, plan, draft = setup()
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status=status, reason=reason)]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, expected),
                   reference(result, plan, draft, expected))
    assert score.agrees_with_reference and score.correct_mapping_count == 2
    assert score.ledger_status == 'unresolved' and not score.false_complete_against_reference
    assert score.semantic_completeness == 'unverified'


def test_fully_answered_reference_requires_all_expected_claims():
    result, plan, draft = setup(two_claims=True)
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status='mapped', claim_ids=['c2'])]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, expected),
                   reference(result, plan, draft, expected))
    assert score.agrees_with_reference and score.ledger_status == 'all_declared_parts_mapped'
    assert score.mapping_recall == 1.0 and not score.false_complete_against_reference
    assert score.semantic_completeness == 'unverified'


def test_renumbered_reordered_candidate_parts_do_not_change_the_result():
    result, full, draft = setup()
    plan = ledger_api.create_plan(QUESTION, result, [part(QUESTION, 'what is its fee', 1),
                                                    part(QUESTION, 'Where do I submit Form Q', 2)])
    mappings = [dict(part_id='r1', status='uncertain', reason='uncertain'),
                dict(part_id='r2', status='mapped', claim_ids=['c1'])]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, mappings), reference(result, full, draft))
    assert score.agrees_with_reference and score.correct_mapping_count == 2


def test_claim_order_is_ignored_but_a_missing_member_is_not():
    result, full, draft = setup(two_claims=True)
    plan = ledger_api.create_plan(QUESTION, result, [part(QUESTION, QUESTION)])
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1', 'c2'])]
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c2', 'c1'])]
    gold = reference(result, plan, draft, expected)
    assert assess(result, plan, draft, review(QUESTION, result, plan, draft, mappings), gold).agrees_with_reference
    missing = [dict(part_id='r1', status='mapped', claim_ids=['c1'])]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, missing), gold)
    assert not score.agrees_with_reference and score.correct_mapping_count == 0


def test_kind_downgrade_cannot_satisfy_a_structured_reference():
    result, actual, draft = setup()
    gold_plan = ledger_api.create_plan(QUESTION, result, [part(QUESTION, 'Where do I submit Form Q'),
        part(QUESTION, 'what is its fee', 2, kind='structured')])  # Deliberate contract fixture,not semantic annotation.
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status='uncertain', reason='structured_check_not_run')]
    mappings = [dict(part_id='r1', status='mapped', claim_ids=['c1']),
                dict(part_id='r2', status='mapped', claim_ids=['c1'])]
    score = assess(result, actual, draft, review(QUESTION, result, actual, draft, mappings),
                   reference(result, gold_plan, draft, expected))
    assert score.matched_count == 1 and score.kind_mismatched_parts == ('r2',)
    assert score.incorrect_mapping_parts == ('r2',) and score.false_complete_against_reference


def test_alternate_boundaries_require_adjudication_instead_of_automatic_semantic_matching():
    result, full, draft = setup()
    plan = ledger_api.create_plan(QUESTION, result, [part(QUESTION, 'Where'), part(QUESTION, 'what is its fee', 2)])
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1']), dict(part_id='r2', status='uncertain', reason='uncertain')]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, expected), reference(result, full, draft))
    assert score.missing_reference_parts == ('r1',) and score.unexpected_candidate_parts == ('r1',)
    assert score.matched_count == 1 and not score.agrees_with_reference


@pytest.mark.parametrize('support_updates', [dict(within_scope=False), dict(language_appropriate=False),
    dict(verdicts=[]), dict(verdicts=[dict(claim_id='c1', verdict='unsupported')])])
def test_matching_mappings_cannot_bypass_existing_support_guards(support_updates):
    result, plan, draft = setup()
    expected = [dict(part_id='r1', status='mapped', claim_ids=['c1']), dict(part_id='r2', status='uncertain', reason='uncertain')]
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft, expected, **support_updates),
                   reference(result, plan, draft, expected))
    assert score.correct_mapping_count == 2 and score.support_errors
    assert not score.agrees_with_reference and score.ledger_status == 'unresolved'


@pytest.mark.parametrize('mutation', ['question', 'request', 'language', 'release', 'evidence', 'draft'])
def test_reference_cannot_be_reused_after_bound_inputs_change(mutation):
    result, plan, draft = setup()
    gold = reference(result, plan, draft)
    text = QUESTION
    if mutation == 'question':
        text += ' '
    elif mutation == 'request':
        result = result.model_copy(update=dict(request_id='req-other',understanding=
            result.understanding.model_copy(update=dict(request_id='req-other'))))
    elif mutation == 'language':
        result = result.model_copy(update=dict(response_style='fil'))
        draft = draft.model_copy(update=dict(language='fil'))
    elif mutation == 'release':
        raw = result.model_dump(mode='json')
        raw['evidence']['pin']['release_id'] = 'release-other'
        raw['evidence']['documents']['release_id'] = 'release-other'
        raw['understanding']['release_id'] = 'release-other'
        result = IntegrationResult.parse(raw)
        draft = draft.model_copy(update=dict(release_id='release-other'))
    elif mutation == 'evidence':
        raw = result.model_dump(mode='json')
        raw['evidence']['documents']['passages'][0]['text'] += ' Changed.'
        result = IntegrationResult.parse(raw)
        from backend.bintanong_generation.evidence import prepare
        draft = draft.model_copy(update=dict(claims=(draft.claims[0].model_copy(
            update=dict(evidence_ids=(prepare(result).cards[0].evidence_id,))),)))
    else:
        draft = draft.model_copy(update=dict(claims=(draft.claims[0].model_copy(update=dict(text='Changed.')),)))
    plan = ledger_api.create_plan(text, result, [part(text, 'Where do I submit Form Q'), part(text, 'what is its fee', 2)])
    with pytest.raises(ValueError):
        assess(result, plan, draft, review(text, result, plan, draft), gold, text=text)


@pytest.mark.parametrize('expected', [[], [dict(part_id='r1', status='mapped', claim_ids=['c1'])],
    [dict(part_id='r1', status='mapped', claim_ids=['c1'])] * 2,
    [dict(part_id='r1', status='mapped', claim_ids=['c1']), dict(part_id='r3', status='uncertain', reason='uncertain')],
    [dict(part_id='r1', status='mapped', claim_ids=['c2']), dict(part_id='r2', status='uncertain', reason='uncertain')]])
def test_incomplete_duplicate_foreign_or_unknown_claim_labels_are_rejected(expected):
    result, plan, draft = setup()
    with pytest.raises(ValueError):
        gold = reference(result, plan, draft, expected)
        assess(result, plan, draft, review(QUESTION, result, plan, draft), gold)


@pytest.mark.parametrize('kind', ['structured', 'unknown'])
def test_reference_cannot_label_a_rag_document_claim_as_a_structured_answer(kind):
    result, _, draft = setup()
    plan = ledger_api.create_plan(QUESTION, result, [part(QUESTION, QUESTION, kind=kind)])
    with pytest.raises(ValueError):
        reference(result, plan, draft, [dict(part_id='r1', status='mapped', claim_ids=['c1'])])


@pytest.mark.parametrize('update', [dict(synthetic=False), dict(split='final'), dict(annotation_status='university_approved'),
    dict(case_id='sess-other-1'), dict(extra=True), dict(schema_version='unknown')])
def test_reference_stays_strict_synthetic_dev_and_author_labeled(update):
    result, plan, draft = setup()
    gold = reference(result, plan, draft)
    with pytest.raises(ValueError):
        api().QuestionPartsReference.parse(dict(gold.model_dump(mode='json'), **update))


def test_private_or_invalid_integration_cannot_be_scored():
    result, plan, draft = setup()
    gold = reference(result, plan, draft)
    supplied = review(QUESTION, result, plan, draft)
    raw = result.model_dump(mode='json')
    raw['evidence']['documents']['status'] = 'uncalibrated'
    with pytest.raises(ValueError):
        assess(IntegrationResult.parse(raw), plan, draft, supplied, gold)
    with pytest.raises(ValueError):
        assess(result, plan, draft, supplied, gold, text=QUESTION + ' sess-other-1')


def test_score_and_reference_are_frozen_and_cannot_grant_answer_authority():
    result, plan, draft = setup()
    gold = reference(result, plan, draft)
    score = assess(result, plan, draft, review(QUESTION, result, plan, draft), gold)
    for obj in (gold, score):
        assert type(obj).parse(obj.model_dump_json()) == obj
        with pytest.raises(ValueError):
            obj.schema_version = 'changed'
    assert score.candidate_only and not score.activation_allowed and not score.institutional_use_allowed
    assert score.semantic_completeness == 'unverified' and 'text' not in score.model_dump()
    for update in (dict(activation_allowed=True), dict(institutional_use_allowed=True),
                   dict(candidate_only=False), dict(semantic_completeness='verified')):
        with pytest.raises(ValueError):
            score.model_copy(update=update)
