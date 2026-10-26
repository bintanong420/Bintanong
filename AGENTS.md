# Repository documentation and development rules

## Agent communication and ingestion workstream - owner, 26 October 2026

- Always respond to the owner in English. This is the engineering agent's reply
  preference; preserve the student chatbot's English/Filipino/Taglish behavior.
- Use relevant installed skills to supplement repository skills. Read their
  instructions before applying them; owner directions and repository boundaries
  take precedence, including the ingestion-only and hosted-Supabase restrictions.
- This workstream covers the ingestion pipeline and its local researcher review
  UI only. Read `plans/2026-10-26-policy-ingestion-workstream.md` before planning,
  implementing or resuming it; it is the implementation plan derived from the
  supplied feature plan and two-developer ownership workflow.
- Leave hosted Supabase untouched: do not connect to it or run hosted queries,
  review RPCs, staging, publication, activation, rollback, migrations or changes
  to data, schema, policies, credentials or configuration. Use isolated files and
  explicitly targeted disposable local databases for ingestion verification.
  A separate worktree does not make copied hosted configuration safe.
- Preserve the active hosted release, runtime pin and other developers' work.
  Coordinate shared-interface changes with their owner. Earlier hosted access
  permissions and general MCP guidance do not authorize access in this workstream;
  any future hosted operation requires a new explicit owner instruction.

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

## Real-data development - owner decision, 21 October 2026

- The owner directed: proceed with the real public PalSU sources and the reviewed
  structured/Prolog data in the development pipeline now ("it is public data
  anyways and the university will approve of it"); if data must change after
  the university responds, revisit it then. This supersedes holds that kept
  development and testing on fictional fixtures only.
- It authorizes development/testing use of reviewed real data (retrieval over
  real sources, executing reviewed BSCS prerequisite rules) in this research
  build. It is not public deployment, school approval or proof of currentness.
  Source-gap, undergraduate-scope, unknown-versus-unmet and privacy rules still
  apply; unreviewed or held fields (e.g. F04) stay unused.
- Owner decision, 21 October 2026: for matching what students type, a course
  code without spacing or the printed "/L" suffix (e.g. "CC5", "CC 5", "CC5/L")
  resolves to the printed code ("CC 5/L") within the student's curriculum.
  Answers keep the printed code; rules stay as printed; a short form that would
  match two courses is not created. This is not a unit/lab/equivalence finding.

## Curriculum reasoning and architecture alignment

- Standing owner direction, 16 October 2026: curriculum/prospectus work must follow
  the structured-knowledge and Prolog architecture, rather than treating every
  course question as a vector-retrieval problem. Read master sections 3, 11 and 13,
  thesis physical 39–44 and the runtime routing PNG when choosing the next relevant
  task. See `plans/2026-10-16-curriculum-symbolic-routing-clarification.md`.
- Keep course identities, program/curriculum versions, units, placement and reviewed
  prerequisite/co-requisite relationships as structured institutional facts.
  Supported prerequisite, eligibility and dependency checks use reviewed,
  deterministic Prolog rules. Exact course-fact lookups can use version-scoped
  structured operations without semantic search once that capability exists.
- Reviewed structured records and rule specifications are the authoring source of
  truth; generate versioned Prolog fact/rule bundles from them. Do not maintain
  independently edited prerequisite copies or hand-code a separate custom rule
  for every course. Preserve original spans, exceptions and curriculum scope.
- Use RAG for source explanations and documented procedures where text is needed;
  use Hybrid when a symbolic decision and document explanation are both required.
  Retaining curriculum text for citations does not require routing every course
  question through embeddings or using similarity to decide eligibility.
- Owner explanation, 21 October 2026: one student message may mix parts, e.g. a
  course/prospectus question, then (after a period, "and" or similar) a question
  on what to do next. The LLM router splits it into parts: course eligibility or
  prerequisite parts go to Prolog (`structured`), procedure/next-step parts go to
  RAG (`document`), and the whole message routes Hybrid. Each part is answered
  by its own path; documentary parts use per-part answer slots (`parts` profile).
- Owner reply-language rule, 21 October 2026: English question -> English reply;
  Filipino -> mostly everyday Filipino (unavoidable English terms allowed);
  Taglish -> Taglish (Tagalog structure, English for terms like submit, fee,
  office). Never deep Tagalog such as "isusumite" or "nakasaad". This applies to
  model claims and host-rendered text, including Hybrid/Prolog result lines.
  Owner addition: the reply matches the user's communication style overall
  (language mix and casual/formal register), not only the language label.
- Missing grades, curriculum, course identity or rule coverage remain unknown,
  distinct from a documented unmet condition. No recorded prerequisites does not
  prove that a course has none. Preserve all-of/any-of/co-requisite semantics only
  when the actual source establishes them; the thesis example is illustrative.
- Before adding another diagnostic, sidecar or parameter sweep, name the student
  capability, intended evidence path, phase exit requirement and unresolved question
  it advances. Reuse completed evidence; do not expand curriculum retrieval work
  merely to make every accepted question look answerable through RAG. Keep useful
  component probes separate from final routing/capability evaluation and stop a
  diagnostic once its stated question is resolved.
- The owner approved D1–D4's four scenarios / 12 exact language variants and
  expectations at `d2abc8d`; the accepted roster is 75 variants. Do not ask for
  their wording acceptance again. Acceptance does not mean all 75 need fresh
  retrieval experiments or that structured eligibility has been implemented.
- This architecture direction preserves existing source-content holds, candidate
  inactivity and formal phase gates. It does not authorize Phase 06 advancement,
  executable institutional rules or activation before their applicable boundaries.

## Prompt engineering and validation - owner decision,19October2026

- Owner20October2026 asks to preserve the researched response-time recommendation.
  Read `Context/response-time-recommendation.md` when evaluating or changing latency.
  Its15-20s warm student-visible target and conditional20-30s complex-Hybrid range
  are proposals requiring measurement/student validation,not an achieved SLA.
- Owner direction,20October2026: assess response time in the context of the RAG
  and neuro-symbolic architecture. Never sacrifice answer accuracy for speed;
  retain required evidence/reasoning/validation and reject quality regressions.
  Research prototypes may disclose latency limits, but architecture alone does
  not establish acceptable student waiting time or justify weaker safeguards.
- Latency reporting must distinguish warm pipeline,outer backend request,cold
  startup/first response,connection/readiness and student-visible end-to-end time.
  Record excluded factors and unavailable metrics explicitly,including Supabase,
  network/API/browser work and queueing;do not present a backend-only observation
  as browser end-to-end latency. See `plans/2026-10-20-response-time-measurement-contract.md`.
- Read `plans/2026-10-19-prompt-engineering-and-validation-decision.md` in
  Phase07 and subsequent initial-build phases. The owner accepted prompt guidance,
  examples and deterministic guards, with a maximum one-week extension for added
  accuracy work before defense. Carry this decision into later phase plans/handoffs.
- Prompt engineering guides the existing Gemma/Bintu at inference time; it does
  not train parameters or change weights. Do not describe it as model training.
  No fine-tuning, LoRA/QLoRA or learned soft-prompt tuning is part of this build;
  future training needs a demonstrated need and a new explicit owner decision.
- Preserve LLM semantic routing, structured/Prolog curriculum reasoning and RAG
  documents, matching English/Filipino/Taglish response preferences. Validate
  actual per-language performance separately from schema/guard success; keep
  evaluation families separate from prompt examples and disclose remaining errors.
- The deadline does not waive source, privacy, institutional-release or phase
  gates. Freeze the best verified candidate at the improvement cutoff rather than
  starting an unbounded prompt/model sweep. See the record for exact boundaries.

## Natural student questions and intended responses

- Accepted benchmark wordings and their recorded limits (12/36, six/18, nine T1/T2/U3;
  D1-D4 above) are in `plans/owner-decisions-ledger.md`; do not ask for them again.

- Standing owner direction,15October2026: normal users need not say they are
  undergraduates or name a source/memo/date. Undergraduate academic affairs is
  the website's supported context; explain it in website guidelines or equivalent
  scope information. Exact website copy/placement remains future design work.
- Answer natural questions from applicable reviewed evidence and include a concise
  source/date/section reference. Users should not have to discover or select the
  memo first. Preserve material source gaps, conflicts and cohort/date limitations.
- Prefer the latest applicable reviewed material available for the same subject
  and audience. Cosine similarity and k-NN measure relevance, not source recency,
  authority or applicability; scope/version metadata and recorded source decisions
  must guide evidence selection as well. This research-design preference does not
  establish institutional supersession or settle a held field/specific conflict.
  A newer source for another cohort/program does not replace an applicable older
  curriculum. Preserve the settled old/proposed BSCS rules and vehicle choice.
- Website audience context does not establish program, curriculum, cohort, grades
  or eligibility. Clarify missing facts when they materially change the answer;
  do not repeatedly ask every user to declare undergraduate status/source details.
- Explicit faculty/staff-only, Medicine, Law, graduate or laboratory-school requests
  should receive a clear notice that Bintanong covers undergraduate academic
  affairs and cannot answer that excluded procedure/program question. Do not
  substitute undergraduate rules. Determine the intended service/audience in
  context; staff roles within an undergraduate service remain legitimate.
- Missing in-scope information needs an honest unavailable-information response,
  clarification or supported office referral. Keep this distinct from an excluded
  audience notice. Remain advisory; private uploads and institutional knowledge
  stay separate. These are intended requirements, not deployed behavior.

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

## Phase 05 completion boundary — owner approval, 17 October 2026

The owner explicitly approved Phase 05 completion as an offline research/software
milestone (“ye sure approve”), while university approval and actual authorized
real-source runtime validation remain outstanding institutional-release gates.
This supersedes earlier requirements tying Phase 05 completion to those gates.
Preserve all source states, known retrieval misses, uncalibrated response status,
source/edition limits, inactive candidates and release guards. Follow the revised
Phase 05 plan and verified final handoff; this is not school approval, deployment
permission or authorization to execute institutional rules in Phase 06.

## Repository workflow

- Each phase works in its own worktree under
  `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/` (Phase 09: `p09`;
  `plans/INDEX.md` names the active one). Keep routine handoff reading to the active phase
  MD files plus INDEX/current progress and required shared scope/architecture evidence. Open
  older phase documents only for a specific dependency or boundary. Conduct source-to-rule
  human reviews in short batches with exact original regions; reuse settled source
  transcriptions and record actual translation decisions.

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
- Keep the active index, current progress, checkpoint and handoff as compact current-state snapshots, not append-only activity logs. Replace superseded status, running-test notes and old next actions in place; retain one current next action. Aim for at most 80 lines each for index/progress, 120 for handoff and 160 for checkpoint; retain essential evidence even if a justified exception is needed. Keep exact source decisions, commands, hashes and long histories in their existing dated reports and link them only when relevant. Before condensation, record the last full snapshot commit so history remains recoverable with `git show`; do not copy bulk history into another default-read file. This owner-directed snapshot policy supersedes append-only wording in handoff skills. Do not add the same update to all four files: the index holds pointers/phase ledger, progress holds the latest change, checkpoint holds resumable state, and handoff holds delivery/recovery evidence. Update only files whose purpose or state actually changes.
- Start from `plans/INDEX.md`, `plans/plan_current_progress/current_progress.md`, and the relevant sections of `plans/master_implementation_plan_original_long.md`. When ingestion evidence is needed, consult `plans/ingestion/README.md` for its plans and delivery status. Git and fresh verification outrank historical notes.
- When starting or resuming a phase, including in another CLI/account or after context rollover, inspect `Context/` alongside the handoff documents. Read the relevant pages of `Context/bintanong_thesis_for_context.pdf` and inspect `Context/bintanong_full_runtime_routing_architecture.png` to check scope and routing assumptions; record the context consulted and any discrepancy in the active checkpoint. Use targeted pages rather than repeatedly reading the entire thesis.
- For original-source or practice-exam work, read `plans/dataset-locations.md`: the ignored dataset now lives at repository-root `dataset/`; the prospectus corpus is `dataset/PalSU Undergraduate Prospectus Website Dump/`. The old backend dataset directory was moved on 14 October 2026. Resolve the corpus root explicitly, preserve originals and relative paths, and update that guide after a move. Historical sealed evidence may retain old absolute paths: use the recorded relocation mapping and verify byte hashes; do not rewrite history or recreate the old directory.
- Record implementation discoveries in repository decision records and current status. Preserve the master plan and historical plan snapshots; do not infer phase completion or institutional approval from candidate-code delivery.
- Keep task datasets, private inputs, generated conversions/Prolog/JSON, test temporaries and raw execution evidence untracked under `C:\Coding-projects\bintanong_workspace`, using ignored `audit-evidence` folders. This owner location instruction supersedes the earlier outside-all-Git-roots rule; do not stage private artifacts. The main checkout is `bintanong_workspace\Bintanong`; phase code lives in isolated worktrees under `worktrees\Bintanong` (active: `plans/INDEX.md`). Existing external model weights remain under `C:\Coding-projects\bintanong_workspace\MODELS` (`MODELS_DIR=C:/Coding-projects/bintanong_workspace/MODELS`; the old `C:/Coding-projects/MODELS` no longer exists); never duplicate or download model weights inside Git.
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

## Pre-phase research - owner direction, 23 October 2026

- Before starting each implementation-plan phase (Phase 10 onward), and before writing its
  phase plan, do intensive research on: (1) how to optimize that phase's workstream
  (accuracy, latency, memory on the RTX 4060 8 GB target, maintainability); (2) the latest
  stable technologies, library releases, techniques and published practice relevant to it;
  (3) how to build it faster (reuse of existing modules/tests, parallelizable tasks, tooling,
  scaffolds, subagents, skipping work already done).
- Use current official sources (release notes, docs, model cards, papers) via web search and
  Context7; verify dates and versions, and cite them. Also reuse repository evidence (prior
  handoffs, latency profile, audit) so research does not repeat settled work.
- Record findings in `plans/YYYY-MM-DD-phase-NN-pre-phase-research.md` (options, evidence,
  expected gain, cost/risk, recommendation) and link it from the phase plan. Show the owner a
  short summary of recommendations before substantial implementation.
- Research proposes; it does not authorize. Changing a thesis-named technology (master section
  2), adding/upgrading dependencies, downloading models, or changing scope/phase gates still
  needs an explicit owner decision. Never trade answer accuracy, safeguards, privacy or
  source/scope rules for speed. Bound the research to the phase; it is not a reason to delay
  indefinitely or reopen settled decisions.

## Settled owner decisions

- Settled Phase 05/06 source-review, source-intake and benchmark decisions (review01-03,
  P06-T01/T02, G01-G03, F1/F04, V01-V06, E01-E04, USG/CSG, school-letter status) are recorded
  verbatim in `plans/owner-decisions-ledger.md`. Read it before any source review, source
  intake, benchmark wording, evaluation or school-validation step; never re-ask a decision
  recorded there or in a dated review record.
- F04's printed fee amount stays held until an actual owner answer. School/source approval is
  never inferred from elapsed time, "continue", a CLI change or candidate delivery; candidate
  output stays inactive.
- The owner is available for human verification: surface consequential or ambiguous source
  readings early, in short batches, showing program/course/title and the exact printed text
  inline (the owner cannot open repository files). Routine technical fixes proceed autonomously.
- Commits carry no Claude/AI attribution trailers (owner, 23 October 2026).
