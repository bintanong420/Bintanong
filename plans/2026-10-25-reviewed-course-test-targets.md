# Live Supabase course test targets,25October2026

Read-only inspection of the app's active p09-research-selected-20261022 research
release through its existing runtime/anon PostgREST client (Supabase MCP unavailable).
All39 linked curriculum ledgers rebuilt successfully with matching review digests.
No credentials in this report; no database writes/source reviews/activation.

2132 course records:965 reviewed direct prerequisite expressions,1167 unresolved.
Every supplied curriculum has at least one unresolved rule, so global affected-course
queries can still hit the confirmed partial-list fallback. Course identities/facts
being reviewed does not establish complete prerequisite coverage.

BSCS2018–2019:54 reviewed identities;33 reviewed direct rules,21 unresolved.
BSCS proposed2025–2026:55 reviewed identities;31 reviewed direct rules,24 unresolved.
Curriculum versions differ: select BSCS2018–2019 for the following targets.

| Course | Title | Reviewed prerequisites (all required) |
| --- | --- | --- |
| CC 3/L | Computer Programming 2 | CC 2/L |
| CC 4/L | Data Structures and Algorithms | CC 3/L and CS 1/L |
| CC 5/L | Information Management | CC 3/L and CC 4/L |
| CS 2/L | Object-Oriented Programming | CC 3/L |
| CS 13/L | Information Assurance and Security | CC 5/L |

Each row has a reviewed identity/direct expression, no pending identity reference,
and preserved prospectus source spans on physical page1. Original printed codes,
titles and source-backed relationships are retained.

## Suggested manual probes

- What are the prerequisites of CC5? Expected reviewed CC3/L and CC4/L requirements.
- Passed na ako sa CC2. Pwede ko na bang kunin ang CC3? Expected eligible prerequisite result.
- Passed na ako sa CC3 at CC4. Pwede na ba ako sa CC5? Expected eligible prerequisite result.
- Failed ako sa CC4. Pwede ba akong kumuha ng CC5? Expected unmet prerequisite result.
- What are the prerequisites of CS13? Expected CC5/L requirement.

These are optional manual diagnostic inputs, not additions to the accepted evaluation
roster and not proof of actual enrollment permission, university validation or currentness.

## Fresh direct runtime verification

Fetched the release-linked BSCS2018–2019 ledger again by its exact digest, rebuilt
and bound research authorization, executed real Janus/Prolog with synthetic student
facts for all five target courses. All required prerequisites passed -> eligible;
first required prerequisite failed -> ineligible.10/10 checks passed, all coverage verified.
This validates direct prerequisite results only; no live router/model/browser claims.

Ignored raw evidence/scripts: workspace audit-evidence/p11-20261025/reviewed-course-testing/
live-reviewed-courses.json, direct-runtime-checks.json, read_reviewed_courses.py,
check_direct_prerequisites.py. No private student records were used.
