# Repository documentation and development rules

## Study scope: undergraduate academic affairs only

- Apply `plans/undergraduate-scope-policy.md` to every task, including handbook,
  Citizens' Charter, curriculum, extraction review, retrieval, rules and evaluation.
  Bintanong supports PalSU undergraduate academic affairs for the 2026–2027 study.
- Exclude Medicine and Law professional programs, graduate programs, laboratory
  school, and procedures intended for faculty or staff from the supported corpus,
  active review queue, benchmark cases and executable rules. Undergraduate Nursing
  and Health Sciences remain in scope. Do not expand scope to fill extraction gaps.
- Positive policy tests and benchmark fixtures must stay within that undergraduate
  scope. Remove dedicated excluded-audience policy cases when found, while keeping
  generic synthetic parser/geometry tests and negative scope/privacy/security tests.
  Staff-record rejection and undergraduate laboratory-unit checks remain valid.
- Select by a clause/service's intended audience and applicability, not keywords
  or the whole PDF's title. Student-facing services can legitimately name staff
  roles; those references do not make the service a staff-only procedure.
- Keep complete original PDFs, raw conversions and historical evidence unchanged.
  Derive undergraduate-only review/corpus candidates separately. A shared original
  heading such as undergraduate/School of Law is provenance, not authorization to
  support Law. Use its undergraduate content only after applicability review.
- On every phase start/resume or scope decision, read thesis physical pages17–18
  (printed16–17: Scope and Limitations), alongside other relevant Context pages.
  Record the consulted scope evidence in the active checkpoint. Unknown or mixed
  applicability stays unresolved and cannot be activated by default.
- Remain a read-only advisory tool. Missing authorized information requires
  clarification, an unavailable-information response or university-office referral;
  it does not authorize autonomous acquisition, enrollment, grade changes or COR
  issuance. Private uploads stay separate from institutional knowledge.

## Incomplete or defective institutional sources

- Apply `plans/source-gap-policy.md` to all institutional source review, ingestion,
  retrieval, rule authoring, answer generation and evaluation. Record clipped,
  missing, unreadable, malformed or conflicting source content with its original
  hash/page/field and affected claims. Preserve complete originals and history.
- Correct extraction/transcription omissions only from visible original evidence
  and actual review decisions. A defect in the university-provided original remains
  a documented gap; never invent a continuation, omitted condition or process end.
- Carry known gaps with the affected evidence. Answer from verified visible content
  only, state the limitation when it affects the student's question, and indicate
  unavailable information or refer to the relevant named university office. Do not
  present a broken process as complete or compile its unknown portion into rules.
- Missing or blank content does not mean zero, no fee, no prerequisite, no penalty,
  automatic approval or completion. A known gap limits the affected capability;
  do not repeatedly ask the owner to reconstruct unavailable source content or
  expand the study scope. These are standing requirements, not a deployment claim.

## Repository workflow

- For every prompt concerning Bintanong, read and apply `.agents/skills/bintanong-handoff-reminder/SKILL.md`, which routes to `.agents/skills/bintanong-phase-handoff/SKILL.md`. Reload both after context rollover before continuing work.
- Use `plans/plan_current_progress/current_progress.md` for current changes, decisions, blockers and the next action; update it after material work and before ending a turn or pausing. Maintain formal phase plans/checkpoints/handoffs in `plans/` through the handoff skill as well. Read `plans/ingestion/` only when the current task or relevant master-plan section requires ingestion evidence; preserve its existing documents.
- Maintain Bintanong plans, specifications, decisions, progress and developer handoffs in this repository, including isolated repository worktrees. Do not keep the only current plan in an external scratch directory.
- Start from `plans/INDEX.md`, `plans/plan_current_progress/current_progress.md`, and the relevant sections of `plans/master_implementation_plan_original_long.md`. When ingestion evidence is needed, consult `plans/ingestion/README.md` for its plans and delivery status. Git and fresh verification outrank historical notes.
- When starting or resuming a phase, including in another CLI/account or after context rollover, inspect `Context/` alongside the handoff documents. Read the relevant pages of `Context/bintanong_thesis_for_context.pdf` and inspect `Context/bintanong_full_runtime_routing_architecture.png` to check scope and routing assumptions; record the context consulted and any discrepancy in the active checkpoint. Use targeted pages rather than repeatedly reading the entire thesis.
- For original-source or practice-exam work, read `plans/dataset-locations.md`: the ignored corpus currently lives deep under `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump` and the owner intends to relocate it. Resolve the corpus root explicitly, preserve originals and relative paths, and update that guide after a move.
- Record implementation discoveries in repository decision records and current status. Preserve the master plan and historical plan snapshots; do not infer phase completion or institutional approval from candidate-code delivery.
- Keep task datasets, private inputs, generated conversions/Prolog/JSON, test temporaries and raw execution evidence untracked under `C:\Coding-projects\bintanong_workspace`, using ignored `audit-evidence` folders. This owner location instruction supersedes the earlier outside-all-Git-roots rule; do not stage private artifacts. The main checkout is `bintanong_workspace\Bintanong`; this phase's code lives in isolated `worktrees\Bintanong\p05`. Existing external model weights remain under `C:\Coding-projects\MODELS` (`MODELS_DIR=C:/Coding-projects/MODELS`); never duplicate or download model weights inside Git.
- `plans/progress_plans/` is an ignored bulk scratch-copy area. Curate text documents into `plans/` before explicit staging; never stage the bulk tree or use broad staging to publish documentation.
- Preserve owner changes and external workers. Use explicit staging, no attribution, system Python 3.13, pytest without cache and external basetemp. No installs/downloads or dependency/lock changes without an applicable owner instruction.
- Commit frequently in small, cohesive, verified units ("commit early and often"); avoid accumulating large uncommitted working-tree diffs across multi-step tasks.
- Use test-driven development for implementation, bug fixes and behavior changes: write a focused regression, observe its expected failure (RED), implement the smallest correction, then verify GREEN and relevant regressions before committing. Record commands and results in the active phase checkpoint and current progress; use synthetic fixtures in tracked tests and keep source-derived evidence ignored.
- Read and apply appropriate available `SKILL.md` workflows when necessary, including test-driven-development for implementation, systematic-debugging for failures, and verification-before-completion before success claims. Continue the active phase from verified Git and handoff evidence after an account/session change; do not repeat completed setup or infer approval from candidate delivery.
- Naturally utilize available MCP tools in the development and handoff workflows: GitHub MCP (`github-mcp-server`) for inspecting branches/commits/PRs and remote repository synchronization, and Supabase MCP (`supabase` alongside local CLI) for database health, schema inspection, advisor checks, and migration workflows.
- Candidate output remains inactive. Runtime/API/Docker work, executable Prolog, release activation and institutional use retain their applicable approval boundaries.
- Parser success and absence from an extraction-refusal queue do not establish
  content accuracy or human approval. Include consequential source fields intended
  for release, especially numeric grades, penalties, conditions and executable-rule
  inputs, in the applicable independent review even when structural parsing passes.
  State review-queue coverage and estimates explicitly; do not call a selected
  problem queue a complete handbook/Charter audit or corpus accuracy result.
- Apply `plans/service-table-association-policy.md` to procedure/service tables.
  Review complete logical client steps across page breaks. Keep each agency action
  linked to its processing time, responsible-person label, office and conditions;
  line wrapping does not create new roles. Preserve explicit shared fees and source
  references separately from blank continuation cells. Do not flatten columns into
  unrelated lists or approve a whole step from a partial field correction.
