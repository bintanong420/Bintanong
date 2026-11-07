# Current progress

Updated 6 November 2026. Development: `p12-dev` / `p12-post-gathering-fixes`.
Last full snapshot before condensation: `d2ad9fef` (recover with `git show`).
Gathering checkout and owner USG notes remain separate. No numbered phase is active;
Phase 12 research/software write-up is complete with disclosures; Phase 13 is cancelled.

## Delivered repairs

- [Benchmark repair checkpoint](../2026-11-06-owner-benchmark-repairs.md) records source/routing,
  registration, Taglish, grade-4 and INC fixes. Final code `bdf6d50a`, handoff `d2ad9fef`.
- R3 owner export: 21 tested, 20 Y / 1 N, 51 untested; grade answers needed brevity work.
  Subsequent live B13-TL registration and ID Taglish checks pass. Final English grade-4/INC
  outputs retain method, approval and source limitations; 25.4%/52.5% shorter than earlier candidate.
  Final focused grade gate: 174 pass. No frozen full-72 accuracy claim.
- Published integrated repairs to `origin/p12-evaluation-harness` at `c8cd43c8`, preserving
  remote architecture image commit `abd007b4`. Integrated gate: 585 pass. No force push.
  Publication worktree: `p12-eval-publish`; dev checkout remains isolated.
- [Earlier continuation](../2026-11-04-codex-continuation-log.md) and
  [isolation handoff](../2026-11-04-development-isolation-handoff.md) retain memory,
  prerequisite-listing, term checks and recovery-planner evidence. Do not repeat setup.

## Chat self-information index

Owner: capabilities and research scope must be callable in chat.
[Design and checks](../2026-11-06-system-information-index.md).
- Dedicated semantic `system_information` control and fixed English/Taglish index cover
  implemented features, undergraduate 2026–2027 research scope, excluded audiences,
  advisory limits, source gaps, private-PDF isolation and pending university validation.
- This is project metadata, not university-policy corpus content. No fake institutional citations,
  embedding changes, new dependencies or model weights. Academic answer ledgers stay mandatory.
- Coverage questions naming programs do not select student curriculum. Mixed self/academic
  clarification is preserved before policy-topic repair; it asks for separate questions.
- Initial RED: 6 failures; program-resolution RED: 2; mixed-request RED: 1.
  Focused gates: 337 pass; later 266 pass; final guard/compile/routing integration: 319 pass.
  Frontend workspace/transport: 22 pass; TypeScript passes. Gates overlap; not a full-suite total.
- Live router: four standalone EN/Filipino/Taglish/graduate-coverage questions select self-info;
  mixed capability+INC query finally selects `clarify` / `compound_request`. Earlier model outage
  and wrong mixed fallback were diagnosed, not counted as successful checks.
- Context rechecked: thesis physical17–18 and runtime routing PNG, master architecture and
  undergraduate scope policy. This adds a non-academic terminal control; academic routes unchanged.

## Runtime and boundaries

- Main web/API 3216/8021, dev web/API 3217/8022, shared model18088.
  Luna confirmed all five HTTP200; model container healthy; hidden keepalive PID72532.
- Dev API reloaded for index and shifting repair. Frontends/main/model untouched.
  Final wording reload ready200: root52864 / server46896; all five services HTTP200.
  Dev-only zero rate window and measured grade budget5120 remain ignored launcher overrides.
  Main controls unchanged. Keep `pause-dev-api` sentinel during intentional dev reloads.
- Wider [audit proposal](../2026-11-06-deferred-audit-remediation-proposal.md) remains deferred.
  Undergraduate advisory scope, unknown-versus-unmet, source conflicts, F04 hold,
  English/Taglish replies and private-upload isolation remain mandatory.

## Evaluation testing mode (6 Nov)
Owner asked to plan, not implement, a website testing mode for Accuracy/Precision/Recall/F1.
[Feasibility and plan](../2026-11-06-evaluation-testing-mode-plan.md). Owner: keep the 72 queries typed singly; both lists; keys with human judging; row10 Handbook.
[Tasks](../2026-11-06-evaluation-testing-mode-implementation.md) built: page `/dev/evaluation` on 3217/API 8022, off unless launcher sets passcode. Pilot 5/5 ran at `a73b6128`; final `1e499828`, focused 137 pass. Keys: rows1-10 draft, 11-24 human-judged unless owner confirms. Full suite not run; not a results claim.
7 Nov: owner running the 72 by hand via ngrok at pinned `1e499828`; 20 runs saved at last check. Stack is detached from the CLI; shut down API, web, ngrok and Docker memory when owner finishes. Ignored `audit-evidence/evaluation-testing-mode-20261106/chunk-reference/` has the searchable all-chunk PDF (C001-C560; read-back 560/560 IDs, 2160/2160 field values).
7 Nov final metrics sheet: owner's `Context/for_f1scoreprecisionaccuracyrecall.pdf` (42 = 14 RAG rows x 3, prerequisite rows removed). Ran all 42 PDF wordings on a separate API 8023 at the same pinned commit, own log (`audit-evidence/final-metrics-20261107/`), so the owner's 72-run log stayed at 20 lines; 42/42 completed, 8023 then stopped. Rule calibrated on owner's English Q1 (3/0/1/556): TP/FP = as-run top-3, FN = relevant chunk in the all-chunk top 3 that was not retrieved, TN = 560 minus the rest. Pooled, so recall can be overstated. Q11 x3 routed `clarify` (no retrieval, P shown as 0). Macro P .7679 / R .7623 / F1 .7396 / Acc .9977. Output: untracked `Context/for_f1scoreprecisionaccuracyrecall_completed.pdf` (pages 1-2 original). Owner approved the Q1 fix: page 1 now reads 3/(3+0) = 1, applied as a page overlay (`q1_fix.py`), with the original PDF unchanged. Owner asked for a Q11 rerun replying "Leaving PalSU" and approved fixing what blocked it. The router changes in `router.py` / `topic_selection.py` came with RED/GREEN tests in `test_routing_transfer_direction.py`:
- Once the transfer side is known, only that side's topics are offered.
- A reply to the direction question is offered only its reply topic, with its part pinned (the model had quoted the earlier question).
- Filipino "lilipat/magta-transfer [na po ako] ng ibang university" now counts as leaving.

Live, the "Leaving PalSU" routing prompt went 8319 -> 7362 tokens (7416 usable). All three Q11 wordings now answer from the 2025 Charter, pp. 11-12. Q11 counts: EN 2/1/0/557; TL and Taglish 2/1/2/555. Macro P .8155 / R .8099 / F1 .7858 / Acc .9977. Q11 ran on newer code than the other 41 rows and than the owner's pinned 72-run. 8022 still runs the old code until restarted.
Open gap: `evaluation/system_metrics.py` cannot count a relevant chunk in neither top-3 list, so recall is overstated for unkeyed rows. Proposed `FN: C123, C145` in the page's Note box; awaiting owner yes/no; scorer change needs RED/GREEN and no page or API restart. Undecided: RAGAS install/judge, BATAYAN source, Integration box rename.

## RAGAS branch (7 Nov)
Branch `p12-ragas-benchmark` in worktree `p12`. Owner approved: separate venv (ignored
`audit-evidence/ragas-20261107/`, ragas 0.4.3, langchain-community pinned <0.4, frozen list kept), DeepSeek
`deepseek-chat` judge (key in that folder's `.env`, outside Git), local SEA-LION E5 embeddings, telemetry off.
Shared references `51048843`: `docs/evaluation/references/` = verbatim TP+FN chunks per Q1-Q14 (owner rule);
BERTScore pairs now carry them. Full 42-row run done (no errors, 481k in / 185k out tokens): faithfulness .52,
answer relevancy .58, context precision .90, context recall .75 (optimistic), factual correctness (precision) .57.
Relevancy is 0 on 7 rows where the judge called source-limitation notices noncommittal. Low faithfulness not
yet inspected; results are a research measurement, not yet reported.

## Next action

Index committed `11b2e015`; 3217 proxy chat returned HTTP200 with `system_information`.
[Shifting repair](../2026-11-06-program-shifting-repair.md): exact “Pano po lumipat ng kurso?”
retrieved the right policy but generation quoted only cross-college section 4.1. Both college branches
and Registrar guidance now use clean exact source quotes for generic whole-program questions;
FAQ companion cue and conditional office closing repaired at `9830a030`: worker 309 / parent 57 pass.
Exact 3217 proxy question returned answered/Taglish with both branches, FAQ and Registrar guidance.
Closing grammar correction `a5e5a6a0` passed 57 tests after its RED; final dev-only reload is ready.
Adaptive [procedure source fit](../2026-11-06-adaptive-procedure-source-fit.md) now addresses
the good-moral report without a blanket source switch: menus expose reviewed workflow
bindings; whole selected procedures retain step facts within the existing eight-claim bound.
Policy, explicit source and requirements-only scope remain. `b5312a47` committed;
reviewed five-case good-moral router checks pass; later gate362 pass.
Round4 [intake](../2026-11-06-round4-benchmark-intake.md): latest63Y/6P/3untested;
good moral/gate pass all partial, shifting FinalY but verbose, B15 form-location note remains.
Shifting short-referral cleanup `e8a848a1`:141 tests pass, source quotations retained.
Removal form is reviewed Charterphysical112 step1 (Registrar's office); new bounded
client-step hints expose it. Context/aggregate binding regressions fixed; pinned145topicsload;
`622b68b0` committed; optional selector hints reduced to fit existing8192modelcontext.
Reviewed client-step object phrases expand candidates only, preserving semantic source selection.
All3gate-pass router variants pass; compound grade4/form correctly splits Handbook/Charter.
`f048a75c` final combined gate501 pass. Live3217 good moral/gate pass/compound grade4+form
all answered with correct sources; form Registrar location now present, source limits retained.
Gate-pass partial-coverage notice is now outside cited claims; condition/support guards unchanged.
Final `b8a59e02` gate-pass HTTP200/answered includes memo guidance and incomplete-process notice.
Notice gate152 / malformed-field26 pass; earlier combined501 pass (overlapping, no full72 claim).
All automated queries stopped. API12524/server56864 ready200, allfive200, keepalive36880 active.
New [request/location overflow](../2026-11-06-good-moral-request-location-overflow.md): exact
“Paano mag-request ng Good Moral? Saan po ito kinukuha?” added too many optional examples.
Distinctive-label hints/global3-example bound: selector7749->7240tokens;338tests pass,
isolated router exactquestion passes. `c20c1d1a` live3217 exactquestion answered/Taglish,
Charter procedure/OSAS, HTTP9.92s (not browser time). API61132/server18844 ready200;
allfive200, keepalive36880. Automated queries stopped. Owner18:33 validation sign-off:
Final72Y; A07 inferred/waived, gate-pass selected-fragment condition retained.
[Publication](../2026-11-06-owner-signoff-publication.md): push origin P12 first, then working
branch, preserving remote image/history. Integrated542Python/22frontend/TypeScript pass;
[alignment audit](../2026-11-06-human-automation-alignment.md) checks reported behaviors,
four saved live outputs and gaps. Both origin branches verified at integrated `1685647e`,
P12 pushed first, working second; no force/runtime changes. Next: owner testing and remaining
explicitly unexecuted A07 cases; receipt follow-up is documentation only.
No new source/Supabase or runtime changes; no independent full72 execution claim.
