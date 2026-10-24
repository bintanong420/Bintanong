"""Student view of a validated answer (owner O4, 23 Oct 2026: students never see variable or function names).

The canonical `CandidateAnswer.text` is what the validator checks byte for byte, so it is never changed; it stays
the researcher diagnostic. The student view drops the check-scope line, evidence ids and citation lines (citations
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


def humanize_codes(line: str, language: str) -> str:
    index = _LANGUAGES.index(language) if language in _LANGUAGES else 0

    def phrase(match):
        value = match.group(2).strip()
        words = _PHRASES.get(match.group(1))
        return f'{value}: {words[index]}' if words else value  # an unknown code never shows its prefix
    return _CODE.sub(phrase, line)


def student_text(answer) -> str:
    words = _WORDS.get(answer.language, _WORDS['en'])
    listed = tuple(f'{words[key]}: ' for key in ('conditions', 'missing', 'dependency'))
    scope = (tuple(f'{label}: {answer.structured_context.operation};' for label in _SCOPE_LABELS)
             if answer.structured_context is not None else ())
    claims = {f"{c.text} [{', '.join(c.evidence_ids)}]": c.text for c in answer.claims}
    cited = tuple(f'[{card.evidence_id}] ' for card in answer.citations)
    shown = []
    for line in answer.text.splitlines():
        if (scope and line.startswith(scope)) or (cited and line.startswith(cited)):
            continue
        if line in claims:
            line = claims[line]
        elif line.startswith(listed):
            line = humanize_codes(line, answer.language)
        shown.append(line)
    return '\n'.join(shown)
