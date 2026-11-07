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
from backend.bintanong_planning.contracts import PlanReason
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


def run(text, value, language='taglish', topics=(), recovery=(POLICY, ROUTES), *,
        conversation=None, routed_sink=None, curriculum=CURRICULUM, route_proof=False):
    runtime = build(curriculum)
    codes = CURRICULA[curriculum]
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True, rule_bundle_version=runtime.rule_bundle_version,
                                sources=[dict(version_id=SOURCE.version_id, byte_sha256=SOURCE.byte_sha256)], documents=[]))
    proof = None
    if route_proof:
        from test_plan_route_sources import inputs
        source_pin, routes, proof = inputs(recovery[1])
        pin = pin.model_copy(update=dict(documents=source_pin.documents,
                                        plan_routes_sha256=source_pin.plan_routes_sha256))
        proof = proof.model_copy(update=dict(release_id=pin.release_id))
        recovery = recovery[0], routes
    registry = CapabilityRegistry({'list_affected_courses': Capability('synthetic_dependency_inspection',
                                                                       ('curriculum_id', 'course_id'))})
    catalog = tuple(entry(entity=cid(code), alias=code, curriculum=curriculum).model_copy(
        update=dict(source_ref=SOURCE.version_id)) for code in codes.values())
    resources = ReleaseResources(pin, catalog, registry, None, SymbolicAdapter(runtime, recovery=recovery),
                                 topics=topics, course_labels=tuple((cid(code), code) for code in codes.values()),
                                 plan_route_sources=proof)
    style = style_proposal(language, english=[text.split()[0]] if language == 'en' else [],
                                        filipino=[] if language == 'en' else [text.split()[0]])
    integration = asyncio.run(Orchestrator(FakeTransport(json.dumps(value), style_outputs=[json.dumps(style)]),
        releases=SyntheticReleaseProvider(resources)).run(text, RequestContext.parse(dict(
            session_id='sess-a', request_id='req-a', program_id='program-a', curriculum_id=curriculum, facts=[],
            conversation=conversation.model_dump(mode='json') if conversation else None)), routed_sink=routed_sink))
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


def test_recovery_returns_pinned_handbook_passages_in_the_source_registry():
    from backend.bintanong_api.sources import SourceRegistry, source_view
    integration, answer = run(RECOVERY_TEXT, clarify_with_failure(RECOVERY_TEXT), route_proof=True)
    assert answer.status == 'answered'
    assert integration.evidence.plan_routes is not None
    registry = SourceRegistry()
    registry.remember(answer.citations)
    excerpts = [source_view(registry.get(c.evidence_id))['excerpt'] for c in answer.citations]
    assert all(any(clause.text in excerpt for excerpt in excerpts) for clause in answer.recovery.clauses)
    from backend.bintanong_orchestration.contracts import IntegrationResult
    data = integration.model_dump(mode='json')
    data['recovery']['clauses'][0]['text'] = 'Invented recovery guidance.'
    with pytest.raises(ValueError, match='recovery_clauses_must_match_pinned_routes'):
        IntegrationResult.parse(data)
    data = integration.model_dump(mode='json')
    data['recovery'] = None
    with pytest.raises(ValueError, match='dependency_routes_require_recovery'):
        IntegrationResult.parse(data)


def test_the_plain_recovery_question_is_answered_with_delays_routes_and_drafts_in_order(answered):
    integration, answer, lines = answered
    assert answer.status == 'answered' and integration.recovery is not None
    text = '\n'.join(lines)
    assert lines[0] == ('**Draft D**: balik ka sa prescribed sequence mo pagdating ng fourth year, first semester. '
                        'Kailangan pa rin ng approval ang bawat step.')
    delayed = lines.index('### Ano ang maaatras')
    routes = lines.index(f'### Mga option mo para sa {X}')
    first_draft = lines.index('### Mga draft')
    sources = lines.index('### Sources / rules')
    assert 0 < delayed < routes < first_draft < sources
    assert f'- Second year, second semester: {CODES["Y"]}, {CODES["Z"]}' in lines
    assert text.count('"Fictional special_class clause."') == 1  # quoted once under Sources / rules
    assert '- **Special class** (Student Handbook p. 1): "Fictional special_class clause."' in lines[sources:]
    assert 'Hindi ito ang "regular student" classification ng Student Handbook.' in text


def test_every_draft_is_headed_and_says_what_needs_confirmation(answered):
    _, _, lines = answered
    headers = [l for l in lines if l.startswith('#### Draft ')]
    assert [h.split('Draft ')[1][0] for h in headers] == ['D', 'A', 'C', 'B']
    # 2b wording; each note is its own sentence (no "i-confirm.; ").
    assert any(f'Works, may kailangan pang i-confirm. {X}: special class na ni-request, hindi pa approved (tingnan ang '
               'Special class).' in l for l in lines)
    assert not any('.;' in l for l in lines)
    assert any(l.startswith('Nauuna ang Draft D: ') for l in lines)
    assert lines[-1].startswith('Mga draft lang ito, hindi pa approved: ipakita mo sa program adviser mo.')


def test_a_term_over_its_prescribed_total_carries_the_d5_heads_up(answered):
    _, _, lines = answered
    assert any('Heads-up: 12 units, 6 lang ang nakalista sa curriculum mo; puwedeng hindi ma-credit ang sobra '
               '(tingnan ang Maximum load). I-check muna sa Dean o sa Registrar.' in l for l in lines)
    assert any(l.startswith('- **Maximum load** (Student Handbook p. 1):') for l in lines)


def test_the_assumed_start_term_is_said(answered):
    _, _, lines = answered
    assert (f'Assuming na kinuha mo ang {X} sa prescribed term nito (second year, first semester) at hindi naipasa, at '
            'naipasa mo ang ibang courses bago ang second year, second semester, magsisimula ang mga draft sa second '
            'year, second semester.') in lines


def test_the_english_wording_of_the_same_result(answered):
    integration, answer, _ = answered
    shown = lambda course: integration.course_labels.get(course, course)
    lines = recovery_lines(integration.recovery, 'en', shown, dependencies=answer.dependencies)
    assert lines[0] == ('**Draft D** gets you back on your prescribed sequence by fourth year, first semester. Each '
                        'step still needs approval.')
    assert lines[1].startswith('By "regular load" I take it you mean getting back on your curriculum')
    assert f'### Your options for {X}' in lines
    assert ('- Retake it at its next regular offering (third year, first semester) (see Regular class, p. 1). '
            'The class schedule for that term is not confirmed here.') in lines
    assert '#### Draft A: retake at the next regular offering only.' in lines
    assert any('Works, needs confirmation.' in l for l in lines)
    assert any('Heads-up: 12 units, your curriculum lists 6; extra units may not be credited (see Maximum load). '
               'Check with your Dean or the Registrar.' in l for l in lines)
    assert lines[-1] == ('These are drafts, not approved: show them to your program adviser. None of this confirms a '
                         'class offering, an approval, a grade or your academic standing.')


def test_the_rejoin_line_names_a_regular_term(answered):
    _, _, lines = answered
    assert not any('simula summer' in l or 'pagdating ng summer' in l for l in lines)
    assert 'Balik sa prescribed sequence mo simula fourth year, first semester.' in lines


def test_unchecked_prerequisites_are_one_line_under_the_draft_table(answered):
    integration, answer, _ = answered
    shown = lambda course: integration.course_labels.get(course, course)
    draft = integration.recovery.drafts[0]
    terms = list(draft.terms)
    electives = [cid(CODES['Q2']), cid(CODES['R1'])]
    for i, course in enumerate(electives):
        verdict = terms[i].verdict.model_copy(update=dict(outcome='unknown', reasons=(
            PlanReason(kind='prerequisite_unknown', course_id=course),)))
        terms[i] = terms[i].model_copy(update=dict(verdict=verdict))
    recovery = integration.recovery.model_copy(update=dict(drafts=(
        draft.model_copy(update=dict(terms=tuple(terms))), *integration.recovery.drafts[1:])))
    lines = recovery_lines(recovery, 'taglish', shown)
    next_header = next(i for i, line in enumerate(lines) if line.startswith('#### Draft A:'))
    lines = lines[:next_header]
    assert not any(l.startswith('|') and 'prerequisites' in l for l in lines)
    note = (f'Hindi ma-check nang buo ang prerequisites ng {CODES["Q2"]}, {CODES["R1"]}; paki-confirm sa program '
            'adviser.')
    assert lines.count(note) == 1
    rows = [i for i, l in enumerate(lines) if l.startswith('| ') and not l.startswith('| Term')]
    assert lines.index(note) == rows[-1] + 1  # right under the draft table


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
        f'Courses that use {X} as a prerequisite, directly or through another course: {CODES["Y"]}, {CODES["Z"]}, {CODES["W"]}.')
    assert not any(l.startswith('#### Draft') for l in student_text(answer).splitlines())


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
    assert lines[-1] == ('Hindi ko ma-match yung part tungkol sa "tapos saan ang office ng dean?" sa reviewed '
                         'document topic. Hindi pa na-check yung part na ito; paki-clarify o ask sa tamang office.')
    assert 'wala pa sa reviewed sources' not in lines[-1]  # unmatched topic was never a corpus search result
    assert lines[0].startswith(f'Mga course na may {X} bilang prerequisite')


@pytest.mark.parametrize('curriculum', sorted(CURRICULA))
def test_dependency_then_summer_followup_attaches_recovery_without_new_results(curriculum, monkeypatch):
    from backend.bintanong_private_context.conversation import capture
    from test_routing_compile import wire
    code = CURRICULA[curriculum]['X']
    text = f'What courses are blocked if I fail {code}?'
    start = text.index(code)
    first = proposal(text=text, language='en', mentions=[dict(kind='course', text=code,
        start=start, end=start+len(code))], operations=[dict(name='list_affected_courses', target=0)],
        parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured', operation_indices=[0])])
    routed = []
    initial, _ = run(text, first, language='en', routed_sink=routed.append, curriculum=curriculum)
    assert initial.recovery is None
    assert initial.status == 'ready', initial
    memory = capture(routed[0])
    assert memory.course_id == cid(code)
    monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', '1')
    follow = 'paano kung summer?'
    reply = wire(parts=[], control='clarify', route=None)
    result, answer = run(follow, reply, conversation=memory, curriculum=curriculum)
    assert result.status == 'ready' and result.recovery is not None
    assert result.recovery.failed_course_id == cid(code)
    assert result.recovery.term_stated is False
    assert result.assumed_facts == ()
    assert 'summer' in student_text(answer).lower()
    assert 'Assuming' in student_text(answer)
