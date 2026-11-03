"""Memory/eligibility plan, Task 4: "What can I take next sem?" checks every reviewed course of the requested term
with the same release and facts. Synthetic ledger shaped like the plan's old-BSCS case: SYN 131 and SYN 141 are
first-year courses; in second year, second semester SYN 251 needs both, SYN 241 needs SYN 141, SYN 290 has a blank
printed cell, SYN 260 has a reviewed "None" and SYN 270 needs SYN 105. Year three is absent from the source."""
import asyncio

import pytest

from backend.bintanong_contracts.runtime import PredicateRequest
from backend.bintanong_orchestration.adapters import SymbolicAdapter
from backend.bintanong_orchestration.term_assessment import TermAssessmentResult, assess_term
from backend.bintanong_routing.contracts import RequestContext
from backend.bintanong_symbolic.authoring import build_curriculum_ledger
from backend.bintanong_symbolic.runtime import CurriculumRuntime, StudentFacts
from test_symbolic_course_facts import SCOPE, SOURCE, fact

ROWS = [('SYN 131', 'FIRST YEAR', 'FIRST SEMESTER', None), ('SYN 141', 'FIRST YEAR', 'FIRST SEMESTER', None),
        ('SYN 105', 'FIRST YEAR', 'SECOND SEMESTER', None),
        ('SYN 251', 'SECOND YEAR', 'SECOND SEMESTER', ('all_of', 'SYN 131', 'SYN 141')),
        ('SYN 241', 'SECOND YEAR', 'SECOND SEMESTER', ('course', 'SYN 141')),
        ('SYN 290', 'SECOND YEAR', 'SECOND SEMESTER', 'blank'),
        ('SYN 260', 'SECOND YEAR', 'SECOND SEMESTER', None),
        ('SYN 270', 'SECOND YEAR', 'SECOND SEMESTER', ('course', 'SYN 105'))]


def cid(code):
    return 'course-' + code.replace(' ', '').lower()


def rule(value):
    spans = fact('rule')['source_spans']
    if value is None:
        return {'kind': 'verified_none', 'source_spans': spans}
    if value == 'blank':
        return {'kind': 'unresolved', 'reason': 'Printed prerequisite cell is blank', 'source_spans': spans}
    if value[0] == 'course':
        return {'kind': 'course', 'course_id': cid(value[1]), 'source_spans': spans}
    return {'kind': value[0], 'items': [rule(('course', c)) for c in value[1:]], 'source_spans': spans}


def ledger():
    courses = []
    for top, (code, year, term, prerequisite) in enumerate(ROWS):
        courses.append({'course_id': cid(code), **SCOPE, 'source_version_id': SOURCE.version_id,
                        'facts': {'course_code': fact(code, 700 - top * 10), 'course_title': fact('Fictional ' + code),
                                  'year_level': fact(year), 'semester': fact(term)},
                        'prerequisites': rule(prerequisite), 'review_state': 'draft', 'review_refs': []})
    digests = {c['course_id']: c['content_sha256'] for c in build_curriculum_ledger(SCOPE, [SOURCE], courses)['courses']}
    for c in courses:
        c['review_state'], c['review_refs'] = 'reviewed', ['review-1']
    reviews = [{'review_id': 'review-1', 'source_version_id': SOURCE.version_id, 'course_digests': digests,
                'reviewer_label': 'Synthetic researcher'}]
    return build_curriculum_ledger(SCOPE, [SOURCE], courses, reviews=reviews)


def term_request(year='2', semester='second_semester'):
    return PredicateRequest.parse({'predicate': 'assess_term_prerequisites', 'inputs': [
        {'name': 'curriculum_id', 'value': 'curriculum-synthetic-1', 'fact_ref': None},
        {'name': 'year_level', 'value': year, 'fact_ref': None},
        {'name': 'semester', 'value': semester, 'fact_ref': None}]})


def groups(result):
    found = {}
    for course in result.courses:
        found.setdefault(('retake ' if course.retake else '') + course.group, []).append(course.code)
    return found


FAILED_FIRST_YEAR = StudentFacts(failed=(cid('SYN 131'), cid('SYN 141')))


def test_explicit_failures_block_their_dependents_and_a_blank_cell_stays_unresolved():
    result = assess_term(CurriculumRuntime(ledger()), term_request(), FAILED_FIRST_YEAR)
    assert type(result) is TermAssessmentResult and result.status == 'complete'
    assert groups(result) == {'blocked': ['SYN 251', 'SYN 241'], 'needs_info': ['SYN 290', 'SYN 270'],
                              'met': ['SYN 260'], 'retake met': ['SYN 131', 'SYN 141']}
    by_code = {c.code: c for c in result.courses if not c.retake}
    assert by_code['SYN 251'].violated == (f'not_completed:{cid("SYN 131")}', f'not_completed:{cid("SYN 141")}')
    assert by_code['SYN 241'].violated == (f'not_completed:{cid("SYN 141")}',)
    assert by_code['SYN 290'].unresolved_reason == 'Printed prerequisite cell is blank'
    assert by_code['SYN 270'].missing == (f'completion_unknown:{cid("SYN 105")}',)
    assert result.rule_spans and result.scope is not None


def test_a_course_already_passed_is_kept_apart_from_what_can_be_taken():
    facts = StudentFacts(passed=(cid('SYN 260'), cid('SYN 131'), cid('SYN 141'), cid('SYN 105')))
    result = assess_term(CurriculumRuntime(ledger()), term_request(), facts)
    assert groups(result) == {'met': ['SYN 251', 'SYN 241', 'SYN 270'], 'needs_info': ['SYN 290'],
                              'already_passed': ['SYN 260']}


def test_a_term_missing_from_the_source_is_not_covered_never_empty():
    result = assess_term(CurriculumRuntime(ledger()), term_request(year='3', semester='first_semester'), StudentFacts())
    assert result.status == 'not_covered' and result.courses == ()
    assert result.covered_terms == ('1:first_semester', '1:second_semester', '2:second_semester')


def test_the_adapter_runs_the_term_check_with_the_projected_session_facts():
    context = RequestContext.parse(dict(session_id='sess-a', request_id='req-a', program_id='program-synthetic',
        curriculum_id='curriculum-synthetic-1', facts=[
            dict(fact_id='fact-a', session_id='sess-a', program_id='program-synthetic',
                 curriculum_id='curriculum-synthetic-1', course_id=cid('SYN 131'), state='failed'),
            dict(fact_id='fact-b', session_id='sess-a', program_id='program-synthetic',
                 curriculum_id='curriculum-synthetic-1', course_id=cid('SYN 141'), state='not_taken')]))
    result = asyncio.run(SymbolicAdapter(CurriculumRuntime(ledger())).execute(term_request(), context))
    assert type(result) is TermAssessmentResult
    assert groups(result)['blocked'] == ['SYN 251', 'SYN 241']
    assert groups(result)['retake met'] == ['SYN 131']  # never taken is not a retake


# ---- through the router, orchestrator and generator (the plan's Example B) -------------------------------------
import json

from backend.bintanong_api.presentation import student_text
from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
from test_generation_research import NoModel
from test_routing_contracts import proposal
from test_routing_router import FakeTransport
from test_routing_validation import entry

EXAMPLE_B = 'I failed SYN 131 and SYN 141. What can I take in second year, second sem?'


def release():
    runtime = CurriculumRuntime(ledger())
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True, rule_bundle_version=runtime.rule_bundle_version,
                                sources=[dict(version_id=SOURCE.version_id, byte_sha256=SOURCE.byte_sha256)], documents=[]))
    registry = CapabilityRegistry({'assess_term_prerequisites': Capability(
        'synthetic_term_prerequisites', ('curriculum_id', 'year_level', 'semester'))})
    catalog = tuple(entry(entity=cid(code), alias=code, curriculum='curriculum-synthetic-1').model_copy(
        update=dict(source_ref=SOURCE.version_id)) for code, *_ in ROWS)
    return ReleaseResources(pin, catalog, registry, None, SymbolicAdapter(runtime),
                            course_labels=tuple((cid(code), code) for code, *_ in ROWS))


def interpretation(text=EXAMPLE_B, term='second year, second sem', language='en'):
    start = text.index(term)
    mentions = [dict(kind='course', text='SYN 131', start=9, end=16), dict(kind='course', text='SYN 141', start=21, end=28),
                dict(kind='term', text=term, start=start, end=start + len(term))]
    value = proposal(text=text, language=language, mentions=mentions,
                     claims=[dict(entity=0, state='failed', mode='asserted', text='I failed SYN 131', start=0, end=16),
                             dict(entity=1, state='failed', mode='asserted', text='I failed SYN 131 and SYN 141',
                                  start=0, end=28)],
                     operations=[dict(name='assess_term_prerequisites', target=2)])
    question = text.index('What')
    value['parts'] = [dict(part_id='r1', text=text[question:], start=question, end=len(text),
                           evidence_need='structured', operation_indices=[0])]
    return value


def run(text=EXAMPLE_B, **options):
    from test_routing_contracts import context
    ctx = RequestContext.parse(context(curriculum_id='curriculum-synthetic-1'))
    from test_routing_router import style_proposal
    language = options.get('language', 'en')
    style = style_proposal(language, english=['What can I take'], filipino=[] if language == 'en' else ['I failed'])
    return asyncio.run(Orchestrator(FakeTransport(json.dumps(interpretation(text, **options)),
                                                  style_outputs=[json.dumps(style)]),
                                    releases=SyntheticReleaseProvider(release())).run(text, ctx))


def test_example_b_groups_the_term_with_reasons_and_separates_retakes():
    integration = run()
    assert integration.status == 'ready' and integration.evidence.term_assessment is not None
    answer = asyncio.run(Generator(NoModel()).generate(EXAMPLE_B, integration))
    assert answer.status == 'answered'
    assert student_text(answer).splitlines() == [
        'Second year, second semester courses in your prospectus, checked against what you told me:',
        'Prerequisites met: SYN 260',
        'Blocked by a known prerequisite: SYN 251 (needs SYN 131 and SYN 141), SYN 241 (needs SYN 141)',
        'Needs information or source review: SYN 290 (no prerequisite is printed for it in the prospectus; '
        'please confirm with your program adviser), SYN 270 (have you passed SYN 105?)',
        'Possible retakes (failed earlier): SYN 131 (prerequisites met), SYN 141 (prerequisites met)',
        'This is the prospectus list for that term. It does not confirm section offerings, slots or enrollment approval.']
    assert answer.citations  # the checked rules are cited


def test_a_term_the_source_does_not_cover_says_so():
    text = 'I failed SYN 131 and SYN 141. What can I take in third year, first sem?'
    answer = asyncio.run(Generator(NoModel()).generate(text, run(text, term='third year, first sem')))
    assert student_text(answer).splitlines()[0] == (
        'The reviewed prospectus for this curriculum does not include third year, first semester, so I cannot list '
        'its courses. It covers: first year, first semester; first year, second semester; second year, second semester.')


def test_taglish_grouping_keeps_the_same_groups():
    answer = asyncio.run(Generator(NoModel()).generate(EXAMPLE_B, run(language='taglish')))
    lines = student_text(answer).splitlines()
    assert lines[1] == 'Pasok sa prerequisites: SYN 260'
    assert lines[2] == 'Blocked ng kilalang prerequisite: SYN 251 (kailangan ang SYN 131 at SYN 141), SYN 241 (kailangan ang SYN 141)'


def test_a_term_question_without_a_year_asks_only_for_the_term_and_keeps_the_failures():
    text = 'I failed SYN 131 and SYN 141. What can I take next sem?'
    integration = run(text, term='next sem')
    assert integration.status == 'clarify' and integration.missing_facts == ('term',)
    answer = asyncio.run(Generator(NoModel()).generate(text, integration))
    assert student_text(answer) == ('Which year level and semester is this for? For example: '
                                    '"second year, second semester".')
