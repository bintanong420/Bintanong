"""Owner report, 4 Nov 2026: "what if bagsak ako sa CS 13/L, ano 'yong mga subject na hindi ko ma-ttake?" listed every
unresolved course as missing information. A dependency question is answered: the courses whose reviewed rules need the
failed course (or none), and only a short note for courses whose printed condition could still include it.
Synthetic ledger from the term tests, plus a year-standing course (SYN 299)."""
import asyncio
import json

import pytest

from backend.bintanong_api.presentation import student_text
from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.adapters import SymbolicAdapter
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_generation_research import NoModel
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import entry
import test_term_prerequisite_advising as term
from test_symbolic_course_facts import SCOPE, SOURCE, fact


def ledger(include_group=True):
    rows = [r for r in term.ROWS if include_group or r[0] != 'SYN 280'] + [('SYN 299', 'SECOND YEAR', 'SECOND SEMESTER', 'standing')]
    courses = []
    for top, (code, year, semester, prerequisite) in enumerate(rows):
        rule = ({'kind': 'unresolved', 'reason': 'Printed condition "4th Year Standing" is a year-level standing, not a '
                 'course; unknown unless the student states their year level', 'source_spans': fact('r')['source_spans']}
                if prerequisite == 'standing' else term.rule(prerequisite))
        courses.append({'course_id': term.cid(code), **SCOPE, 'source_version_id': SOURCE.version_id,
                        'facts': {'course_code': fact(code, 700 - top * 10), 'course_title': fact('Fictional ' + code),
                                  'year_level': fact(year), 'semester': fact(semester)},
                        'prerequisites': rule, 'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(SCOPE, [SOURCE], courses)['courses']}
    for c in courses:
        c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    return build_curriculum_ledger(SCOPE, [SOURCE], courses, reviews=[{'review_id': 'review-1',
        'source_version_id': SOURCE.version_id, 'course_digests': digests, 'reviewer_label': 'Synthetic researcher'}])


def test_a_year_standing_condition_names_no_course_so_it_cannot_make_a_list_partial():
    from test_term_prerequisite_advising import course_request
    result = CurriculumRuntime(ledger()).list_affected_courses(course_request('list_affected_courses', 'SYN 260'))
    assert result.course_ids == ()
    assert result.unknown_conditions == (f'rule_unresolved:{term.cid("SYN 280")}',)  # the printed group condition
    complete = CurriculumRuntime(ledger(include_group=False)).list_affected_courses(course_request('list_affected_courses', 'SYN 131'))
    assert complete.status == 'complete' and complete.course_ids == (term.cid('SYN 251'),)


def ask(text, target, language='en', claims=(), part=None):
    runtime = CurriculumRuntime(ledger())
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True, rule_bundle_version=runtime.rule_bundle_version,
                                sources=[dict(version_id=SOURCE.version_id, byte_sha256=SOURCE.byte_sha256)], documents=[]))
    registry = CapabilityRegistry({'list_affected_courses': Capability('synthetic_dependency_inspection',
                                                                       ('curriculum_id', 'course_id'))})
    codes = [r[0] for r in term.ROWS] + ['SYN 299']
    catalog = tuple(entry(entity=term.cid(c), alias=c, curriculum='curriculum-synthetic-1').model_copy(
        update=dict(source_ref=SOURCE.version_id)) for c in codes)
    resources = ReleaseResources(pin, catalog, registry, None, SymbolicAdapter(runtime),
                                 course_labels=tuple((term.cid(c), c) for c in codes))
    start = text.index(target)
    value = proposal(text=text, language=language, mentions=[dict(kind='course', text=target, start=start, end=start + len(target))],
                     claims=list(claims), operations=[dict(name='list_affected_courses', target=0)])
    part = text if part is None else part
    value['parts'] = [dict(part_id='r1', text=part, start=text.index(part), end=text.index(part) + len(part),
                           evidence_need='structured', operation_indices=[0])]
    style = style_proposal(language, english=[text.split()[0]] if language == 'en' else [], filipino=[] if language == 'en' else [text.split()[0]])
    integration = asyncio.run(Orchestrator(FakeTransport(json.dumps(value), style_outputs=[json.dumps(style)]),
        releases=SyntheticReleaseProvider(resources)).run(text, RequestContext.parse(context(curriculum_id='curriculum-synthetic-1'))))
    return asyncio.run(Generator(NoModel()).generate(text, integration))


def test_failing_a_course_nothing_depends_on_blocks_no_course_with_a_short_note():
    answer = ask('What courses are blocked if I fail SYN 260?', 'SYN 260')
    assert answer.status == 'answered'
    assert student_text(answer).splitlines()[:2] == [
        'No course in your prospectus lists SYN 260 as a prerequisite, so failing it does not block another course.',
        'Note: SYN 280 requires "All major subjects" (as printed). I can\'t check that from individual course results, '
        'so please confirm it with your program adviser.']


def test_failing_a_course_lists_the_courses_whose_reviewed_rules_need_it():
    answer = ask('What courses are blocked if I fail SYN 131?', 'SYN 131')
    assert student_text(answer).splitlines()[0] == (
        'If you fail SYN 131, these courses are affected because their prerequisites include it (directly or through '
        'another course): SYN 251.')


def test_taglish_dependency_answer():
    answer = ask('Kung bagsak ako sa SYN 260, ano ang hindi ko ma-take?', 'SYN 260', language='taglish')
    assert student_text(answer).splitlines()[0] == (
        'Walang course sa prospectus mo na may SYN 260 bilang prerequisite, kaya hindi nito mabo-block ang ibang course.')



# Owner report, 4 Nov 2026: "Im currently first year, what specific course i can not take in second semester when i
# fail computer programming 1?" listed every dependent course of all four years.
def test_a_question_that_names_a_term_answers_for_that_term_first():
    answer = ask("I'm second year. What can't I take in second semester if I fail SYN 131?", 'SYN 131')
    assert student_text(answer).splitlines()[0] == 'In second year, second semester, failing SYN 131 blocks: SYN 251.'


def test_a_named_term_with_no_affected_course_says_so_and_names_later_ones():
    answer = ask("I'm first year. What can't I take in second semester if I fail SYN 131?", 'SYN 131')
    assert student_text(answer).splitlines()[:2] == [
        'In first year, second semester, no course needs SYN 131.',
        'Courses in other terms that need it: SYN 251 (second year, second semester).']



def test_the_year_is_read_from_the_whole_question_even_outside_the_asked_part():
    # Live 4 Nov 2026: the model quoted only the question sentence; "Im currently second year" stood outside it.
    text = "Im currently second year. What can't I take in second semester if I fail SYN 131?"
    answer = ask(text, 'SYN 131', part="What can't I take in second semester if I fail SYN 131?")
    assert student_text(answer).splitlines()[0] == 'In second year, second semester, failing SYN 131 blocks: SYN 251.'


def test_several_affected_courses_are_listed_in_curriculum_order():
    # Live 4 Nov 2026: reordering the listed courses raised a contract error with more than one course.
    answer = ask('What courses are blocked if I fail SYN 141?', 'SYN 141')
    assert answer.status == 'answered'
    assert student_text(answer).splitlines()[0].endswith('(directly or through another course): SYN 241, SYN 251.')


def test_curriculum_order_can_differ_from_id_order_without_touching_the_result():
    from backend.bintanong_generation.dependency_reply import dependency_lines
    from test_term_prerequisite_advising import course_request
    result = CurriculumRuntime(ledger()).list_affected_courses(course_request('list_affected_courses', 'SYN 141'))
    swapped = result.model_copy(update=dict(placements=((term.cid('SYN 251'), 1, 'first_semester'),
                                                        (term.cid('SYN 241'), 2, 'second_semester'))))
    shown = {term.cid('SYN 241'): 'SYN 241', term.cid('SYN 251'): 'SYN 251', term.cid('SYN 141'): 'SYN 141'}.get
    lines = dependency_lines(swapped, term.cid('SYN 141'), 'en', lambda c: shown(c, c))
    assert lines[0].endswith(': SYN 251, SYN 241.')
