# Course facts plan: titles, units, year/semester (Phase 11 step 2h, draft for owner approval)

Status: **draft, not approved**. Owner request 24 Oct 2026: "What subjects are in first year BSIT?" must be
answered (`owner-decisions-ledger.md`). Same data unblocks course-title matching (probe R5) and unit questions (R6).

## Problem (verified 24 Oct)

The 39 hosted curriculum ledgers hold per course only `course_code`, `prerequisites` and provenance/review
fields (BSIT: 53 courses, fact keys = `course_code` only). The Prolog bundles are generated from them, so they
know prerequisites only. Prospectus PDFs are not retrieval chunks. No source holds the answer at runtime.

## Goal and acceptance criteria

1. For a reviewed curriculum, "What subjects are in first year, first semester of BSIT?" lists every printed
   course of that term (code, title, units) with the prospectus citation; no course missing or extra versus the
   printed page (owner spot-check per batch).
2. "How many units is CC 5 in BSCS 2018-2019?" answers the printed units (lecture/lab as printed, no arithmetic).
3. A printed course title ("Data Structures and Algorithms") resolves to its code within the student's curriculum
   when exactly one course carries it; two matches keep the "give the printed code" reply.
4. Unreviewed curricula stay unanswered for these questions (the E1 referral), never guessed. Source gaps
   (clipped, merged or unreadable cells) are recorded and stated, never filled.
5. No embedding/similarity decides a listing; answers come from version-scoped structured facts.

## Design

- **Facts** (authoring source of truth, per AGENTS.md): add `course_title`, `units` (as printed, split lecture/lab
  only where printed), `year_level`, `semester` to each ledger course, each with its own source spans and
  `review_state`. Ledger schema version bump; Prolog rules unchanged.
- **Extraction**: reuse `backend/bintanong_tools/prospectus_extractor` (it already parses year/semester
  banners via `placement.py`/`audit.py` and course rows) plus the geometry checks of the prerequisite author
  script (drawn row rules, cell-own char runs, U+FFFE wrap repair). Byte-identical regression of existing
  prerequisite ledgers after any shared-script change.
- **Review**: owner batches per curriculum page, showing program, code, title, units, year/semester and the
  printed text inline (owner cannot open files). Only reviewed facts are exported.
- **Runtime**: a deterministic structured lookup `list_term_courses(curriculum, year, semester)` and
  `course_facts(curriculum, course)` over the reviewed facts (no Prolog needed; same release pin). Router gets
  one new operation name; renderer writes host text in en/fil/Taglish. Title aliases join the catalog only when
  unique within the curriculum.

## Tasks (dependency order)

1. Extraction dry run for BSIT and BSCS 2018-2019: compare extractor output with the printed pages; list gaps.
2. Owner review batches for those two (code/title/units/term), record decisions in a dated review record.
3. Ledger schema + authoring/compiler support for the new facts (TDD, synthetic fixtures); regenerate the two
   ledgers; byte-identical prerequisite regression.
4. Hosted upload of the two updated ledgers (database change: owner approval first; migration-history rules).
5. Lookup operations, router operation, renderer text, catalog title aliases (TDD each; live re-check of the
   R5/R6/R10 probe questions; roster run to confirm no routing regressions from the prompt change).
6. Remaining 37 curricula in batches as review time allows; each stays unanswered until reviewed.

## Estimate, risks, decisions needed

- Medium: tasks 1-5 for two curricula about 1.5-2 working days plus owner review time; the other 37 depend on
  layout quirks (BS Architecture needed several rulings).
- Risks: layout variation per program; the router prompt change can shift other outputs (re-run roster);
  unit notation differences (e.g. "3 (2/1)") need owner readings.
- Owner decisions: approve this plan; which curricula first (proposal: BSIT + BSCS 2018-2019); approve the
  hosted ledger upload when it is ready.
