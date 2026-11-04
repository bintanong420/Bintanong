"""Bind model-selected dialogue acts to owned turns; every academic request is checked again."""
from .contracts import ConversationContext, DialogueAct

COURSE_REQUESTS = ('check_prerequisite_eligibility', 'list_course_prerequisites',
                   'list_missing_prerequisites', 'list_affected_courses', 'course_facts')


class DialogueReferenceError(ValueError):
    pass


def bind_dialogue(data, text, context, catalog, topics=()):
    raw = data.get('dialogue')
    if raw is None:
        return data, context
    act = DialogueAct.parse(raw)
    if act.act in ('new_topic', 'switch_topic'):
        if act.turn_id is not None or act.course_id is not None:
            raise DialogueReferenceError('dialogue_reference_missing')
        return data, context.model_copy(update={'conversation': None})
    turn = next((t for t in context.dialogue.turns if t.turn_id == act.turn_id), None) if context.dialogue else None
    if turn is None or turn.truncated:
        raise DialogueReferenceError('dialogue_reference_missing')
    saved = turn.context
    if saved is not None and (saved.program_id, saved.curriculum_id) != (context.program_id, context.curriculum_id):
        raise DialogueReferenceError('dialogue_reference_missing')
    candidates = set(turn.course_ids) | ({saved.course_id} if saved and saved.course_id else set())
    course = act.course_id or (saved.course_id if saved else None)
    if act.course_id is not None and act.course_id not in candidates:
        raise DialogueReferenceError('dialogue_reference_missing')
    if course is not None and not any(c.kind == 'course' and c.reviewed and c.entity_id == course
            and (c.program_id, c.curriculum_id) == (context.program_id, context.curriculum_id) for c in catalog):
        raise DialogueReferenceError('dialogue_reference_missing')
    if course is None and candidates:
        raise DialogueReferenceError('dialogue_ambiguous')
    selected = (saved or ConversationContext(program_id=context.program_id,
                                            curriculum_id=context.curriculum_id)).model_copy(update={'course_id': course})
    context = context.model_copy(update={'conversation': selected})
    # The act selects a request, never its old conclusion. Current quoted claims stay intact.
    if selected.operation in COURSE_REQUESTS and course is not None and (
            not data.get('operations') or act.act == 'answer_clarification'):
        if any(p.get('subject_id') for p in data.get('parts', ())):
            return data, context
        if len(text) > 4096:
            raise DialogueReferenceError('dialogue_reference_missing')
        quote = dict(text=text, occurrence=0)
        data = dict(data, route='Symbolic', control=None, ambiguities=[], part_count=1,
            previous_course_quote=quote, operations=[dict(name=selected.operation, target=quote)],
            parts=[dict(part_id='r1', quote=quote, evidence_need='structured', operation_indices=[0])])
    return data, context
