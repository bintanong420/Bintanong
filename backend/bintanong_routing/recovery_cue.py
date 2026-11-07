"""Ask mode for academic recovery (owner, 4 Nov 2026): a plain "I failed X, what can I take / how do I recover?"
is one recovery request. The cue list lives here only; routing and orchestration both read it.

A dependency check on a failed course plus a recovery cue becomes one `list_affected_courses` request on that
course; the host then adds the cited recovery routes and the greedy drafts. Nothing here names a program or course.
"""
from __future__ import annotations

import re

from .contracts import Interpretation

RECOVERY_CUE = re.compile(r'''\b(?:
    options?|plans?|plano|regular|back\s+on\s+track|catch\s+up|recover(?:y)?|resolve|fix\s+(?:it|this)
  | what\s+(?:can|should|could)\s+i\s+(?:take|do)|what\s+(?:do|should)\s+i\s+do
  | (?:pwede|puwede|pede)\s+ko(?:ng)?\s+(?:i-?)?take|ano(?:ng|\s+ang)?\s+(?:pwede|puwede|dapat)\s+(?:kong\s+)?(?:i-?)?take
  | ano(?:ng|\s+ang)?\s+gagawin|paano(?!\s+(?:kung|kapag|pag)\b)
  | ma-?resolve|ma-?recover|mabawi|makabawi|makahabol|humabol|habulin
)\b''', re.I | re.X)


def asks_recovery(text: str) -> bool:
    return bool(RECOVERY_CUE.search(text))


def asks_fastest_recovery(text: str) -> bool:
    """An explicit ordering preference, used only after recovery has been requested."""
    text = re.sub(r'\b(?:not|hindi)(?:\s+necessarily|\s+naman)?\s+(?:the\s+|ang\s+)?'
                  r'(?:fastest|earliest|pinakamabilis)\b', '', text, flags=re.I)
    return bool(re.search(r'\b(?:fastest|earliest\s+return|as\s+soon\s+as\s+possible|asap|'
                          r'pinakamabilis|makabalik\s+agad)\b', text, re.I))


def recovery_request(proposed: Interpretation, text: str) -> Interpretation | None:
    """The interpretation as one dependency check on the failed course, or None when it is not a recovery request.

    The course is the target of a `list_affected_courses` operation, else the course of a stated failure. Any other
    operation must target that course or a term; a request about another named course is left as the model read it.
    """
    if proposed.audience != 'undergraduate' or proposed.control not in (None, 'clarify') or not asks_recovery(text):
        return None
    targets = [o.target for o in proposed.operations if o.name == 'list_affected_courses']
    failed = [c.entity for c in proposed.claims if c.state == 'failed' and c.mode != 'reported'
              and proposed.mentions[c.entity].kind == 'course']
    candidates = set(targets) or set(failed)
    if len(candidates) != 1:
        return None
    (target,) = candidates
    if proposed.mentions[target].kind != 'course':
        return None
    if any(o.target != target and proposed.mentions[o.target].kind != 'term' for o in proposed.operations):
        return None
    already = (len(proposed.operations) == 1 and proposed.operations[0].name == 'list_affected_courses'
               and all(p.evidence_need == 'structured' and p.operation_indices == (0,) for p in proposed.parts))
    if already and proposed.control is None:
        return None
    value = proposed.model_dump(mode='json')
    value.update(operations=[dict(name='list_affected_courses', target=target)], route='Symbolic', control=None,
                 ambiguities=[], reason='academic recovery request',
                 parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured',
                             operation_indices=[0])])
    return Interpretation.parse(value)


_OFFERING_FOLLOWUP = re.compile(r'(?:paano\s+kung|what\s+(?:about|if)|how\s+about)\s+'
    r'(?:sa\s+|in\s+|a\s+)?(?:summer|special[- ]class|off[- ]semester)(?:\s+class)?\s*[?.!]*', re.I)


def recovery_follow_up(text: str, context) -> bool:
    """A short offering alternative to one scoped dependency question; never a result or a new policy question."""
    previous = context.conversation
    return bool(previous is not None and previous.operation == 'list_affected_courses' and previous.course_id
        and previous.program_id == context.program_id and previous.curriculum_id == context.curriculum_id
        and previous.subject_id is None and _OFFERING_FOLLOWUP.fullmatch(text.strip()))
