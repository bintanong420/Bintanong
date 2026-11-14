"""Owner, 29 Oct 2026: reviewed Filipino shorthand expansion, used for understanding only.

Whole words only; a single letter is expanded only when typed lowercase; uppercase "PWD" (person with
disability) and course codes stay as typed. The student's own wording is what the conversation displays.
Dropped-vowel words copied from the shorthand test questions were left out at the owner's request.
"""
from __future__ import annotations

import re

_REVIEWED = {
    'pwede': ('pwd', 'pwde', 'pde', 'pwdi'), 'paano': ('pno', 'pano', 'panu'), 'ano': ('anu',),
    'bakit': ('bkt', 'bket'), 'kailan': ('kelan',), 'gaano': ('gano',), 'ilan': ('ilng',),
    'magkano': ('mgkno', 'mgkano'), 'sino': ('cno', 'cnu'), 'hindi': ('di', 'hnd', 'hndi'),
    'ako': ('aq', 'aku'), 'yung': ('ung',), 'kahit': ('kht', 'khit'), 'mag': ('mg',), 'pag': ('pg',),
    'maka': ('mka',), 'para': ('pra',), 'naman': ('nmn',), 'lang': ('lng',), 'na lang': ('nlng',),
    'kasi': ('kc', 'ksi'), 'sana': ('sna',), 'talaga': ('tlga',), 'din': ('dn',), 'rin': ('rn',),
    'siguro': ('cguro', 'sguro'), 'na ba': ('nb',), 'sakin': ('skn',), 'subject': ('subj',),
    'prerequisite': ('prereq',), 'prerequisites': ('prereqs',), 'requirement': ('req',),
    'requirements': ('reqs',), 'first': ('1st',), 'second': ('2nd',), 'third': ('3rd',), 'fourth': ('4th',),
    'sigarilyo': ('yosi',), 'paninigarilyo': ('pgyoyosi', 'pagyoyosi'), 'naninigarilyo': ('nagyoyosi',),
}
_LETTERS = {'b': 'ba', 's': 'sa', 'p': 'pa', 'd': 'hindi'}  # lowercase only
_WORDS = {short: full for full, shorts in _REVIEWED.items() for short in shorts}
# A word ends at a space or punctuation; a following hyphen is allowed so prefixes ("mka-graduate") expand.
_TOKEN = re.compile(r"(?<![\w'’\-/])([A-Za-z0-9]+)(?![\w'’/])")


def _expand(match):
    word = match.group(1)
    if word in _LETTERS:
        return _LETTERS[word]
    if word == 'PWD' or len(word) == 1:
        return word
    full = _WORDS.get(word.casefold())
    if full is None:
        return word
    return full[0].upper() + full[1:] if word[0].isupper() else full


def expand_shorthand(text: str) -> str:
    return _TOKEN.sub(_expand, text)
