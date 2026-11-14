"""Review-wire aliases preserve source text,canonical claims and support guards."""
import asyncio
from dataclasses import replace
import json

import pytest

from backend.bintanong_generation.contracts import AnswerDraft
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.part_answers import confirm_messages
from backend.bintanong_generation.references import EvidenceReferences
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_generation_part_slots import PartModel
from test_generation_part_references import ShortParts
from test_request_understanding_pipeline import TEXT, source
from test_service_record_coverage import covered_integration
from test_quoted_field_answers import fixture as quote_fixture, expected as quote_text


def draft(pack,text='Literal e1 and ev-'+'a'*64+' remain in prose.'):
    return AnswerDraft.parse(dict(schema_version=AnswerDraft.SCHEMA_VERSION,
        release_id=pack.release_id,language=pack.language,decision_outcome=None,
        claims=[dict(claim_id='c1',text=text,evidence_ids=[c.evidence_id for c in pack.cards])]))


def payload(messages):
    return json.loads(messages[1]['content'])


def test_short_review_maps_every_structured_reference_without_rewriting_prose():
    pack=prepare(covered_integration())
    subject=pack.understanding.parts[0].subject_id
    claim=pack.understanding.parts[0].requested_claims[0]
    pack=replace(pack,record_order=((subject,claim,tuple(c.evidence_id for c in pack.cards)),))
    proposal=draft(pack);slots={'r1':('answered',('c1',))}
    before=pack.model_payload();canonical=payload(confirm_messages(TEXT,pack,proposal,slots))
    short=payload(confirm_messages(TEXT,pack,proposal,slots,references=EvidenceReferences(pack)))
    assert [s['evidence_id'] for s in short['available_sources']]==['e1','e2']
    assert short['parts'][0]['claims'][0]['claim']['evidence_ids']==['e1','e2']
    assert short['parts'][0]['claims'][0]['source_ids']==['e1','e2']
    # Keep the existing canonical coverage order;the explicit step order is separate.
    assert short['required_records']=={'r1':['e2','e1']}
    assert short['record_order']=={'r1':[['e1','e2']]}
    assert [s['text'] for s in short['available_sources']]==[s['text'] for s in canonical['available_sources']]
    assert short['parts'][0]['claims'][0]['claim']['text']==proposal.claims[0].text
    assert short['parts'][0]['requested_claims']==canonical['parts'][0]['requested_claims']
    assert pack.model_payload()==before
    assert all(ref.startswith('ev-') for ref in proposal.claims[0].evidence_ids)


def test_short_review_keeps_exact_quote_words_and_complete_source_cards():
    value,text=quote_fixture();pack=prepare(IntegrationResult.parse(value))
    proposal=draft(pack,quote_text());short=payload(confirm_messages(text,pack,proposal,
        {'r1':('answered',('c1',))},references=EvidenceReferences(pack)))
    assert short['quoted_field_answers']['r1']=={'text':quote_text(),'evidence_id':'e1'}
    assert len(short['available_sources'])==2
    assert short['available_sources'][1]['text']==pack.cards[1].text


def test_review_rejects_even_identical_content_references_from_another_request_pack():
    pack=prepare(source());other=replace(pack)
    with pytest.raises(ValueError,match='reference_pack_mismatch'):
        confirm_messages(TEXT,pack,draft(pack),{'r1':('answered',('c1',))},references=EvidenceReferences(other))


@pytest.mark.parametrize('draft_profile,model_type',[('canonical',PartModel),('short',ShortParts)])
def test_generator_opt_in_reviews_short_ids_but_returns_canonical_host_claims(draft_profile,model_type):
    model=model_type()
    answer=asyncio.run(Generator(model,reference_profile=draft_profile,review_reference_profile='short').generate(TEXT,source()))
    assert answer.status=='answered' and answer.draft_attempts==answer.check_attempts==1
    assert [s['evidence_id'] for s in payload(model.calls[1][0])['available_sources']]==['e1']
    assert all(ref.startswith('ev-') for c in answer.claims for ref in c.evidence_ids)
    assert answer.part_ledger.semantic_completeness=='unverified'


def test_short_review_does_not_bypass_a_negative_part_verdict():
    model=PartModel(verdicts={'r2':'does_not_answer'})
    answer=asyncio.run(Generator(model,review_reference_profile='short').generate(TEXT,source()))
    assert answer.status=='insufficient_evidence' and not answer.claims
    assert answer.draft_attempts==answer.check_attempts==1


@pytest.mark.parametrize('profile',['legacy','scoped','guarded','covered'])
def test_short_review_is_restricted_to_the_per_part_confirmation_path(profile):
    with pytest.raises(ValueError,match='short_review_requires_parts'):
        Generator(PartModel(),explanation_profile=profile,review_reference_profile='short')


@pytest.mark.parametrize('profile',['unknown',None,True])
def test_unknown_review_profiles_are_rejected(profile):
    with pytest.raises(ValueError,match='invalid_review_reference_profile'):
        Generator(PartModel(),review_reference_profile=profile)
