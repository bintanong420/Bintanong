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
- Shared use with master's students or a School of Law reference does not exclude
  an undergraduate-applicable clause. Exclude content specifically intended only
  for unsupported audiences or otherwise inapplicable to undergraduates. The owner
  confirmed five selected policy areas for provisional undergraduate research on
  14 October 2026, retaining all existing limitations; this is not school validation
  or authorization to support graduate/professional programs.
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

- Use a human-in-the-loop for source-content decisions and recurring source-handling
  dead ends. If clipped/incomplete text, ambiguous layout, field selection or chunk
  sizing needs a judgment about what content to retain, show the owner the exact
  original page/region, affected wording and proposed treatment before proceeding
  with dependent content changes. Explain whether the problem comes from the PDF,
  extraction or added metadata; do not make the owner diagnose packaging overhead.
- After a bounded extraction/partition attempt fails, do not keep trying equivalent
  variations without new evidence. Notify the owner of the result and request a
  focused judgment when the next step depends on source-content choices. Continue
  independent verification and ordinary technical fixes where authorized; this is
  not a requirement to ask about every test failure or routine implementation choice.
- Record the owner's decision in current progress and the active checkpoint, then
  apply it without reopening the same question. Known original cutoffs remain
  untouched, with their limitations attached; do not repeatedly request missing
  text that the owner has already said is unavailable. A retention/transcription
  decision does not establish institutional authority, effectivity or activation.

- For every prompt concerning Bintanong, read and apply `.agents/skills/bintanong-handoff-reminder/SKILL.md`, which routes to `.agents/skills/bintanong-phase-handoff/SKILL.md`. Reload both after context rollover before continuing work.
- Use `plans/plan_current_progress/current_progress.md` for current changes, decisions, blockers and the next action; update it after material work and before ending a turn or pausing. Maintain formal phase plans/checkpoints/handoffs in `plans/` through the handoff skill as well. Read `plans/ingestion/` only when the current task or relevant master-plan section requires ingestion evidence; preserve its existing documents.
- Maintain Bintanong plans, specifications, decisions, progress and developer handoffs in this repository, including isolated repository worktrees. Do not keep the only current plan in an external scratch directory.
- Start from `plans/INDEX.md`, `plans/plan_current_progress/current_progress.md`, and the relevant sections of `plans/master_implementation_plan_original_long.md`. When ingestion evidence is needed, consult `plans/ingestion/README.md` for its plans and delivery status. Git and fresh verification outrank historical notes.
- When starting or resuming a phase, including in another CLI/account or after context rollover, inspect `Context/` alongside the handoff documents. Read the relevant pages of `Context/bintanong_thesis_for_context.pdf` and inspect `Context/bintanong_full_runtime_routing_architecture.png` to check scope and routing assumptions; record the context consulted and any discrepancy in the active checkpoint. Use targeted pages rather than repeatedly reading the entire thesis.
- For original-source or practice-exam work, read `plans/dataset-locations.md`: the ignored dataset now lives at repository-root `dataset/`; the prospectus corpus is `dataset/PalSU Undergraduate Prospectus Website Dump/`. The old backend dataset directory was moved on 14 October 2026. Resolve the corpus root explicitly, preserve originals and relative paths, and update that guide after a move. Historical sealed evidence may retain old absolute paths: use the recorded relocation mapping and verify byte hashes; do not rewrite history or recreate the old directory.
- Record implementation discoveries in repository decision records and current status. Preserve the master plan and historical plan snapshots; do not infer phase completion or institutional approval from candidate-code delivery.
- Keep task datasets, private inputs, generated conversions/Prolog/JSON, test temporaries and raw execution evidence untracked under `C:\Coding-projects\bintanong_workspace`, using ignored `audit-evidence` folders. This owner location instruction supersedes the earlier outside-all-Git-roots rule; do not stage private artifacts. The main checkout is `bintanong_workspace\Bintanong`; this phase's code lives in isolated `worktrees\Bintanong\p05`. Existing external model weights remain under `C:\Coding-projects\MODELS` (`MODELS_DIR=C:/Coding-projects/MODELS`); never duplicate or download model weights inside Git.
- `plans/progress_plans/` is an ignored bulk scratch-copy area. Curate text documents into `plans/` before explicit staging; never stage the bulk tree or use broad staging to publish documentation.
- Preserve owner changes and external workers. Use explicit staging, no attribution, system Python 3.13, pytest without cache and external basetemp. No installs/downloads or dependency/lock changes without an applicable owner instruction.
- Commit frequently in small, cohesive, verified units ("commit early and often"); avoid accumulating large uncommitted working-tree diffs across multi-step tasks.
- Before creating, amending or rewording every commit, read and apply
  `.agents/skills/conventional-commits/SKILL.md`. Use clear Conventional Commits
  messages for code, tests, documentation, checkpoints and handoffs. Select the
  type and summary from the actual staged change; preserve published history.
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

## Owner decisions to preserve across CLI sessions

These are standing owner instructions from the Phase 05 conversation. Read them
alongside the phase ledger; do not ask the owner to repeat settled decisions.
The latest cleanup/resume record is
`plans/2026-10-14-dataset-relocation-and-cli-handoff.md`.

- This is thesis development/testing, not imminent official university guidance.
  Continue provisional offline retrieval with the supplied public undergraduate
  sources while school validation is pending. Keep candidate status and source
  limitations visible; owner research authorization does not fabricate school approval.
- The owner planned to submit the source-use/authenticity/current-school-year letter
  on 15 October 2026 and does not expect a same-day reply. Hold school verification
  until actual evidence arrives; raise it before institutional activation or when
  the owner reports a response. Do not repeatedly block ordinary development on it
  or infer approval from elapsed time. Printed source year is not verification date.
- The owner confirms 2018–2019 curricula remain valid when no newer edition for the
  same program is supplied. Older students can retain an older curriculum when
  editions coexist; incoming students use the supplied proposed 2025–2026 BSCS
  curriculum under owner guidance. Preserve its proposed label. Unknown student
  curriculum needs clarification; similarity, age and continuing status do not pick it.
- Eight selected curriculum rows/46 source fields and expected evidence for all
  12 scenarios were confirmed by the owner. Do not reopen those reviews. Original
  Charter physical103 step3 cuts off after "for"; handbook physical47 has conflicting
  completion deadlines. Preserve these gaps/conflicts, without appending text or
  inventing a precedence rule. See scope/source-gap policies and confirmed evidence report.
- The accepted retrieval set has 12 scenarios/36 English, Filipino and Taglish
  variants. Show proposed new or changed benchmark questions to the owner before
  testing them. The exact thesis wording "Pwede ko bang kunin ang CC5 kahit bumagsak
  ako sa CC4?" is case `cs-cc5-failed-cc4-tl` and ranked CC5 first. The observed mismatch
  was the approved paraphrase "CS student ako: pwede ko bang i-take ang CC5 kahit failed
  ako sa CC4?" (`cs-cc5-failed-cc4-taglish`); do not conflate their scores or wordings.
- Additional source data is expected when the owner says it is ready. The incoming
  batch will not include more college-specific Citizens' Charters; it may include
  memoranda such as vehicle gatepass. Undergraduate student gatepass transactions
  are in study scope even if staff also use the service. No new memo has been
  supplied or approved; retain the existing university Charter and review actual
  new source audience/content/effectivity at intake.
- On 15 October 2026 the owner supplied and chose to retain the student-facing
  vehicle/gatepass, special-class-fee and enrollment additions, plus USG
  Constitution/election material, for provisional undergraduate review. This
  supersedes the older no-memo-received note and interim advice to defer them.
  Do not reopen retention or exclude a source solely for image quality or year.
  Use the human to confirm difficult/consequential fields in short batches;
  unreadable/cropped content remains a documented gap. Retention does not approve
  all transcriptions, benchmark wordings, school authority or activation. Start
  from `plans/2026-10-15-additional-source-human-review.md` and the current checkpoint.
- The owner reports that CSG constitutions pattern/reference the USG Constitution.
  Preserve the statement as reported. Use only reviewed explicit CSG provisions
  in the supplied USG source; do not infer unsupplied college-specific rules or
  claim separate college constitutions have been acquired.
- On 15 October 2026 the owner replied `confirm F1`, accepting F01–F09 in the
  short human-review packet: seven special-class unit/hour/amount mappings,
  the printed rate/weekly hours and date/resolution/effectivity readings.
  Do not reopen that batch. Preserve its printed sums, unknown per-student
  division and cropped acknowledgement; content confirmation is not school
  authority/current-year verification or activation. Next source batch is V01–V06.
- Continue authorized work until a new human source-content decision is genuinely
  needed, the task is finished, or a verified progress checkpoint is ready for handoff.
  Record decisions/results/next action in this repository. Reuse completed setup,
  model assets and compatible saved vectors; do not repeat conversions or settled
  questions merely because a CLI changed. Candidate results remain recoverable;
  formal Phase 05 completion/Phase 06 advancement follows the existing exit gates.
