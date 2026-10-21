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
        version = schema['properties']['schema_version']['const']
        payload = json.loads(messages[1]['content'])
        if version == 'bintanong-part-explanation-v1':
            card = payload['evidence']['sources'][0]['evidence_id']
            answers = {p: dict(status=s, claims=[dict(text=t, evidence_ids=[card]) for t in texts])
                       for p, (s, texts) in self.slots.items()}
            return json.dumps(dict(schema_version=version, release_id=payload['evidence']['release_id'],
                                   language=payload['evidence']['language'], answers=answers))
        assert version == 'bintanong-part-confirmation-v1'
        identity = payload['review_identity']
        claims = [c['claim']['claim_id'] for p in payload['parts'] for c in p['claims']]
        parts = {p['part_id']: self.verdicts.get(p['part_id'], 'answers') for p in payload['parts']}
        support = report(verdicts=[dict(claim_id=c, verdict='supported') for c in claims])
        return json.dumps(dict(schema_version=version, requirements_sha256=identity['requirements_sha256'],
                               draft_sha256=identity['draft_sha256'], parts=parts,
                               support=support.model_dump(mode='json')))


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


def test_part_declared_not_in_evidence_is_withheld_without_a_review_call():
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('not_in_evidence', [])))
    answer = run(model)
    assert answer.status == 'insufficient_evidence' and not answer.claims
    assert answer.part_ledger.entries[1].status == 'unavailable'
    assert answer.part_ledger.entries[1].reason == 'not_in_evidence'
    assert len(model.calls) == 1


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
        if schema['properties']['schema_version']['const'] == 'bintanong-part-explanation-v1':
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
    assert 'isusumite' in PART_PROMPT and 'submit' in PART_PROMPT  # named as a word to avoid
    assert 'slip S' not in PART_PROMPT and 'Office K' not in PART_PROMPT


def test_prompt_gives_each_language_its_own_style_and_forbids_copying_english_sources():
    from backend.bintanong_generation.part_answers import PART_PROMPT
    assert 'Tagalog sentence structure' in PART_PROMPT and 'mostly Filipino' in PART_PROMPT
    assert 'do not copy an English source sentence' in PART_PROMPT


@pytest.mark.parametrize('language,phrase', [('taglish', 'Tagalog sentence structure'),
                                             ('fil', 'mostly Filipino')])
def test_style_repair_carries_a_plain_rewrite_instruction_for_the_requested_language(language, phrase):
    model = Drafts(ENGLISH, TAGLISH)
    asyncio.run(Generator(model).generate(TEXT, styled(language)))
    first, repair = (json.loads(model.calls[i][0][1]['content']) for i in (0, 1))
    assert 'repair_instruction' not in first
    assert phrase in repair['repair_instruction'] and 'Rewrite' in repair['repair_instruction']


def test_filler_claims_in_an_unavailable_slot_are_dropped_and_the_part_is_withheld():
    # Observed: the model marks a part not_in_evidence but adds a placeholder claim.
    model = PartModel(slots=dict(r1=('answered', [OFFICE]), r2=('not_in_evidence', ['not_in_evidence'])))
    answer = run(model)
    assert answer.status == 'insufficient_evidence' and answer.validation == 'parts_unresolved'
    assert answer.part_ledger.entries[1].reason == 'not_in_evidence' and len(model.calls) == 1


@pytest.mark.parametrize('word', ['isusumite', 'nakasaad', 'ihahain'])
def test_owner_named_deep_tagalog_uses_the_style_repair(word):
    deep = dict(r1=('answered', [f'Ang slip ay {word} sa Office V.']), r2=('answered', [TL_FEE]))
    model = Drafts(deep, TAGLISH)
    answer = asyncio.run(Generator(model).generate(TEXT, styled('fil')))
    assert answer.status == 'answered' and answer.draft_attempts == 2
    assert json.loads(model.calls[1][0][1]['content'])['validation_errors'] == ['claim_not_in_requested_style']
