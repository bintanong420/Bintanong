# Candidate curriculum selection implementation plan

> Execute inline under executing-plans and test-driven-development; one fresh
> final review. Owner authorizes continuation from `b8866b9` and has settled the
> eight row/46 field, 12-scenario evidence and conditional cohort guidance decisions.

**Goal:** Prepare and select program/version restrictions for the eight inactive
curriculum chunks without changing source registers or the runtime retrieval API.

**Architecture:** A standalone offline preparation module builds a source/event-bound
catalogue from reviewed rows and pending chunks. A deterministic selector returns
candidate chunk/version IDs or a focused scope gap. The original chunks stay intact;
the catalogue carries suggested program/curriculum tags and owner usage conditions.
Runtime release/scope authorization remains a separate later gate.

**Tech stack:** Existing Python3.13.7 contracts/pytest; no new libraries or database work.
**Spec:** Latest next action in `2026-10-14-reviewed-heading-metadata-report.md`, master10.2
and actual owner curriculum/cohort guidance recorded in its ignored packet.

## Constraints and behavior

- Undergraduate/read-only, Phase05; candidate-only output/zero active releases.
- Preserve old curricula and the newer printed proposal, original bytes/gaps/history.
- Explicit version selects only that program/version. Wrong-program version returns
  unavailable; never substitute a nearby programme or newest edition.
- An unspecified program requires clarification. A program with one supplied version
  can select it using the owner's continued-validity guidance. Multiple versions require
  the applicable curriculum unless trusted caller context identifies new incoming use.
- Incoming context selects the uniquely owner-assigned newer incoming version;
  continuing context alone does not imply older curriculum. An explicit older version
  conflicting with incoming context requires clarification rather than silent override.
- No admission-year cutoff, query-text cohort inference, automatic supersession or
  whole-source institutional approval. Pending registers/whole-source audits stay unchanged.

## Review focus

1. Version IDs belonging to another program cannot leak into a selection.
2. Old/new coexisting versions cannot be collapsed by ranking or year ordering.
3. Partial, changed, duplicate or unbound chunks/row fields/event hashes fail preparation.
4. Stored catalogue tampering and contradictory incoming/version hints fail closed.
5. Unknown incoming/continuing student context must not invent a numeric cohort boundary.

## Task1: Offline catalogue and selector

Create `backend/bintanong_tools/document_ingest/candidate_curriculum.py` and synthetic
`tests/test_candidate_curriculum.py`; no changes to runtime, SQL or existing adapters.

Interfaces:
`prepare_candidate_curriculum_catalogue(bundle, pending_chunks, *, sources,
review_events, source_versions, version_assignments) -> dict`;
`select_candidate_curriculum(catalogue, *, program_id=None, version_id=None,
student_context=None) -> dict`. Assignment entries are explicit trusted caller program
IDs/labels, curriculum labels, usage (`single_supplied`, `older_coexisting`,
`newer_incoming`), the existing owner event hash and source-linked evidence reference.
Selector contexts are only `None`, `new_incoming`, `continuing`; arbitrary values error.

- [x] Tests first: wrong/default/program/version/cohort selection, mixed versions,
  unchanged chunks, exact accepted fields and source/event/hash/coverage failures.
  Expected unknown BSCS =>needs_scope; explicitold=>old only; incoming=>new only;
  continuing alone=>needs_scope; wrong-program ID=>unavailable; single programme=>matched.
- [x] Observe RED for missing implementation; implement minimum validation/selection.
- [x] GREEN and related preparation/context/retrieval regressions; commit verified unit.

## Task2: Actual restrictions and verification

- [x] Build separate ignored catalogue for six selected versions/five programs/eightchunks.
  Use accepted scenario/program labels and actual cohort event; do not promote registers.
- [x] Replay existing multilingual cases without changing wording: curriculum scenarios
  Q2/8–12 get candidate selection traces, 18 language variants; policy cases stay separate.
  This is scope selection, not semantic retrieval/Precision@k/Recall@k calibration.
- [x] Inspect source-governance states and produce a concrete readiness matrix describing
  what existing evidence satisfies and which institutional/release evidence is absent.
  Do not invent formal source approval or repeat settled human judgments.
- [ ] Full suite/no cache/external basetemp, one fresh review, fix consequential findings
  in one TDD pass, seal evidence, update plan/report/index/checkpoint/handoff/progress.
  Keep Phase05 blocked, preserve isolated branch and ignored history, explicit commits.

Context: scope thesis physical17–18, runtime routing PNG, master10/11, active Phase05
plan/checkpoint/handoffs and dataset guide consulted; no scope/routing discrepancy.
Execution evidence lives under workspace audit-evidence per owner rather than generic
skill scratch directories. Existing isolated p05 worktree remains; no install/download.

## Ledger

- Baseline clean `b8866b9`; metadata/cohort content decisions complete, no repeat work.
- Preflight: Task2 consumes exactly Task1's offline catalogue/selector; runtime untouched.
- Ruling: keep restrictions in a separate catalogue until governed publication can
  enforce them. Editing pending chunk IDs/scope after creation would invalidate bindings;
  runtime wiring now would imply unauthorized source use. Cost: this is preparation
  and must be enforced by later publication/retrieval integration before active use.
- Task1 pending RED; Task2 pending Task1.

- Task1 candidate implemented; initial missing-moduleRED and missing-source-limitRED,
  final related82tests132subtests pass2.04s. Task2 actual scope traces5programs/6versions/
  8chunks/46fields/18variants pass;1203previous hashes/registers unchanged.
- Initial full predates final source-limit guard; final full/review/closure pending.
- One fresh final review complete: one Important, zero Critical/Minor. Six mutation
  subcases reproduced RED; one TDD correction pass replays original candidate
  construction, GREEN83tests/138subtests2.52s. Actual catalogue/traces/source bindings
  unchanged; full post-review run pending. No second review or deferred findings.
