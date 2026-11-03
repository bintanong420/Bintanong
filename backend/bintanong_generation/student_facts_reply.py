"""Host wording for course results the student stated (memory/eligibility plan, Tasks 1-2).

The stated state is kept as said, so an unattempted course is never called a failure."""
from __future__ import annotations

_STATES = {
    'en': dict(passed='you passed {c}', failed='you failed {c}', not_passed='you have not passed {c} yet',
               not_taken='you have not taken {c} yet', taken_unknown='you took {c} (the result was not stated)',
               enrolled='you are taking {c} this term', not_enrolled='you are not taking {c} this term'),
    'taglish': dict(passed='passed mo na ang {c}', failed='failed ka sa {c}', not_passed='hindi mo pa na-pass ang {c}',
                    not_taken='hindi mo pa na-take ang {c}',
                    taken_unknown='na-take mo na ang {c} (hindi pa sinabi ang result)',
                    enrolled='naka-enroll ka sa {c} ngayong term', not_enrolled='hindi ka naka-enroll sa {c} ngayong term'),
}
_JOIN = {'en': ', and ', 'taglish': ', at '}
_NOTED = {'en': 'Noted: {facts}. I will use this in this chat for your selected curriculum.',
          'taglish': 'Noted: {facts}. Gagamitin ko ito sa chat na ito para sa napili mong curriculum.'}


def _language(language):
    return 'en' if language in ('en', 'unknown') else 'taglish'


def stated_facts(pairs, language) -> str:
    """pairs: (state, printed course label) in the order stated."""
    lang = _language(language)
    phrases = [_STATES[lang][state].format(c=course) for state, course in pairs]
    return phrases[0] if len(phrases) == 1 else ', '.join(phrases[:-1]) + _JOIN[lang] + phrases[-1]


_ASSUMED = {'en': 'This answer assumes, as you asked, that {facts}. It is not saved as your record.',
            'taglish': 'Assumption lang ito base sa tanong mo: {facts}. Hindi ito sine-save bilang record mo.'}


def assumption_text(assumptions, language, shown) -> str:
    """assumptions: '<state>:<course id>' what-if premises of this check."""
    pairs = [(a.split(':', 1)[0], shown(a.split(':', 1)[1])) for a in assumptions]
    return _ASSUMED[_language(language)].format(facts=stated_facts(pairs, language))


def noted_text(fields, language, shown) -> str:
    """fields: 'noted_<state>:<course_id>' entries; shown maps an internal course id to its printed code."""
    pairs = [(field[len('noted_'):].split(':', 1)[0], shown(field.split(':', 1)[1])) for field in fields]
    return _NOTED[_language(language)].format(facts=stated_facts(pairs, language))
