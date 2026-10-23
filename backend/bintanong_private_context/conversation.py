"""Capture of the ids an answered turn used, and the next turn's request context (master 23)."""
from __future__ import annotations

from ..bintanong_routing.contracts import ConversationContext, RequestContext
from ..bintanong_routing.validation import RoutingResult
from .sessions import SessionView


def capture(result: RoutingResult) -> ConversationContext | None:
    """Only a validated turn is kept. The course is the one the turn's check asked about (owner,
    23 Oct 2026: "Can I take CC 5? I passed CC 4." -> "it" is CC 5); without a check, only a single
    mentioned course is kept, so a later "its" never has to choose between two antecedents."""
    if result.diagnostic != 'validated':
        return None
    request = result.decision.predicate_request
    courses = ({i.value for i in request.inputs if i.name == 'course_id'} if request is not None
               else {e.value for e in result.query.entities if e.kind == 'course'})
    subjects = {p.subject_id for p in result.proposed.parts if p.subject_id} if result.proposed else set()
    return ConversationContext(program_id=result.program_id, curriculum_id=result.curriculum_id,
                               course_id=courses.pop() if len(courses) == 1 else None,
                               subject_id=subjects.pop() if len(subjects) == 1 else None)


def follow_up_context(view: SessionView, *, request_id: str, program_id: str | None = None,
                      curriculum_id: str | None = None) -> RequestContext:
    """Scope the student did not restate comes from the previous turn; facts outside it stay out."""
    conversation = view.conversation
    if program_id is None and curriculum_id is None and conversation is not None:
        program_id, curriculum_id = conversation.program_id, conversation.curriculum_id
    facts = tuple(f for f in view.facts if (f.program_id, f.curriculum_id) == (program_id, curriculum_id))
    return RequestContext(session_id=view.session_id, request_id=request_id, program_id=program_id,
                          curriculum_id=curriculum_id, facts=facts, conversation=conversation)
