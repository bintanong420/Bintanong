# Phase 11 resumed source-package preparation

Owner resumed25 Oct: frontend ready; integrate after remaining pending work. This continues the approved
supplementary-source plan; no new phase, institutional approval or public release.

## Compatibility correction

Fresh disposable-DB reproduction reached the expected selected-review codec failure after restoring
Docker with installed `docker desktop start`. The initial attempt failed only because Docker was stopped.
Ordinary blanks use `value: ""`, `source_blank: true`, `span_indexes: []`. Supplementary Python/SQL now
agree with the codec; null, content and invented spans reject. Original C1 strictness stays unchanged.

Focused RED:4 failures,2 passes,+5 passing subtests. A generated SQL JSON literal was initially invalid;
corrected with `to_jsonb(''::text)` before final GREEN. Final **42 passed,+26 subtests**,94.10s, across
`test_storage_supplementary_review.py`, `test_storage_supplementary_review_database.py`,
`test_runtime_multi_curriculum.py`, `test_runtime_research_catalog.py`. Fresh-context read-only review:
no actionable findings. Document-only embedding/review changes now change the root release identity;
unchanged curriculum rules retain their symbolic version; both factories are covered.

Command prefix: shared Python3.13 venv, `PYTHONUTF8=1`, `-X utf8 -B -m pytest -q -p no:cacheprovider`;
external basetemp/DB evidence. Logs under workspace `audit-evidence/p11-topic-filter-20261024`:
`resume-contract-red.log`, `resume-contract-green2.log`. Full `tests` suite on5440368 production:
**6635 passed,6 skipped,2 xfailed,+1595 subtests**,6 existing warnings,1483.77s; `resume-full-suite.log`,
`.exit=0`. This precedes the scoped budget/menu change below; that final tree has its own suite run.

## Source preparation

- Frozen authority report SHA256:`a619ba37500831b6db1a58306aa4f2b9b11c4909170b0b2d643335f39acf39b9`.
  Rebuilt the61-record draft against it; printed readings unchanged. Original PDF byte hashes verified;
  actual sources resolved from this worktree's ignored `dataset/`, not the absent historical p05 tree.
- Reused105 nonblank mapped fields, located114 further fields by original glyph regions, retained54
  ordinary blanks with no fabricated text/span. Punctuation-insensitive matching only locates already
  reviewed original-image transcriptions; it does not certify native text or make source decisions.
- Existing policy builders emit61 records, all passing the real codec, with8 limitations: untyped
  two-week penalty, malformed weapon exception, fraud precedence on2 rows, additional-measure
  applicability, missing22, Charter step3 cutoff and printed-total discrepancy.
- Exact E5 tokenizer, truncation/padding disabled: all61 fit480. One484-token record was corrected
  by shortening generated limitation wording only. Misconduct required pairs fit2048 (maximum1699
  observed); complete six-record Charter context needs3827 including citations and rejects2048.
  At sufficient diagnostic budget, all6 emit with no gaps. No field dropped or silently truncated.
- Owner delegated the choice: pre_enrollment4096, other topics2048, with live accuracy/latency checks.
  Exact recorded-decision excerpts/stable timestamps now bind event wrappers; original Charter event
  reused. Cumulative receipts validate (Charter8/Handbook66 snapshots), parent arrays unchanged.
  Embedding/rehearsal and hosted staging results follow below; activation remains gated.
  Old19 chunks and39 curriculum links remain active.

All source/currentness/privacy, undergraduate-scope and one-week improvement limits remain.

Compatibility commits: febd6c1 (canonical source blanks),5440368 (document-snapshot root binding).
Final stable source compilation: complete Charter group3816/4096, largest misconduct pair1692/2048;
all61 within480 exact E5 tokens. Source-aware catalogue validates80 chunks,77 assignments,3 preserved
retired records unassigned,66 source-bound claims across7 subjects. Old claims kept and re-bound;
new row-specific claims avoid demanding the entire disciplinary table for one offense question.

Real-source append rehearsal:61 new chunks,2 cumulative receipts,80-chunk selected review accepted.
Existing source/register/release/receipt/chunk rows unchanged; anon/authenticated still see19 chunks.
Initial selected-review order mistake corrected by sorting chunk snapshots; no production change.
`source-append-rehearsal2.log` and `source-package/source-append-rehearsal.json`; disposable DB dropped,
14 original input artifacts unchanged. Hosted read-back: old release active,19 chunks/39 curriculum
links, g2 table absent. Hosted g2 still unapplied.

Embedding set `9584e084ade6c1e93fb56a2394bbf35d25e03a186e08de5f2751c564a426f261`:
61 new CPU vectors,19 original records retained byte-for-byte; actual SentenceTransformer tokenizer IDs
match the standalone no-truncation/no-padding tokenizer. Max477 exact tokens; document prompt empty;
same model/assets/config;68.12s including local load/asset verification. `source-embeddings.log` and
`source-package/embedding-verification.json`. No training/download/dependency change.

Complete local governed release rehearsal passed:80 chunks/39 identical hosted-baseline curriculum
links; anon/authenticated see80 after activation,19 after rollback,80 after reactivation. Original source
register/receipts/chunk/span/ledger rows and old membership unchanged; disposable DB dropped and14
original inputs unchanged. `expanded-release-rehearsal.log`, `source-package/expanded-release-rehearsal.json`.

## Scoped context-budget implementation plan

Follow-on component finding:60 positive claim probes using each source's own vector (not semantic
accuracy evidence) exposed10 same-subject refusals: unrelated ranked rows consume context budget even
when the requested reviewed row/group is present. See `retrieval-component-probe.log`. This directly
advances the new source capability's pre-activation retrieval gate; stop the probe once resolved.

Fix plan: RED actual PackageStorage/engine regression with unrelated same-topic context crowding;
narrow trusted pre-ranking chunk ids to requested visible-claim fields plus required dependency closure.
Keep full-subject behavior for unknown, negative, mixed or absent claim coverage. Retain similarity,
scope, source/version binding and post-retrieval validation. GREEN focused/actual source probe, then
fresh full suite. The5dbc706 full run was stopped as obsolete at94%, not treated as passing; existing
6635-test full result on5440368 remains valid only for that earlier production tree. Hosted staging
was subsequently allowed under the scoped ruling below; no activation has occurred.

Ruling: additive hosted staging may proceed using the completed5440368 core/storage full suite and
full local release/rollback proof while the final Python runtime suite runs. Staging verifies storage/
migration code has no diff from5440368 and keeps the old release active; activation still requires
the final suite and live quality checks. Why: later changes affect runtime evidence selection only.
Cost if wrong: inactive administrative records require investigation/cleanup; no student-visible source
switch is authorized by staging alone. This revises the earlier conservative staging dependency;
all approved source, institutional-release and actual activation boundaries remain.

Reuse `RetrievalSettings` validation/fingerprints. A trusted engine constructor mapping supplies only
known policy subjects' budgets; requests/model output cannot set it. Copy frozen settings, report the
effective budget/fingerprint, and apply it to source-aware context assembly. Runtime composition
selects4096 only when pre_enrollment exists in the reviewed register.

1. RED: actual-policy/real-engine synthetic regression exceeds2048 and succeeds under4096; another
   subject retains2048 and refuses. Caller mutation cannot change copied settings. Invalid/unknown/
   no-policy overrides reject; composition supplies the mapping.
2. GREEN: small engine/composition change; focused retrieval/runtime regressions and actual source
   context gates. Keep defaults, scope/gap/review guards and atomic dependency closure unchanged.
3. Fresh full suite on final behavior tree; source/package/tokenizer checks and governed rehearsal,
   then live quality/latency measurement before hosted switch. No new dependency or PDF edit.

Delivered5dbc706. RED10 budget tests,2 factory-wiring tests and2 menu-cap tests observed. Raised only
trusted DocumentTopic.claims16->64 (actual new topics39 misconduct/18 grading); request selections stay8.
Review P2: output_schema previously expanded its maxItems to menu size;2 real-schema RED regressions
confirmed it. Fixed `min(8,len(claims))`; all choices retained. Final focused **73 passed,+31 subtests**,
`subject-budget-review-green.log`. No other budget-task findings/deferred minors. That full run was
stopped as obsolete after the component crowding finding; its `.exit=-1` is not a passing result.

Claim filter delivered fb4e1e8:3 initial RED failures, then76 focused +31 subtests; actual storage
regressions8 +22 subtests. Source component probe now60/60 accepted with expected uncalibrated labels
and complete required groups. Review P2: prefilter could hide alternate editions/curricula;2 real
PackageStorage RED regressions confirmed it. Added conservative subject-wide fallback for ambiguous
snapshots, retaining explicit scope filtering. Final focused79 +31 subtests. A test-scope fixture was
corrected to include the undergraduate tag; no assertion or production source safeguard weakened.
No deferred findings. Fresh final suite on fb4e1e8: **6658 passed,6 skipped,2 xfailed,+1595 subtests**,
6 existing warnings,1347.61s (22m27s), `claim-final-full-suite.log`/`.exit=0`.

## Hosted inactive staging

Migration20261024114711 applied via MCP; tool timestamp20261024172718 normalized immediately to the
repository version. SQL SHA256:`1118aec0d878d2074f7a16c0a0609fe31c511635127f363600fb738d76ec88ae`.
All10 changed function bodies/grants exactly match a newly migrated disposable local DB after CR
normalization; all SECURITY INVOKER. Supplement table RLS enabled; anon/authenticated cannot read its
rows or execute the review RPC. Parent-link proof trigger present. Advisors unchanged: accepted Auth
WARN, existing1 FK/19 unused-index INFOs. No new advisory finding relative to the saved baseline.

`p11-research-expanded-20261025` is staged as an inactive research draft:80 chunks,39 identical
curriculum links and new embedding set. `stage_expanded_hosted.py` verifies storage/migrations have
no diff from the completed5440368 core suite. Source/register/old receipts/chunks/spans/membership
read back unchanged; anonymous runtime still sees19; active release remains
`p09-research-selected-20261022`. Results: `hosted-staging.log`, `source-package/hosted-staging-result.json`,
schema/advisor readbacks in the same ignored package. Final suite/live candidate/roster gates precede
coordinated activation and local runtime-pin switch. No public/institutional release claim.

## Actual-model gate — failed; do not activate

Nine candidate questions completed with0 exceptions,7 `answered` and2 `insufficient_evidence`; status/
schema validation is not quality. Exact logs/outputs: `live-expanded-candidate.log`,
`live-expanded-candidate/results.jsonl`. English service question additionally selects grade_completion;
Filipino/Taglish requirements+steps answers list requirements only. Taglish plagiarism selects missing22.
English plagiarism lists first/second sanctions; Filipino gives first only. Grade3.0 mapping correct.
Weapon answer invents a usable coursework/permit exception from the malformed clause, then adds only a
generic warning. Fraud answer selects barred-from-university without the overlapping-sanction warning.
These breach source/completeness requirements; the guard's activation-quality record is NOT approved.

Resident-model pipeline observations11.021–38.290s, encoder/composition excluded; first expanded prompt
cache unprimed, prefix reuse requested. Includes routing/retrieval/generation calls; browser/API and
student-visible end-to-end not measured. This is9 development observations, not an accuracy/latency SLA.
All80 source/embedding artifacts remain sealed and inactive; old19-chunk hosted release/pin unchanged.
Source-limit menu correction delivered in5856e82: all recorded unresolved affected claims are selectable,
including malformed conditions/cutoffs/conflicts, instead of only claim_not_stated. RED5 failures/1 pass
(`source-menu-red.log`), GREEN44 (`source-menu-green.log`); fresh handoff check44 passed in2.36s
(`handoff-focused.log`). Command: shared Python -X utf8 -B -m pytest -q -p no:cacheprovider
 tests/test_runtime_research_catalog.py tests/test_runtime_multi_curriculum.py
 tests/test_routing_topic_capacity.py tests/test_retrieval_claim_filter.py, external --basetemp.
The6658 full-suite result predates this one-line change; a fresh final suite remains required. Independent
review was attempted but returned a usage-limit error, with no review delivered; manual diff review only.

Four router-only traces AFTER the menu correction (`source-router-trace/`) still show English service
misclassification, combined Filipino needs/steps, visible weapon claim instead of its gap, and a spurious
fraud prerequisite operation. This correction restores expression of known limits; it does not solve
semantic routing/completeness or authorize activation. No equivalent prompt sweep is authorized by it.

Owner25 Oct replied "aight continue, then hit a handoff soon so i can /clear" to the explicit eight-call
checker comparison question. The bounded experiment in
[the proposal](2026-10-21-checker-completeness-diagnosis-and-proposal.md) is now authorized; no need to
ask again. Exactly4 frozen synthetic inputs × off/on, at most8 completions, original stop rules/defaults
unchanged. No diagnostic completions have run: owner-requested session handoff comes first. Preflight
must revalidate57 sealed files, reconstruct exact current public review messages/schema, verify resident
build/template and off/on rendered activation/headroom, freeze runner/labels before any completion.
A preflight mismatch stops with zero calls. No production thinking/default change follows automatically.

Supabase error investigation: connected app SQL/advisor/log calls work; exact historical local failure
is OAuth refresh parsing. Latest reported occurrence remains uncorrelated; see
[diagnosis](2026-10-25-supabase-mcp-diagnosis.md). No credential/config/schema change made.
