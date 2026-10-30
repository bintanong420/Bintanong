"""Per-part generation: every document part gets a required answer slot.

The generator must answer or explicitly mark each declared document part; the
host derives the part->claim mapping from those slots, and the reviewer only
confirms each part's own claims. Semantic truth remains model-fallible.
"""
import asyncio
import json

import pytest

from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.evidence import prepare
from test_generation_validation import report
from test_request_understanding_pipeline import TEXT, source

OFFICE = 'File Form Q at fictional Office V.'
FEE = 'The fictional fee is 40 tokens.'


class PartModel:
    """Scripted draft slots and per-part confirmations; records every call."""
    def __init__(self, slots=None, verdicts=None):
        self.slots = slots or dict(r1=('answered', [OFFICE]), r2=('answered', [FEE]))
        self.verdicts = verdicts or {}
        self.calls = []

    async def infer(self, messages, schema):
        self.calls.append((messages, schema))
        version = schema['properties'].get('schema_version', {}).get('const')
        payload = json.loads(messages[1]['content'])
        if version == 'bintanong-part-explanation-v1':
            card = payload['evidence']['sources'][0]['evidence_id']
            answers = {p: dict(status=s, claims=[dict(text=t, evidence_ids=[card]) for t in texts])
                       for p, (s, texts) in self.slots.items()}
            return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                                   language=payload['evidence']['language'], answers=answers))
        assert set(schema['properties']) == {'parts', 'support'}  # host attaches identity
        claims = [c['claim']['claim_id'] for p in payload['parts'] for c in p['claims']]
        parts = {p['part_id']: self.verdicts.get(p['part_id'], 'answers') for p in payload['parts']}
        support = report(verdicts=[dict(claim_id=c, verdict='supported') for c in claims])
        return json.dumps(dict(parts=parts, support=support.model_dump(mode='json')))


def run(model, integration=None):
    return asyncio.run(Generator(model).generate(TEXT, integration or source()))


def test_per_part_generation_is_the_selected_default():
    assert Generator(PartModel()).explanation_profile == 'parts'


def test_draft_schema_requires_one_slot_for_every_document_part():
    model = PartModel()
    run(model)
    schema = model.calls[0][1]
    answers = schema['properties']['answers']
    assert answers['required'] == ['r1', 'r2'] and answers['additionalProperties'] is False


def test_structured_part_gets_no_document_slot_in_hybrid():
    model = PartModel(slots=dict(r2=('answered', [FEE])))
    answer = run(model, source(route='Hybrid'))
    assert model.calls[0][1]['properties']['answers']['required'] == ['r2']
    assert answer.status == 'answered' and answer.part_ledger.canonical_parts == ('r1',)


def test_complete_slots_map_each_part_to_its_own_host_numbered_claims():
    model = PartModel()
    answer = run(model)
    assert answer.status == 'answered' and len(model.calls) == 2
    assert answer.decision_guard is None and answer.question_coverage is None
    assert [c.claim_id for c in answer.claims] == ['c1', 'c2']
    assert [(e.part_id, e.claim_ids) for e in answer.part_ledger.entries] == [('r1', ('c1',)), ('r2', ('c2',))]
    assert answer.part_ledger.semantic_completeness == 'unverified'


UNCOVERED_FEE = ('The part about "what is the fee?" is not in Bintanong\'s reviewed sources yet. '
                 'Please ask the relevant university office.')
SOURCE_GAP_FEE = ('The source for the part about "what is the fee?" is incomplete or unclear, '
                  'so I cannot verify that answer. Please ask the relevant university office.')


@pytest.mark.parametrize('reason', ['not_in_evidence', 'source_gap'])
def test_covered_part_is_answered_and_the_unavailable_part_is_named(reason):
    # Owner, 24 Oct 2026 ("Answer what's covered"): replaces all-or-nothing withholding.
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=(reason, [])))
    answer = run(model)
    assert answer.status == 'answered' and [c.text for c in answer.claims] == [OFFICE]
    assert answer.part_ledger.status == 'some_parts_unavailable'
    assert [(e.part_id, e.status, e.reason) for e in answer.part_ledger.entries] == [
        ('r1', 'mapped', None), ('r2', 'unavailable', reason)]
    assert (SOURCE_GAP_FEE if reason == 'source_gap' else UNCOVERED_FEE) in answer.text.splitlines()
    review = json.loads(model.calls[1][0][1]['content'])
    assert [p['part_id'] for p in review['parts']] == ['r1']  # only the answered part is reviewed
    assert model.calls[1][1]['properties']['parts']['required'] == ['r1']


def test_every_part_unavailable_is_still_withheld_without_a_review_call():
    model = PartModel(slots=dict(r1=('not_in_evidence', []), r2=('not_in_evidence', [])))
    answer = run(model)
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert answer.validation == 'parts_unresolved' and len(model.calls) == 1


def test_a_rejected_part_still_withholds_the_whole_answer():
    # Dropping a reviewed claim would unbind the review identity; only declared gaps are named.
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('not_in_evidence', [])),
                      verdicts=dict(r1='does_not_answer'))
    answer = run(model)
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert answer.part_ledger.status == 'unresolved'


@pytest.mark.parametrize('language,note', [
    ('en', UNCOVERED_FEE),
    ('fil', 'Yung part tungkol sa "what is the fee?" ay wala pa sa reviewed sources ng Bintanong. '
            'Paki-ask sa tamang university office.'),
    ('taglish', 'Yung part tungkol sa "what is the fee?" ay wala pa sa reviewed sources ng Bintanong. '
                'Paki-ask sa tamang university office.')])
def test_hybrid_check_is_answered_when_its_document_part_is_unavailable(language, note):
    model = PartModel(slots=dict(r2=('not_in_evidence', [])))
    integration = source(route='Hybrid')
    integration = type(integration).parse(dict(integration.model_dump(mode='json'), response_style=language))
    answer = run(model, integration)
    assert answer.status == 'answered' and answer.decision is not None and not answer.claims
    assert answer.part_ledger.canonical_parts == ('r1',) and answer.part_ledger.status == 'some_parts_unavailable'
    assert note in answer.text.splitlines() and len(model.calls) == 1


def test_reviewer_rejecting_a_parts_own_claims_withholds_the_answer():
    # The observed English failure: an office claim placed under the fee part.
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('answered', [OFFICE])),
                      verdicts=dict(r2='does_not_answer'))
    answer = run(model)
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert answer.part_ledger.entries[1].status == 'uncertain'


def test_reviewer_sees_each_part_with_only_its_own_claims():
    model = PartModel()
    run(model)
    payload = json.loads(model.calls[1][0][1]['content'])
    assert [p['part_id'] for p in payload['parts']] == ['r1', 'r2']
    assert payload['parts'][1]['text'] == 'what is the fee?'
    assert [c['claim']['text'] for c in payload['parts'][1]['claims']] == [FEE]
    assert model.calls[1][1]['properties']['parts']['required'] == ['r1', 'r2']


def test_answered_slot_without_claims_is_invalid_and_repaired_once():
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('answered', [])))
    answer = run(model)
    assert answer.status == 'abstained' and answer.validation == 'repair_exhausted'
    assert len(model.calls) == 2  # two invalid drafts, no review


def test_slot_claim_budget_keeps_total_claims_within_eight():
    model = PartModel()
    run(model)
    slot = model.calls[0][1]['$defs']['PartSlot']['properties']['claims']
    assert slot['maxItems'] * 2 <= 8


def test_mapping_outside_declared_slots_cannot_reach_final_ledger():
    from backend.bintanong_generation.validation import validate_final
    from backend.bintanong_generation.contracts import CandidateAnswer
    integration = source()
    answer = run(PartModel(), integration)
    changed = answer.model_dump(mode='json')
    changed['part_ledger']['entries'][1]['claim_ids'] = ['c1']
    with pytest.raises(ValueError, match='part_claim'):
        validate_final(CandidateAnswer.parse(changed), prepare(integration), answer.claims)


def test_runtime_settings_select_per_part_generation_by_default():
    from backend.bintanong_runtime import application
    settings = [v for v in vars(application).values()
                if isinstance(v, type) and 'explanation_profile' in getattr(v, '__dataclass_fields__', {})]
    assert settings and all(s.__dataclass_fields__['explanation_profile'].default == 'parts' for s in settings)


def test_observation_reports_the_per_part_prompt_hashes():
    from backend.bintanong_generation.evaluation import load_cases, observe
    from backend.bintanong_generation.part_answers import CONFIRM_PROMPT_SHA256, PART_PROMPT_SHA256
    case = dict(case_id='parts-a', family_id='parts', split='dev', synthetic=True, question=TEXT,
                integration=source().model_dump(mode='json'))
    result = asyncio.run(observe(load_cases([case]), Generator(PartModel()), evaluation_kind='mock'))
    assert result['prompt_sha256'] == PART_PROMPT_SHA256
    assert result['support_prompt_sha256'] == CONFIRM_PROMPT_SHA256
    assert result['observations'][0]['support_prompt_sha256'] == CONFIRM_PROMPT_SHA256
    assert result['observations'][0]['generation_mode'] == 'documentary_model'


TL_OFFICE = 'I-submit mo yung Form Q sa fictional Office V.'
TL_FEE = 'Ang fee ay 40 tokens lang.'


class Drafts(PartModel):
    """Returns a different slot set for each successive draft call."""
    def __init__(self, *drafts):
        super().__init__()
        self.drafts = list(drafts)

    async def infer(self, messages, schema):
        if schema['properties'].get('schema_version', {}).get('const') == 'bintanong-part-explanation-v1':
            self.slots = self.drafts.pop(0)
        return await super().infer(messages, schema)


def styled(language):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    data = source().model_dump(mode='json')
    data['response_style'] = language
    return IntegrationResult.parse(data)


ENGLISH = dict(r1=('answered', [OFFICE]), r2=('answered', [FEE]))
TAGLISH = dict(r1=('answered', [TL_OFFICE]), r2=('answered', [TL_FEE]))


@pytest.mark.parametrize('language', ['taglish', 'fil'])
def test_english_only_claims_for_filipino_styles_use_the_one_existing_repair(language):
    model = Drafts(ENGLISH, TAGLISH)
    answer = asyncio.run(Generator(model).generate(TEXT, styled(language)))
    assert answer.status == 'answered' and answer.draft_attempts == 2
    assert [c.text for c in answer.claims] == [TL_OFFICE, TL_FEE]
    repair = json.loads(model.calls[1][0][1]['content'])
    assert repair['validation_errors'] == ['claim_not_in_requested_style']


def test_english_only_taglish_claims_twice_are_never_released():
    model = Drafts(ENGLISH, ENGLISH)
    answer = asyncio.run(Generator(model).generate(TEXT, styled('taglish')))
    assert answer.status == 'abstained' and answer.validation == 'repair_exhausted'
    assert not answer.claims and len(model.calls) == 2  # no review of an off-style draft


def test_english_requests_are_not_style_checked_for_filipino_words():
    answer = run(PartModel())
    assert answer.status == 'answered' and answer.draft_attempts == 1


@pytest.mark.parametrize('text,expected', [
    ('I-submit mo yung form sa registrar.', True), ('Ang fee ay 40 tokens.', True),
    ('Pwede ka mag-enroll after ng deadline.', True), ('Submit the form at Office V.', False),
    ('Pay the fee at the office, may 2026.', False)])
def test_filipino_function_word_detection_ignores_english_lookalikes(text, expected):
    from backend.bintanong_generation.part_answers import has_filipino_function_word
    assert has_filipino_function_word(text) is expected


def test_taglish_guidance_prefers_everyday_english_terms_without_evaluation_fixtures():
    from backend.bintanong_generation.part_answers import PART_PROMPT
    assert 'everyday' in PART_PROMPT and 'English policy terms' in PART_PROMPT
    assert 'slip S' not in PART_PROMPT and 'Office K' not in PART_PROMPT


def test_prompt_uses_two_reply_targets_and_preserves_source_terms():
    from backend.bintanong_generation.part_answers import PART_PROMPT
    assert 'Tagalog structure' in PART_PROMPT and 'mostly Filipino' not in PART_PROMPT
    assert 'source quotations' in PART_PROMPT and 'do not copy unrelated English sentences' in PART_PROMPT


@pytest.mark.parametrize('language,phrase', [('taglish', 'Tagalog sentence structure'),
                                             ('fil', 'Tagalog sentence structure')])
def test_style_repair_carries_a_plain_rewrite_instruction_for_the_requested_language(language, phrase):
    model = Drafts(ENGLISH, TAGLISH)
    asyncio.run(Generator(model).generate(TEXT, styled(language)))
    first, repair = (json.loads(model.calls[i][0][1]['content']) for i in (0, 1))
    assert 'repair_instruction' not in first
    assert phrase in repair['repair_instruction'] and 'Rewrite' in repair['repair_instruction']


def test_filler_claims_in_an_unavailable_slot_are_dropped_and_the_part_is_named():
    # Observed: the model marks a part not_in_evidence but adds a placeholder claim.
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('not_in_evidence', ['not_in_evidence'])))
    answer = run(model)
    assert answer.status == 'answered' and [c.text for c in answer.claims] == [OFFICE]
    assert answer.part_ledger.entries[1].reason == 'not_in_evidence' and UNCOVERED_FEE in answer.text


@pytest.mark.parametrize('word', ['isusumite', 'nakasaad', 'ihahain'])
def test_formal_filipino_word_is_a_preference_not_a_hard_rejection(word):
    # Owner25Oct supersedes the earlier hard exclusion; a supported answer still receives review.
    deep = dict(r1=('answered', [f'Ang slip ay {word} sa Office V.']), r2=('answered', [TL_FEE]))
    model = Drafts(deep, TAGLISH)
    answer = asyncio.run(Generator(model).generate(TEXT, styled('fil')))
    assert answer.status == 'answered' and answer.draft_attempts == 1 and answer.check_attempts == 1
    assert answer.claims[0].text == f'Ang slip ay {word} sa Office V.'


def test_model_inputs_carry_source_text_and_a_short_label_not_citation_geometry():
    model = PartModel()
    run(model)
    for messages, _ in model.calls:
        payload = json.loads(messages[1]['content'])
        sources = (payload['evidence']['sources'] if 'evidence' in payload else
                   payload['available_sources'])
        assert sources
        for source in sources:
            assert set(source) == {'evidence_id', 'kind', 'text', 'source'}
            assert 'p.' in source['source']


def test_a_deep_word_the_student_used_may_be_mirrored():
    # Owner: replies match the student's style; the ban targets words the student did not use.
    from test_request_understanding_pipeline import source as plain_source
    question = TEXT + ' Kanino isusumite?'
    from backend.bintanong_orchestration.contracts import IntegrationResult
    data = plain_source(text=question).model_dump(mode='json')
    data['response_style'] = 'fil'
    deep = dict(r1=('answered', ['Ang Form Q ay isusumite sa Office V.']), r2=('answered', [TL_FEE]))
    model = Drafts(deep)
    answer = asyncio.run(Generator(model).generate(question, IntegrationResult.parse(data)))
    assert answer.status == 'answered' and answer.draft_attempts == 1


def test_checker_output_excludes_identity_hashes_that_the_host_attaches():
    # 146 of ~212 real checker output tokens were copied hashes/version (~7 s on the dev GPU).
    model = PartModel()
    answer = run(model)
    schema = model.calls[1][1]
    assert not {'requirements_sha256', 'draft_sha256', 'schema_version'} & set(schema['properties'])
    assert answer.status == 'answered'


def test_prompts_make_recorded_source_limits_binding_without_evaluation_wording():
    # Real case: a source recorded "individual student assessment" as unavailable, yet the
    # printed total was released as the per-student answer and the checker accepted it.
    from backend.bintanong_generation.part_answers import CONFIRM_PROMPT, PART_PROMPT
    for prompt in (PART_PROMPT, CONFIRM_PROMPT):
        assert 'source_limits' in prompt and 'calculate' in prompt
        assert 'ten students' not in prompt.lower() and 'special class' not in prompt.lower()
    assert 'not_in_evidence' in PART_PROMPT and 'does_not_answer' in CONFIRM_PROMPT


@pytest.mark.parametrize('entries,valid', [
    ([('r1', 'mapped', ('c1',), None), ('r2', 'unavailable', (), 'source_gap')], True),
    ([('r1', 'mapped', ('c1',), None), ('r2', 'uncertain', (), 'uncertain')], False),
    ([('r1', 'unavailable', (), 'not_in_evidence'), ('r2', 'unavailable', (), 'source_gap')], False),
    ([('r1', 'mapped', ('c1',), None), ('r2', 'mapped', ('c2',), None)], False)])
def test_partial_ledger_needs_a_mapped_part_and_only_declared_gaps(entries, valid):
    from backend.bintanong_generation.ledger_contracts import BoundRequirementLedger
    value = dict(schema_version=BoundRequirementLedger.SCHEMA_VERSION, status='some_parts_unavailable',
        identity=dict(schema_version='bintanong-part-review-identity-v1', requirements_sha256='a'*64,
                      draft_sha256='b'*64), canonical_parts=[],
        entries=[dict(part_id=p, status=s, claim_ids=list(c), reason=r) for p, s, c, r in entries])
    if valid:
        assert BoundRequirementLedger.parse(value).status == 'some_parts_unavailable'
    else:
        with pytest.raises(ValueError, match='ledger_status_mismatch'):
            BoundRequirementLedger.parse(value)


def test_taglish_keeps_printed_wording_in_english_with_filipino_connectors():
    # Owner 30 Oct 2026: "we keep the answers that came from the data as english as is ... the connecting as
    # filipino". Observed: "shall not exceed one (1) academic year" became "hindi dapat lumagpas sa isang (1) ...".
    from backend.bintanong_generation.part_answers import PART_PROMPT, REWRITE
    for text in (PART_PROMPT, REWRITE['taglish']):
        assert "printed wording in the source's English" in text and 'only the connecting words' in text
