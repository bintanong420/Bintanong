# Opt-in short references for per-part drafts

Code2ce3daf; default remains canonical; expanded release remains inactive.
[Diagnosis/implementation plan](2026-10-25-taglish-failed-infer-diagnosis.md).

## Confirmed failure and bounded diagnosis

One instrumented Taglish pipeline case reproduced temporarily_unavailable/tool_error
at PartExplanation,66.957s inner pipeline. Logging mistakenly read nonexistent
RuntimeFailure.code and recorded unclassified. The exception stores its fixed
reason in args[0]. Input/schema capture before infer succeeded.

One explicit extra generation-only replay used that exact saved request, same
768 cap/seed0/temperature0/thinking off/prefix cache. It took37.321s and returned
RuntimeFailure(truncated_output): raw finish_reason=length, completion_tokens768,
prompt_tokens3636 (3631 cached). It ends inside the last canonical citation hash.
This is generation-only timing, not full pipeline/browser/API/end-to-end latency.
No truncated response rescued or released. No further completion afterward.

Tokenizer-only replacement of four complete IDs in the saved output prefix:
766->539 tokens,227 saved; prose/partial final ID unchanged. This measures potential
wire overhead reduction, not actual-model success, semantic accuracy or latency.
Raw evidence: workspace/audit-evidence/p11-taglish-infer-20261025, including the
initial failed logger and exact replay/raw response. The one-call extension is
recorded in the plan; it is not hidden as a successful original capture.

## Software change and verification

Existing request-local EvidenceReferences now supports opt-in short per-part drafts.
Separate strict ShortPart* wire contracts accept e1..e32; message/source IDs and
record_coverage references use that map. Source/prose strings stay unchanged.
Restore canonical IDs before to_draft, cutoff/fraud/coverage/style checks, ordinary
review, ledger hashing and final rendering. Review sources and final citations
remain canonical. Repair reuses the same map. Unavailable-slot placeholders retain
the canonical ignore-placeholder semantics. Other profile restrictions remain.
No new source facts, DB/pin/embedding/model/default/output-budget/frontend changes.

- Initial RED9 at unsupported profile composition. First GREEN8/1 exposed a fixture
  question-binding mismatch; fixed the fixture, retaining that guard.
- Broad752 passed24.50s; added placeholder regression RED1/13; corrected decoder.
- Final broad753 passed24.15s. Independent review no blockers/14 passed1.12s.
- Tests cover canonical restoration/review, unknown/canonical/private/duplicate/rule
  wire refs, invalid slots/fields, repair, request isolation/binding, unchanged
  source/prose/coverage payloads and source-cutoff integration. Synthetic fixtures.
- Full suite running on frozen2ce3daf, session60055; evidence root E = workspace/
  audit-evidence/p11-part-references-20261025; E/full-suite.head/.log/.exit.
  No production/test changes after start. No installed linter/formatter.
- Prior593de5f full6749 +1595 subtests,6skip2xfail6warnings,1297.74s,exit0 completed;
  retain it without rerun. It is not substituted for the current candidate's suite.

## Recovery and remaining gates

Read existing full-suite.exit/log before restarting; E/full-suite.processes.json
records process IDs/creation times. A missing exit and absent bound process mean
interrupted, never passed. No actual-model run of the short per-part profile yet.
Selecting it as a default requires bounded actual-model quality evidence; no such
selection or expanded source activation is made here. Source-quote language
presentation question remains unanswered; "continue" is not recorded as its answer.
Source order is still not a reviewed ordinal contract; no inference from hashes,
retrieval rank or ID spelling. Other quality/roster/switch/frontend gates remain.
