"""Student view of a validated answer (owner O4, 23 Oct 2026: students never see variable or function names).

The canonical `CandidateAnswer.text` is what the validator checks byte for byte, so it is never changed; it stays
the researcher diagnostic. The student view drops the candidate-preview and supplied-evidence lines, the check-scope line, evidence ids and aliases and citation lines (citations
travel as separate source parts) and turns the Prolog runtime's condition codes into plain phrases.
"""
from __future__ import annotations

import re

from backend.bintanong_generation.render import _WORDS

# One phrase per condition prefix the runtime emits (backend/algorithms/curriculum_runtime.pl).
_PHRASES = {
    'passed': ('passed', 'pasado', 'passed'),
    'not_completed': ('not completed yet', 'hindi pa tapos', 'hindi pa completed'),
    'completion_unknown': ('not known yet whether you completed it', 'hindi pa alam kung natapos mo na',
                           'hindi pa alam kung na-complete mo na'),
    'completion_conflict': ('the information on completing it conflicts', 'magkasalungat ang info kung natapos mo',
                            'may conflicting info kung na-complete mo'),
    'enrolled': ('currently enrolled', 'naka-enroll ka ngayon', 'currently enrolled ka'),
    'not_enrolled': ('not enrolled', 'hindi ka naka-enroll', 'hindi ka enrolled'),
    'enrollment_unknown': ('not known yet whether you are enrolled', 'hindi pa alam kung naka-enroll ka',
                           'hindi pa alam kung enrolled ka'),
    'enrollment_conflict': ('the information on your enrollment conflicts', 'magkasalungat ang info kung naka-enroll ka',
                            'may conflicting info kung enrolled ka'),
    'identity_unreviewed': ('this course record is not reviewed yet', 'hindi pa na-review ang record ng kursong ito',
                            'hindi pa reviewed ang course record na ito'),
    'rule_unresolved': ('its prerequisite rule is not fully reviewed yet',
                        'hindi pa buo ang na-review na prerequisite rule nito',
                        'hindi pa fully reviewed ang prerequisite rule nito'),
    'verified_none': ('the reviewed prospectus lists no prerequisite', 'walang prerequisite sa na-review na prospectus',
                      'walang prerequisite based sa reviewed prospectus'),
}
_LANGUAGES = ('en', 'fil', 'taglish')
_CODE = re.compile(r'\b([a-z]+(?:_[a-z]+)*):(\S[^,\n]*)')
_SCOPE_LABELS = ('Check scope', 'Sakop ng check')
# Short evidence aliases (e1, e2, ...) the model may write into a claim; its citations travel as source parts.
_ALIASES = re.compile(r'\s*\(e\d+(?:\s*(?:,|and|at)\s*e\d+)*\)')


def humanize_codes(line: str, language: str) -> str:
    index = _LANGUAGES.index(language) if language in _LANGUAGES else 0

    def phrase(match):
        value = match.group(2).strip()
        words = _PHRASES.get(match.group(1))
        return f'{value}: {words[index]}' if words else value  # an unknown code never shows its prefix
    return _CODE.sub(phrase, line)


# Owner, 29 Oct 2026: the student view leaves out the candidate-preview line; its guidance sentence is sent
# separately (`guidance_notice`) and shown subtly by the frontend.
_PREVIEWS = frozenset(words['preview'] for words in _WORDS.values())


def guidance_notice(language: str) -> str:
    return _WORDS.get(language, _WORDS['en'])['preview'].split('. ', 1)[1]


def student_text(answer) -> str:
    words = _WORDS.get(answer.language, _WORDS['en'])
    listed = tuple(f'{words[key]}: ' for key in ('conditions', 'missing', 'dependency'))
    scope = (tuple(f'{label}: {answer.structured_context.operation};' for label in _SCOPE_LABELS)
             if answer.structured_context is not None else ())
    claims = {f"{c.text} [{', '.join(c.evidence_ids)}]": _ALIASES.sub('', c.text) for c in answer.claims}
    # Replace whole claims first: a host-rendered claim can span several lines, with its IDs after the last.
    text = answer.text
    for rendered, plain in claims.items():
        text = text.replace(rendered, plain)
    claim_lines = {line for plain in claims.values() for line in plain.splitlines()}
    cited = tuple(f'[{card.evidence_id}] ' for card in answer.citations)
    shown = []
    for line in text.splitlines():
        if line in _PREVIEWS or line == words['answered'] or (scope and line.startswith(scope)) or (
                cited and line.startswith(cited)):
            continue
        if line in claim_lines:
            pass
        elif line.startswith(listed):
            line = humanize_codes(line, answer.language)
        shown.append(line)
    return '\n'.join(shown)


_YEAR = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th'}
_SEMESTER = {'first_semester': (0, '1st sem'), 'second_semester': (1, '2nd sem'), 'summer': (2, 'Summer')}
_PLAN_WORDS = {
    'en': dict(fastest='Fastest', notice='This is a draft, not an approval. Show it to your program adviser.',
               above='{units} units, above the {ceiling} listed for this term',
               summer_above='{units} units, above the {ceiling}-unit summer load',
               load_unknown='Unit load not checked: {reason}', prereq_unknown='{course}: prerequisites not fully checked',
               unchecked='{course}: could not be checked'),
    'taglish': dict(fastest='Pinakamabilis', notice='Draft lang ito, hindi approval. Ipakita sa program adviser.',
                    above='{units} units, lampas sa {ceiling} na nakalista sa term na ito',
                    summer_above='{units} units, lampas sa {ceiling}-unit summer load',
                    load_unknown='Hindi na-check ang unit load: {reason}',
                    prereq_unknown='{course}: hindi pa buo ang check ng prerequisites',
                    unchecked='{course}: hindi ma-check'),
}


def _units(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def _term(term):
    """A draft term as (sort key, label); a summer follows the second semester of its year."""
    order, semester = _SEMESTER[term.semester]
    return (term.year, order), f'{_YEAR[term.year]} yr · {semester}'


def plan_view(answer, course_labels) -> dict | None:
    """The checked recovery drafts as a comparison and timeline; only host results, never model text."""
    recovery = answer.recovery
    if recovery is None or not recovery.drafts:
        return None
    words = _PLAN_WORDS['en' if answer.language in ('en', 'unknown') else 'taglish']
    code = lambda course: course_labels.get(course, course)
    drafts, keys = [], {}
    for draft in recovery.drafts:
        terms = []
        for term in draft.terms:
            verdict = term.verdict
            if not term.moved and verdict.outcome == 'works':
                continue  # an unchanged prescribed term, left out as in the reply text
            unconfirmed = {u.course_id for u in verdict.unconfirmed}
            courses = [(p.course_id, p.mode) for p in term.moved] + [(c, 'prescribed') for c in term.kept]
            notes = [words['above' if w.kind == 'load_above_prescribed' else 'summer_above'].format(
                units=_units(w.units), ceiling=_units(w.ceiling)) for w in verdict.warnings]
            notes += [words['prereq_unknown' if r.kind == 'prerequisite_unknown' else 'unchecked'].format(
                course=code(r.course_id)) for r in verdict.reasons
                if r.kind in ('prerequisite_unknown', 'not_in_curriculum', 'rule_error')]
            if verdict.load.status == 'unknown':
                notes.append(words['load_unknown'].format(reason=verdict.load.reason))
            terms.append(dict(label=_term(term.term)[1], outcome=verdict.outcome,
                              courses=[dict(code=code(c), mode=m, needsConfirmation=c in unconfirmed)
                                       for c, m in courses],
                              load=dict(status=verdict.load.status, units=verdict.load.units,
                                        ceiling=verdict.load.ceiling), notes=notes))
        moved = [p for t in draft.terms for p in t.moved]
        rejoin = _term(next((t for t in reversed(draft.terms) if t.moved), draft.terms[-1]).term)
        keys[draft.variant] = (rejoin[0], draft.requests)
        drafts.append(dict(variant=draft.variant, label=f'Draft {draft.variant}', terms=terms, summary=dict(
            rejoinAfter=rejoin[1], specialClassRequests=sum(p.mode == 'special_class_request' for p in moved),
            summerCourses=sum(p.mode == 'summer' for p in moved), requests=draft.requests,
            majorWarnings=sum(len(t.verdict.warnings) for t in draft.terms),
            beyondCurriculum=draft.beyond_curriculum)))
    return dict(drafts=drafts, fastest=min(keys, key=keys.get), fastestLabel=words['fastest'],
                notice=words['notice'])


def clarification_view(answer, course_labels) -> dict:
    """Only canonical unknowns supply choices; never extract courses from generated prose."""
    courses = []
    fields = list(answer.missing_facts)
    if answer.decision is not None:
        fields.extend(answer.decision.unknown_conditions)
    for field in fields:
        prefix, _, course_id = field.partition(':')
        kind = {'completion_unknown': 'completion', 'enrollment_unknown': 'enrollment'}.get(prefix)
        code = course_labels.get(course_id)
        if kind and code and code != course_id and len(code) <= 240:
            entry = {'code': code, 'kind': kind}
            if entry not in courses:
                courses.append(entry)
    values = ({i.name: i.value for i in answer.structured_context.inputs}
              if answer.structured_context is not None else {})
    scope = ({'programId': values['program_id'], 'curriculumId': values['curriculum_id']}
             if values.get('program_id') and values.get('curriculum_id') else None)
    return {'courses': courses[:32], 'scope': scope}
