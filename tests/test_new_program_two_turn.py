"""Memory/eligibility plan, "Adding another program" gate: a new reviewed ledger with unfamiliar course ids joins
through the release builder, and the regular chat path resolves a two-turn check with no prompt, evaluator or
template edit. Fictional ledger (SYN201 requires SYN101); the model is scripted, Prolog is real."""
import asyncio
import json

from backend.bintanong_api.chat import ChatRequest, ChatTurns, CurriculumOption
from backend.bintanong_api.presentation import student_text
from backend.bintanong_api.research_pipeline import ResearchPipeline
from backend.bintanong_api.session import Session
from backend.bintanong_orchestration.ports import SyntheticReleaseProvider
from backend.bintanong_private_context.sessions import SessionStore
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, style_proposal
from test_runtime_multi_curriculum import build, real_ledger

NEW = 'curriculum-zz-new'
QUESTION = 'Can I take SYN201?'


def transport(explanation, *, reply_to=None):
    interpretation = proposal(text=QUESTION, language='en',
                              mentions=[dict(kind='course', text='SYN201', start=11, end=17)])
    style = style_proposal('en', english=['Can I take'], filipino=[])
    if reply_to is not None:
        from backend.bintanong_private_context.memory import turn_ref
        interpretation = dict(schema_version='bintanong-interpretation-wire-v4', language='en',
            audience='undergraduate', control='clarify', part_count=0, intent='answer clarification',
            route=None, ambiguities=[], mentions=[], claims=[], operations=[], parts=[],
            dialogue=dict(act='answer_clarification', turn_id=turn_ref(reply_to), course_id=None))
        style = style_proposal('en', english=['yes'], filipino=[])
    reply = json.dumps(dict(schema_version='bintanong-decision-explanation-v1', language='en', explanation=explanation))
    return FakeTransport(json.dumps(interpretation), reply, style_outputs=[json.dumps(style)])


def test_a_new_programs_ledger_answers_a_two_turn_check_through_the_regular_chat(monkeypatch):
    from backend.bintanong_runtime import research
    original = research.build_multi_research_resources

    def with_new(ledgers, package, **options):  # the new program joins the release like any other ledger
        return original({**ledgers, NEW: real_ledger(NEW, 'course-zx-alpha', 'course-zx-beta')}, package, **options)
    monkeypatch.setattr(research, 'build_multi_research_resources', with_new)
    resources, _ = build(monkeypatch)
    assert NEW in {m.curriculum_id for m in resources.pin.curricula}

    transports = [transport('SYN201 builds on SYN101.'),
                  transport('SYN201 builds on SYN101, which you passed.', reply_to='msg-1')]
    pipeline = ResearchPipeline(lambda: transports.pop(0), SyntheticReleaseProvider(resources))
    store = SessionStore()
    issued = store.issue()
    turns = ChatTurns(store, pipeline, (CurriculumOption('program-synthetic', NEW, 'New program', 'New edition'),),
                      course_labels=dict(resources.course_labels))

    def ask(text, message_id):
        request = ChatRequest.model_validate(dict(messages=[dict(id=message_id, role='user', parts=[dict(type='text', text=text)])],
                                                  programId='program-synthetic', curriculumId=NEW))
        return asyncio.run(turns.answer(Session(issued.credential, store.resolve(issued.credential)), request))

    first = ask(QUESTION, 'msg-1')
    assert first.status == 'clarification_needed'
    assert student_text(first).splitlines()[:2] == ["SYN201 needs SYN101. Have you passed SYN101? Tell me and I'll check for you.",
                                                     'SYN201 builds on SYN101.']
    assert store.resolve(issued.credential).pending_check.course_id == 'course-zx-alpha'

    second = ask('yes', 'msg-2')
    assert second.status == 'answered' and second.decision.outcome == 'eligible'
    assert student_text(second).splitlines()[0] == "Yes, you can take SYN201! You've passed its prerequisite, SYN101."
    ledger = real_ledger(NEW, 'course-zx-alpha', 'course-zx-beta')
    sources = {s['version_id'] for s in ledger['sources']}
    assert second.citations and all(c.version_id in sources for card in second.citations for c in card.citations)
    assert [(f.course_id, f.state) for f in store.resolve(issued.credential).facts] == [('course-zx-alpha', 'passed')]
