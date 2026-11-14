"""Compiled routing (owner, 4 Nov 2026: "the router itself is the problem, due to how it is implemented").

The router model's wire reply is read for meaning only: which checks and document topics were asked for, the
course/term words involved, stated results, control and language. Offsets, occurrence counts, part_count,
operation_indices and the route label are ignored; the host rebuilds the structure from the message text and the
reviewed catalog, so a small structural slip no longer refuses the whole message. The output is the ordinary
Interpretation that validation already checks; nothing here names a program or course.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import TERM_OPERATIONS, Interpretation, RequestContext, prepare_query, quote_matches
from .terms import parse_term
from .recovery_cue import recovery_follow_up

COURSE_OPERATIONS = ('check_prerequisite_eligibility', 'list_course_prerequisites', 'list_missing_prerequisites',
                     'list_affected_courses', 'course_facts')
_STATES = ('passed', 'failed', 'not_passed', 'not_taken', 'taken_unknown', 'enrolled', 'not_enrolled')
_MODES = ('asserted', 'hypothetical', 'reported')
_DETAILS = ('whole', 'requirements', 'fees', 'processing_time', 'specific')
_LANGUAGES = ('en', 'fil', 'taglish', 'unknown')
_AUDIENCES = ('undergraduate', 'excluded', 'unrelated', 'unknown')
MAX_PART_TEXT = 4096


@dataclass(frozen=True)
class Check:
    name: str
    target: str | None


@dataclass(frozen=True)
class Topic:
    subject_id: str | None  # None: a document question the model gave no reviewed topic
    claims: tuple[str, ...]
    detail: str
    quote: str | None
    with_check: bool  # the model put the topic on a structured part (a stray topic beside a check)


@dataclass(frozen=True)
class Stated:
    quote: str | None
    entity: str
    state: str
    mode: str


@dataclass(frozen=True)
class Meaning:
    language: str
    audience: str
    control: str | None
    intent: str
    checks: tuple[Check, ...]
    topics: tuple[Topic, ...]
    claims: tuple[Stated, ...]
    mentions: tuple[tuple[str, str], ...]  # (kind, words)
    part_quotes: tuple[str, ...]
    structured_quotes: tuple[str, ...]
    previous_course: str | None
    ambiguities: tuple[str, ...]


def _words(value):
    """The words of a quote object ({"text": ...}) or a bare string; None when absent or malformed."""
    if isinstance(value, dict):
        value = value.get('text')
    return value if isinstance(value, str) and value.strip() else None


def _items(data, name):
    value = data.get(name, [])
    if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
        raise ValueError('compile_malformed_collection')
    return value


def read_meaning(wire, text: str) -> Meaning:
    """The meaning of a router reply (a parsed JSON object or a WireInterpretation). Structure is not trusted."""
    prepare_query(text)
    data = wire.model_dump(mode='json') if hasattr(wire, 'model_dump') else wire
    if not isinstance(data, dict):
        raise ValueError('compile_unreadable_reply')
    if data.get('schema_version') != 'bintanong-interpretation-wire-v4':
        raise ValueError('compile_unsupported_schema')
    checks = []
    for op in _items(data, 'operations'):
        name = op.get('name')
        if isinstance(name, str) and re.fullmatch(r'[a-z][a-z0-9_]*', name) and len(name) <= 64:
            check = Check(name, _words(op.get('target')))
            if check not in checks:
                checks.append(check)
    topics, quotes, structured = [], [], []
    for part in _items(data, 'parts'):
        quote = _words(part.get('quote')) or _words(part.get('text'))
        if quote:
            quotes.append(quote)
            if part.get('evidence_need') == 'structured':
                structured.append(quote)
        need = part.get('evidence_need')
        subject = part.get('subject_id') if isinstance(part.get('subject_id'), str) else None
        requested = part.get('requested_claims', [])
        if not isinstance(requested, list) or any(not isinstance(c, str) for c in requested):
            raise ValueError('compile_malformed_collection')
        claims = tuple(c for c in requested if c)
        detail = part.get('detail') if part.get('detail') in _DETAILS else 'whole'
        if subject is not None and claims:
            topics.append(Topic(subject, claims, detail, quote, need == 'structured'))
        elif need == 'document':
            topics.append(Topic(None, (), 'whole', quote, False))
    claims = []
    for claim in _items(data, 'claims'):
        entity, state, mode = _words(claim.get('entity')), claim.get('state'), claim.get('mode')
        if entity and state in _STATES and mode in _MODES:
            claims.append(Stated(_words(claim.get('quote')), entity, state, mode))
    mentions = tuple((m.get('kind'), _words(m.get('quote')) or _words(m.get('text'))) for m in _items(data, 'mentions')
                     if m.get('kind') in ('program', 'curriculum', 'course', 'term')
                     and (_words(m.get('quote')) or _words(m.get('text'))))
    control = data.get('control') if isinstance(data.get('control'), str) else None
    intent = data.get('intent') if isinstance(data.get('intent'), str) and data.get('intent').strip() else 'request'
    if (control == 'clarify' and not checks and
            {p.get('evidence_need') for p in _items(data, 'parts')} == {'unknown', 'document'}):
        intent = 'system_information_mixed'
    raw_ambiguities = data.get('ambiguities', [])
    if not isinstance(raw_ambiguities, list) or any(not isinstance(a, str) for a in raw_ambiguities):
        raise ValueError('compile_malformed_collection')
    ambiguities = tuple(a for a in raw_ambiguities if a.strip())
    return Meaning(language=data.get('language') if data.get('language') in _LANGUAGES else 'unknown',
                   audience=data.get('audience') if data.get('audience') in _AUDIENCES else 'unknown',
                   control=control, intent=intent[:240], checks=tuple(checks), topics=tuple(topics),
                   claims=tuple(claims), mentions=mentions, part_quotes=tuple(quotes), structured_quotes=tuple(structured),
                   previous_course=_words(data.get('previous_course_quote')), ambiguities=ambiguities[:16])


def _key(words):
    return prepare_query(words).casefold()


def _trimmed_keys(words):
    keys = {_key(words)}
    trimmed = words.strip().rstrip('.,;:!?')
    if trimmed:
        keys.add(_key(trimmed))
    return keys


@dataclass(frozen=True)
class Found:
    start: int
    end: int
    entries: tuple  # the reviewed course entries these words name (several: the student must choose)


def _scope(meaning, context, catalog):
    program, curriculum = context.program_id, context.curriculum_id
    previous = context.conversation
    if curriculum is None and previous is not None and program in (None, previous.program_id):
        program, curriculum = previous.program_id or program, previous.curriculum_id
    if curriculum is None:
        named = [c for kind, words in meaning.mentions if kind == 'curriculum' for c in catalog
                 if c.kind == 'curriculum' and _key(words) in {_key(a) for a in c.aliases}
                 and program in (None, c.program_id)]
        if len({c.entity_id for c in named}) == 1:
            program, curriculum = named[0].program_id, named[0].entity_id
    if program is not None and curriculum is None:
        editions = [c for c in catalog if c.kind == 'curriculum' and c.program_id == program]
        if len(editions) == 1:
            curriculum = editions[0].entity_id
    return program, curriculum


def find_courses(text, courses, named=frozenset()):
    """Every reviewed course name in the message, longest first and never overlapping. Printed codes (with a digit)
    are found case-insensitively; titles and initials only when the model also named those words, so an ordinary
    word is never read as a course."""
    hits = {}
    for entry in courses:
        for alias in entry.aliases:
            if not any(ch.isdigit() for ch in alias) and _key(alias) not in named:
                continue
            pattern = r'(?<![0-9A-Za-z])' + r'\s+'.join(map(re.escape, alias.split())) + r'(?![0-9A-Za-z])'
            for m in re.finditer(pattern, text, re.IGNORECASE):
                hits.setdefault((m.start(), m.end()), {})[entry.entity_id] = entry
    chosen = []
    for (start, end), entries in sorted(hits.items(), key=lambda kv: (-(kv[0][1] - kv[0][0]), kv[0][0])):
        if all(end <= f.start or f.end <= start for f in chosen):
            chosen.append(Found(start, end, tuple(entries.values())))
    return sorted(chosen, key=lambda f: f.start)


def _locate(text, words):
    """Where the model's words occur in the message: exact first, then ignoring case; None when absent."""
    if not words:
        return None
    at = text.find(words)
    if at < 0:
        matches = quote_matches(text, words)
        if matches:
            return matches[0]
    if at < 0:
        at = text.casefold().find(words.casefold()) if len(words.casefold()) == len(words) else -1
    return (at, at + len(words)) if at >= 0 else None


def _sentences(text):
    return [(m.start(), m.end()) for m in re.finditer(r'[^?!\n]+?(?:[?!]+|\.(?=\s|$)|$|(?=\n))', text)
            if text[m.start():m.end()].strip()]


def _strip(text, span):
    start, end = span
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _looks_like_code(words):
    """A course code or abbreviation ("CS 999", "XYZ"), as opposed to an ordinary word ("Anything")."""
    stripped = re.sub(r'[^0-9A-Za-z]', '', words)
    return any(c.isdigit() for c in stripped) or (stripped.isupper() and len(stripped) >= 2)


def compile_meaning(meaning: Meaning, text: str, context: RequestContext, catalog=(), topics=()) -> Interpretation:
    """Rebuild one Interpretation from the meaning. Raises ValueError when nothing coherent can be built, so the
    caller can use the existing path instead."""
    if len(text) > MAX_PART_TEXT:
        raise ValueError('compile_message_too_long')
    if meaning.control == 'clarify' and meaning.intent == 'system_information_mixed':
        return _build(meaning, (), (), (), (), None, 'clarify')
    if meaning.control in ('greeting', 'system_information', 'unsupported_scope') or meaning.audience in ('excluded', 'unrelated'):
        raise ValueError('compile_terminal_left_to_existing_path')  # nothing to rebuild; existing guards apply
    previous = context.conversation
    if meaning.previous_course and (previous is None or previous.course_id is None):
        raise ValueError('course_reference_unavailable')  # a back-reference with no previous course stays refused
    menu = {t.subject_id: t for t in topics}
    for topic in meaning.topics:
        offered = menu.get(topic.subject_id)
        if topic.subject_id is not None and (offered is None or not set(topic.claims) <= {*offered.claims,
                                                                                         *offered.not_stated}):
            raise ValueError('topic_outside_menu')  # never answered from a topic the selection did not offer
    program, curriculum = _scope(meaning, context, catalog)
    prior_term = ((previous.year_level, previous.semester or 'any') if previous is not None
                  and previous.operation in TERM_OPERATIONS and previous.year_level is not None else None)
    courses = tuple(c for c in catalog if c.kind == 'course' and (c.program_id, c.curriculum_id) == (program, curriculum)
                    ) if curriculum is not None else ()
    named = frozenset(k for words in (*(c.target for c in meaning.checks if c.target),
                                      *(s.entity for s in meaning.claims),
                                      *(w for kind, w in meaning.mentions if kind == 'course'))
                      for k in _trimmed_keys(words))
    found = find_courses(text, courses, named)
    noncourse = {k for c in catalog if c.kind != 'course' for a in c.aliases for k in _trimmed_keys(a)}

    def resolving(words):
        """The found course spans the model's words name (its exact words first, then any spelling of them)."""
        keys = _trimmed_keys(words)
        exact = [f for f in found if _key(text[f.start:f.end]) in keys]
        if exact:
            return exact
        ids = {c.entity_id for c in courses if keys & {_key(a) for a in c.aliases}}
        return [f for f in found if ids & {e.entity_id for e in f.entries}]

    def within(spans, area):
        inside = [f for f in spans if area and area[0] <= f.start and f.end <= area[1]]
        return (inside or spans)[0] if spans else None

    def area_of(words):
        """The model part quote (located in the message) that contains these words, shortest first."""
        areas = [a for q in meaning.part_quotes for a in [_locate(text, q)] if a]
        hit = _locate(text, words) if words else None
        holding = [a for a in areas if hit and a[0] <= hit[0] and hit[1] <= a[1]]
        return min(holding, key=lambda a: a[1] - a[0]) if holding else None

    # Stated results: only about a course of the selected curriculum (a failure attached to a program is no fact).
    claims = []
    for stated in meaning.claims:
        spans = resolving(stated.entity)
        if not spans:
            continue
        area = _locate(text, stated.quote) if stated.quote else None
        entity = within(spans, area)
        if not (area and area[0] <= entity.start and entity.end <= area[1]):
            area = next((s for s in (_strip(text, s) for s in _sentences(text)) if s[0] <= entity.start
                         and entity.end <= s[1]), (entity.start, entity.end))
        claims.append((area, entity, stated))
    claimed = {e.entity_id for _, f, _ in claims for e in f.entries}

    # Checks: each operation's meaning, bound to words of this message.
    built, unbound = [], []  # (name, kind, span, reference); checks with no course
    distinct = list({tuple(sorted(e.entity_id for e in f.entries)): f for f in found}.values())
    unclaimed = [f for f in distinct if not {e.entity_id for e in f.entries} & claimed]

    def only_course():
        pool = distinct if len(distinct) == 1 else unclaimed
        return pool[0] if len(pool) == 1 and len(pool[0].entries) == 1 else None

    def held_course(words):
        """The one reviewed course inside a longer target phrase ("anything that uses X as pre-req", "X next sem"),
        when the rest of the phrase is ordinary words. A second course or another code-like word (an unknown code
        the student may want to take) leaves the phrase as it was."""
        area = _locate(text, words) if words else None
        if area is None:
            return None
        inside = [f for f in found if area[0] <= f.start and f.end <= area[1]]
        if len({tuple(sorted(e.entity_id for e in f.entries)) for f in inside}) != 1 or len(inside[0].entries) != 1:
            return None
        rest, cursor = [], area[0]
        for f in inside:
            rest.append(text[cursor:f.start])
            cursor = f.end
        rest.append(text[cursor:area[1]])
        if any(_looks_like_code(w) and not _trimmed_keys(w) & noncourse for w in ' '.join(rest).split()):
            return None
        return inside[0]

    def back_reference():
        if (meaning.previous_course is None or previous is None or previous.course_id is None
                or not any(c.entity_id == previous.course_id for c in courses)):
            return None
        return _locate(text, meaning.previous_course)

    for check in meaning.checks:
        target = check.target
        if check.name == 'check_study_plan':
            span = _locate(text, target)
            if span is None:
                raise ValueError('compile_plan_unlocated')
            built.append((check.name, 'term', span, None))
            continue
        if check.name in TERM_OPERATIONS:
            spans = resolving(target) if target else []
            if spans and check.name == 'assess_term_prerequisites':  # a term check aimed at a named course
                built.append(('check_prerequisite_eligibility', 'course', within(spans, area_of(target)), None))
                continue
            term = next((s for w in (target, *(w for k, w in meaning.mentions if k in ('term', 'program', 'curriculum')))
                         for s in [_locate(text, w)] if s and parse_term(text[s[0]:s[1]], prior_term)), None)
            if term is None and parse_term(text, prior_term):
                term = _strip(text, (0, len(text)))
            if term is None and check.name == 'assess_term_prerequisites' and only_course() is not None:
                # "Can I take X next semester?": the only course without a stated result is the target.
                built.append(('check_prerequisite_eligibility', 'course', only_course(), None))
                continue
            span = term or _locate(text, target)
            if span is None:
                raise ValueError('compile_term_unlocated')
            built.append((check.name, 'term', span, None))
            continue
        spans = resolving(target) if target else []
        if spans:
            area = area_of(target)
            course = within(spans, area)
            area = area or next((s for s in _sentences(text) if s[0] <= course.start < course.end <= s[1]),
                                (0, len(text)))
            reverse = (check.name in (*_ELIGIBILITY, 'list_course_prerequisites')
                       and sum(area[0] <= f.start < f.end <= area[1] for f in found) == 1
                       and _DEPENDANTS_BEFORE.search(text[area[0]:course.start])
                       and _AS_PREREQUISITE.match(text[course.end:area[1]]))
            built.append(('list_affected_courses' if reverse else check.name, 'course', course, None))
            continue
        if not courses:  # no curriculum yet: keep the words so validation asks for the missing scope
            span = _locate(text, target) or (_locate(text, meaning.previous_course) if meaning.previous_course else None)
            if span is None:
                raise ValueError('compile_target_unlocated')
            built.append((check.name, 'course', span, None))
            continue
        inner = held_course(target)
        if inner is not None:
            # "Can I take anything that uses X as pre-req?" with the whole phrase as the target: X is the reference
            # point and the student asks about the courses that depend on it, not about a course named "Anything".
            area = _locate(text, target)
            own = area is not None and bool(_OWN_PREREQS_BEFORE.search(text[area[0]:inner.start])
                                            or _OWN_PREREQS_AFTER.match(text[inner.end:area[1]]))
            name = ('list_affected_courses' if check.name == 'check_prerequisite_eligibility'
                    and _OTHER_COURSES.match(target) and not own else check.name)
            built.append((name, 'course', inner, None))
            continue
        word_target = target is None or not _looks_like_code(target) or bool(_trimmed_keys(target) & noncourse)
        single = only_course() if word_target else None
        if single is not None:
            # "Can I take anything that uses X as pre-req?": the named course is the reference point and the
            # student asks about the courses that depend on it, not about taking X itself.
            name = ('list_affected_courses' if check.name in _ELIGIBILITY and target and _OTHER_COURSES.match(target)
                    else check.name)
            built.append((name, 'course', single, None))
            continue
        reference = back_reference() if word_target and not found else None
        if reference is not None:
            built.append((check.name, 'course', reference, reference))
            continue
        if word_target:
            unbound.append((check.name, target))  # no course to check; a topic beside it may still answer
            continue
        span = _locate(text, target)
        if span is None:
            raise ValueError('compile_target_unlocated')
        built.append((check.name, 'course', span, None))  # validation asks for the printed code
    if unbound and not built and not meaning.topics:
        # Nothing else was asked: the words stand for the course, so validation asks for its printed code.
        name, target = unbound[0]
        span = _locate(text, target)
        if span is None:
            raise ValueError('compile_no_course')
        built.append((name, 'course', span, None))

    # Follow-ups from memory when the model asked nothing executable.
    if not built and not meaning.topics and previous is not None and meaning.audience != 'excluded':
        single = only_course()
        if previous.operation in COURSE_OPERATIONS and single is not None:
            built.append((previous.operation, 'course', single, None))  # "how about CC 5?" / "If I fail X?"
        elif (not found and recovery_follow_up(text, context)
              and any(c.entity_id == previous.course_id for c in courses)):
            span = _strip(text, (0, len(text)))
            built.append(('list_affected_courses', 'course', span, span))
        elif (previous.operation is None and previous.subject_id is None and previous.course_id is None
              and previous.program_id is not None and not found and _LISTING.search(text)):
            # Bare program name, then "yung subjects": list that program's term courses.
            term = _strip(text, (0, len(text)))
            built.append(('list_term_courses', 'term', term, None))

    # Mentions, claims and operations.
    mentions, operations = [], []

    def mention(kind, span):
        if isinstance(span, Found):
            start, end = span.start, span.end
        else:
            start, end = span
        for i, m in enumerate(mentions):
            if (m['start'], m['end']) == (start, end):
                if m['kind'] != kind:
                    raise ValueError('compile_mention_kind_conflict')
                return i
        mentions.append(dict(kind=kind, text=text[start:end], start=start, end=end))
        return len(mentions) - 1

    reference_span = None
    for name, kind, span, reference in built:
        index = mention(kind, span)
        if reference is not None:
            reference_span = reference
        if not any(o == dict(name=name, target=index) for o in operations):
            operations.append(dict(name=name, target=index))
    claim_values = []
    for area, entity, stated in claims:
        claim_values.append(dict(text=text[area[0]:area[1]], start=area[0], end=area[1],
                                 entity=mention('course', entity), state=stated.state, mode=stated.mode))
    for kind, words in meaning.mentions:  # model-listed names the host keeps (programs, other courses)
        if kind in ('program', 'curriculum') and not parse_term(words):
            span = _locate(text, words)
            if span and not any(m['start'] < span[1] and span[0] < m['end'] for m in mentions):
                mention(kind, span)
        elif kind == 'course':
            spans = resolving(words)
            if spans and not any((m['start'], m['end']) == (spans[0].start, spans[0].end) for m in mentions):
                if not any(m['start'] < spans[0].end and spans[0].start < m['end'] for m in mentions):
                    mention('course', spans[0])

    # A structured question part naming a course no check is about, and stating no result, is a second question the
    # model gave no operation ("Can I take A1 and can I take B1?"); it is never dropped silently.
    targets = [(mentions[o['target']]['start'], mentions[o['target']]['end']) for o in operations]
    for words in meaning.structured_quotes:
        area = _locate(text, words)
        if area is None:
            continue
        if (any(area[0] <= s and e <= area[1] for s, e in targets)
                or any(c['start'] <= area[0] and area[1] <= c['end'] for c in claim_values)):
            continue
        if any(area[0] <= f.start and f.end <= area[1] for f in found):
            raise ValueError('compile_unbound_structured_part')

    # Mentions in message order, as the existing path lists them.
    order = sorted(range(len(mentions)), key=lambda i: (mentions[i]['start'], mentions[i]['end']))
    moved = {old: new for new, old in enumerate(order)}
    mentions = [mentions[i] for i in order]
    for operation in operations:
        operation['target'] = moved[operation['target']]
    for claim in claim_values:
        claim['entity'] = moved[claim['entity']]

    # Parts: one per ask, each with its own span.
    menu = {t.subject_id: t for t in topics}
    asks = []  # (need, span, operation index or None, topic or None)
    for index, operation in enumerate(operations):
        target = mentions[operation['target']]
        area = area_of(target['text'])
        if area is None or not area[0] <= target['start'] < target['end'] <= area[1]:
            area = next((s for s in (_strip(text, s) for s in _sentences(text))
                         if s[0] <= target['start'] and target['end'] <= s[1]), None)
        asks.append(['structured', area, index, None, target])
    for topic in meaning.topics:
        if topic.with_check and operations:
            continue  # the check is the explicit request; its stray topic is dropped
        if topic.subject_id is not None and topics:
            offered = menu.get(topic.subject_id)
            kept = tuple(c for c in topic.claims if offered is not None and c in {*offered.claims, *offered.not_stated})
            topic = Topic(topic.subject_id, kept[:8], topic.detail, topic.quote, topic.with_check) if kept else \
                Topic(None, (), 'whole', topic.quote, topic.with_check)
        area = _locate(text, topic.quote) if topic.quote else None
        if area is not None:
            area = _strip(text, area)
        asks.append(['document', area, None, topic, None])
    whole = _strip(text, (0, len(text)))
    if len(asks) == 1:
        asks[0][1] = whole
    for a in asks:
        if a[1] is None:
            a[1] = whole
    # A topic-less document ask on the same words as a check adds nothing to answer; other clashes give up.
    checked = {tuple(a[1]) for a in asks if a[0] == 'structured'}
    asks = [a for a in asks if not (a[0] == 'document' and a[3].subject_id is None and tuple(a[1]) in checked)]
    if len({tuple(a[1]) for a in asks}) != len(asks):
        raise ValueError('compile_duplicate_span')
    asks.sort(key=lambda a: (a[1][0], a[1][1]))
    if len(asks) > 8:
        raise ValueError('compile_too_many_parts')
    parts = []
    for number, (need, area, index, topic, _) in enumerate(asks, 1):
        start, end = area
        part = dict(part_id=f'r{number}', text=text[start:end], start=start, end=end, evidence_need=need,
                    operation_indices=[index] if index is not None else [])
        if topic is not None and topic.subject_id is not None:
            part.update(subject_id=topic.subject_id, requested_claims=list(topic.claims), detail=topic.detail)
        parts.append(part)

    control = None
    if not parts:
        control = meaning.control if meaning.control not in (None, 'greeting', 'system_information', 'unsupported_scope') else 'clarify'
    elif meaning.control is not None and not operations:
        control = meaning.control  # a clarification over document words stays the model's choice
    reference = None
    if reference_span is not None:
        reference = dict(text=text[reference_span[0]:reference_span[1]], start=reference_span[0], end=reference_span[1])
    return _build(meaning, mentions, claim_values, operations, parts, reference, control)


_ELIGIBILITY = ('check_prerequisite_eligibility', 'list_missing_prerequisites')
# Words that stand for "some other course" rather than a course or a back-reference ("it", "sya").
_OTHER_COURSES = re.compile(r'^\s*(any|anything|something|what|which|ano|anong|alin|alinman|kahit\s+ano|'
                            r'(?:mga\s+)?(?:other\s+)?(?:subjects?|courses?))\b', re.I)
# "prerequisites of X" / "X needs": the course's own prerequisites, the opposite direction of "what uses X".
_OWN_PREREQS_BEFORE = re.compile(r'\b(?:pre-?req\w*|requirements?)\s+(?:of|for|ng|ni)\s*\Z', re.I)
_OWN_PREREQS_AFTER = re.compile(r'\s*(?:needs?|requires?)\b', re.I)
_DEPENDANTS_BEFORE = re.compile(r'\b(?:subjects?|courses?)\b[^.?!;\n]*\Z', re.I)
_AS_PREREQUISITE = re.compile(r'\s*(?:(?:as|ang|yung|is|a|the|their)\s+)*pre[-\s]?req(?:uisite)?s?\b', re.I)
_LISTING = re.compile(r'\b(subjects?|courses?|kurso|prospectus|curriculum)\b', re.I)


def _build(meaning, mentions, claims, operations, parts, reference, control):
    needs = frozenset(p['evidence_need'] for p in parts)
    route = None if control is not None else (
        {frozenset({'document'}): 'RAG', frozenset({'structured'}): 'Symbolic'}.get(needs, 'Hybrid'))
    terminal = control in ('greeting', 'system_information', 'unsupported_scope')
    value = dict(schema_version=Interpretation.SCHEMA_VERSION, language=meaning.language, audience=meaning.audience,
                 intent=meaning.intent, mentions=[] if terminal else mentions, claims=[] if terminal else claims,
                 operations=[] if terminal else operations, parts=[] if terminal else parts, route=route,
                 control=control, ambiguities=list(meaning.ambiguities),
                 reason=f'interpreter proposed {"route " + route if route else "control " + control}')
    if reference is not None and not terminal:
        value['context_reference'] = reference
    return Interpretation.parse(value)


def compile_reply(wire, text: str, context: RequestContext, catalog=(), topics=()) -> Interpretation:
    from .wire import WireInterpretation, _topic_parts_as_documents
    try:
        parsed = WireInterpretation.parse(wire.model_dump(mode='json') if hasattr(wire, 'model_dump') else wire)
    except ValueError:
        pass  # Structural slips still use the compiler's existing reconstruction.
    else:
        if not any(m.kind in ('course', 'term') for m in parsed.mentions):
            wire = _topic_parts_as_documents(parsed, frozenset(
                prepare_query(a).casefold() for entry in catalog if entry.kind == 'course' for a in entry.aliases))
    return compile_meaning(read_meaning(wire, text), text, context, catalog, topics)


SHIFT_TOPICS = ('handbook_shifting', 'handbook_drop_shift_faq')
TRANSFER_FAMILIES = ('leaving_palsu_transfer_credentials', 'transferring_into_palsu')


def stay_on_shifting(proposed: Interpretation, menu, text, conversation, direction_stated) -> Interpretation | None:
    """After a shifting answer, a transfer follow-up that names no direction (live: "ilang units ang mate-transfer?")
    is about the shift (a program change inside the university), not leaving or entering it: it stays on the previous
    shifting topic. A message naming a direction, a course or a check is left as read."""
    if (conversation is None or conversation.subject_id not in SHIFT_TOPICS or direction_stated
            or proposed.operations or len(text.split()) > 8):
        return None
    families = {t.subject_id: t.family for t in menu}
    if not proposed.parts or not all(families.get(p.subject_id) in TRANSFER_FAMILIES for p in proposed.parts):
        return None
    topic = next((t for t in menu if t.subject_id == conversation.subject_id), None)
    if topic is None:
        return None
    printed = [c for c in topic.claims if c not in topic.not_stated][:8]
    if not printed:
        return None
    part = dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document', operation_indices=[],
                subject_id=topic.subject_id, requested_claims=printed, detail='whole')
    return Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=[part], route='RAG', control=None,
                                     claims=[], operations=[], ambiguities=[],
                                     mentions=[m for m in proposed.model_dump(mode='json')['mentions']
                                               if m['kind'] not in ('course',)]))
