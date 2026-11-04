"""Compiled routing (owner, 4 Nov 2026: "the router itself is the problem, due to how it is implemented").

Each wire reply below has the exact shape of a recorded live router output (audit-evidence
p12-common-queries-20261030: dsa2/dsa, img18, memory3, codex-evidence, gui-cc4, understanding, nottaken), rewritten
onto two synthetic curricula with unfamiliar codes. With BINTANONG_ROUTER_COMPILE=1 the host reads the reply for
meaning and rebuilds the structure; no program or course is named in the code under test."""
import asyncio
import json

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_private_context.conversation import capture
from backend.bintanong_routing.compile import compile_reply, read_meaning
from backend.bintanong_routing.contracts import CatalogEntry, ConversationContext, DocumentTopic, RequestContext
from backend.bintanong_routing.router import Router
from test_routing_router import FakeTransport, style_proposal

CURRICULA = {
    # key: program, curriculum, program name, main course (typed, entity, aliases), second, initials of main
    'x': dict(program='program-x', curriculum='curriculum-x', name='ZQX', long='Zeta Quill Studies',
              main=('ZQ4/L', 'course-x4', ('ZQ 4/L', 'ZQ4/L', 'ZQ 4', 'ZQ4', 'Quill Rune Shapes', 'QRS')),
              second=('ZQ1/L', 'course-x1', ('ZQ 1/L', 'ZQ1/L', 'ZQ 1', 'ZQ1')), other='PROGZW'),
    'y': dict(program='program-y', curriculum='curriculum-y', name='MRV', long='Marrow Vale Arts',
              main=('MRV-3/L', 'course-y3', ('MRV-3/L', 'MRV-3', 'Tarn Kettle Slopes', 'TKS')),
              second=('MRV-2/L', 'course-y2', ('MRV-2/L', 'MRV-2')), other='PROGVW'),
}
INITIALS = {'x': 'QRS', 'y': 'TKS'}
OPS = ('check_prerequisite_eligibility', 'list_missing_prerequisites', 'list_affected_courses', 'course_facts')
REGISTRY = CapabilityRegistry({**{op: Capability('synthetic_' + op, ('curriculum_id', 'course_id')) for op in OPS},
    **{op: Capability('synthetic_' + op, ('curriculum_id', 'year_level', 'semester'))
       for op in ('list_term_courses', 'assess_term_prerequisites')}})
POLICY = DocumentTopic(subject_id='fictional_prereq_policy', claims=('printed prerequisite policy fields',))
SHIFTING = DocumentTopic(subject_id='handbook_shifting', claims=('printed shifting fields',))
TRANSFER_IN = DocumentTopic(subject_id='fictional_transfer_in', claims=('printed transfer fields',),
                            family='transferring_into_palsu')
TRANSFER_OUT = DocumentTopic(subject_id='fictional_transfer_out', claims=('printed leaving fields',),
                             family='leaving_palsu_transfer_credentials')
TOPICS = (POLICY, SHIFTING, TRANSFER_IN, TRANSFER_OUT)


def entry(kind, entity, program, curriculum, aliases, code=None):
    value = dict(kind=kind, entity_id=entity, program_id=program, curriculum_id=curriculum, aliases=list(aliases),
                 source_ref='ver-a', review_ref='review-a', reviewed=True)
    if code:
        value['course_code'] = code
    return CatalogEntry.parse(value)


def catalog():
    entries = []
    for c in CURRICULA.values():
        entries += [entry('program', c['program'], c['program'], None, (c['name'], c['long'])),
                    entry('curriculum', c['curriculum'], c['program'], c['curriculum'], ('Edition ' + c['name'],))]
        for _, entity, aliases in (c['main'], c['second']):
            entries.append(entry('course', entity, c['program'], c['curriculum'], aliases, aliases[0]))
        other = c['other']
        entries.append(entry('program', other.lower(), other.lower(), None, (other,)))
        entries.append(entry('curriculum', other.lower() + '-ed', other.lower(), other.lower() + '-ed', ('Ed ' + other,)))
    return tuple(entries)


def quote(text, occurrence=0):
    return dict(text=text, occurrence=occurrence)


def part(part_id, words, need, indices=(), subject=None, claims=(), occurrence=0):
    return dict(part_id=part_id, quote=quote(words, occurrence), evidence_need=need, operation_indices=list(indices),
                subject_id=subject, requested_claims=list(claims), detail='whole')


def wire(*, parts, mentions=(), claims=(), operations=(), control=None, route='Symbolic', part_count=None,
         language='taglish', previous=None):
    value = dict(schema_version='bintanong-interpretation-wire-v4', language=language, audience='undergraduate',
                 control=control, part_count=len(parts) if part_count is None else part_count, parts=list(parts),
                 intent='request', mentions=[dict(kind=k, quote=quote(w, n)) for k, w, n in mentions],
                 claims=list(claims), operations=list(operations), route=route, ambiguities=[])
    if previous is not None:
        value['previous_course_quote'] = quote(previous)
    return value


def context(key=None, conversation=None, scoped=True):
    c = CURRICULA[key] if key else None
    return RequestContext.parse(dict(session_id='sess-a', request_id='req-a',
        program_id=c['program'] if c and scoped else None, curriculum_id=c['curriculum'] if c and scoped else None,
        facts=[], conversation=None if conversation is None else conversation.model_dump(mode='json')))


def route(text, value, ctx, monkeypatch, *, compiled=True):
    if compiled:
        monkeypatch.setenv('BINTANONG_ROUTER_COMPILE', '1')
    else:
        monkeypatch.delenv('BINTANONG_ROUTER_COMPILE', raising=False)
    raw = json.dumps(value)
    style = json.dumps(style_proposal('en', english=[text.split()[0]], filipino=[]))
    transport = FakeTransport(raw, raw, style_outputs=[style, style])
    router = Router(transport, catalog=catalog(), registry=REGISTRY, documents_available=True, synthetic=True,
                    topics=TOPICS)
    return asyncio.run(router.route(text, ctx))


def predicate(result):
    request = result.decision.predicate_request
    return (request.predicate, {i.name: i.value for i in request.inputs}.get('course_id')) if request else None


CURRICULUM_KEYS = pytest.mark.parametrize('key', sorted(CURRICULA))


@CURRICULUM_KEYS
def test_dsa_operation_index_slip_beside_a_stray_topic_compiles_to_the_dependency_check(key, monkeypatch):
    """run-837646b3-dsa2: operation_indices [1] with one operation, and a topic on the structured part."""
    init = INITIALS[key]
    text = f'What subjects ang hindi ko matake if nabagsak ko {init}?'
    value = wire(parts=[part('r1', text, 'structured', [1], POLICY.subject_id, POLICY.claims)],
                 mentions=[('course', init, 0)], operations=[dict(name='list_affected_courses', target=quote(init))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert predicate(result) == ('list_affected_courses', CURRICULA[key]['main'][1])


def img18_text(key):
    c = CURRICULA[key]
    return f"Pwede ko bang i-take ang {c['main'][0]} next sem?\n\nHindi pa ako passed sa {c['second'][0]}."


@CURRICULUM_KEYS
@pytest.mark.parametrize('split', [False, True])
def test_a_grade_statement_part_repeating_the_check_qualifies_it(key, split, monkeypatch):
    """run-72b0755b-img18 (one part) and run-32d46805-memory3 (statement split into its own part with [0])."""
    c = CURRICULA[key]
    text = img18_text(key)
    first, statement = f"Pwede ko bang i-take ang {c['main'][0]} next sem?", f"Hindi pa ako passed sa {c['second'][0]}."
    parts = ([part('r1', first, 'structured', [0]), part('r2', statement, 'structured', [0], occurrence=1)] if split
             else [part('r1', text, 'structured', [0], POLICY.subject_id, POLICY.claims)])
    value = wire(parts=parts, mentions=[('course', c['main'][0], 0), ('course', c['second'][0], 1)],
                 claims=[dict(quote=quote(statement, 1), entity=quote(c['second'][0], 1), state='failed', mode='asserted')],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated'
    assert predicate(result) == ('check_prerequisite_eligibility', c['main'][1])
    assert [f.course_id for f in result.claims] == [c['second'][1]]
    assert len(result.proposed.parts) == 1


@CURRICULUM_KEYS
@pytest.mark.parametrize('long', [False, True])
def test_a_bare_program_name_with_a_placeholder_part_asks_what_to_know(key, long, monkeypatch):
    """run-63c6e3a4 cx-bare-bscs / cx-bare-cs: part_count 0 with one unknown placeholder part."""
    c = CURRICULA[key]
    text = c['long'] if long else c['name']
    value = wire(parts=[dict(part_id='r1', quote=quote(text), evidence_need='unknown', operation_indices=[])],
                 part_count=0, mentions=[('program', text, 0)], route='RAG', language='en')
    result = route(text, value, context(), monkeypatch)
    assert result.compiled and result.diagnostic == 'bare_program_name'
    assert result.decision.missing_facts == ('program_topic:' + c['program'],)


@CURRICULUM_KEYS
def test_a_failed_course_claim_attached_to_a_program_is_no_fact_and_shifting_is_answered(key, monkeypatch):
    """run-63c6e3a4 cx-shift: the check and the failure both targeted the destination program."""
    other = CURRICULA[key]['other']
    text = f'Pwede ba akong mag-shift sa {other} kasi bagsak ako?'
    value = wire(parts=[part('r1', text, 'structured', [0], SHIFTING.subject_id, SHIFTING.claims)],
                 mentions=[('program', other, 0)], route='Hybrid',
                 claims=[dict(quote=quote('bagsak ako'), entity=quote(other), state='failed', mode='asserted')],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(other))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated' and result.decision.route == 'RAG'
    assert result.claims == () and result.decision.predicate_request is None
    assert [p.subject_id for p in result.proposed.parts] == ['handbook_shifting']


@CURRICULUM_KEYS
@pytest.mark.parametrize('filipino', [False, True])
def test_a_statement_only_message_is_noted(key, filipino, monkeypatch):
    """cx-statement ("I passed CC 5/L." with a trailing-period mention, route RAG) and cx-statement-fil (part_count 0,
    no mentions, the entity typed without spacing)."""
    c = CURRICULA[key]
    code = c['main'][2][1]  # the no-space printed form
    text = f'Pasado na ako sa {code}.' if filipino else f'I passed {code}.'
    if filipino:
        value = wire(parts=[dict(part_id='r1', quote=quote(text), evidence_need='unknown', operation_indices=[],
                                 subject_id=None, requested_claims=[], detail='whole')], part_count=0, route='RAG',
                     claims=[dict(quote=quote(text), entity=quote(code), state='passed', mode='asserted')])
    else:
        value = wire(parts=[part('r1', text, 'structured')], route='RAG', mentions=[('course', code + '.', 0)],
                     claims=[dict(quote=quote(text), entity=quote(code + '.'), state='passed', mode='asserted')])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'facts_noted'
    assert result.decision.missing_facts == (f"noted_passed:{c['main'][1]}",)


@CURRICULUM_KEYS
def test_a_dependency_check_with_a_topicless_recovery_part_is_one_recovery_request(key, monkeypatch):
    """run-56c967f3 gui-cc4: index [1] and a document part with no topic."""
    c = CURRICULA[key]
    first = f"Anong subs ang affected if I fail {c['main'][0]}"
    text = first + ' tapos paano ko sya maresolve?'
    value = wire(parts=[part('r1', first, 'structured', [1]), part('r2', 'tapos paano ko sya maresolve?', 'document')],
                 mentions=[('course', c['main'][0], 0)], route='Hybrid',
                 operations=[dict(name='list_affected_courses', target=quote(c['main'][0]))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert predicate(result) == ('list_affected_courses', c['main'][1])


@CURRICULUM_KEYS
def test_a_clarify_control_naming_a_check_and_course_becomes_that_check(key, monkeypatch):
    """run-56c967f3 und-iffail-followup: "If I fail CC1/L?" after an affected-courses answer; control clarify,
    language unknown, previous_course_quote on the named course, no mentions."""
    c = CURRICULA[key]
    code = c['second'][0]
    text = f'If I fail {code}?'
    memory = ConversationContext(program_id=c['program'], curriculum_id=c['curriculum'], course_id=c['main'][1],
                                 operation='list_affected_courses')
    value = wire(parts=[part('r1', text, 'structured', [0])], control='clarify', route=None, language='unknown',
                 previous=code, operations=[dict(name='list_affected_courses', target=quote(code))])
    result = route(text, value, context(key, memory), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated'
    assert predicate(result) == ('list_affected_courses', c['second'][1])


@CURRICULUM_KEYS
def test_a_follow_up_naming_only_a_course_repeats_the_previous_check(key, monkeypatch):
    """The same follow-up when the model asked nothing at all (control clarify, no operation)."""
    c = CURRICULA[key]
    text = f"If I fail {c['second'][0]}?"
    memory = ConversationContext(program_id=c['program'], curriculum_id=c['curriculum'], course_id=c['main'][1],
                                 operation='list_affected_courses')
    value = wire(parts=[], control='clarify', route=None, language='en')
    result = route(text, value, context(key, memory), monkeypatch)
    assert result.compiled and predicate(result) == ('list_affected_courses', c['second'][1])


@CURRICULUM_KEYS
def test_an_eligibility_check_aimed_at_an_ordinary_word_uses_the_named_course(key, monkeypatch):
    """run-56c967f3 und-uses-as-prereq: the check targeted "Anything"; a document part and a stray topic."""
    c = CURRICULA[key]
    code = c['second'][0]
    first = f'What do the reviewed institutional sources say about retaking {code}?'
    second = f'Can I take Anything that uses {code} as pre-req under my selected curriculum? Please check the reviewed prerequisite rules.'
    text = first + ' ' + second
    value = wire(parts=[part('r1', first, 'document', (), POLICY.subject_id, POLICY.claims),
                        part('r2', second, 'structured', [0], POLICY.subject_id, POLICY.claims, occurrence=1)],
                 mentions=[('course', code, 0)], route='Hybrid', language='en',
                 operations=[dict(name='check_prerequisite_eligibility', target=quote('Anything', 1))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated' and result.decision.route == 'Hybrid'
    # The question asks which courses use the named one as a prerequisite: its dependency check.
    assert predicate(result) == ('list_affected_courses', c['second'][1])
    assert [(p.evidence_need, p.subject_id) for p in result.proposed.parts] == [
        ('document', POLICY.subject_id), ('structured', None)]


@CURRICULUM_KEYS
@pytest.mark.parametrize('aimed_at_course', [False, True])
def test_a_term_check_for_a_named_course_checks_that_course(key, aimed_at_course, monkeypatch):
    """run-3b5acdd8 nottaken: assess_term_prerequisites on "next semester" (s006) or on the course itself (s018)."""
    c = CURRICULA[key]
    main, second = c['main'][0], c['second'][0]
    text = f"Can I take {main} next semester? I haven't taken {second} yet."
    target = main if aimed_at_course else 'next semester'
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en',
                 mentions=[('course', main, 0), ('course', second, 0), ('term', 'next semester', 0)],
                 claims=[dict(quote=quote(f"I haven't taken {second} yet."), entity=quote(second),
                              state='not_taken', mode='asserted')],
                 operations=[dict(name='assess_term_prerequisites', target=quote(target))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated'
    assert predicate(result) == ('check_prerequisite_eligibility', c['main'][1])
    assert [(f.course_id, f.state) for f in result.claims] == [(c['second'][1], 'not_taken')]


@CURRICULUM_KEYS
def test_a_shifting_follow_up_about_transferred_units_stays_on_shifting(key, monkeypatch):
    """Open bug (live ca82cc22): "ilang units ang mate-transfer?" after a shifting answer was read as a transfer
    topic and asked whether the student is leaving PalSU."""
    c = CURRICULA[key]
    text = 'ilang units ang mate-transfer?'
    memory = ConversationContext(program_id=c['program'], curriculum_id=c['curriculum'], subject_id='handbook_shifting')
    value = wire(parts=[part('r1', text, 'document', (), TRANSFER_IN.subject_id, TRANSFER_IN.claims)], route='RAG')
    before = route(text, value, context(key, memory), monkeypatch, compiled=False)
    assert before.diagnostic == 'transfer_direction_unstated'
    result = route(text, value, context(key, memory), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated' and result.decision.route == 'RAG'
    assert [(p.subject_id, p.requested_claims) for p in result.proposed.parts] == [
        ('handbook_shifting', SHIFTING.claims)]


@CURRICULUM_KEYS
def test_a_transfer_question_naming_a_direction_after_shifting_keeps_its_topic(key, monkeypatch):
    c = CURRICULA[key]
    text = 'How do I transfer out to another school?'
    memory = ConversationContext(program_id=c['program'], curriculum_id=c['curriculum'], subject_id='handbook_shifting')
    value = wire(parts=[part('r1', text, 'document', (), TRANSFER_OUT.subject_id, TRANSFER_OUT.claims)], route='RAG',
                 language='en')
    result = route(text, value, context(key, memory), monkeypatch)
    assert result.compiled and [p.subject_id for p in result.proposed.parts] == [TRANSFER_OUT.subject_id]


@CURRICULUM_KEYS
def test_a_bare_program_name_then_subjects_keeps_the_program_and_asks_the_term(key, monkeypatch):
    """Open bug (live ca82cc22): "Computer Science" then "yung subjects" ended in a bare clarification."""
    c = CURRICULA[key]
    first = wire(parts=[dict(part_id='r1', quote=quote(c['long']), evidence_need='unknown', operation_indices=[])],
                 part_count=0, mentions=[('program', c['long'], 0)], route='RAG', language='en')
    memory = capture(route(c['long'], first, context(), monkeypatch))
    assert memory is not None and memory.program_id == c['program']
    text = 'yung subjects'
    reply = wire(parts=[], control='clarify', route=None)
    result = route(text, reply, context(None, memory), monkeypatch)
    assert result.compiled and result.diagnostic == 'missing_term' and result.decision.missing_facts == ('term',)
    assert result.program_id == c['program']
    named = route(text + ' sa first year first sem', reply, context(None, memory), monkeypatch)
    assert named.diagnostic == 'validated' and named.decision.predicate_request.predicate == 'list_term_courses'


@CURRICULUM_KEYS
def test_a_code_not_in_the_curriculum_asks_for_the_printed_code(key, monkeypatch):
    """A code-like target that matches nothing is never swapped for another course named in the message."""
    c = CURRICULA[key]
    text = f"Can I take QQ 999 after {c['main'][0]}?"
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en',
                 mentions=[('course', 'QQ 999', 0), ('course', c['main'][0], 0)],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote('QQ 999'))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'unresolved_entity'
    assert result.decision.missing_facts == ('course_id',)


@CURRICULUM_KEYS
def test_a_course_of_another_curriculum_is_not_a_target(key, monkeypatch):
    other = CURRICULA['y' if key == 'x' else 'x']['main'][0]
    text = f'Can I take {other}?'
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en', mentions=[('course', other, 0)],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(other))])
    result = route(text, value, context(key), monkeypatch)
    assert result.decision.predicate_request is None and result.diagnostic == 'unresolved_entity'


@CURRICULUM_KEYS
def test_a_reported_result_about_someone_else_is_no_fact(key, monkeypatch):
    c = CURRICULA[key]
    text = f"Can I take {c['main'][0]}? My friend failed {c['second'][0]}."
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en',
                 mentions=[('course', c['main'][0], 0), ('course', c['second'][0], 0)],
                 claims=[dict(quote=quote(f"My friend failed {c['second'][0]}."), entity=quote(c['second'][0]),
                              state='failed', mode='reported')],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    result = route(text, value, context(key), monkeypatch)
    assert result.compiled and result.diagnostic == 'validated' and result.claims == ()


def test_flag_off_never_compiles(monkeypatch):
    c = CURRICULA['x']
    text = f"Can I take {c['main'][0]}?"
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en', mentions=[('course', c['main'][0], 0)],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    result = route(text, value, context('x'), monkeypatch, compiled=False)
    assert not result.compiled and result.diagnostic == 'validated'


def test_an_uncompilable_reply_falls_back_to_the_existing_path(monkeypatch):
    c = CURRICULA['x']
    text = f"Can I take {c['main'][0]}?"
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en', mentions=[('course', c['main'][0], 0)],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    value['operations'].append(dict(name='list_term_courses', target=quote('a term the message never says')))
    with pytest.raises(ValueError):
        compile_reply(value, text, context('x'), catalog(), TOPICS)
    result = route(text, value, context('x'), monkeypatch)
    assert not result.compiled


def test_meaning_ignores_structure_fields():
    text = 'Can I take ZQ4/L?'
    a = wire(parts=[part('r1', text, 'structured', [3])], part_count=0, route='RAG',
             operations=[dict(name='check_prerequisite_eligibility', target=quote('ZQ4/L', 7))])
    b = wire(parts=[part('r1', text, 'structured', [0])], route='Symbolic',
             operations=[dict(name='check_prerequisite_eligibility', target=quote('ZQ4/L'))])
    assert read_meaning(a, text) == read_meaning(b, text)


@CURRICULUM_KEYS
def test_a_second_structured_question_without_a_check_is_not_discarded(key):
    c = CURRICULA[key]
    first = f"Can I take {c['main'][0]}?"
    second = f"Can I take {c['second'][0]}?"
    text = first + ' ' + second
    value = wire(parts=[part('r1', first, 'structured', [0]), part('r2', second, 'structured')],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    with pytest.raises(ValueError, match='compile_unbound_structured_part'):
        compile_reply(value, text, context(key), catalog(), TOPICS)


@CURRICULUM_KEYS
@pytest.mark.parametrize('terminal', ['greeting', 'unsupported_scope'])
def test_terminal_controls_keep_the_existing_parser_guards(key, terminal):
    value = wire(parts=[], control=terminal)
    with pytest.raises(ValueError, match='compile_terminal_left_to_existing_path'):
        compile_reply(value, 'Hello', context(key), catalog(), TOPICS)


@CURRICULUM_KEYS
def test_a_previous_course_quote_without_memory_is_not_a_new_target(key):
    c = CURRICULA[key]
    text = f"Can I take {c['main'][0]}?"
    value = wire(parts=[part('r1', text, 'structured', [0])], previous=c['main'][0],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    with pytest.raises(ValueError, match='course_reference_unavailable'):
        compile_reply(value, text, context(key), catalog(), TOPICS)


@pytest.mark.parametrize('subject,claims', [('unoffered', POLICY.claims),
                                           (POLICY.subject_id, ('invented condition',))])
def test_a_document_topic_or_claim_outside_the_menu_is_not_dropped(subject, claims):
    text = 'What does that policy require?'
    value = wire(parts=[part('r1', text, 'document', (), subject, claims)], route='RAG')
    with pytest.raises(ValueError, match='topic_outside_menu'):
        compile_reply(value, text, context('x'), catalog(), TOPICS)


@CURRICULUM_KEYS
def test_mentions_follow_message_order_and_keep_claim_and_target_bindings(key):
    c = CURRICULA[key]
    statement = f"I passed {c['second'][0]}."
    text = statement + f" Can I take {c['main'][0]}?"
    value = wire(parts=[part('r1', text, 'structured', [0])],
                 claims=[dict(quote=quote(statement), entity=quote(c['second'][0]), state='passed', mode='asserted')],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))])
    result = compile_reply(value, text, context(key), catalog(), TOPICS)
    assert [m.start for m in result.mentions] == sorted(m.start for m in result.mentions)
    assert result.mentions[result.operations[0].target].text == c['main'][0]
    assert result.mentions[result.claims[0].entity].text == c['second'][0]


@pytest.mark.parametrize('value', [{}, {'language': 'en'}, {'schema_version': 'retired-wire', 'control': 'clarify'}])
def test_compiler_requires_the_current_wire_protocol(value):
    with pytest.raises(ValueError, match='compile_unsupported_schema'):
        read_meaning(value, 'Hello')


@pytest.mark.parametrize('field', ['requested_claims', 'ambiguities'])
def test_malformed_meaning_collections_fall_back_instead_of_crashing(field, monkeypatch):
    value = wire(parts=[part('r1', 'Hello', 'document')])
    if field == 'requested_claims':
        value['parts'][0][field] = 1
    else:
        value[field] = 1
    with pytest.raises(ValueError):
        read_meaning(value, 'Hello')
    result = route('Hello', value, context('x'), monkeypatch)
    assert not result.compiled and result.diagnostic == 'invalid_model_output'


def test_two_questions_about_one_topic_keep_both_requested_claims():
    menu = (DocumentTopic(subject_id='fictional_service', claims=('required documents', 'printed fee')),)
    first, second = 'What documents do I need?', 'How much is the fee?'
    text = first + ' ' + second
    value = wire(parts=[part('r1', first, 'document', (), menu[0].subject_id, ('required documents',)),
                        part('r2', second, 'document', (), menu[0].subject_id, ('printed fee',))], route='RAG')
    result = compile_reply(value, text, context('x'), catalog(), menu)
    assert [p.text for p in result.parts] == [first, second]
    assert [p.requested_claims for p in result.parts] == [('required documents',), ('printed fee',)]


@CURRICULUM_KEYS
def test_a_result_beside_a_second_question_does_not_hide_the_missing_check(key):
    c = CURRICULA[key]
    first = f"Can I take {c['main'][0]}?"
    statement = f"I passed {c['second'][0]}."
    second = statement + f" Can I take {c['second'][0]}?"
    text = first + ' ' + second
    value = wire(parts=[part('r1', first, 'structured', [0]), part('r2', second, 'structured')],
                 operations=[dict(name='check_prerequisite_eligibility', target=quote(c['main'][0]))],
                 claims=[dict(quote=quote(statement), entity=quote(c['second'][0]), state='passed', mode='asserted')])
    with pytest.raises(ValueError, match='compile_unbound_structured_part'):
        compile_reply(value, text, context(key), catalog(), TOPICS)


@CURRICULUM_KEYS
def test_an_unknown_course_title_is_not_the_previous_course(key, monkeypatch):
    c = CURRICULA[key]
    text = 'Can I take Watercolor Studio?'
    memory = ConversationContext(program_id=c['program'], curriculum_id=c['curriculum'], course_id=c['main'][1],
                                 operation='check_prerequisite_eligibility')
    value = wire(parts=[part('r1', text, 'structured', [0])], language='en',
                 operations=[dict(name='check_prerequisite_eligibility', target=quote('Watercolor Studio'))])
    result = route(text, value, context(key, memory), monkeypatch)
    assert result.decision.predicate_request is None
    assert result.diagnostic == 'unresolved_entity'
