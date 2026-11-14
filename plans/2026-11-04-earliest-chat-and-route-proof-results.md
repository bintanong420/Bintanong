# Earliest-term chat and offering-source proof (4 November 2026)

Branch `feat/plan-chat`, worktree `p12-plan-chat`. Follows typed-plan chat `b324ec01` and condition/context
correction `a7d9a789`. Imported the independent off-semester checker `05395473` as `b29bf3fa`, excluding its
current-progress hunk; coordinator should integrate the original checker once and only cherry-pick this task's
new commit. No source contents, dependencies, model files, live services or phase boundaries changed.

## Earliest-term path

The existing LLM router selects `earliest_course_term` on a named reviewed course. The host requires a stated
starting year and semester and asks a specific start-term question when missing. A registered signature binds
curriculum/course/year/semester; neither a regex intent classifier nor a second extraction-model call was added.
Both compiler modes use the ordinary validation/scope/assertion guards.

The existing earliest-term helper executes reviewed Prolog checks and keeps the full prerequisite-chain proof.
Its raw result now binds curriculum, target, starting term and exact effective completion facts with a canonical
SHA256; orchestration compares that digest with the owning scoped context. Typed `EarliestTermAssessment`
retains those facts/digest, fixed inputs and source proof and validates them again. A result computed using a
stale pass instead of the student's stated failure is refused before it can answer. Evidence is pinned to the
same curriculum release and original source hashes, reassembled during preparation, and bound to the question
understanding and host answer. Unknown coverage produces unavailable information, not a guessed earliest term.

The host renders the existing English/Taglish explanation: prescribed semester only, explicit assumed passes,
no confirmed offering or approval, adviser referral. Rule spans are grouped by original source/page into cards
while preserving every text and citation. This avoids the 32-card limit rejecting a large proof; the existing
32-card/64KB evidence limits remain. No proof is truncated to make an answer pass.

## Offering routes are pinned evidence

Coordinator review found that carrying configured clauses without their source proof allowed invented conditions
to appear as Handbook quotations. Optional route evidence now uses already loaded reviewed chunks; no retrieval
or model call is added. `ReleasePin.plan_routes_sha256` binds the complete reviewed route configuration including
conditions and references. Optional `DocumentMember.passage_sha256` binds the validated passage's canonical text,
all citations/pages/locators, chunk id and source version. Fields absent on other pins are omitted from dumps.

Before display, route evidence must match the release, chunk membership, original PDF hash and complete passage
hash. Each full approved clause must occur in an actual nonblank printed field whose valid `span_indexes` cite
the clause's own page. Any unresolved source limitation refuses that route evidence. Shortened clauses, omitted
conditions, metadata-only text, forged field+clause content and coordinated clause/citation page corruption are
refused. The full checked route evidence participates in the ledger identity; exact source cards reach citations.
An unproven configured route cannot silently masquerade as a printed condition.

The independent checker correction adds existing `off_semester_request` confirmation when an unsuffixed
prescribed/retake course is planned in another printed semester. An end-to-end unsuffixed-plan case verifies the
condition reaches the student, with the printed off-semester clause and its page. Same semester in a later year
is unchanged. The checker does not change the student's request or persist assumed passes.

## Verification

Existing workspace Python 3.13.5 / pytest 9.1.1; `-B -m pytest`, `-p no:cacheprovider`, `-q`, external basetemp.
Raw evidence remains ignored at `C:/Coding-projects/bintanong_workspace/audit-evidence/`.

- Initial earliest operation: **12 RED failures** before wiring (`p12-earliest-chat-red.log`).
- Full-proof card budget: **4 RED failures** (`generation_evidence_limit`) before grouping source/page cards
  (`p12-earliest-cards-red.log`).
- Stale earliest facts: **4 RED failures**, an adapter using an invented pass answered too early before the
  effective-request binding (`p12-earliest-facts-red.log`).
- Coordinated page corruption and shortened clause: **2 RED failures** before canonical passage/config binding;
  final route boundary suite **11 passed** (`p12-route-citations-green.log`). Negative checks isolate content,
  field location and source-limit refusal rather than passing solely because an unrelated hash changed.
- Previous combined implementation: **131 passed** (`p12-plan-chat-delivery.log`), before the final reviewed
  config/passage and earliest-fact bindings. An older broad run was stopped while code was still changing and
  is partial evidence only (`p12-plan-earliest-regressions.log`); it is not a fresh full-suite pass.
- Final affected suite/result is recorded below after completion (`p12-final-bound-evidence2.log`).

Context/permissions continue from the typed-plan report: undergraduate/advisory scope, owner D1–D7, thesis
physical 17–18 and 39–44, routing PNG and existing handoff records. Shared current progress is coordinator-owned.
Next: coordinator integrates after compiler comparison, verifies the loaded real route proof, runs live typed-plan
and earliest smoke cases plus relevant language/program regressions. No live or student-visible latency claim here.
