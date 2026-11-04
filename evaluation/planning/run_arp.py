"""Academic recovery planner cases ARP-01..ARP-10, run OFFLINE (no model, backend, GUI or server).

Usage (repository root, project venv):

    python -m evaluation.planning.run_arp --ledgers <dir of reviewed ledger json> --out <ignored dir> [--only ARP-03]

Each case in `arp_cases.json` names a curriculum, the student's stated facts, and either a typed plan
(`check_plan`), an earliest-term query, a recovery query (`plan_recovery`) or a term-listing coverage probe. Course
codes are the printed codes; they are resolved to the ledger's course ids at run time and must match exactly one
course (spacing and case ignored), so a case never guesses.

A case whose premise is missing from the reviewed ledgers (curriculum absent, course code absent or ambiguous) is
reported as `premise_not_in_reviewed_data` with the evidence; it is never invented or silently passed.

Timings are `time.perf_counter` around the existing calls. Stages: `prolog` (runtime.check and
runtime.list_affected_courses, each a Prolog worker process), `lookup` (runtime.look_up on the reviewed ledger),
`planner` (the rest of check_plan / earliest_term / plan_recovery: Python control flow, memo, contract parsing) and
`render` (the host reply lines). Gemma router and generation time are not measured here.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

from backend.bintanong_generation.plan_check_reply import earliest_term_lines, plan_check_lines
from backend.bintanong_generation.recovery_reply import recovery_lines
from backend.bintanong_planning.chat import earliest_term
from backend.bintanong_planning.checker import _request, check_plan
from backend.bintanong_planning.contracts import PlanCheckRequest
from backend.bintanong_planning.recovery import palsu_recovery_sources, plan_recovery

CASES = Path(__file__).with_name('arp_cases.json')
AUTHORIZATION = 'research-owner-20261021'  # backend.bintanong_api.research_app.AUTHORIZATION (pinned research release)
YEARS = range(1, 6)
STAGES = ('prolog', 'lookup', 'planner', 'render')
PROLOG_CALLS = ('check', 'list_affected_courses')


class TimedRuntime:
    """Wraps a runtime and adds up the time spent inside each of its methods (planner code is untouched)."""

    def __init__(self, runtime):
        self._runtime, self.seconds, self.calls = runtime, defaultdict(float), defaultdict(int)

    def __getattr__(self, name):
        attribute = getattr(self._runtime, name)
        if not callable(attribute):
            return attribute

        def timed(*args, **kwargs):
            started = time.perf_counter()
            try:
                return attribute(*args, **kwargs)
            finally:
                self.seconds[name] += time.perf_counter() - started
                self.calls[name] += 1
        return timed


def normalize(code):
    return ''.join(code.split()).casefold()


class Catalog:
    """Printed code <-> course id for one curriculum, from the runtime's own listings (nothing guessed)."""

    def __init__(self, runtime, curriculum_id):
        self.by_id, self.by_code, self.statuses = {}, defaultdict(list), {}
        for year in YEARS:
            listing = runtime.look_up(_request('list_term_courses', curriculum_id, year_level=str(year), semester='any'))
            self.statuses[year] = listing.status
            for course in listing.courses:
                self.by_id[course.course_id] = course.code
                self.by_code[normalize(course.code)].append(course.course_id)

    def resolve(self, code):
        found = self.by_code.get(normalize(code), [])
        if len(found) != 1:
            raise KeyError(f'{code!r} matches {len(found)} reviewed courses')
        return found[0]

    def shown(self, course_id):
        return self.by_id.get(course_id, course_id)


def load_ledger_runtime(ledgers_dir, curriculum_id):
    """The real reviewed ledger as an offline-research runtime (non-synthetic; same authorization as the gates)."""
    from backend.bintanong_runtime.research import OPERATIONS
    from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
    from backend.bintanong_symbolic.runtime import CurriculumRuntime
    path = Path(ledgers_dir) / f'{curriculum_id}.json'
    if not path.exists():
        return None
    bundle = prepare_runtime_bundle(json.loads(path.read_text(encoding='utf-8')))
    return CurriculumRuntime.for_offline_research(bundle, authorization=dict(
        purpose='offline_curriculum_acceptance', authorization_ref=AUTHORIZATION,
        bundle_sha256=bundle['content_sha256'], operations=list(OPERATIONS)))


def shape_of(verdict, catalog):
    """The prerequisite and approval verdict as a student reads it: works / needs_confirmation / heads_up / blocked /
    unknown. A missing printed unit total is reported separately (`units_missing`, `term_outcome`, `load`): it makes the
    whole term outcome unknown but says nothing about the prerequisites, so it must not hide them."""
    shown = catalog.shown
    unmet = [r for r in verdict.reasons if r.kind == 'unmet_prerequisite']
    undecided = [r for r in verdict.reasons if r.kind not in ('unmet_prerequisite', 'units_missing')]
    if unmet:
        shape = 'blocked'
    elif undecided:
        shape = 'unknown'
    elif verdict.warnings:
        shape = 'heads_up'
    else:
        shape = 'needs_confirmation' if verdict.unconfirmed else 'works'
    return dict(shape=shape, blocked_by=sorted({shown(m) for r in unmet for m in r.missing}),
                unknown_for=sorted({shown(r.course_id) for r in undecided}),
                unconfirmed=sorted(shown(u.course_id) for u in verdict.unconfirmed),
                units_missing=sorted({shown(r.course_id) for r in verdict.reasons if r.kind == 'units_missing'}),
                term_outcome=verdict.outcome, load=verdict.load.status)

def compare(expected, observed):
    """Return the list of mismatches between one expected term spec and the observed shape."""
    problems = []
    if expected['shape'] != observed['shape']:
        problems.append(f"shape {observed['shape']} != expected {expected['shape']}")
    for key in ('blocked_by', 'unknown_for', 'unconfirmed'):
        if key in expected and sorted(expected[key]) != observed[key]:
            problems.append(f'{key} {observed[key]} != expected {sorted(expected[key])}')
    if 'load' in expected and expected['load'] != observed['load']:
        problems.append(f"load {observed['load']} != expected {expected['load']}")
    return problems


def missing_premise(case, catalog):
    return [code for code in case.get('premise_courses', []) if len(catalog.by_code.get(normalize(code), [])) != 1]


def build_plan(case, catalog):
    terms = []
    for term in case['plan']:
        courses = [dict(course_id=catalog.resolve(code), mode=mode) for code, mode in term['courses']]
        if term.get('summer'):
            terms.append(dict(kind='summer', year_level=None, semester=None, courses=courses))
        else:
            terms.append(dict(kind='regular', year_level=term['year'], semester=term['semester'], courses=courses))
    facts = [dict(course_id=catalog.resolve(code), state=state) for code, state in case.get('facts', [])]
    return PlanCheckRequest.parse(dict(schema_version=PlanCheckRequest.SCHEMA_VERSION,
                                       curriculum_id=case['curriculum'], facts=facts, terms=terms))


def timing_row(timed, total, render):
    prolog = sum(timed.seconds[name] for name in PROLOG_CALLS)
    lookup = timed.seconds['look_up']
    return dict(total_s=round(total + render, 4), prolog_s=round(prolog, 4), lookup_s=round(lookup, 4),
                planner_s=round(total - prolog - lookup, 4), render_s=round(render, 4),
                prolog_calls=sum(timed.calls[name] for name in PROLOG_CALLS), lookup_calls=timed.calls['look_up'])


def run_case(case, runtime, policy, routes):
    """Run one case on a runtime (real or synthetic). Returns a result dict; never raises for a missing premise."""
    row = dict(id=case['id'], title=case['title'], curriculum=case['curriculum'], kind=case['kind'])
    if runtime is None:
        return dict(row, status='premise_not_in_reviewed_data',
                    evidence=f"no reviewed ledger for curriculum {case['curriculum']!r} in the cache")
    timed = TimedRuntime(runtime)
    catalog = Catalog(timed, case['curriculum'])
    absent = missing_premise(case, catalog)
    if absent:
        return dict(row, status='premise_not_in_reviewed_data',
                    evidence=f'course codes not found exactly once in the reviewed ledger: {absent}')
    timed.seconds.clear(), timed.calls.clear()
    expected = case['expect']
    kind = case['kind']
    if kind == 'plan_check':
        request = build_plan(case, catalog)
        started = time.perf_counter()
        result = check_plan(request, timed, policy)
        total = time.perf_counter() - started
        started = time.perf_counter()
        lines = plan_check_lines(request, result, 'en', catalog.shown, routes=routes)
        render = time.perf_counter() - started
        observed = [shape_of(v, catalog) for v in result.terms]
        problems = ([f'{len(observed)} terms != expected {len(expected["terms"])}']
                    if len(observed) != len(expected['terms']) else
                    [f't{i}: {p}' for i, (e, o) in enumerate(zip(expected['terms'], observed)) for p in compare(e, o)])
    elif kind == 'earliest_term':
        query = case['query']
        started = time.perf_counter()
        result = earliest_term(timed, case['curriculum'], catalog.resolve(query['course']),
                               [(catalog.resolve(c), s) for c, s in case.get('facts', [])], tuple(query['start']))
        total = time.perf_counter() - started
        started = time.perf_counter()
        lines = earliest_term_lines(result, 'en', catalog.shown)
        render = time.perf_counter() - started
        observed = dict(status=result.status, reason=result.reason,
                        term=None if result.term is None else [result.term.year, result.term.semester])
        problems = [f'{k} {observed[k]} != expected {v}' for k, v in expected.items() if observed.get(k) != v]
    elif kind == 'recovery':
        query = case['query']
        failed = catalog.resolve(query['failed_course'])
        started = time.perf_counter()
        affected = timed.list_affected_courses(_request('list_affected_courses', case['curriculum'],
                                                        course_id=failed)).course_ids
        result = plan_recovery(timed, case['curriculum'], failed, affected,
                               [(catalog.resolve(c), s) for c, s in case.get('facts', [])],
                               None if query.get('term') is None else tuple(query['term']), policy, routes)
        total = time.perf_counter() - started
        started = time.perf_counter()
        lines = recovery_lines(result, 'en', catalog.shown)
        render = time.perf_counter() - started
        observed = dict(affected=sorted(catalog.shown(c) for c in affected),
                        drafts={d.variant: [[t.verdict.outcome, sorted(catalog.shown(c.course_id) for c in t.moved)]
                                            for t in d.terms] for d in result.drafts},
                        dropped={d.variant: d.reason for d in result.dropped})
        problems = [f'{k} {observed[k]} != expected {v}' for k, v in expected.items() if observed.get(k) != v]
    elif kind == 'term_assessment':  # coverage probe: a term the reviewed ledger does not list must say so
        from backend.bintanong_orchestration.term_assessment import assess_term
        from backend.bintanong_symbolic.runtime import StudentFacts
        query = case['query']
        started = time.perf_counter()
        result = assess_term(timed, _request('assess_term_prerequisites', case['curriculum'],
                                             year_level=str(query['year']), semester=query['semester']), StudentFacts())
        total, render, lines = time.perf_counter() - started, 0.0, []
        observed = dict(status=result.status, covered_terms=list(result.covered_terms))
        problems = [f'{k} {observed[k]} != expected {v}' for k, v in expected.items() if observed.get(k) != v]
    else:
        raise ValueError(f'unknown case kind {kind!r}')
    return dict(row, status='pass' if not problems else 'fail', problems=problems, observed=observed,
                expected=expected, reply_lines=lines, timing=timing_row(timed, total, render),
                evidence=case.get('premise_note'))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--ledgers', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--cases', type=Path, default=CASES)
    parser.add_argument('--only', action='append', default=[])
    args = parser.parse_args(argv)
    cases = json.loads(args.cases.read_text(encoding='utf-8'))['cases']
    policy, routes = palsu_recovery_sources()
    runtimes, builds, rows = {}, {}, []
    for case in cases:
        if args.only and not any(case['id'].startswith(o) for o in args.only):
            continue
        curriculum = case['curriculum']
        if curriculum not in runtimes:
            started = time.perf_counter()
            if case.get('synthetic'):
                sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tests'))
                import test_planning_check as synthetic
                runtimes[curriculum] = synthetic.build(curriculum)
                runtimes[curriculum + '#policy'] = synthetic.POLICY
            else:
                runtimes[curriculum] = load_ledger_runtime(args.ledgers, curriculum)
            builds[curriculum] = round(time.perf_counter() - started, 3)
        row = run_case(case, runtimes[curriculum], runtimes.get(curriculum + '#policy', policy), routes)
        row['runtime_build_s'] = builds[curriculum]
        rows.append(row)
        print(f"{row['id']:<10} {row['status']:<30} {row['curriculum']}", flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'arp-results.json').write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding='utf-8')
    failed = [r['id'] for r in rows if r['status'] == 'fail']
    print('failed:', failed or 'none')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
