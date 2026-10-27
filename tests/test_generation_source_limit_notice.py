"""Source-gap policy: an answer citing a conflicting or defective source says so (host text).

Found in roster run 7 (22 October 2026): both printed completion deadlines were answered
without saying the handbook conflicts on which one applies.
"""
import dataclasses
import json

import pytest

from backend.bintanong_generation import render
from backend.bintanong_generation.evidence import prepare
from test_generation_evidence import integrated
from test_generation_validation import draft


def limited(issue, resolution='unresolved'):
    return json.dumps(dict(fields=[dict(name='3.7', source_blank=False, value='Fictional rule.')],
        source_limits=[dict(issue=issue, resolution=resolution, affected_claims=['applicable deadline'],
            field_names=['3.7'], gap_id='g1', locator=dict(field='3.7', physical_pages=[1]),
            message='Unavailable information: applicable deadline.')]))


def pack_with(text, language='en'):
    pack = prepare(integrated(response_style=language))
    cards = tuple(c.model_copy(update=dict(text=text)) if c.kind == 'document' else c for c in pack.cards)
    return dataclasses.replace(pack, cards=cards)


def answer(pack):
    doc = next(c for c in pack.cards if c.kind == 'document')
    claims = draft(pack, claims=[dict(claim_id='c1', text='Fictional rule.', evidence_ids=[doc.evidence_id])]).claims
    return render.render_text(pack, claims, 'answered')


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_conflicting_source_adds_a_notice_in_the_reply_language(language):
    text = answer(pack_with(limited('conflicting_deadlines'), language))
    assert render._LIMIT_NOTICES['taglish' if language=='fil' else language]['conflict'] in text


@pytest.mark.parametrize('issue', ['source_cutoff', 'malformed_source_condition', 'printed_total_discrepancy'])
def test_defective_source_adds_the_defect_notice(issue):
    assert render._LIMIT_NOTICES['en']['defect'] in answer(pack_with(limited(issue)))


@pytest.mark.parametrize('text', [limited('conflicting_deadlines', resolution='resolved'),
                                  limited('claim_not_stated'), limited('effectivity_currentness_unknown'),
                                  'Fictional plain passage.'])
def test_no_notice_for_resolved_not_stated_currentness_or_plain_text(text):
    rendered = answer(pack_with(text))
    assert all(n not in rendered for n in render._LIMIT_NOTICES['en'].values())


def test_notice_only_for_cards_the_answer_cites():
    pack = pack_with(limited('conflicting_deadlines'))
    assert render._LIMIT_NOTICES['en']['conflict'] not in render.render_text(pack, (), 'insufficient_evidence')


def test_notices_avoid_deep_tagalog():
    for language in ('fil', 'taglish'):
        for notice in render._LIMIT_NOTICES[language].values():
            assert not {'nakasaad', 'isusumite', 'ihahain'} & set(notice.lower().replace('.', ' ').split())
