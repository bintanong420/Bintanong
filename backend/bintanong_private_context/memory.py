"""Session-chat memory (memory/eligibility plan, Task 2): the course results a student stated, and the one check
waiting on their reply. Ids, states and printed codes only; never raw chat text, grades or model reasoning.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Literal

from ..bintanong_routing.claim_evidence import clause_reading
from ..bintanong_routing.contracts import ScopedFact, fact_dimension
from ..bintanong_routing.terms import parse_term

# Operations whose answer can wait on one student result and be asked again once it is supplied.
RESUMABLE = ('check_prerequisite_eligibility', 'list_missing_prerequisites')


@dataclass(frozen=True)
class PendingCheck:
    """The check that asked the student for one course result, in its own scope."""
    program_id: str
    curriculum_id: str
    operation: str
    target_course_id: str
    target_code: str
    course_id: str
    course_code: str
    dimension: Literal['completion', 'enrollment', 'term']  # 'term': a term check waiting for its year level


@dataclass(frozen=True)
class BoundReply:
    fact: ScopedFact | None  # None when the reply supplied the waiting term, not a course result
    text: str  # the waiting check asked again, so it runs through the normal route


def fact_id(session_id, program_id, curriculum_id, course_id, state) -> str:
    identity = f'{session_id}:{program_id}:{curriculum_id}:{course_id}:{state}:user_statement'
    return 'fact-' + hashlib.sha256(identity.encode()).hexdigest()


def turn_ref(message_id: str) -> str:
    return 'turn-' + hashlib.sha256(message_id.encode()).hexdigest()[:16]


def _key(fact):
    return fact.program_id, fact.curriculum_id, fact.course_id, fact_dimension(fact.state)


def merge_facts(existing, new):
    """A newer self-report replaces an older one for the same course and dimension; "took it" never erases a known
    result; a confirmed upload is kept beside a disagreeing statement, so the check asks instead of choosing."""
    merged = list(existing)
    for fact in new:
        same = [f for f in merged if _key(f) == _key(fact)]
        if fact.state == 'taken_unknown' and any(f.state != 'taken_unknown' for f in same):
            continue
        if any(f.state == fact.state for f in same if f.source != 'user_statement'):
            merged = [f for f in merged if not (_key(f) == _key(fact) and f.source == 'user_statement')]
            continue
        merged = [f for f in merged if not (_key(f) == _key(fact) and f.source == 'user_statement')] + [fact]
    return tuple(merged)


def accepted_facts(routed, message_id: str) -> tuple[ScopedFact, ...]:
    """Validated asserted claims of a completed turn; a what-if or a reported result is never remembered."""
    if routed is None or not getattr(routed, 'claims', ()):
        return ()
    facts = []
    for claim in routed.claims:
        if claim.mode != 'asserted':
            continue
        facts.append(ScopedFact(fact_id=fact_id(claim.session_id, claim.program_id, claim.curriculum_id,
                                                claim.course_id, claim.state),
                                session_id=claim.session_id, program_id=claim.program_id,
                                curriculum_id=claim.curriculum_id, course_id=claim.course_id, state=claim.state,
                                source='user_statement', ref=turn_ref(message_id), period=claim.period))
    return tuple(facts)


def pending_from(routed, answer, labels) -> PendingCheck | None:
    """A checked answer missing exactly one student result waits for it; anything else waits for nothing."""
    if routed is not None and routed.diagnostic == 'missing_term':  # "What can I take next sem?" without a year
        return PendingCheck(routed.program_id, routed.curriculum_id, 'assess_term_prerequisites', '', '', '', '',
                            'term')
    decision = getattr(answer, 'decision', None)
    if (routed is None or routed.diagnostic != 'validated' or decision is None or decision.outcome != 'unknown'
            or routed.decision.predicate_request is None
            or routed.decision.predicate_request.predicate not in RESUMABLE):
        return None
    waiting = {}
    for field in (*decision.missing_facts, *decision.unknown_conditions):
        prefix, _, course = field.partition(':')
        dimension = {'completion_unknown': 'completion', 'enrollment_unknown': 'enrollment'}.get(prefix)
        if dimension:
            waiting.setdefault(course, set()).add(dimension)
    if len(waiting) != 1:
        return None
    (course, dimensions), = waiting.items()
    request = routed.decision.predicate_request
    target = next(i.value for i in request.inputs if i.name == 'course_id')
    if len(dimensions) != 1 or course not in labels or target not in labels:
        return None
    return PendingCheck(routed.program_id, routed.curriculum_id, request.predicate, target, labels[target],
                        course, labels[course], dimensions.pop())


_AFFIRM = {'oo', 'opo', 'yes', 'yeah', 'yep', 'yup', 'sige', 'tama', 'correct', 'oum', 'oho'}
_DENY = {'no', 'nope', 'nah', 'hindi', 'di', 'wala', 'not', 'yet', 'pa', "haven't", 'havent', "didn't", 'didnt'}
_FILLER = {'i', 'ive', "i've", 'have', 'has', 'already', 'it', 'na', 'po', 'ako', 'ko', 'sa', 'ang', 'yung', 'the',
           'course', 'subject', 'naman', 'din', 'rin', 'okay', 'ok', 'still', 'am', "i'm", 'im', 'did', 'do', 'this',
           'term', 'sem', 'semester', 'ngayon', 'currently', 'eh', 'e', 'ba', 'that', 'one', 'yan', 'iyan', 'iyon'}
_RESULT = {'pasado', 'passed', 'pass', 'napasa', 'naipasa', 'nakapasa', 'pumasa', 'napapasa', 'failed', 'fail',
           'bagsak', 'bumagsak', 'binagsak', 'taken', 'took', 'take', 'natake', 'natatake', 'nakuha', 'enrolled',
           'enroll', 'naka-enroll', 'nakaenroll', 'taking', 'completed', 'natapos', 'tapos'}
_REPLY_WORDS = _AFFIRM | _DENY | _FILLER | _RESULT
_FILIPINO = {'oo', 'opo', 'oho', 'sige', 'tama', 'hindi', 'di', 'wala', 'pa', 'na', 'po', 'ako', 'ko', 'sa', 'ang',
             'yung', 'naman', 'din', 'rin', 'ngayon', 'pasado', 'napasa', 'naipasa', 'nakapasa', 'pumasa', 'bagsak',
             'bumagsak', 'binagsak', 'natake', 'natatake', 'nakuha', 'naka-enroll', 'nakaenroll', 'natapos', 'tapos',
             'ba', 'yan', 'iyan', 'iyon'}
_ASK = {('check_prerequisite_eligibility', 'en'): 'Can I take {code}?',
        ('check_prerequisite_eligibility', 'taglish'): 'Pwede ko na bang i-take ang {code}?',
        ('list_missing_prerequisites', 'en'): 'What prerequisites am I missing for {code}?',
        ('list_missing_prerequisites', 'taglish'): 'Ano pa ang kulang kong prerequisite para sa {code}?'}


_ORDINAL = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth'}
_TERM = {'first_semester': ', first semester', 'second_semester': ', second semester', 'summer': ', summer', 'any': ''}
_TERM_FILIPINO = {'taon', 'unang', 'una', 'ikalawang', 'ikalawa', 'pangalawang', 'ikatlong', 'pangatlong', 'ikaapat',
                  'ika-apat', 'ikalimang', 'po', 'na', 'sa', 'yung', 'ang', 'ako'}


def _term_reply(text) -> BoundReply | None:
    """A short reply naming a year level (and semester) answers a waiting term check."""
    term = parse_term(text)
    if term is None or '?' in text or len(text.split()) > 10:
        return None
    name = f'{_ORDINAL[term[0]]} year{_TERM[term[1]]}'
    filipino = set(re.findall(r"[a-z]+(?:-[a-z]+)*", text.casefold())) & _TERM_FILIPINO
    return BoundReply(None, f'Ano ang pwede kong i-take sa {name}?' if filipino else f'What can I take in {name}?')


def _without_code(text, code):
    """The reply with the waiting course's printed code removed (spacing and a "/L" suffix may differ)."""
    stem = re.sub(r'/L$', '', code.replace(' ', ''), flags=re.I)
    pattern = r'\s*'.join(map(re.escape, stem)) + r'(?:\s*/\s*L)?'
    return re.sub(r'(?<![\w-])' + pattern + r'(?![\w-])', ' ', text, flags=re.I)


def bind_reply(text, check: PendingCheck | None, scope, *, session_id) -> BoundReply | None:
    """A short reply ("Oo, pasado", "not yet") answers the waiting question only in the same scope; a reply that
    asks something, names another course or states no result is routed as a new message."""
    if check is None or tuple(scope) != (check.program_id, check.curriculum_id):
        return None
    if check.dimension == 'term':
        return _term_reply(text)
    remaining = _without_code(text, check.course_code).casefold().replace('’', "'")
    tokens = re.findall(r"[a-z]+(?:[-'][a-z]+)*", remaining)
    if re.search(r'[0-9?]', remaining) or not tokens or len(tokens) > 10 or not set(tokens) <= _REPLY_WORDS:
        return None
    reading = clause_reading(remaining)
    denied, affirmed = bool(set(tokens) & _DENY), bool(set(tokens) & _AFFIRM)
    if check.dimension == 'completion':
        state = reading if reading in ('passed', 'failed', 'not_passed', 'not_taken') else (
            None if reading is not None else 'not_passed' if denied else 'passed' if affirmed else None)
    else:
        state = reading if reading in ('enrolled', 'not_enrolled') else (
            None if reading is not None else 'not_enrolled' if denied else 'enrolled' if affirmed else None)
    if state is None:
        return None
    language = 'taglish' if set(tokens) & _FILIPINO else 'en'
    fact = ScopedFact(fact_id=fact_id(session_id, check.program_id, check.curriculum_id, check.course_id, state),
                      session_id=session_id, program_id=check.program_id, curriculum_id=check.curriculum_id,
                      course_id=check.course_id, state=state, source='user_statement',
                      period='current' if check.dimension == 'enrollment' else None)
    return BoundReply(fact, _ASK[(check.operation, language)].format(code=check.target_code))
