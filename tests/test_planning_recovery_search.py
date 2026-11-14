"""Recovery search (owner, 4 Nov 2026: "just in time", for every curriculum). Synthetic shape of the owner's BSCS gold
route when the first-semester course F is failed:

  2:1 F needs BASE (failed)          2:2 G, H, J each need F
  3:1 K needs H; M needs J; P1       3:2 L needs G; P2           every course 3 units, summer load 9

The preferred draft (D) places each delayed course in the latest term that still delays none of the courses that need
it (its deadline: the term before its earliest dependant's prescribed term). F is already late, so it goes at once as a
special class; H and J are needed by 3:1, so they take the summer; G is needed only by 3:2, so it waits for a special
class in 3:1 (load heads-up) although the summer has room. Back on sequence by 3:2. Draft D is named first.
"""
import pytest

import test_planning_recovery as base
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
TWELVE = LoadPolicy.parse(dict(POLICY.model_dump(mode='json'), summer_normal_units=12))


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


@pytest.fixture(params=sorted(base.CURRICULA), scope='module')
def other(request):
    """The second synthetic shape (test_planning_recovery): X failed; Y, Z need X; W needs Y; Z unlocks nothing."""
    codes = base.CURRICULA[request.param]
    return request.param, base.build(request.param), (lambda name: cid(codes[name]))


def recover(gold, policy=POLICY, **kw):
    curriculum_id, runtime, c = gold
    affected = runtime.list_affected_courses(_request('list_affected_courses', curriculum_id,
                                                      course_id=c('F'))).course_ids
    return plan_recovery(runtime, curriculum_id, c('F'), affected, [(c('BASE'), 'passed'), (c('F'), 'failed')],
                         None, policy, ROUTES, **kw)


def moved(draft, c, names=SHAPE):
    back = {c(n[0] if isinstance(n, tuple) else n): (n[0] if isinstance(n, tuple) else n) for n in names}
    return {(t.term.year, t.term.semester): [(back[p.course_id], p.mode) for p in t.moved] for t in draft.terms if t.moved}


GOLD = {(2, 'second_semester'): [('F', 'special_class_request')],
        (2, 'summer'): [('H', 'summer'), ('J', 'summer')],
        (3, 'first_semester'): [('G', 'special_class_request'), ('K', 'prescribed'), ('M', 'prescribed')],
        (3, 'second_semester'): [('L', 'prescribed')]}


def test_the_first_draft_is_the_owner_just_in_time_shape(gold):
    _, _, c = gold
    draft = recover(gold).drafts[0]
    assert draft.variant == 'D' and moved(draft, c) == GOLD
    third = next(t for t in draft.terms if (t.term.year, t.term.semester) == (3, 'first_semester'))
    assert third.verdict.outcome == 'works_with_warning' and (third.verdict.load.units, third.verdict.load.ceiling) == (12, 9)
    summer = next(t for t in draft.terms if t.term.semester == 'summer')
    assert summer.verdict.load.units == 6  # within the 9-unit summer load, with room left for G
    assert (draft.rejoin_term.year, draft.rejoin_term.semester) == (3, 'second_semester') and draft.requests == 4


def test_the_earliest_summer_alternative_is_preserved(gold):
    _, _, c = gold
    result = recover(gold)
    earliest = next(d for d in result.drafts if d.variant == 'C')
    assert moved(earliest, c)[(2, 'summer')] == [('H', 'summer'), ('J', 'summer'), ('G', 'summer')]
    assert (earliest.rejoin_term.year, earliest.rejoin_term.semester) == (3, 'first_semester')
    assert recover(gold, fastest_asked=True).drafts[0].variant == 'C'


def test_a_later_deadline_lets_a_course_wait_even_when_the_summer_has_room(gold, other):
    _, _, c = gold
    assert moved(next(d for d in recover(gold, policy=TWELVE).drafts if d.variant == 'D'), c) == GOLD
    # Z unlocks nothing: it waits for its next regular offering instead of a summer or special class.
    _, _, o = other
    draft = next(d for d in base.recover(other).drafts if d.variant == 'D')
    assert moved(draft, o, base.NAMES) == {(2, 'second_semester'): [('X', 'special_class_request')],
                                           (2, 'summer'): [('Y', 'summer')],
                                           (3, 'first_semester'): [('W', 'prescribed')],
                                           (3, 'second_semester'): [('Z', 'prescribed')]}
    # The rejoin is a regular term: after 3:2 comes the summer, so the student is back from 4:1.
    assert (draft.rejoin_term.year, draft.rejoin_term.semester) == (4, 'first_semester') and draft.requests == 2


def test_when_summer_is_not_needed_the_combined_draft_uses_regular_offerings_only(other):
    # From 3:1, X is retaken at once and Y, Z, W reach their regular offerings without delaying anything further.
    result = base.recover(other, term=(3, 'first_semester'))
    assert [d.variant for d in result.drafts] == ['D', 'C'] and result.drafts[0].requests == 0
    assert {(d.variant, d.reason, d.same_as) for d in result.dropped} == {('A', 'same_as', 'D'), ('B', 'same_as', 'D')}
    assert not any(t.term.semester == 'summer' for t in result.drafts[0].terms)
    assert any(t.term.semester == 'summer' for t in result.drafts[1].terms)  # earliest alternative retained


def test_a_course_with_no_dependant_takes_a_special_class_only_to_finish_within_the_curriculum(other):
    curriculum_id, runtime, o = other
    result = plan_recovery(runtime, curriculum_id, o('S1'), (), [(o('S1'), 'failed')], None, POLICY, ROUTES)
    by_variant = {d.variant: d for d in result.drafts}
    assert moved(by_variant['D'], o, base.NAMES) == {(4, 'second_semester'): [('S1', 'special_class_request')]}
    assert moved(by_variant['A'], o, base.NAMES) == {(5, 'first_semester'): [('S1', 'retake')]}


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


def test_the_fastest_ordering_is_kept_when_asked(gold):
    plain, fastest = recover(gold), recover(gold, fastest_asked=True)
    assert plain.drafts[0].variant == 'D' and not plain.fastest_asked and fastest.fastest_asked
    rest = plain.drafts[1:]
    assert [d.requests for d in rest] == sorted(d.requests for d in rest)
    keys = [(d.rejoin_term.year, recovery.SLOTS.index(d.rejoin_term.semester)) if d.rejoin_term else (6, 0)
            for d in fastest.drafts]
    assert keys == sorted(keys)
    assert all(d.rejoin_term is None or d.rejoin_term.semester != 'summer' for d in plain.drafts)


def test_memoized_and_unmemoized_drafts_are_identical(gold, monkeypatch):
    remembered = recover(gold)

    class NoMemo:
        def __init__(self, runtime):
            self._runtime = runtime

        def __getattr__(self, name):
            return getattr(self._runtime, name)
    monkeypatch.setattr(recovery, '_Memo', NoMemo)
    assert recover(gold).model_dump(mode='json') == remembered.model_dump(mode='json')
