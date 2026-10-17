# Phase 06 foundation and compiler increment

Owner resumed Phase 06 on 17 October 2026 in `feat/p06-prolog-janus-rules`.
This resolves the prior phase-alignment wait. Preserve Task 1 (`67ed4bd`).
The checkpoint already records approval of the next compiler proposal; this
bounded increment implements its offline preparation, not runtime reasoning.

## Verified worktree readiness

- All 62 local dataset files match the p05 copy by relative path and SHA-256.
  Use this worktree's `dataset/` explicitly; no originals were moved or edited.
- `.env`, root/frontend `node_modules`, and `backend/artifacts` are present.
  Presence does not establish frontend installation/build health.
- Default Python is 3.13.7, with Pydantic but no pytest or Janus. Reuse
  `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`;
  its pytest/Pydantic/PDF reader are usable. No local backend venv is needed now.
- SWI-Prolog 10.1.15 is installed. Janus is absent from that Python environment;
  integration/installation requires its separate scoped dependency decision.
- Both model weights exist at `C:/Coding-projects/bintanong_workspace/MODELS`.
  The standing `C:/Coding-projects/MODELS` path is absent; local `.env` still names
  it. No model path, weight, environment file or standing storage rule was changed.
  Resolve that mismatch before model execution; this increment needs no models.
- Raw path/hash/size inventory is outside Git at workspace `audit-evidence/`
  `p06-foundation-20261017/asset-inventory.json`. Model SHA-256 values are
  SEA-LION `df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1`
  and Gemma `3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80`.

## Bounded compiler contract

Student capability advanced: a future version-scoped prerequisite/dependency
check with original evidence. Evidence path: reviewed authoring ledger to an
inactive, reproducible Prolog preview. Phase exit advanced: compilation integrity;
no eligibility evaluation or final Phase 06 exit is claimed.

`backend/bintanong_symbolic/compiler.py` exposes
`compile_curriculum_preview(ledger) -> dict`. It rebuilds the ledger through Task 1
and checks canonical equality, including digests/flags; a caller cannot forge a
derived field, stale review or privilege claim. Invalid structure/references reject.
Valid drafts, unresolved expressions and a detected prerequisite cycle return
explicit diagnostics and no Prolog. Cycle detection is deterministic and reports
one witness, not an exhaustive enumeration. All branches of alternatives are
inspected conservatively; a witness needs human review, not an automatic denial.
Co-requisites remain distinct and are not treated as prior-completion edges.
Ruling: valid authoring text rejected by the stricter atom-quoting contract is held
as `unrenderable_text`, with original values preserved; never normalize a policy
value silently merely to make its preview render.

Reviewed, structurally complete records can produce only `candidate_*` ground
facts: scope, course identity/content, facts, explicit expression trees, original
records, sources and review receipts. Preserve expression order and provenance.
Reuse the existing atom quoting contract. Do not regenerate legacy flat extraction
rules, silently flatten alternatives, invent facts or emit an eligibility predicate.
The existing extraction candidate compiler remains unchanged.

Output includes compiler version, ledger digest, preview text/digest, diagnostics,
source states and a digest of the complete result. It always states
`activation_allowed=false`, `eligibility_executable=false`, `approval_id=null`.
Pending source states remain pending and are listed as release holds; a review
receipt does not authenticate a reviewer or authorize institutional execution.
Even fully reviewed synthetic input retains the inactive release hold. No file
write, consulting of real-source Prolog, registry change, dependency or network use.

## Inline implementation and verification

Use executing-plans and TDD; preserve the existing p06 worktree. No new worktree.
Synthetic fixtures only in `tests/test_symbolic_compiler.py`.

- [x] RED: reviewed fixture must yield detached deterministic candidate facts;
  draft/unresolved/cyclic records must yield diagnostics without Prolog.
- [x] GREEN: implement the pure compiler, reusing Task 1 and atom quoting.
- [x] Boundaries: forged ledger/digests, stale receipts, dangling references,
  nested alternatives/co-requisites, source holds, quoted data/injection and
  missing values. Parse synthetic output as data in installed SWI-Prolog with
  a timeout; never consult it as institutional rules.
- [x] Run focused/related regressions, docs hygiene and phase validation; one
  fresh final code review. Record exact commands/results in the checkpoint.
- [x] Commit explicit cohesive files using Conventional Commits.

Product `0a2faa8`; final related checks: 315 passed. Docs/phase: 534 passed /
11 subtests. One final reviewer found the quote incompatibility (RED2, fixed)
and stale README (fixed). Exact commands/logs are in the active checkpoint.

## Human source-to-rule review

Review small batches in this phase. For each proposed real translation show the
exact original page/region, source/version/hash, program/curriculum, literal
prerequisite wording and proposed expression in plain language. Ask about actual
meaning/coverage/exception choices; record the answer against the exact content
digest. Carry blanks/cutoffs/conflicts as unresolved, never verified none.
Reuse previously confirmed source fields; a new logic translation may need review
without reopening their transcription. Separate researcher translation review,
institutional source authority and activation. No real translation is approved
by this foundation or by tests. The [first two-translation packet](2026-10-17-phase06-translation-review-01.md)
is prepared; the actual owner answer remains pending.

## Reading policy

Routine resume: INDEX, progress, Phase 06 plan/checkpoint and this phase's linked
records. Earlier phase files only for a specific dependency/boundary; this resume
read only the Phase 05 final handoff's frontmatter/outcome. No bulk history reads.
Shared scope/source-gap policy and required Context evidence still apply.
