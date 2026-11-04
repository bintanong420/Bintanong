# Course abbreviations: offline delivery, 4 November 2026

Owner task: generate title initials, numbered initials (joined and spaced), and
three-letter word starts for reviewed course identities within a curriculum.
Branch `feat/course-abbreviations`, base `d3e454da`, worktree `p12ab`.
No active numbered phase; Phase 12 remains complete and Phase 13 cancelled.

## Change and decision

`backend/bintanong_runtime/research.py`: `_title_abbreviations` replaces the private
initials helper; `research_catalog` builds base aliases first, then checks all
candidate abbreviations against course ownership within each curriculum.
Case/punctuation/spacing-normalized collisions with another course's code, title,
accepted code alias or proposed abbreviation suppress that abbreviation on every
affected course. Printed code aliases remain present for CatalogEntry validation.
Title uniqueness is curriculum-scoped. No routing files, rules, printed labels,
dependencies, configuration or source records changed.

The owner's explicit task supersedes the 29 October shared-initials behavior:
colliding abbreviations are omitted. Stopwords are exactly `and of the in for to
a an with on`, including when first. Existing trailing Roman numeral handling
and the multi-word abbreviation boundary remain. Matching uses the existing
case-insensitive resolver. No new promise about live ambiguity replies is made.

## Verification

Python: `C:/Coding-projects/bintanong_workspace/audit-evidence/p12-env-20261031/venv/Scripts/python.exe`.
All runs used `-B -m pytest <files> -p no:cacheprovider --basetemp <root>/<name> -q`,
where root is `C:/Coding-projects/bintanong_workspace/audit-evidence/p12ab-bt`.
Family files: sorted `tests/test_*.py` matching `^test_(routing|runtime_research|orchestration)`.

| Run | Selection / basetemp name | Result |
| --- | --- | --- |
| Before | families / `abbreviations-before` | 813 passed, 28.40 s |
| RED | catalog / `abbreviations-red` | 12 failed, 28 passed; missing forms/shared initials |
| Initial GREEN | catalog / `abbreviations-green` | 40 passed |
| Interim | families / `abbreviations-after` | 828 passed |
| Scope RED | catalog `-k identical_titles` / `abbreviations-scope-red` | 1 failed, 43 deselected |
| Final catalog | catalog / `abbreviations-catalog-final` | 44 passed, 1.16 s |
| Final families | families / `abbreviations-final` | 829 passed, 27.13 s |

Synthetic tests cover generated forms, skipped stopwords/punctuation, numeric and
Roman suffixes, shared initials/word starts, collisions with codes/code aliases/
titles/other abbreviation types, curriculum isolation, schema validation and
existing mixed/lower/uppercase matching. `git diff --check` passed.
Full repository suite and live model/backend/GUI checks were not run. No services
were started, called or stopped; no installs, downloads, push or activation.

## Read-only real-ledger check

Input: `audit-evidence/p12-memory-gates-20261104/ledgers/bscs-2018-2019.json`
under `C:/Coding-projects/bintanong_workspace/`; 54 courses, 54 catalog entries.
SHA-256: `c815ca6964512a6b2c422372dbbd818b67fd3fe30acd647a8a32da1510bcc367`.
Ignored output: `audit-evidence/p12ab-bt/course-abbreviations-bscs.json`.

| Printed code | Printed title | Generated abbreviations |
| --- | --- | --- |
| CC 4/L | Data Structures and Algorithms | DSA, DatStrAlg |
| CS 7/L | Networks and Communications | NC, NetCom |
| CS 1/L | Discrete Structures 1 | DS1, DS 1, DisStr1 |
| CS 3 | Discrete Structure 2 | DS2, DS 2, DisStr2 |

Skipped: 4 course/abbreviation assignments, 2 distinct normalized forms:
FE on PATH Fit 2 and Electronics/L; ME on MATH ELEC and PATH Fit 1.

Context consulted: current index/progress, Phase 12 handoff, master sections 3,
11 and 13, owner ledger, undergraduate scope policy, thesis physical 17–18 and
39–44 (pypdfium2 text), runtime routing PNG. Catalog aliases do not change the
LLM routing / structured Prolog / documentary RAG boundaries. Thesis closed-world
examples remain illustrative; missing evidence retains the repository's unknown
semantics. No new source-content or institutional-authority decision.

## Delivery blocker and next action

No commit created: Git add/commit could not create
`C:/Users/Hawksprey/source/repos/Bintanong/.git/worktrees/p12ab/index.lock`:
`Permission denied`. No retries after the failure, per owner instruction.
Next: from an environment with Git index permission, explicitly stage the five
delivered paths and commit `feat(runtime): add unique title-based course abbreviations`.
Do not push or edit routing as part of this task.

- `backend/bintanong_runtime/research.py`
- `tests/test_runtime_research_catalog.py`
- `plans/owner-decisions-ledger.md`
- `plans/plan_current_progress/current_progress.md`
- `plans/2026-11-04-course-abbreviations-results.md`

## Coordinator correction (Claude, 4 Nov 2026)

Codex's version dropped initials shared by two courses and the 29 October rule that a small first word counts, and
added an owner-ledger entry saying it superseded the 29 October decision. That changes an owner ruling, so it was
reverted: the 29 October initials are kept exactly (shared initials stay on both courses so the router asks which;
DSA and DS1 already came from them). Only the new forms are added: the first three letters of each main word joined
(NetCom) and the spaced number form (DS 1), each only when it names one course in its curriculum and matches no printed
code. The ledger entry and the current_progress edit were not kept. Real BSCS 2018-2019: CC 4/L DSA, DatStrAlg;
CS 7/L NC, NetCom; CS 1/L DS1, DS 1, DisStr1; CS 3 DS2, DS 2, DisStr2.
