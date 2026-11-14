"""Synthetic partial review artifacts; no institutional queries or activation."""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import shutil
import subprocess

import pytest

from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY
from backend.bintanong_symbolic.compiler import compile_curriculum_preview
from test_symbolic_authoring import fixture, run
from test_symbolic_compiler import rereview


def compile_bundle(ledger):
    return importlib.import_module('backend.bintanong_symbolic.compiler').compile_curriculum_review_bundle(ledger)


def partial():
    data = fixture()
    course = data[2][0]
    course['review_state'], course['review_refs'] = 'draft', []
    course['prerequisites'] = {'kind': 'unresolved', 'reason': 'Blank source cell; coverage unknown',
                               'source_spans': course['prerequisites']['source_spans']}
    return data


def test_partial_export_keeps_reviewed_target_and_labels_draft_unknown_reference():
    ledger = run(partial())
    before = copy.deepcopy(ledger)
    strict = compile_curriculum_preview(ledger)
    result = compile_bundle(ledger)
    assert result['compiler_version'] == 'curriculum-prolog-review-bundle-v1'
    assert result['status'] == 'partial_review_candidate'
    assert result['activation_allowed'] is result['eligibility_executable'] is result['runtime_ready'] is False
    assert result['approval_id'] is None
    assert 'partial_coverage_requires_explicit_handling' in result['release_holds']
    assert result['ledger'] == ledger == before
    assert result['source_states'] == ledger['sources']
    coverage = {c['course_id']: c for c in result['coverage']}
    assert coverage['course-1']['identity_review'] == 'draft'
    assert coverage['course-1']['direct_rule'] == 'unresolved'
    assert coverage['course-1']['unresolved'][0]['reason'] == 'Blank source cell; coverage unknown'
    assert coverage['course-2']['identity_review'] == coverage['course-2']['direct_rule'] == 'reviewed'
    assert coverage['course-2']['pending_identity_refs'] == ['course-1']
    assert "candidate_requirement('course-2',course('course-1'))." in result['prolog']
    assert "candidate_fact('course-1'," not in result['prolog']
    assert "candidate_requirement('course-1'," not in result['prolog']
    assert "candidate_reference_identity('course-1'" in result['prolog']
    assert ",'SYN101','draft')." in result['prolog']
    assert "candidate_coverage('course-1'," in result['prolog']
    assert "candidate_record('course-1'," in result['prolog']  # audit only
    assert 'eligible(' not in result['prolog'] and 'can_enroll(' not in result['prolog']
    assert not EMPTY_REGISTRY.supports('check_prerequisite_eligibility')
    assert compile_curriculum_preview(ledger) == strict and strict['prolog'] is None
    assert result['prolog_sha256'] == hashlib.sha256(result['prolog'].encode()).hexdigest()
    content = {k: v for k, v in result.items() if k != 'content_sha256'}
    assert result['content_sha256'] == hashlib.sha256(json.dumps(content, ensure_ascii=True,
        sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    assert compile_bundle(json.loads(json.dumps(ledger))) == result
    data = partial()
    data[2].reverse()
    assert compile_bundle(run(data)) == result
    result['ledger']['courses'][0]['facts']['course_code']['value'] = 'mutated output'
    assert ledger == before


def test_reviewed_unknown_is_distinct_from_reviewed_verified_none():
    unknown = compile_bundle(rereview(partial()))
    assert unknown['coverage'][0]['identity_review'] == 'reviewed'
    assert unknown['coverage'][0]['direct_rule'] == 'unresolved'
    assert unknown['coverage'][1]['pending_identity_refs'] == []
    assert "candidate_fact('course-1','course_code','SYN101')." in unknown['prolog']
    assert "candidate_requirement('course-1'," not in unknown['prolog']
    known = compile_bundle(run(fixture()))
    assert known['status'] == 'review_candidate'
    assert "candidate_requirement('course-1',verified_none)." in known['prolog']
    assert known['runtime_ready'] is False


def test_all_draft_artifact_exports_only_identity_coverage_and_audit():
    data = fixture()
    for c in data[2]:
        c['review_state'], c['review_refs'] = 'draft', []
    result = compile_bundle(run(data))
    assert result['status'] == 'partial_review_candidate'
    assert all(c['direct_rule'] == 'draft' for c in result['coverage'])
    assert 'candidate_requirement(' not in result['prolog']
    assert 'candidate_fact(' not in result['prolog']


def test_preserves_nested_order_corequisites_and_does_not_prune_unknown_branches():
    data = fixture()
    leaf = copy.deepcopy(data[2][1]['prerequisites'])
    data[2][1]['prerequisites'] = {'kind': 'any_of', 'items': [
        {'kind': 'all_of', 'items': [{**leaf, 'kind': 'co_requisite'}, leaf],
         'source_spans': leaf['source_spans']}, leaf], 'source_spans': leaf['source_spans']}
    known = compile_bundle(rereview(data))
    assert "any_of([all_of([co_requisite('course-1'),course('course-1')]),course('course-1')])" in known['prolog']
    data[2][1]['prerequisites']['items'][1] = {'kind': 'unresolved', 'reason': 'Exception clipped',
                                             'source_spans': leaf['source_spans']}
    unknown = compile_bundle(rereview(data))
    assert "candidate_requirement('course-2'," not in unknown['prolog']
    assert unknown['coverage'][1]['unresolved'][0]['path'] == 'prerequisites.items[1]'


@pytest.mark.parametrize('reviewed', [False, True])
def test_only_reviewed_complete_rules_contribute_prior_completion_cycle(reviewed):
    data = fixture()
    c = data[2][0]
    c['prerequisites'] = {'kind': 'course', 'course_id': 'course-2',
                           'source_spans': c['prerequisites']['source_spans']}
    ledger = rereview(data)
    if not reviewed:
        c['review_state'], c['review_refs'] = 'draft', []
        ledger = run(data)
    result = compile_bundle(ledger)
    if reviewed:
        assert result['status'] == 'blocked' and result['prolog'] is result['prolog_sha256'] is None
        assert result['diagnostics'][0]['reason'] == 'prerequisite_cycle'
    else:
        assert result['status'] == 'partial_review_candidate' and result['prolog']
        assert not result['diagnostics']


def test_mutual_corequisites_are_not_prior_completion_cycle():
    data = fixture()
    for c, target in zip(data[2], ['course-2', 'course-1']):
        c['prerequisites'] = {'kind': 'co_requisite', 'course_id': target,
                              'source_spans': c['prerequisites']['source_spans']}
    assert compile_bundle(rereview(data))['status'] == 'review_candidate'


def test_strict_quoting_failure_holds_whole_bundle_without_mutating_text():
    data = partial()
    for c in data[2]:
        c['review_state'], c['review_refs'] = 'draft', []
    fact = data[2][0]['facts']['course_code']
    fact['value'] = fact['source_spans'][0]['text'] = 'SYN\u00a0101'
    ledger = run(data)
    result = compile_bundle(ledger)
    assert result['status'] == 'blocked' and result['prolog'] is result['prolog_sha256'] is None
    assert result['diagnostics'][0]['reason'] == 'unrenderable_text'
    assert result['ledger'] == ledger


@pytest.mark.parametrize('change', ['flag', 'receipt', 'digest', 'scope', 'dangling', 'private'])
def test_rejects_forged_stale_foreign_and_private_records(change):
    ledger = run(partial())
    if change == 'flag':
        ledger['activation_allowed'] = True
    elif change == 'receipt':
        ledger['reviews'][0]['course_digests']['course-2'] = '0' * 64
    elif change == 'digest':
        ledger['courses'][0]['content_sha256'] = '0' * 64
    elif change == 'scope':
        ledger['courses'][1]['curriculum_id'] = 'another-curriculum'
    elif change == 'dangling':
        ledger['courses'][1]['prerequisites']['course_id'] = 'missing'
    else:
        ledger['courses'][0]['facts']['course_code']['source_spans'][0]['text'] = 'session-private-123'
    with pytest.raises(ValueError):
        compile_bundle(ledger)


def test_bundle_parses_as_ground_candidate_data_without_executing_injected_text(tmp_path):
    swipl = shutil.which('swipl')
    if not swipl:
        pytest.skip('installed SWI-Prolog optional parser check')
    data = partial()
    for c in data[2]:
        c['review_state'], c['review_refs'] = 'draft', []
    fact = data[2][0]['facts']['course_code']
    fact['value'] = fact['source_spans'][0]['text'] = "SYN'\\101). :- halt(99). %"
    result = compile_bundle(run(data))
    candidate = tmp_path/'review.pl'
    candidate.write_text(result['prolog'], encoding='utf-8')
    parser = tmp_path/'parser.pl'
    parser.write_text('''
check(S) :- read_term(S,T,[]), (T == end_of_file -> true ;
    ground(T), functor(T,F,_), atom_concat(candidate_,_,F), check(S)).
main :- current_prolog_flag(argv,[P]), open(P,read,S,[encoding(utf8)]),
    (check(S) -> close(S), halt(0) ; close(S), halt(1)).
:- initialization(main,main).
''', encoding='utf-8')
    checked = subprocess.run([swipl, '-q', '-f', 'none', '-s', str(parser), '--', str(candidate)],
                             capture_output=True, text=True, timeout=10)
    assert checked.returncode == 0 and not checked.stderr, checked.stderr
