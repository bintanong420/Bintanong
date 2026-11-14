"""One bounded projection of owned dialogue; its text supplies intent, never academic facts."""
from ..bintanong_routing.contracts import DialogueContext, DialogueTurn
from .memory import turn_ref


def compile_context(view, program_id, curriculum_id):
    eligible = [e for e in view.dialogue.exchanges
                if (e.program_id, e.curriculum_id) == (program_id, curriculum_id)]
    if not eligible:
        return None
    pending = view.dialogue.unresolved
    origin = next((e for e in eligible if pending and e.message_id == pending.originating_message_id), None)
    selected = eligible[-4:]
    if origin is not None and origin not in selected:
        selected = [origin, *selected[-3:]]
    # Keep whole exchanges. Never clip a negation/condition to make a request appear answerable.
    while sum(len((e.user_text+e.assistant_text).encode('utf-8')) for e in selected) > 16384:
        removable = next((e for e in selected if e is not origin), None)
        if removable is None:
            return None
        selected.remove(removable)
    return DialogueContext(session_id=view.session_id, revision=view.dialogue.revision,
        turns=tuple(DialogueTurn(turn_id=turn_ref(e.message_id), user_text=e.user_text,
            assistant_text=e.assistant_text, context=e.context,
            course_ids=tuple(c.entity_id for c in e.entities if c.kind == 'course'), documents=e.documents,
            truncated=e.text_truncated) for e in selected),
        pending_turn_id=turn_ref(origin.message_id) if origin else None,
        missing_slots=pending.missing_slots if origin else ())
