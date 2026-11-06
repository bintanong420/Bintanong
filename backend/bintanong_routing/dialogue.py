"""Bind model-selected dialogue acts to owned turns; every academic request is checked again."""
from .contracts import ConversationContext, DialogueAct, prepare_query, quote_matches

COURSE_REQUESTS = ('check_prerequisite_eligibility', 'list_course_prerequisites',
                   'list_missing_prerequisites', 'list_affected_courses', 'course_facts')


class DialogueReferenceError(ValueError):
    pass


def _standalone_course_request(data, text, context, catalog):
    from .wire import WireInterpretation
    wire = WireInterpretation.parse(data)
    if not wire.operations or wire.previous_course_quote is not None or wire.control is not None:
        return False
    names = {prepare_query(a).casefold() for c in catalog if c.kind == 'course' and c.reviewed
             and (c.program_id, c.curriculum_id) == (context.program_id, context.curriculum_id)
             for a in c.aliases}
    return all(op.name in COURSE_REQUESTS and prepare_query(op.target.text).casefold() in names
               and op.target.occurrence < len(quote_matches(text, op.target.text))
               for op in wire.operations)


def bind_dialogue(data, text, context, catalog, topics=()):
    if not isinstance(data, dict):
        raise ValueError('invalid_dialogue_packet')
    raw = data.get('dialogue')
    if raw is None:
        if context.dialogue is not None:
            if _standalone_course_request(data, text, context, catalog):
                return data, context.model_copy(update={'conversation': None})
            raise DialogueReferenceError('dialogue_reference_missing')
        return data, context
    act = DialogueAct.parse(raw)
    if act.act in ('new_topic', 'switch_topic'):
        if act.turn_id is not None or act.course_id is not None:
            raise DialogueReferenceError('dialogue_reference_missing')
        return data, context.model_copy(update={'conversation': None})
    turn = next((t for t in context.dialogue.turns if t.turn_id == act.turn_id), None) if context.dialogue else None
    if turn is None or turn.truncated:
        raise DialogueReferenceError('dialogue_reference_missing')
    from .wire import WireInterpretation
    WireInterpretation.parse(data)
    saved = turn.context
    if saved is not None and (saved.program_id, saved.curriculum_id) != (context.program_id, context.curriculum_id):
        raise DialogueReferenceError('dialogue_reference_missing')
    candidates = set(turn.course_ids) | ({saved.course_id} if saved and saved.course_id else set())
    course = act.course_id or (saved.course_id if saved else None)
    if act.course_id is not None and act.course_id not in candidates:
        raise DialogueReferenceError('dialogue_reference_missing')
    if act.act != 'refine' and saved is not None and saved.course_id is not None:
        course = saved.course_id  # explaining/correcting the answer keeps its goal, not a mentioned premise
    if course is not None and not any(c.kind == 'course' and c.reviewed and c.entity_id == course
            and (c.program_id, c.curriculum_id) == (context.program_id, context.curriculum_id) for c in catalog):
        raise DialogueReferenceError('dialogue_reference_missing')
    if course is None and candidates:
        raise DialogueReferenceError('dialogue_ambiguous')
    selected = (saved or ConversationContext(program_id=context.program_id,
                                            curriculum_id=context.curriculum_id)).model_copy(update={'course_id': course})
    context = context.model_copy(update={'conversation': selected})
    if selected.subject_id and not data.get('parts') and act.act in ('explain', 'repair', 'answer_clarification'):
        recorded = next((d for d in turn.documents if d.subject_id == selected.subject_id), None)
        offered = next((t for t in topics if t.subject_id == selected.subject_id), None)
        if recorded is None or offered is None or not set(recorded.claims) <= set(offered.claims) | set(offered.not_stated):
            raise DialogueReferenceError('dialogue_reference_missing')
        data = dict(data, route='RAG', control=None, ambiguities=[], part_count=1, operations=[],
            parts=[dict(part_id='r1', quote=dict(text=text, occurrence=0), evidence_need='document',
                operation_indices=[], subject_id=recorded.subject_id, requested_claims=list(recorded.claims),
                detail=recorded.detail)])
    # The act selects a request, never its old conclusion. Current quoted claims stay intact.
    operations = data.get('operations', ())
    operation = (operations[0]['name'] if len(operations) == 1 and operations[0]['name'] in COURSE_REQUESTS
                 else selected.operation if not operations else None)
    if operation in COURSE_REQUESTS and course is not None:
        if any(p.get('subject_id') for p in data.get('parts', ())):
            return data, context
        if len(text) > 4096:
            raise DialogueReferenceError('dialogue_reference_missing')
        quote = dict(text=text, occurrence=0)
        data = dict(data, route='Symbolic', control=None, ambiguities=[], part_count=1,
            previous_course_quote=quote, operations=[dict(name=operation, target=quote)],
            parts=[dict(part_id='r1', quote=quote, evidence_need='structured', operation_indices=[0])])
    return data, context
