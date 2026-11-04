"""Recovery search (owner, 4 Nov 2026: "greedy as much as it can be", for every curriculum). Synthetic shape of the
owner's BSCS gold route when the first-semester course F is failed:

  2:1 F needs BASE (failed)          2:2 G, H, J each need F
  3:1 K needs H; M needs J; P1       3:2 L needs G; P2           every course 3 units

The combined draft (C) takes F as a special class at once, uses summer first within the summer load, takes the course
whose dependents come soonest first (then unlock weight), keeps only the special-class requests that make the student
rejoin the prescribed sequence earlier, and never pulls a course ahead of its prescribed term. With a 6-unit summer it
is the gold shape: F special in 2:2; H and J in summer; G special in 3:1 (load heads-up); back on sequence by 3:2.
"""
import pytest

from backend.bintanong_planning import recovery
from backend.bintanong_planning.checker import _request
from backend.bintanong_planning.policies import LoadPolicy
from backend.bintanong_planning.recovery import plan_recovery
from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_planning_check import POLICY, cid
from test_planning_recovery import ROUTES
from test_symbolic_course_facts import SOURCE, fact

Y1, Y2, Y3, Y4 = 'FIRST YEAR', 'SECOND YEAR', 'THIRD YEAR', 'FOURTH YEAR'
FIRST, SECOND = 'FIRST SEMESTER', 'SECOND SEMESTER'
SHAPE = [('BASE', Y1, FIRST, None), ('F', Y2, FIRST, 'BASE'), ('G', Y2, SECOND, 'F'), ('H', Y2, SECOND, 'F'),
         ('J', Y2, SECOND, 'F'), ('K', Y3, FIRST, 'H'), ('M', Y3, FIRST, 'J'), ('P1', Y3, FIRST, None),
         ('L', Y3, SECOND, 'G'), ('P2', Y3, SECOND, None), ('S1', Y4, FIRST, None)]
CURRICULA = {'curriculum-gold-1': {n: f'GLD {200 + i}' for i, (n, *_) in enumerate(SHAPE)},
             'curriculum-gold-unfamiliar': {n: f'ZQ-{chr(75 + i)}{i}/L' for i, (n, *_) in enumerate(SHAPE)}}
SIX = LoadPolicy.parse(dict(POLICY.model_dump(mode='json'), summer_normal_units=6))


def build(curriculum_id):
    codes = CURRICULA[curriculum_id]
    scope = {'program_id': 'program-synthetic', 'curriculum_id': curriculum_id}
    spans = fact('rule')['source_spans']
    courses = []
    for top, (name, year, term, needs) in enumerate(SHAPE):
        rule = ({'kind': 'verified_none', 'source_spans': spans} if needs is None else
                {'kind': 'course', 'course_id': cid(codes[needs]), 'source_spans': spans})
        courses.append({'course_id': cid(codes[name]), **scope, 'source_version_id': SOURCE.version_id,
                        'facts': {'course_code': fact(codes[name], 700 - top * 10), 'course_title': fact('Fictional ' + name),
                                  'year_level': fact(year), 'semester': fact(term), 'units.printed': fact('2/1')},
                        'prerequisites': rule, 'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(scope, [SOURCE], courses)['courses']}
    for c in courses:
        c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    reviews = [{'review_id': 'review-1', 'source_version_id': SOURCE.version_id, 'course_digests': digests,
                'reviewer_label': 'Synthetic researcher'}]
    return CurriculumRuntime(build_curriculum_ledger(scope, [SOURCE], courses, reviews=reviews))


@pytest.fixture(params=sorted(CURRICULA), scope='module')
def gold(request):
    codes = CURRICULA[request.param]
    return request.param, build(request.param), (lambda name: cid(codes[name]))


def recover(gold, policy=SIX, **kw):
    curriculum_id, runtime, c = gold
    affected = runtime.list_affected_courses(_request('list_affected_courses', curriculum_id,
                                                      course_id=c('F'))).course_ids
    return plan_recovery(runtime, curriculum_id, c('F'), affected, [(c('BASE'), 'passed'), (c('F'), 'failed')],
                         None, policy, ROUTES, **kw)


def moved(draft, c):
    back = {c(n): n for n, *_ in SHAPE}
    return {(t.term.year, t.term.semester): [(back[p.course_id], p.mode) for p in t.moved] for t in draft.terms if t.moved}


def test_the_combined_draft_is_the_owner_gold_shape(gold):
    _, _, c = gold
    draft = next(d for d in recover(gold).drafts if d.variant == 'C')
    assert moved(draft, c) == {(2, 'second_semester'): [('F', 'special_class_request')],
                               (2, 'summer'): [('H', 'summer'), ('J', 'summer')],
                               (3, 'first_semester'): [('G', 'special_class_request'), ('K', 'prescribed'),
                                                       ('M', 'prescribed')],
                               (3, 'second_semester'): [('L', 'prescribed')]}
    third = next(t for t in draft.terms if (t.term.year, t.term.semester) == (3, 'first_semester'))
    assert third.verdict.outcome == 'works_with_warning' and (third.verdict.load.units, third.verdict.load.ceiling) == (12, 9)
    assert (draft.rejoin_term.year, draft.rejoin_term.semester) == (3, 'second_semester')


def test_a_summer_that_holds_all_three_rejoins_a_term_earlier(gold):
    _, _, c = gold
    draft = next(d for d in recover(gold, policy=POLICY).drafts if d.variant == 'C')
    assert moved(draft, c)[(2, 'summer')] == [('H', 'summer'), ('J', 'summer'), ('G', 'summer')]
    assert (draft.rejoin_term.year, draft.rejoin_term.semester) == (3, 'first_semester') and draft.requests == 4


def test_no_course_is_pulled_ahead_of_its_prescribed_term(gold):
    _, runtime, c = gold
    prescribed = {cid: key for cid, key in (
        (cr.course_id, (cr.year, recovery.SLOTS.index(cr.term)))
        for y in range(1, 6) for cr in runtime.look_up(_request('list_term_courses', gold[0], year_level=str(y),
                                                                semester='any')).courses)}
    for draft in recover(gold).drafts:
        for term in draft.terms:
            for p in term.moved:
                assert (term.term.year, recovery.SLOTS.index(term.term.semester)) >= prescribed[p.course_id]


def test_the_fastest_draft_is_named_first_when_asked(gold):
    plain, fastest = recover(gold), recover(gold, fastest_asked=True)
    assert plain.drafts[0].variant == 'A' and not plain.fastest_asked
    assert fastest.drafts[0].variant == 'C' and fastest.fastest_asked
    keys = [(d.rejoin_term.year, recovery.SLOTS.index(d.rejoin_term.semester)) if d.rejoin_term else (6, 0)
            for d in fastest.drafts]
    assert keys == sorted(keys)


def test_memoized_and_unmemoized_drafts_are_identical(gold, monkeypatch):
    remembered = recover(gold)

    class NoMemo:
        def __init__(self, runtime):
            self._runtime = runtime

        def __getattr__(self, name):
            return getattr(self._runtime, name)
    monkeypatch.setattr(recovery, '_Memo', NoMemo)
    assert recover(gold).model_dump(mode='json') == remembered.model_dump(mode='json')
