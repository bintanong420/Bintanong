# PR #20 — Orca ADE / Codex implementation runbook

**Destination:** bintanong420/Bintanong, branch feature/p12-unified-answer-pipeline → p12-dev. **Status at creation:** planning-only draft; no source code port or tests executed yet.

## Safety and scope

Read AGENTS.md, plans/INDEX.md, plans/plan_current_progress/current_progress.md, scope/source-gap policies, thesis physical pp.17–18, architecture/master plan, docs/development/2026-11-07-pr20-deep-audit.md and plans/2026-11-07-pr20-unified-answer-pipeline-plan.md BEFORE changing runtime code. Do not touch the p12-evaluation-harness gathering worktree/service, shared model or data, production configs/secrets, source records or institutional release status. No forced Git push, automatic merge, uncontrolled runtime switch, or arbitrary model-generated Prolog goals. Input languages: English/Filipino/Taglish; output English or Taglish. Reviewed blank prerequisite cell exception is specific to prerequisites.

## 1 — Isolated worktree and branch preflight (PowerShell)

~~~powershell
cd C:\Coding-projects\bintanong_workspace\Bintanong
git fetch origin --prune
git worktree list
git status --short
git rev-parse origin/p12-dev
git rev-parse origin/feature/p12-unified-answer-pipeline
$wt = "C:\Coding-projects\bintanong_workspace\worktrees\Bintanong\p12-pr20"
# A new web-created branch may have no local ref yet.
if (git show-ref --verify --quiet refs/heads/feature/p12-unified-answer-pipeline) {
    git worktree add $wt feature/p12-unified-answer-pipeline
} else {
    git worktree add -b feature/p12-unified-answer-pipeline $wt origin/feature/p12-unified-answer-pipeline
}
cd $wt
git status --short
git merge-base --is-ancestor origin/p12-dev HEAD
~~~

If that branch is already checked out in another worktree, use its safe existing checkout; never force-move it. Confirm the p12-dev base SHA and current worktree changes. If origin/p12-dev moved, merge it into the task branch by a normal merge with semantic conflict resolution, not by resetting the task branch.

## 2 — Import prior draft source in exact order

PR #18 has three commits and PR #19 adds two on top. Import once on top of the current PR #20 branch (no whole-branch merge afterwards):

~~~powershell
git cherry-pick -x bd904be829c274c8359454123428479a136c3a63
git cherry-pick -x c835d862710a35662503a7c711f559803d0320ec
git cherry-pick -x 1f8ee4a47b59a630c04305521f98a9f9bb9e476f
git cherry-pick -x 4c61e6cb83c85e0d9a5a93bbf8505de1f84ecf46
git cherry-pick -x 27ef19ec9cd565ced81c3c6746bb0ad225c18f7b
~~~

**These are individual steps, not a script to run through conflicts.** If a cherry-pick stops, inspect git status and both versions of the relevant function, resolve, stage, run git cherry-pick --continue, then proceed. If equivalent code already exists, record proof in a tracked source-port ledger before skipping. Never use wholesale “theirs” over 51 newer mainline commits. Ensure imported #18 domain and calibration gates still fail closed, and #19 compound.py is *still* candidate-only, no student activation.

## 3 — Commit sequence in the SAME #20 PR

A. Source integration and focused safety tests.

B. Multi-topic partial-document evidence: per-topic/per-part statuses and provenance; preserve successful topic when another independent one fails; conflicts/release errors fail closed.

C. Versioned AnswerPresentationV2 and backwards-compatible SSE text, strict Zod, safe React part/status/source rendering; no raw HTML; no unvalidated drafts.

D. Wire the existing PR #19 two independent eligibility checks and optional one documentary part behind default-OFF research flag. Validate same curriculum/version/release/operation targets and unknown grades. No arbitrary/more-than-two/dependent operation execution.

E. Language and clarification parity, server-owned dialogue, English/Taglish reply, negation and edition-independent regression tests; compiler OFF/ON paired measurements without changing default.

F. Full verification/handoff: test evidence with actual SHA, model, release, flags, source limits, blocked/unrun cases, latency stage definitions, and owner review. Do not close #18/#19 before parity is proven.

## 4 — Focused and complete software gates

~~~powershell
# Repo root, Python 3.13 with appropriate locked backend dependencies
python -m pytest tests/test_routing_domains.py tests/test_retrieval_calibration_gate.py tests/test_compound_symbolic.py tests/test_routing_validation.py tests/test_routing_operation_coverage.py tests/test_routing_compile.py tests/test_orchestration_pipeline.py tests/test_orchestration_multi_topic.py tests/test_orchestration_adapters.py tests/test_orchestration_research_evidence.py tests/test_generation_pipeline.py tests/test_generation_part_slots.py -q
python -m pytest tests -q

# Frontend requires Node 24.21.0
cd frontend
npm ci
npm run typecheck
npm run test:ui
npm run build
cd ..
git diff --check
git diff --stat origin/p12-dev...HEAD
git status --short
~~~

Do not claim that passing Python/Node component tests means real Gemma / Supabase / SEA-LION / Prolog / PDF-backed behavior passed. Real model/source evaluations require a separate owner-authorized dev window and source pins. Record each execution as PASSED / FAILED / BLOCKED / NOT RUN. Preserve privately held source files.

## 5 — Push to the *existing* PR, not a second PR

~~~powershell
git fetch origin
git push --set-upstream origin feature/p12-unified-answer-pipeline
gh pr view 20 --repo bintanong420/Bintanong --web
~~~

If remote moved, reconcile by normal fetch/merge; no force push. Update PR #20's body/checklist as work is completed, with actual executed commands/results. Keep it Draft until reviewable, and obtain owner approval for any merge or activation. After #18/#19 capabilities are proven preserved, close those two **unmerged as superseded** with links to #20.

## 6 — Paste into Orca/Codex task input

> Implement ONLY PR #20, feature/p12-unified-answer-pipeline → p12-dev, in an isolated worktree. Read the checked-in PR #20 deep audit, implementation plan and runbook, plus AGENTS and thesis-required context. Snapshot current branches/worktrees first. Port #18 three commits and #19 two commits in the correct order, resolving conflicts by intent; do not overwrite newer p12-dev behavior. Then implement and test per-topic partial-document evidence before versioned backend/SSE/frontend presentation. Reuse #19's research two-check executor and integrate bounded Hybrid behind a default-OFF flag after per-part evidence is validated. Fix dialogue/clarification truthfulness and multilingual semantics under English/Taglish output decision. Preserve all source/curriculum/review/release and privacy guards, including the 4 Nov reviewed-blank-prereq exception; no proposed-as-operative curriculum or assumed grade pass. Run focused/full Python and frontend checks plus isolated real-source/model tests only when authorized. Capture exact executed SHA/config/test pass-fail-block counts and remaining unsupported shapes. Push solely to PR #20; do not force push, alter the evaluation harness, auto-merge, deploy, or close source PRs until equivalence is proven. Report any blockers precisely and leave the PR Draft.

**The existing Codex --yolo setting removes many confirmation prompts; it does not relax these repository boundaries or supply a test environment.**
