"""Ask mode replies (owner, 4 Nov 2026): a plain "bagsak ako sa X, ano pwede ko itake / options?" answers, in order,
what gets delayed (each course with its prescribed term), the recovery routes quoted from the reviewed clauses, and
the greedy drafts already run through the plan checker, each headed for adviser review with the 2b wording and the
D5 heads-up. Without a recovery cue the dependency reply is unchanged. Synthetic curriculum (test_planning_recovery).
"""
import asyncio
import json

import pytest

from backend.bintanong_api.presentation import student_text
from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_generation.generator import Generator
from backend.bintanong_generation.recovery_reply import recovery_lines
from backend.bintanong_orchestration.adapters import SymbolicAdapter
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from test_generation_research import NoModel
from test_planning_check import POLICY, cid
from test_planning_recovery import CURRICULA, ROUTES, build
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import entry
from test_symbolic_course_facts import SOURCE

CURRICULUM = 'curriculum-synthetic-1'
CODES = CURRICULA[CURRICULUM]
X = CODES['X']  # 'SYN 302'
RECOVERY_TEXT = (f'Hala, bagsak ako sa {X}, paano na yung major subs ko? Ano pwede ko itake para maging regular load '
                 'ako agad? Ano pwede options ko?')


def run(text, value, language='taglish', topics=(), recovery=(POLICY, ROUTES)):
    runtime = build(CURRICULUM)
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True, rule_bundle_version=runtime.rule_bundle_version,
                                sources=[dict(version_id=SOURCE.version_id, byte_sha256=SOURCE.byte_sha256)], documents=[]))
    registry = CapabilityRegistry({'list_affected_courses': Capability('synthetic_dependency_inspection',
                                                                       ('curriculum_id', 'course_id'))})
    catalog = tuple(entry(entity=cid(code), alias=code, curriculum=CURRICULUM).model_copy(
        update=dict(source_ref=SOURCE.version_id)) for code in CODES.values())
    resources = ReleaseResources(pin, catalog, registry, None, SymbolicAdapter(runtime, recovery=recovery),
                                 topics=topics, course_labels=tuple((cid(code), code) for code in CODES.values()))
    style = style_proposal(language, english=[X], filipino=[] if language == 'en' else [text.split()[0]])
    integration = asyncio.run(Orchestrator(FakeTransport(json.dumps(value), style_outputs=[json.dumps(style)]),
        releases=SyntheticReleaseProvider(resources)).run(text, RequestContext.parse(dict(
            session_id='sess-a', request_id='req-a', program_id='program-a', curriculum_id=CURRICULUM, facts=[]))))
    return integration, asyncio.run(Generator(NoModel()).generate(text, integration))


def clarify_with_failure(text, language='taglish'):
    """The shape that ended in an empty clarification: control clarify, the stated failure, no operation."""
    start = text.index(X)
    claim = f'bagsak ako sa {X}'
    return proposal(text=text, language=language, route=None, control='clarify', operations=[],
                    mentions=[dict(kind='course', text=X, start=start, end=start + len(X))],
                    claims=[dict(text=claim, start=text.index(claim), end=text.index(claim) + len(claim), entity=0,
                                 state='failed', mode='asserted')],
                    parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='unknown',
                                operation_indices=[])])


@pytest.fixture(scope='module')
def answered():
    integration, answer = run(RECOVERY_TEXT, clarify_with_failure(RECOVERY_TEXT))
    return integration, answer, student_text(answer).splitlines()


def test_the_plain_recovery_question_is_answered_with_delays_routes_and_drafts_in_order(answered):
    integration, answer, lines = answered
    assert answer.status == 'answered' and integration.recovery is not None
    text = '\n'.join(lines)
    delayed = next(i for i, l in enumerate(lines) if l.startswith(f'Kung ma-fail mo ang {X}'))
    routes = next(i for i, l in enumerate(lines) if l.startswith(f'Mga paraan para kunin ulit ang {X}'))
    first_draft = next(i for i, l in enumerate(lines) if l.startswith('Draft lang, hindi pa approved.'))
    assert delayed < routes < first_draft
    assert f'{CODES["Y"]} (second year, second semester)' in lines[delayed]  # each with its prescribed term
    assert 'Student Handbook p. 1: "Fictional special_class clause."' in text  # quoted from the route record
    assert 'Hindi ito ang "regular student" classification ng Student Handbook.' in text


def test_every_draft_is_headed_and_says_what_needs_confirmation(answered):
    _, _, lines = answered
    headers = [l for l in lines if l.startswith('Draft lang, hindi pa approved. Ipakita mo ito sa program adviser mo.')]
    assert [h.split('Draft ')[2][0] for h in headers] == ['A', 'C', 'B']
    assert any(l.endswith('Works, may kailangan pang i-confirm.') for l in lines)  # 2b wording
    assert any(f'{X}: special class na ni-request, hindi pa approved' in l for l in lines)


def test_a_term_over_its_prescribed_total_carries_the_d5_heads_up(answered):
    _, _, lines = answered
    assert ("  Heads-up: 12 units ang sem na 'to, pero 6 lang ang nakalista sa curriculum mo. Ayon sa Student Handbook, "
            'puwedeng hindi ma-credit ang sobrang units (p. 1). Mas okay kung i-check mo muna sa Dean o sa Registrar '
            'bago ka mag-enroll.') in lines


def test_the_assumed_start_term_is_said(answered):
    _, _, lines = answered
    assert (f'Assuming na kinuha mo ang {X} sa prescribed term nito (second year, first semester) at hindi naipasa, at '
            'naipasa mo ang ibang courses bago ang second year, second semester, magsisimula ang mga draft sa second '
            'year, second semester.') in lines


def test_the_english_wording_of_the_same_result(answered):
    integration, _, _ = answered
    shown = lambda course: integration.course_labels.get(course, course)
    lines = recovery_lines(integration.recovery, 'en', shown)
    assert lines[0].startswith('By "regular load" I take it you mean getting back on your curriculum')
    assert lines[1] == f'Ways to take {X} again (not ranked; each needs confirmation):'
    assert lines[2].startswith('- Retake it at its next regular offering (third year, first semester).')
    assert ('Draft, not approved. Show this to your program adviser. Draft A: retake at the next regular offering '
            'only.') in lines
    assert any(l.endswith('Works, needs confirmation.') for l in lines)
    assert any(l.startswith('  Heads-up: this semester comes to 12 units, but your curriculum lists 6 for it.')
               for l in lines)
    assert lines[-1] == 'None of this confirms a class offering, an approval, a grade or your academic standing.'


def test_without_a_recovery_cue_the_dependency_reply_is_unchanged():
    text = f'What courses are blocked if I fail {X}?'
    start = text.index(X)
    value = proposal(text=text, language='en', mentions=[dict(kind='course', text=X, start=start, end=start + len(X))],
                     operations=[dict(name='list_affected_courses', target=0)],
                     parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured',
                                 operation_indices=[0])])
    integration, answer = run(text, value, language='en')
    assert integration.recovery is None
    assert student_text(answer).splitlines()[0] == (
        f'If you fail {X}, these courses are affected because their prerequisites include it (directly or through '
        f'another course): {CODES["Y"]}, {CODES["Z"]}, {CODES["W"]}.')
    assert not any(l.startswith('Draft') for l in student_text(answer).splitlines())


def test_a_part_with_no_reviewed_topic_is_named_unavailable_beside_the_answered_dependency_part():
    # Owner GUI 4 Nov 2026 robustness: the structured part answers; the other part says it has no reviewed source.
    asked = f'Anong subs ang affected if I fail {X}'
    text = asked + ' tapos saan ang office ng dean?'
    start = text.index(X)
    value = proposal(text=text, language='taglish', route='Hybrid',
                     mentions=[dict(kind='course', text=X, start=start, end=start + len(X))],
                     operations=[dict(name='list_affected_courses', target=0)],
                     parts=[dict(part_id='r1', text=asked, start=0, end=len(asked), evidence_need='structured',
                                 operation_indices=[0]),
                            dict(part_id='r2', text='tapos saan ang office ng dean?', start=len(asked) + 1, end=len(text),
                                 evidence_need='document', operation_indices=[])])
    topic = DocumentTopic(subject_id='fictional_policy', claims=('printed Form Q policy',))
    integration, answer = run(text, value, topics=(topic,))
    lines = student_text(answer).splitlines()
    assert answer.status == 'answered' and integration.route == 'Symbolic'
    assert lines[-1] == ('Yung part tungkol sa "tapos saan ang office ng dean?" ay wala pa sa reviewed sources ng '
                         'Bintanong. Paki-ask sa tamang university office.')
    assert lines[0].startswith(f'Kung ma-fail mo ang {X}')
