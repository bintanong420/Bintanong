"""ARP-01..ARP-10 evaluation runner: synthetic data only, plus a check that the case file is well formed.

The real-ledger run (`python -m evaluation.planning.run_arp`) reads reviewed ledgers kept outside the repository and is
not part of the test suite. Here the runner is exercised on the synthetic unfamiliar curriculum (ARP-10), and its
verdict-shape comparison, premise-gap reporting and stage timer are checked directly.
"""
import json
from pathlib import Path

import pytest

from backend.bintanong_planning.contracts import PlanCheckRequest
from evaluation.planning import run_arp
from test_planning_check import POLICY, build

CASE_FILE = json.loads(Path(run_arp.CASES).read_text(encoding='utf-8'))
CASES = {case['id']: case for case in CASE_FILE['cases']}
KINDS = {'plan_check', 'earliest_term', 'recovery', 'term_assessment'}
SHAPES = {'works', 'needs_confirmation', 'heads_up', 'blocked', 'unknown'}


def test_case_file_covers_arp_01_to_10():
    assert CASE_FILE['schema'] == 'bintanong-arp-cases-v1'
    assert {i.split('-')[1][:2] for i in CASES} == {f'{n:02d}' for n in range(1, 11)}
    assert len(CASES) == len(CASE_FILE['cases'])


@pytest.mark.parametrize('case', CASE_FILE['cases'], ids=lambda c: c['id'])
def test_case_is_well_formed(case):
    assert case['kind'] in KINDS and case['title'] and case['curriculum']
    assert isinstance(case['expect'], dict) and isinstance(case.get('premise_courses', []), list)
    for code, state in case.get('facts', []):
        assert code and state in ('passed', 'failed', 'not_passed', 'not_taken', 'taken_unknown', 'enrolled',
                                  'not_enrolled')
    if case['kind'] == 'plan_check':
        assert len(case['expect']['terms']) == len(case['plan'])
        for expected, term in zip(case['expect']['terms'], case['plan']):
            assert expected['shape'] in SHAPES and term['courses']
            assert term.get('summer') or (term['year'] in range(1, 6) and term['semester'].endswith('_semester'))
            assert all(mode == 'summer' for _, mode in term['courses']) == bool(term.get('summer'))
            if expected['shape'] == 'blocked':
                assert expected['blocked_by']
    if case['kind'] in ('earliest_term', 'recovery', 'term_assessment'):
        assert 'query' in case
    if case['kind'] == 'plan_check':
        used = {code for code, _ in case.get('facts', [])} | {c for t in case['plan'] for c, _ in t['courses']}
        assert used <= set(case['premise_courses'])


@pytest.fixture(scope='module')
def synthetic():
    case = CASES['ARP-10']
    assert case['synthetic']
    return case, build(case['curriculum'])


def test_arp_10_runs_on_an_unfamiliar_synthetic_curriculum(synthetic):
    case, runtime = synthetic
    _, routes = run_arp.palsu_recovery_sources()
    result = run_arp.run_case(case, runtime, POLICY, routes)
    assert result['status'] == 'pass', result.get('problems')
    assert [o['shape'] for o in result['observed']] == ['works', 'blocked', 'unknown']
    assert any('QZV-B1/L' in line for line in result['reply_lines'])  # the reply names the unmet course


def test_stage_timings_add_up_and_are_nonnegative(synthetic):
    case, runtime = synthetic
    _, routes = run_arp.palsu_recovery_sources()
    timing = run_arp.run_case(case, runtime, POLICY, routes)['timing']
    assert timing['prolog_calls'] > 0 and timing['lookup_calls'] > 0
    parts = timing['prolog_s'] + timing['lookup_s'] + timing['planner_s'] + timing['render_s']
    assert abs(parts - timing['total_s']) < 1e-3
    assert min(timing[k] for k in ('prolog_s', 'lookup_s', 'planner_s', 'render_s')) >= 0


def test_a_wrong_expectation_fails_the_case(synthetic):
    case, runtime = synthetic
    _, routes = run_arp.palsu_recovery_sources()
    wrong = json.loads(json.dumps(case))
    wrong['expect']['terms'][1] = {'shape': 'works'}
    result = run_arp.run_case(wrong, runtime, POLICY, routes)
    assert result['status'] == 'fail' and any('t1' in p for p in result['problems'])


def test_missing_curriculum_or_course_is_a_premise_gap_not_a_pass(synthetic):
    case, runtime = synthetic
    _, routes = run_arp.palsu_recovery_sources()
    assert run_arp.run_case(case, None, POLICY, routes)['status'] == 'premise_not_in_reviewed_data'
    absent = json.loads(json.dumps(case))
    absent['premise_courses'] = ['NO-SUCH-1']
    result = run_arp.run_case(absent, runtime, POLICY, routes)
    assert result['status'] == 'premise_not_in_reviewed_data' and 'NO-SUCH-1' in result['evidence']


def test_course_codes_must_resolve_to_exactly_one_course(synthetic):
    case, runtime = synthetic
    catalog = run_arp.Catalog(runtime, case['curriculum'])
    assert catalog.resolve('qzv-e4 /L') == catalog.resolve('QZV-E4/L')
    with pytest.raises(KeyError):
        catalog.resolve('QZV-E4')


def test_plan_built_from_codes_is_a_valid_typed_request(synthetic):
    case, runtime = synthetic
    request = run_arp.build_plan(case, run_arp.Catalog(runtime, case['curriculum']))
    assert isinstance(request, PlanCheckRequest) and len(request.terms) == 3
