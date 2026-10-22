"""Synthetic ledger compilation only; no real-source reasoning or Janus."""
from __future__ import annotations

import copy
import importlib
import json
import shutil
import subprocess

import pytest

from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY
from test_symbolic_authoring import fixture, run


def compile_preview(ledger):
    return importlib.import_module('backend.bintanong_symbolic.compiler').compile_curriculum_preview(ledger)


def rereview(data):
    for course in data[2]:
        course['review_state'], course['review_refs'] = 'draft', []
    prepared = run(data[:3] + ([],))
    data[3][0]['course_digests'] = {c['course_id']: c['content_sha256'] for c in prepared['courses']}
    for course in data[2]:
        course['review_state'], course['review_refs'] = 'reviewed', ['review-1']
    return run(data)


def test_reviewed_ledger_compiles_to_detached_reproducible_candidate_data():
    ledger = run(fixture())
    before = copy.deepcopy(ledger)
    result = compile_preview(ledger)
    assert result['status'] == 'review_candidate'
    assert result['activation_allowed'] is False and result['eligibility_executable'] is False
    assert result['approval_id'] is None
    assert result['ledger_sha256'] == ledger['content_sha256']
    assert result['diagnostics'] == []
    assert result['release_holds']
    assert "candidate_requirement('course-2',course('course-1'))." in result['prolog']
    assert "candidate_requirement('course-1',verified_none)." in result['prolog']
    assert "candidate_fact('course-1','units.total',3)." in result['prolog']
    assert 'can_enroll(' not in result['prolog'] and 'eligible(' not in result['prolog']
    assert not EMPTY_REGISTRY.supports('check_prerequisite_eligibility')
    assert len(result['prolog_sha256']) == len(result['content_sha256']) == 64
    assert compile_preview(json.loads(json.dumps(ledger))) == result
    assert ledger == before
    ledger['courses'][0]['facts']['units.total']['value'] = 100
    assert result['ledger']['courses'][0]['facts']['units.total']['value'] == 3


@pytest.mark.parametrize('change,reason', [('draft', 'course_review_required'),
                                         ('unresolved', 'unresolved_requirement'),
                                         ('cycle', 'prerequisite_cycle')])
def test_blocks_drafts_unknown_conditions_and_cycles_without_prolog(change, reason):
    data = fixture()
    if change == 'draft':
        data[2][0]['review_state'], data[2][0]['review_refs'] = 'draft', []
        ledger = run(data)
    elif change == 'unresolved':
        data[2][1]['prerequisites'] = {'kind': 'unresolved', 'reason': 'Clipped source condition',
                                      'source_spans': data[2][1]['prerequisites']['source_spans']}
        ledger = rereview(data)
    else:
        data[2][0]['prerequisites'] = {'kind': 'course', 'course_id': 'course-2',
                                      'source_spans': data[2][0]['prerequisites']['source_spans']}
        ledger = rereview(data)
    result = compile_preview(ledger)
    assert result['status'] == 'blocked'
    assert result['prolog'] is None and result['prolog_sha256'] is None
    assert reason in [d['reason'] for d in result['diagnostics']]
    assert compile_preview(ledger) == result


def test_nested_alternatives_corequisites_and_missing_values_preserve_meaning():
    data = fixture()
    leaf = copy.deepcopy(data[2][1]['prerequisites'])
    concurrent = {**copy.deepcopy(leaf), 'kind': 'co_requisite'}
    data[2][1]['prerequisites'] = {'kind': 'all_of', 'items': [
        {'kind': 'any_of', 'items': [concurrent, leaf], 'source_spans': leaf['source_spans']}],
        'source_spans': leaf['source_spans']}
    data[2][1]['facts'].pop('units.total')
    ledger = rereview(data)
    result = compile_preview(ledger)
    assert "all_of([any_of([co_requisite('course-1'),course('course-1')])])" in result['prolog']
    assert "candidate_fact('course-2','units.total'" not in result['prolog']
    assert result['ledger']['courses'][1]['prerequisites'] == ledger['courses'][1]['prerequisites']


def test_mutual_corequisites_are_not_prior_completion_cycles():
    data = fixture()
    for index, target in [(0, 'course-2'), (1, 'course-1')]:
        data[2][index]['prerequisites'] = {'kind': 'co_requisite', 'course_id': target,
                                          'source_spans': data[2][index]['prerequisites']['source_spans']}
    result = compile_preview(rereview(data))
    assert result['status'] == 'review_candidate'
    assert not result['diagnostics']


@pytest.mark.parametrize('field,value', [('content_sha256', '0' * 64),
                                       ('activation_allowed', True),
                                       ('eligibility_executable', True),
                                       ('approval_id', 'invented'),
                                       ('synthetic', False), ('unexpected', 'field')])
def test_rejects_forged_ledger_metadata(field, value):
    ledger = run(fixture())
    ledger[field] = value
    with pytest.raises(ValueError):
        compile_preview(ledger)


@pytest.mark.parametrize('change', ['course_digest', 'course_fact', 'review_receipt', 'dangling_reference'])
def test_rechecks_course_digests_receipts_and_references(change):
    ledger = run(fixture())
    if change == 'course_digest':
        ledger['courses'][0]['content_sha256'] = '0' * 64
    elif change == 'course_fact':
        ledger['courses'][0]['facts']['units.total']['value'] = 30
    elif change == 'review_receipt':
        ledger['reviews'][0]['course_digests']['course-1'] = '0' * 64
    else:
        ledger['courses'][1]['prerequisites']['course_id'] = 'missing'
    with pytest.raises(ValueError):
        compile_preview(ledger)


def test_source_holds_survive_authoring_review_without_promoting_authority():
    ledger = run(fixture())
    result = compile_preview(ledger)
    assert result['source_states'] == ledger['sources']
    assert 'inactive_preview_only' in result['release_holds']
    source = ledger['sources'][0]
    assert f"{source['version_id']}:approval_state:{source['approval_state']['state']}" in result['release_holds']
    assert result['ledger']['sources'][0]['approval_id'] is None


@pytest.mark.parametrize('field', ['course_code', 'course_title'])
def test_valid_authoring_text_incompatible_with_quote_contract_is_held(field):
    data = fixture()
    fact = copy.deepcopy(data[2][0]['facts']['course_code'])
    fact['value'] = 'SYN\u00a0101'
    fact['source_spans'][0]['text'] = fact['value']
    data[2][0]['facts'][field] = fact
    ledger = rereview(data)
    result = compile_preview(ledger)
    assert result['status'] == 'blocked'
    assert result['prolog'] is None and result['prolog_sha256'] is None
    assert result['diagnostics'][0]['reason'] == 'unrenderable_text'
    assert result['ledger'] == ledger
    assert result['ledger']['courses'][0]['facts'][field]['value'] == 'SYN\u00a0101'


def test_synthetic_preview_parses_only_as_ground_facts_in_swipl(tmp_path):
    swipl = shutil.which('swipl')
    if swipl is None:
        pytest.skip('optional installed SWI-Prolog parser check')
    data = fixture()
    code = "SYN'\\101). :- halt(99). %"
    data[2][0]['facts']['course_code']['value'] = code
    data[2][0]['facts']['course_code']['source_spans'][0]['text'] = code
    result = compile_preview(rereview(data))
    candidate = tmp_path / 'synthetic-candidate.pl'
    candidate.write_text(result['prolog'], encoding='utf-8')
    # read_term reads the generated text as DATA, never consults directives/rules.
    script = tmp_path / 'parse.pl'
    script.write_text('''
check(S) :- read_term(S,T,[]),
    (T == end_of_file -> true ;
     ground(T), functor(T,F,_), atom_concat(candidate_,_,F), check(S)).
main :- current_prolog_flag(argv,[P]), open(P,read,S,[encoding(utf8)]),
    (check(S) -> close(S), halt(0) ; close(S), halt(1)).
:- initialization(main, main).
''', encoding='utf-8')
    checked = subprocess.run([swipl, '-q', '-f', 'none', '-s', str(script), '--', str(candidate)],
                             capture_output=True, text=True, timeout=10)
    assert checked.returncode == 0, checked.stderr
    assert not checked.stderr
