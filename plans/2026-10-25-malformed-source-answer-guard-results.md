# Malformed-source answer guard — verified increment

25 October 2026. Code `c5f0d07`; [focused plan](2026-10-25-malformed-source-answer-guard-plan.md).
Existing source-gap/partial-answer requirements reviewed; no product-scope or source-content change.

The selected per-part path now marks a model slot `source_gap` if an answered claim cites a document
record held for an unresolved `malformed_source_condition`. All proposed citation identities are
validated first. Filtering happens before claim numbering and reviewer identity binding. Independent
parts and canonical structured results survive. Host fee/grade paths are unchanged.

This is deliberately conservative at record level: even valid details from the same affected record
are withheld. No sentence classification or invented interpretation resolves a held field. Resolved
limits, other defect types and uncited affected records do not trigger this guard. It does not detect
a model using an unrelated citation to launder an unsupported claim; existing support checks remain
fallible. Historical alternate generation profiles are unchanged; production selects `parts`.

Source-gap replies now explain the unclear/incomplete source separately from information absent
from the corpus in English, Filipino and Taglish. When another part also fails verification, the
overall verification warning remains alongside gap notices. No withheld model claim is rendered.

## Test and review evidence

Ignored workspace root: `audit-evidence/p11-malformed-source-20261025/`.
Shared Python3.13 `-X utf8 -B -m pytest -q -p no:cacheprovider`, external basetemp per run.

- `red.log`:7 expected failures/5 passes; unsafe claims were released despite source holds.
- `green.log`:67 passed (new tests, per-part slots, source-limit notices).
- `notice-red.log`:6 expected failures/6 passes; source gaps incorrectly described missing corpus.
- `notice-green.log`:67 passed.
- `regression.log`:490 generation/request-understanding checks passed,11.01s.
- Independent review: no citation/identity bypass; one P2 mixed gap/uncertain notice omission found.
  `review-red.log`:1 expected failure/12 passes. Corrected renderer retains overall verification warning.
- `review-green.log`:491 passed,10.93s. Independent follow-up13 passed; no blocking findings.
  Declined judgments: accepted field-level precision tradeoff, unchanged host-written paths,
  actual source/model accuracy, and historical generation profiles outside this selected-path change.
- Previously pending5856e82 topic-menu change independently reviewed: no blocking findings;31 catalog,
  capacity and separation checks passed. Actual model/source selection accuracy remains outside that review.
- Final evidence seal verifies15 files and unchanged tested code;67 local documentation links resolve.
  Delivery manifest SHA256 `810064c5343695d0f7185e45b65a58cd09c95571dbe19922045c40821cfa3a31`.
  Phase-state and Git whitespace checks pass; this is a verified increment, not Phase11 completion.
- Full `tests/` suite on committed `c5f0d07`:6677 passed,6 skipped,2 xfailed,1595 subtests passed,
  6 existing warnings,1356.64s (22m36s),exit0. See `full-suite.log`,`.head`,`.exit`.
  This covers the earlier5856e82 change as well. No code/test changes occurred during the run;
  subsequent edits are documentation only. No installed linter/formatter; none run. Six skips and
  two photo-related expected failures remain disclosed; this is not full source/model accuracy.

## Single current-pipeline replay

Reused only the saved question: "Does the handbook allow a bladed weapon for coursework?"
Existing local80-chunk draft composition; no hosted activation/pin switch, student facts or private data.
One attempt, no rescue or prompt/model changes. `live_weapon_current.py` derives from the existing live
harness; its original SHA256 is4625647b88f97704aebbda5b331bd9a4db5ba621eeedc6158452320834e925c1.

Observed: RAG, integration `ready`, chosen visible II.2 fields, final `insufficient_evidence` /
`parts_unresolved`; reply says its source is incomplete/unclear and refers to the university office.
No interpreted exception is released.29.37s is resident-model inner pipeline, excluding composition/
encoder startup and browser/API; queueing is not isolated. Existing encoder long-sequence warning
was logged during composition; no tokenizer/dependency change is made or accuracy claim inferred.
Raw draft not captured: this trace does not distinguish model self-refusal from host suppression;
synthetic adversarial tests independently establish the host floor. One safe refusal is not corpus
accuracy, a latency SLA or clearance of the full9-case gate. Raw source-derived evidence stays ignored.

## Remaining boundary and next action

The code increment passed full verification and scoped independent review. The source
release remains inactive; university/public/institutional gates unchanged. Misrouted service questions,
omitted procedure steps/sanction progression, Taglish plagiarism routing and fraud precedence remain.
Next focused correction should retain both reviewed fraud labels and explicitly expose unresolved
precedence, without selecting a student's sanction or editing sealed source evidence. Reuse existing
traces; no checker-thinking rerun or unbounded prompt experiment. Frontend integration still deferred.
Read-only next-step finding: II.6 and II.8a are already mutual `required_neighbor_chunk_ids` in the
sealed draft. Both carry the same unresolved precedence claim under `claim_not_stated`; current
`render.limit_notices` intentionally ignores that issue. Do not repeat a ranking/retrieval sweep to
explain the missing warning. Carrying the limitation and both printed entries is the unresolved work.
