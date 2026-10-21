"""Owner-authorized research release inputs derived from reviewed records only.

Research mode (AGENTS.md, 21 October 2026) is development use of reviewed real data,
not school approval or institutional activation.
"""
from collections import Counter

from ..bintanong_routing.contracts import CatalogEntry, DocumentTopic


def _printed_forms(code):
    return {code, code.replace(' ', '')}


def _short_forms(code):
    # Owner alias rule: students may omit spacing and the printed "/L" suffix.
    return _printed_forms(code[:-2]) if code.endswith('/L') else set()


def research_catalog(ledger):
    """Course entries for reviewed identities; draft identities are left out."""
    courses = [c for c in ledger['courses'] if c['review_state'] == 'reviewed' and c['review_refs']]
    printed = {c['course_id']: _printed_forms(c['facts']['course_code']['value']) for c in courses}
    if sum(len(v) for v in printed.values()) != len(set().union(*printed.values()) if printed else ()):
        raise ValueError('duplicate_printed_course_code')
    short = {cid: _short_forms(c['facts']['course_code']['value']) for c in courses for cid in [c['course_id']]}
    counts = Counter(a for forms in [*printed.values(), *short.values()] for a in forms)
    entries = []
    for c in courses:
        cid = c['course_id']
        aliases = printed[cid] | {a for a in short[cid] if counts[a] == 1}
        entries.append(CatalogEntry(kind='course', entity_id=cid, program_id=c['program_id'],
            curriculum_id=c['curriculum_id'], aliases=tuple(sorted(aliases)),
            source_ref=c['source_version_id'], review_ref=c['review_refs'][0], reviewed=True))
    return tuple(entries)


def topic_menu(register):
    """One topic per reviewed subject with all of its reviewed claim strings, in register order."""
    subjects = {}
    for review in register['reviews']:
        subjects.setdefault(review['subject_id'], []).append(review['claim'])
    return tuple(DocumentTopic(subject_id=s, claims=tuple(dict.fromkeys(c))) for s, c in subjects.items())
