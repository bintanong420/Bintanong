"""Host wording for a turn the host could not follow (audit A03, 4 Nov 2026).

A conversational repair ("huh i already said it") is never answered with a source gap or an office referral. When
the previous turn's context names a course or topic, the reply names it back; otherwise it says plainly that the
host lost track. Only ids from session context are used, shown by printed code; never stored chat text.
"""

PREVIOUS = ('previous_course:', 'previous_topic:')

_WORDS = {
    'en': dict(known='You asked about {thing} earlier — is that the one you mean? Tell me what you\'d like to know '
                     'about it, and I\'ll check.',
               topic='the {name} topic',
               lost='Sorry, I lost track — which subject or topic are you asking about?'),
    'taglish': dict(known='Tungkol sa {thing} ang tanong mo kanina — iyan ba ang ibig mong sabihin? Sabihin mo kung '
                          'ano ang gusto mong malaman tungkol dito, at iche-check ko.',
                    topic='{name} topic',
                    lost='Sorry, na-lost track ako — anong subject o topic ang tinatanong mo?'),
}


def dialogue_text(missing, language, shown=str) -> str:
    words = _WORDS['en' if language in ('en', 'unknown') else 'taglish']
    for field in missing:
        kind, _, value = field.partition(':')
        if kind == 'previous_course':
            return words['known'].format(thing=shown(value))
        if kind == 'previous_topic':  # a topic id such as "handbook_shifting" reads as its words after the source
            name = value.split('_', 1)[-1].replace('_', ' ')
            return words['known'].format(thing=words['topic'].format(name=name))
    return words['lost']
