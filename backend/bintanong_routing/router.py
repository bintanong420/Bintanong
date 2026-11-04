"""Independent Bintu routing/style interpretations with one shared format repair."""
from __future__ import annotations

import json
import os
import re
from dataclasses import replace

from pydantic import ValidationError

from .filipino_terms import printed_terms
from ..bintanong_contracts.runtime import NormalizedQuery
from ..bintanong_contracts.symbolic import EMPTY_REGISTRY
from .contracts import TERM_OPERATIONS, Interpretation, RequestContext, prepare_query
from .terms import parse_term
from .prompt import build_messages, output_schema, previous_turn
from .style import StyleProposal, build_style_messages, floor_style, style_output_schema
from .transport import RuntimeFailure
from . import topic_selection as selection
from .recovery_cue import recovery_request
from .validation import RoutingResult, _decision, validate_interpretation
from .wire import WireInterpretation, normalize_interpretation
from .compile import compile_reply, stay_on_shifting
from .dialogue import bind_dialogue, DialogueReferenceError


def compile_enabled():
    """Owner 4 Nov 2026: compiled routing is on only with BINTANONG_ROUTER_COMPILE=1 (default off)."""
    return os.environ.get('BINTANONG_ROUTER_COMPILE') == '1'


def listing_without_term(result, conversation):
    """A term listing whose words name no year level (e.g. "yung subjects" after a program name) asks for the term,
    like a term check does, instead of a bare clarification."""
    p = result.proposed
    if result.diagnostic != 'unresolved_entity' or p is None or len(p.operations) != 1:
        return False
    op = p.operations[0]
    prior = ((conversation.year_level, conversation.semester or 'any') if conversation is not None
             and conversation.operation in TERM_OPERATIONS and conversation.year_level is not None else None)
    unresolved_courses = [m for m in p.mentions if m.kind == 'course']
    return (op.name == 'list_term_courses' and not unresolved_courses
            and parse_term(p.mentions[op.target].text, prior) is None)


def drop_untopical_parts(proposed, topics):
    """Owner GUI 4 Nov 2026: a document part with no reviewed topic cannot sink an answerable structured part. With a
    topic menu, such parts are taken out and their words returned, so the reply names them as not in the reviewed
    sources; a message with no structured part is left as it was."""
    loose = [p for p in proposed.parts if p.evidence_need == 'document' and p.subject_id is None]
    if not topics or not loose or not any(p.evidence_need == 'structured' and p.operation_indices
                                          for p in proposed.parts):
        return proposed, ()
    kept = [p.model_dump(mode='json') for p in proposed.parts if p not in loose]
    route = 'Hybrid' if any(p['evidence_need'] == 'document' for p in kept) else 'Symbolic'
    return (Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=kept, route=route)),
            tuple(p.text for p in loose))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_json_key')
        result[key] = value
    return result


def _json_proposal(raw):
    if not isinstance(raw, str) or len(raw.encode('utf-8')) > 65536:
        raise ValueError('invalid_output_size')
    return json.loads(raw, object_pairs_hook=_unique_object)


REFERENCE_HINTS = {
    'invalid_course_quote_reference': 'every operation target and claim entity must quote a course '
        'code that is also listed in mentions with kind course; if the student names no specific '
        'course code, return no operation (route RAG, or control clarify).',
    'topic_outside_menu': 'requested_claims must be facts listed under the chosen topic only.',
    'course_reference_unavailable': 'no scoped previous course is available. Do not emit a '
        'previous_course_quote or turn a document subject ID into a course. For a clear document '
        'follow-up, use the previous document subject and its reviewed claims; clarify an unclear '
        'request rather than inventing a course or operation.',
    'unreferenced_operation': 'every operation must be referenced by a question part that requests it. '
        'Interpret the original request again; document-only parts need no course operation. '
        'Do not invent a structured question or course to justify an unused operation.',
}


def _repair_messages(messages, raw, problem=None):
    if problem is None:
        request = ('This is a formatting repair, not a new student question. '
            'Return valid JSON matching the original schema for the ORIGINAL student request '
            'in the payload below. Correct formatting only; preserve its meaning and facts.\n')
    else:  # A reference error is a meaning error: name it and allow reinterpretation.
        request = ('This is a repair, not a new student question. The previous interpretation was '
            f'rejected ({problem}): {REFERENCE_HINTS.get(problem, "fix that invalid reference")} '
            'Return valid JSON matching the original schema for the ORIGINAL student request '
            'in the payload below. Do not invent courses, operations or facts.\n')
    return [*messages, dict(role='assistant', content=raw[:65536] if isinstance(raw, str) else ''),
        dict(role='user', content=request + messages[1]['content'])]



def check_topics(proposed, topics):
    """Host check: topic choices must come from the release menu, claims from that subject."""
    menu = {t.subject_id: {*t.claims, *t.not_stated} for t in topics}
    for part in proposed.parts:
        if part.subject_id is not None and not set(part.requested_claims) <= menu.get(part.subject_id, set()):
            raise ValueError('topic_outside_menu')


# Owner F4 (28 Oct 2026, provisional "b perhaps"): a transfer question that does not say whether the student is
# leaving PalSU or transferring in is asked first. Phrases that state the direction (English/Filipino/Taglish).
TRANSFER_FAMILIES = frozenset(('leaving_palsu_transfer_credentials', 'transferring_into_palsu'))
TRANSFER_DIRECTION_CUES = (
    'honorable dismissal', 'transfer out', 'transferring out', 'leave palsu', 'leaving palsu',
    'leave the university', 'leaving the university', 'to another school', 'to another university',
    'to other school', 'aalis', 'lilipat sa ibang', 'lilipat ng ibang',
    'transferee', 'from another school', 'from other school', 'from another university',
    'galing sa ibang', 'transfer to palsu', 'transferring to palsu', 'lilipat sa palsu', 'lumipat sa palsu',
    # Owner GUI 3 Nov 2026 (#11): typed Taglish.
    'lipat to palsu', 'lipat sa palsu', 'from ibang school', 'galing ibang school', 'to ibang school', 'lipat sa ibang school')


# Owner, 28 Oct 2026: a question explicitly naming an excluded program gets the undergraduate-scope notice even
# when the router labels it undergraduate. Other wording stays with the router.
EXCLUDED_PROGRAM_CUES = (
    'college of law', 'school of law', 'juris doctor', 'college of medicine', 'doctor of medicine',
    'graduate school', "master's program", 'masters program', "master's degree", 'masters degree',
    'doctoral program', 'doctorate program', 'laboratory school')


def _names_any(text, phrases):
    text = text.replace('’', "'")  # a typed curly apostrophe matches master's
    return any(re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', text, re.IGNORECASE) for c in phrases)


# Owner GUI 3 Nov 2026 (H2, #11): replies to the bot's own "Aalis ka ba sa PalSU ..., o lilipat ka sa PalSU galing sa
# ibang school?" question. These read the answer to that question only; they are not a routing word list.
_LEAVING_REPLY = ('aalis', 'alis', 'leaving', 'leave palsu', 'transfer out', 'transferring out', 'honorable dismissal',
                  'to another school', 'sa ibang school ako lilipat', 'to ibang school', 'lipat sa ibang school')
_INCOMING_REPLY = ('transferring in', 'transfer in', 'transferring into', 'transferee', 'lilipat sa palsu',
                   'lilipat ako sa palsu', 'galing sa ibang school', 'from another school', 'papasok',
                   'lipat to palsu', 'lipat sa palsu', 'into palsu', 'from ibang school', 'galing ibang school')


def answer_transfer_direction(proposed, menu, text, conversation):
    """The previous turn asked leaving or transferring in; a reply naming one side is answered from that side's
    topic, keeping the detail the original question asked. A reply naming neither or both returns None."""
    if conversation is None or conversation.pending != 'transfer_direction':
        return None
    leaving, incoming = _names_any(text, _LEAVING_REPLY), _names_any(text, _INCOMING_REPLY)
    if leaving == incoming:
        return None
    family = 'leaving_palsu_transfer_credentials' if leaving else 'transferring_into_palsu'
    preferred = 'charter_transfer' if leaving else 'handbook_transfer_credentials'
    members = [t for t in menu if t.family == family]
    topic = next((t for t in members if t.subject_id == preferred), members[0] if members else None)
    if topic is None:
        return None
    part = dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document', operation_indices=[],
                subject_id=topic.subject_id, requested_claims=[c for c in topic.claims if c not in topic.not_stated][:8],
                detail=conversation.detail or 'whole')
    return Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=[part], route='RAG', control=None,
                                     claims=[], ambiguities=[], operations=[],
                                     mentions=[m for m in proposed.model_dump(mode='json')['mentions']
                                               if m['kind'] != 'course']))


# Owner GUI 3 Nov 2026 ("memory system"): a short follow-up naming one detail ("magkano naman?") after a procedure
# answer re-asks the previous topic for that detail, when the router would otherwise ask an empty clarification.
_DETAIL_CUES = {
    'fees': re.compile(r'\b(magkano|how much|fees?|bayad|babayaran|cost|presyo)\b', re.I),
    'processing_time': re.compile(r'\b(gaano\s+(katagal|kabilis)|how long|ilang\s+araw|processing time|tagal)\b', re.I),
    'requirements': re.compile(r'\b(requirements?|kailangan(g)?\s+dalhin|dadalhin|what (do|should) i (need|bring))\b', re.I),
}


def answer_detail_follow_up(proposed, menu, text, conversation):
    if conversation is None or conversation.subject_id is None or len(text.split()) > 6:
        return None
    if proposed.control != 'clarify' and any(p.evidence_need == 'document' and p.subject_id for p in proposed.parts):
        return None
    named = [detail for detail, cue in _DETAIL_CUES.items() if cue.search(text)]
    topic = next((t for t in menu if t.subject_id == conversation.subject_id), None)
    if len(named) != 1 or topic is None:
        return None
    part = dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document', operation_indices=[],
                subject_id=topic.subject_id, requested_claims=[c for c in topic.claims if c not in topic.not_stated][:8],
                detail=named[0])
    return Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=[part], route='RAG', control=None,
                                     claims=[], ambiguities=[], operations=[],
                                     mentions=[m for m in proposed.model_dump(mode='json')['mentions']
                                               if m['kind'] != 'course']))


# Owner GUI 3 Nov 2026 ("memory system"): "pano yung CS 10/L?" after a prerequisite question keeps that check;
# the router read it as a course-facts lookup. Only a short how-about message naming one course is changed.
_HOW_ABOUT = re.compile(r'^\s*(pano|paano|e|eh|ee|how|what)\s+(yung|about|naman|kung)\b', re.I)
_COURSE_CHECKS = ('check_prerequisite_eligibility', 'list_course_prerequisites', 'list_missing_prerequisites')


def repeat_previous_check(proposed, text, conversation):
    if (conversation is None or conversation.operation not in _COURSE_CHECKS or len(text.split()) > 6
            or not _HOW_ABOUT.search(text) or len(proposed.operations) != 1
            or proposed.operations[0].name != 'course_facts'):
        return None
    value = proposed.model_dump(mode='json')
    value['operations'][0]['name'] = conversation.operation
    return Interpretation.parse(value)


SWITCH_REASON = 'program_switch_follow_up'  # validation binds the previous term or printed course code


def switch_program_follow_up(proposed, text, conversation, catalog):
    """A short named-track follow-up repeats the previous term listing or course check there.
    Returns (interpretation, program_ids); validation binds its reviewed curriculum and course code.
    Track words come from the catalog's program names; several matching tracks ask which one."""
    term = conversation is not None and conversation.operation in TERM_OPERATIONS and conversation.year_level is not None
    course = conversation is not None and conversation.operation in _COURSE_CHECKS and conversation.course_id is not None
    if (not (term or course)
            or conversation.program_id is None or not text.strip() or len(text.split()) > 6 or parse_term(text)
            or any(m.kind == 'course' for m in proposed.mentions) or proposed.claims
            or proposed.control not in (None, 'clarify')):
        return None
    words = lambda entry: {w for a in entry.aliases for w in re.findall(r'[^\W\d_]{4,}', a.casefold())}
    programs = {c.entity_id: c for c in catalog if c.kind == 'program'}
    current = programs.get(conversation.program_id)
    if current is None:
        return None
    family = [c for c in programs.values() if c.entity_id != current.entity_id
              and {a.casefold() for a in c.aliases} & {a.casefold() for a in current.aliases}]
    asked = set(re.findall(r'[^\W\d_]{4,}', text.casefold()))
    named = [c.entity_id for c in family if (words(c) - words(current)) & asked]
    if not named:
        return None
    span = text.strip()
    start = text.index(span)
    value = proposed.model_dump(mode='json')
    value.update(mentions=[dict(kind='term' if term else 'course', text=span, start=start, end=start + len(span))], claims=[],
                 ambiguities=[], control=None, route='Symbolic', reason=SWITCH_REASON,
                 operations=[dict(name=conversation.operation, target=0)],
                 parts=[dict(part_id='r1', text=span, start=start, end=start + len(span), evidence_need='structured',
                             operation_indices=[0], subject_id=None, requested_claims=[], detail='whole')])
    if course:
        value['context_reference'] = dict(text=span, start=start, end=start + len(span))
    return Interpretation.parse(value), tuple(named)


def transfer_direction_unstated(proposed, topics, text):
    families = {t.subject_id: t.family for t in topics}
    return (any(families.get(p.subject_id) in TRANSFER_FAMILIES for p in proposed.parts)
            and not _names_any(text, TRANSFER_DIRECTION_CUES))


def _printed_claims(topic, text):
    """The topic's printed claims for a whole request. A topic with more than a part may request (e.g. a 39-row
    sanctions table) narrows to the claims naming the request's words, either word possibly the short form
    ("exam" names "examinations"; a three-letter asked word such as "ano" never names "another"); none when
    those do not fit."""
    printed = tuple(c for c in topic.claims if c not in topic.not_stated)
    if len(printed) > 8:  # RequestPart.requested_claims bound
        asked = set(_heading_words(text))
        names = lambda claim: len({a for a in asked for w in _heading_words(claim)
                                   if _same_word(w, a) or (len(a) >= 4 and _same_word(a, w))})
        best = max((names(c) for c in printed), default=0)
        printed = tuple(c for c in printed if best and names(c) == best)  # the rows naming the most part words
    return printed if len(printed) <= 8 else ()


def answer_settled_topic(proposed, topics, text):
    """Host guard (owner 30 Oct 2026): after the selector settled on one topic, a clarification naming no part,
    ambiguity, course or operation (e.g. "Kailan ako considered second year?") answers that topic's printed
    claims as one document part instead of leaving the student without an answer."""
    if (len(topics) != 1 or proposed.control != 'clarify' or proposed.parts or proposed.ambiguities
            or proposed.mentions or proposed.operations or proposed.claims):
        return proposed
    claims = _printed_claims(topics[0], text)
    if not claims:
        return proposed
    part = dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document',
                operation_indices=[], subject_id=topics[0].subject_id, requested_claims=list(claims), detail='whole')
    return Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=[part], route='RAG', control=None))


# Words in the printed field names a requested detail is read from (e.g. step2_fee, amount_php_as_printed,
# replacement_owner_expense, step1_time).
_DETAIL_FIELDS = dict(fees=('fee', 'amount', 'php', 'price', 'expense', 'charge', 'payment', 'cost'),
                      processing_time=('time', 'deadline', 'period'), requirements=('requirement',))


def _other_field(topic, part):
    """Live 2 Nov 2026 (#7-8): a fee question chose Charter 2.4's not-stated PD 907 note, which was recorded on the
    service title. A detail question whose every requested not-stated fact was recorded only on fields of another
    kind is not asking for it. A fact recorded on the asked kind, or with no recorded fields, keeps withholding."""
    kind = _DETAIL_FIELDS.get(part.detail)
    fields = [topic.not_stated_fields.get(claim) for claim in part.requested_claims]
    return kind is not None and all(fields) and not any(
        word in name.casefold() for names in fields for name in names for word in kind)


def prefer_printed_procedure(proposed, topics):
    """Host guard: a whole-procedure part asks for the printed procedure, so naming only facts the source
    does not state is replaced by the topic's printed claims (see _printed_claims). Cues then re-add a
    not-stated fact the part's own words name, which keeps withholding for an explicit ask. When the printed
    claims do not fit, the model's choice is kept."""
    menu = {t.subject_id: t for t in topics}
    parts = []
    for part in proposed.parts:
        topic = menu.get(part.subject_id)
        if (topic is not None and part.requested_claims and set(part.requested_claims) <= set(topic.not_stated)
                and (part.detail == 'whole' or _other_field(topic, part))):
            printed = _printed_claims(topic, part.text)
            if printed:
                part = part.model_copy(update=dict(requested_claims=printed))
        parts.append(part)
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


# Words too generic to tie a part to one printed section heading or claim; institutional places and people
# ("smoking on campus" named a littering row printing "inside the University campus", regression 30 Oct 2026).
HEADING_STOPWORDS = frozenset('the and for with from not any are all its ang mga ng sa na at ko'.split()
                              + 'campus university premises school student students'.split())


def _heading_words(text):
    """Content words of a part or heading; a reviewed Filipino word also names its printed English term."""
    words = [w for w in re.findall(r'[^\W\d_]+', text.casefold()) if len(w) >= 3 and w not in HEADING_STOPWORDS]
    return words + [term for w in words for term in printed_terms(w) if term not in words]


def _same_word(heading, asked):
    """A short heading word (an abbreviation such as INC) starts the asked word; longer words share a stem."""
    return asked.startswith(heading) if len(heading) <= 4 else asked[:5] == heading[:5]


def _heading_score(topic, claim, asked):
    """The most of the asked words that one printed heading of the claim names."""
    return max((len({a for a in asked if any(_same_word(w, a) for w in _heading_words(h))})
                for h in topic.claim_headings.get(claim, ())), default=0)


def prefer_heading_claims(proposed, topics):
    """Host guard (owner 30 Oct 2026): when one fact of the chosen topic has a printed section heading naming at
    least two of the part's own words (e.g. "remove an incomplete grade" and 3.4 REMOVAL OF "INC") and no chosen
    fact's heading names any, that fact replaces the choice. Adding both exceeded the topic's context budget.
    A tie or a single-word match keeps the model's choice; only facts of the same topic are considered."""
    menu = {t.subject_id: t for t in topics if t.claim_headings}
    parts = []
    for part in proposed.parts:
        topic = menu.get(part.subject_id)
        if topic is not None and part.evidence_need == 'document':
            asked = set(_heading_words(part.text))
            if not any(_heading_score(topic, claim, asked) for claim in part.requested_claims):
                scores = {claim: _heading_score(topic, claim, asked) for claim in topic.claim_headings
                          if claim in topic.claims and claim not in topic.not_stated}
                best = max(scores.values(), default=0)
                winners = [claim for claim, score in scores.items() if score == best]
                if best >= 2 and len(winners) == 1:
                    part = part.model_copy(update=dict(requested_claims=(winners[0],)))
        parts.append(part)
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


def prefer_heading_topic(proposed, topics):
    """Host guard (regression 30 Oct 2026): the cross-topic counterpart of prefer_heading_claims. When one printed
    fact of another selected topic has a heading naming at least two of the part's words, more than any chosen
    fact's heading names, that topic and fact replace the choice ("residence requirement para maka-graduate" and
    graduation's 1.4 RESIDENCE REQUIREMENTS over 1. RESIDENCE). A tie keeps the model's choice."""
    menu = {t.subject_id: t for t in topics}
    parts = []
    for part in proposed.parts:
        topic = menu.get(part.subject_id)
        if topic is not None and part.evidence_need == 'document':
            asked = set(_heading_words(part.text))
            chosen = max((_heading_score(topic, claim, asked) for claim in part.requested_claims), default=0)
            scores = {(t.subject_id, claim): _heading_score(t, claim, asked) for t in topics
                      for claim in t.claim_headings if claim in t.claims and claim not in t.not_stated}
            best = max(scores.values(), default=0)
            winners = [key for key, score in scores.items() if score == best]
            if best >= 2 and best > chosen and len(winners) == 1 and winners[0][0] != part.subject_id:
                subject, claim = winners[0]
                part = part.model_copy(update=dict(subject_id=subject, requested_claims=(claim,)))
        parts.append(part)
    if all((a.subject_id, a.requested_claims) == (b.subject_id, b.requested_claims) for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


def prefer_named_claim(proposed, topics):
    """Host guard (regression 30 Oct 2026): when no chosen printed fact's own label names any of the part's words
    and exactly one printed fact of the same topic does ("mali ang uniform ko" and "I. Improper Uniform"), that
    fact replaces the choice. Several matches, or a chosen not-stated fact, keep the model's choice."""
    menu = {t.subject_id: t for t in topics}
    parts = []
    for part in proposed.parts:
        topic = menu.get(part.subject_id)
        if (topic is not None and part.evidence_need == 'document' and part.requested_claims
                and not set(part.requested_claims) & set(topic.not_stated)):
            asked = set(_heading_words(part.text))
            names = lambda claim: any(_same_word(w, a) for w in _heading_words(claim) for a in asked)
            if not any(names(claim) for claim in part.requested_claims):
                named = [c for c in topic.claims if c not in topic.not_stated and names(c)]
                if len(named) == 1:
                    part = part.model_copy(update=dict(requested_claims=(named[0],)))
        parts.append(part)
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


def answer_years_to_graduate(proposed, topics, text):
    """Owner 2 Nov 2026 (#2, option B): "how many years before I graduate" (not honours) is answered from the
    graduation rules, whose printed residence requirement the host quotes beside a program-length pointer. Live:
    the router chose year levels instead. A question naming a course or operation is left to the router."""
    from .topic_selection import YEARS_TO_GRADUATE
    claims = {t.subject_id: t.claims for t in topics}.get('handbook_graduation')
    if claims is None or not YEARS_TO_GRADUATE(text) or any(m.kind == 'course' for m in proposed.mentions):
        return proposed  # a named course stays with the router; an operation without one does not (live 2 Nov)
    part = dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document', operation_indices=[],
                subject_id='handbook_graduation', requested_claims=list(claims), detail='specific')
    return Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=[part], route='RAG', control=None,
                                     claims=[], ambiguities=[], operations=[]))


def lead_absence_with_attendance(proposed, topics):
    """Owner 2 Nov 2026 (#3): every absence needs the excuse slip (attendance rule); the sickness certificate is the
    "if you were sick" branch. Live, the router chose the sickness topic, so the host required sickness coverage and
    withheld a correct excuse-slip answer. An absence part on the sickness topic is led by attendance instead; the
    sickness record is still fetched beside it. A question that is not about an absence keeps its topic."""
    from .topic_selection import ABSENCE, ABSENCE_TOPICS
    attendance = {t.subject_id: t for t in topics}.get('handbook_attendance')
    claim = ABSENCE_TOPICS['handbook_attendance']
    if attendance is None or claim not in attendance.claims:
        return proposed
    parts = [part.model_copy(update=dict(subject_id='handbook_attendance', requested_claims=(claim,)))
             if part.subject_id == 'handbook_sickness_access' and ABSENCE.search(part.text) else part
             for part in proposed.parts]
    if all(a.subject_id == b.subject_id for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


def prefer_good_moral_checklist(proposed, topics):
    """Owner 2 Nov 2026 (#4): a requirements part about a good moral certificate that chose the Handbook FAQ is
    answered from the Charter CGMC checklist when that topic is offered; a "how do I get" part keeps the FAQ."""
    from .topic_selection import GOOD_MORAL
    checklist = 'printed good moral metadata and checklist fields'
    offered = {t.subject_id: t for t in topics}.get('charter_good_moral')
    if offered is None or checklist not in offered.claims:
        return proposed
    parts = [part.model_copy(update=dict(subject_id='charter_good_moral', requested_claims=(checklist,)))
             if part.subject_id == 'handbook_student_faq' and part.detail == 'requirements'
             and GOOD_MORAL.search(part.text) else part for part in proposed.parts]
    if all(a.subject_id == b.subject_id for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


def apply_not_stated_cues(proposed, topics):
    """Host guard: a part whose own words name a cued not-stated fact also requests that fact, so the
    evidence policy withholds instead of answering from a nearby printed fact."""
    cues = {t.subject_id: t.cues for t in topics if t.cues}
    parts = []
    for part in proposed.parts:
        claims = list(part.requested_claims)
        for cue in cues.get(part.subject_id, ()):
            if cue.claim not in claims and any(
                    re.search(r'(?<![\w-])' + re.escape(p) + r'(?![\w-])', part.text, re.IGNORECASE)
                    for p in cue.phrases):
                claims.append(cue.claim)
        parts.append(part.model_copy(update=dict(requested_claims=tuple(claims))))
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


class Router:
    def __init__(self, transport, *, catalog=(), registry=EMPTY_REGISTRY,
                 documents_available=False, synthetic=False, topics=(), topic_selection=False):
        self.transport = transport
        self.catalog = tuple(catalog)
        self.registry = registry
        self.documents_available = documents_available
        self.synthetic = synthetic
        self.topics = tuple(topics)
        if type(topic_selection) is not bool:
            raise ValueError('invalid_topic_selection')
        self.topic_selection = topic_selection

    async def route(self, text: str, context: RequestContext) -> RoutingResult:
        normalized = prepare_query(text)
        context = RequestContext.parse(context.model_dump(mode='json'))
        initial_context = context
        follow_up = bool((previous_turn(context, self.catalog) or {}).get('course_available'))
        names = tuple(alias for entry in self.catalog for alias in entry.aliases)  # never style evidence
        proposed = None
        topics = self.topics
        selection_attempts = 0

        def failure(code, attempts, style_attempts=0, style=None, floored=False):
            query = NormalizedQuery(schema_version=NormalizedQuery.SCHEMA_VERSION,
                original_text=text, normalized_text=normalized, language_hints=(), intent=None,
                entities=(), ambiguities=(), negations=(), time_qualifiers=(),
                session_fact_refs=tuple(f.fact_id for f in context.facts))
            control = 'clarify' if code in ('dialogue_reference_missing', 'dialogue_ambiguous') else 'evidence_unavailable'
            return RoutingResult(query, _decision(control=control, reason=code),
                proposed, (), 'unknown' if style is None else style.language, code, attempts,
                style_attempts=style_attempts, style_evidence=style, style_floor_applied=floored,
                selection_attempts=selection_attempts)

        async def clarification_style():
            """One unrepaired style call so a clarification matches the student's style."""
            try:
                style = StyleProposal.parse(_json_proposal(await self.transport.infer(
                    build_style_messages(text), style_output_schema()))).style
                style.ground(text)
            except (RuntimeFailure, ValueError, ValidationError):
                return None, False
            return floor_style(style, text, names)

        if self.topic_selection and len(topics) > selection.MAX_TOPICS:
            selection_attempts = 1
            try:
                raw = await self.transport.infer(selection.build_messages(
                    text, topics, previous_turn(context, self.catalog), context.dialogue), selection.output_schema(topics))
                topics = selection.add_companions(selection.selected_topics(_json_proposal(raw), topics), topics, text)
            except RuntimeFailure as error:
                return failure(str(error), 0)
            except ValueError:
                return failure('topic_selection_unavailable', 0)

        messages = build_messages(text, context, self.catalog, self.registry, topics)

        def guarded(proposed, compiled=False):
            """The host guards every interpretation passes through, whichever path built it."""
            check_topics(proposed, topics)
            if selection_attempts:
                proposed = answer_settled_topic(proposed, topics, text)
            proposed = apply_not_stated_cues(prefer_named_claim(prefer_heading_topic(prefer_heading_claims(
                prefer_printed_procedure(proposed, topics), topics), topics), topics), topics)
            proposed = answer_years_to_graduate(lead_absence_with_attendance(
                prefer_good_moral_checklist(proposed, topics), topics), topics, text)
            resolved = (answer_transfer_direction(proposed, self.topics, text, context.conversation)
                        or answer_detail_follow_up(proposed, self.topics, text, context.conversation)
                        or repeat_previous_check(proposed, text, context.conversation)
                        or (stay_on_shifting(proposed, self.topics, text, context.conversation,
                                             _names_any(text, TRANSFER_DIRECTION_CUES)) if compiled else None))
            if resolved is not None:  # owner GUI 3 Nov 2026: the reply to the direction question
                proposed = resolved
            switch = None if resolved is not None else switch_program_follow_up(
                proposed, text, context.conversation, self.catalog)
            if switch is not None:
                proposed = switch[0]
            proposed = recovery_request(proposed, text) or proposed  # owner 4 Nov 2026: Ask mode
            proposed, unavailable = drop_untopical_parts(proposed, topics)
            return proposed, resolved, switch, unavailable

        for attempt in (1, 2):
            try:
                raw = await self.transport.infer(messages, output_schema(topics, follow_up=follow_up))
            except RuntimeFailure as error:
                return failure(str(error), attempt)
            problem = None
            resolved = None
            compiled = False
            try:
                payload, context = bind_dialogue(_json_proposal(raw), text, initial_context, self.catalog, topics)
                follow_up = bool((previous_turn(context, self.catalog) or {}).get('course_available'))
            except DialogueReferenceError as error:
                return failure(str(error), attempt, 1, *await clarification_style())
            except ValueError:
                payload = None
            if compile_enabled():
                # Owner 4 Nov 2026: read the reply for meaning and rebuild its structure; the existing path stays
                # the fallback when nothing coherent can be built.
                try:
                    proposed, resolved, switch, unavailable = guarded(
                        compile_reply(payload, text, context, self.catalog, topics), compiled=True)
                    compiled = True
                except (ValueError, ValidationError):
                    resolved = None
            try:
                if not compiled:
                    wire = WireInterpretation.parse(payload)
                    try:
                        if wire.previous_course_quote is not None and not follow_up:
                            raise ValueError('course_reference_unavailable')
                        proposed = normalize_interpretation(text, wire, course_names=frozenset(
                            prepare_query(a).casefold() for e in self.catalog if e.kind == 'course' for a in e.aliases))
                        proposed, resolved, switch, unavailable = guarded(proposed)
                    except (ValueError, ValidationError) as error:
                        problem = str(error) if str(error) in REFERENCE_HINTS else 'invalid_reference'
                        raise
            except (ValueError, ValidationError):
                if attempt == 2:
                    if problem is None:
                        return failure('invalid_model_output', attempt)
                    return failure('invalid_reference', attempt, 1, *await clarification_style())
                messages = _repair_messages(messages, raw, problem)
                continue
            style_messages = build_style_messages(text)
            style_limit = 2 if attempt == 1 else 1  # one shared repair, maximum three calls
            for style_attempt in range(1, style_limit + 1):
                try:
                    style_raw = await self.transport.infer(style_messages, style_output_schema())
                except RuntimeFailure as error:
                    return failure(str(error), attempt, style_attempt)
                try:
                    style = StyleProposal.parse(_json_proposal(style_raw)).style
                except (ValueError, ValidationError):
                    if style_attempt == style_limit:
                        return failure('invalid_style_output', attempt, style_attempt)
                    style_messages = _repair_messages(style_messages, style_raw)
                    continue
                try:
                    style.ground(text)
                    style, floored = floor_style(style, text, names)
                    effective = Interpretation.parse(dict(proposed.model_dump(mode='json'), language=style.language))
                    scope = context
                    if switch is not None and len(switch[1]) == 1:  # the named program; its curriculum is chosen there
                        scope = RequestContext.parse(dict(context.model_dump(mode='json'), program_id=switch[1][0],
                                                          curriculum_id=None, facts=[]))
                    result = validate_interpretation(text, scope, effective, catalog=self.catalog,
                        registry=self.registry, documents_available=self.documents_available,
                        synthetic=self.synthetic)
                    if switch is not None and len(switch[1]) > 1:  # several tracks fit: ask which one
                        result = replace(result, decision=_decision(control='clarify', reason='program switch ambiguous',
                            missing=tuple('program_choice:' + p for p in switch[1])), diagnostic='program_switch_ambiguous')
                    if selection_attempts and result.decision.dispatchable and any(
                            p.evidence_need == 'document' and p.subject_id is None for p in proposed.parts):
                        return failure('topic_selection_unavailable', attempt, style_attempt, style, floored)
                    if result.decision.dispatchable and _names_any(text, EXCLUDED_PROGRAM_CUES):
                        result = replace(result, decision=_decision(control='unsupported_scope',
                            reason='excluded program named'), diagnostic='excluded_program_named')
                    elif (result.decision.dispatchable and resolved is None
                            and transfer_direction_unstated(proposed, topics, text)):
                        result = replace(result, decision=_decision(control='clarify',
                            missing=('transfer_direction',), reason='transfer direction unstated'),
                            diagnostic='transfer_direction_unstated')
                    if compiled and listing_without_term(result, context.conversation):
                        result = replace(result, decision=_decision(control='clarify', missing=('term',),
                            reason='missing term'), diagnostic='missing_term')
                    if compiled:
                        result = replace(result, compiled=True)
                    return replace(result, proposed=proposed, attempts=attempt,
                        style_attempts=style_attempt, style_evidence=style,
                        style_floor_applied=floored, offset_corrections=0,
                        selection_attempts=selection_attempts,
                        unavailable_parts=unavailable if result.decision.dispatchable else ())
                except ValueError:
                    return failure('invalid_grounding', attempt, style_attempt)
        raise AssertionError('unreachable')
