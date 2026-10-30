"""Owner, 30 Oct 2026: reviewed Filipino words for the English terms printed in penalty rows, used for
understanding only ("use it but uniporme we dont really use this but the rest definitely yes").

Whole words only, so "malaking" never reads as "alak". Affixes change the root ("kumopya", "nangongopya"),
so each accepted form is listed. The student's own wording is displayed; answers keep the printed English.
"""
from __future__ import annotations

_REVIEWED = {
    'cheating': ('kopya', 'kumopya', 'kumukopya', 'kinopya', 'nangopya', 'nangongopya', 'mangopya',
                 'pangongopya', 'pagkopya', 'nagkopya'),
    'examination': ('pagsusulit',),
    'smoking': ('yosi', 'nagyosi', 'magyosi', 'nagyoyosi', 'pagyoyosi', 'sigarilyo', 'paninigarilyo',
                'naninigarilyo', 'nagsisigarilyo'),
    'bullying': ('bully', 'nambully', 'nambubully', 'binully', 'binubully', 'mambully'),
    'drinking': ('alak', 'lasing', 'nalasing', 'naglalasing', 'paglalasing'),
    'gambling': ('sugal', 'nagsusugal', 'sumugal', 'pagsusugal', 'pustahan', 'pumusta', 'nagpupusta'),
    'littering': ('kalat', 'nagkalat', 'magkalat', 'pagkakalat', 'basura'),
}
_TERMS = {form: term for term, forms in _REVIEWED.items() for form in forms}


def printed_terms(word: str) -> tuple[str, ...]:
    """The printed English term a reviewed whole Filipino word names, or () for any other word."""
    term = _TERMS.get(word.casefold())
    return () if term is None else (term,)
