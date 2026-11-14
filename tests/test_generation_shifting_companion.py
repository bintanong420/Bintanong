"""Owner 3 Nov 2026 (H8, "go"): a shifting answer must also cover the fetched FAQ 8 steps. Live, both topics reached
the model but only the Handbook 4.1 records were required, so the OSAS/Guidance steps were left out. Fictional text."""
import json

from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.part_answers import required_record_sources
from backend.bintanong_orchestration.contracts import IntegrationResult
from test_request_understanding_pipeline import source

RULE = json.dumps(dict(fields=[dict(name='body', value='4.1 Fictional shifting rule.', source_blank=False)], source_limits=[]))
FAQ = json.dumps(dict(fields=[dict(name='body', value='8. How to shift? A. Fictional steps.', source_blank=False)], source_limits=[]))


def integration(with_faq=True):
    value = source().model_dump(mode='json')
    first = value['evidence']['documents']['passages'][0]
    member = value['evidence']['pin']['documents'][0]
    ids = [f'{n:064x}' for n in (1, 2)]
    value['evidence']['documents']['passages'] = [dict(first, chunk_id=c, text=t) for c, t in zip(ids, (RULE, FAQ))]
    value['evidence']['pin']['documents'] = [dict(member, chunk_id=c) for c in ids]
    part, other = value['understanding']['parts']
    part.update(subject_id='handbook_shifting', requested_claims=['printed shifting fields'])
    other.update(subject_id='other_subject', requested_claims=['printed other fields'])
    coverage = [dict(subject_id='handbook_shifting', claim='printed shifting fields', chunk_ids=ids[:1])]
    if with_faq:
        coverage.append(dict(subject_id='handbook_drop_shift_faq', claim='printed FAQ 8 shifting steps', chunk_ids=ids[1:]))
    value['evidence']['documents']['record_coverage'] = coverage
    return prepare(IntegrationResult.parse(value))


def test_a_shifting_part_also_requires_the_fetched_faq_steps():
    pack = integration()
    assert required_record_sources(pack)['r1'] == {c.evidence_id for c in pack.cards if c.kind == 'document'}


def test_without_the_faq_fetch_only_the_rule_is_required():
    pack = integration(with_faq=False)
    assert len(required_record_sources(pack)['r1']) == 1
