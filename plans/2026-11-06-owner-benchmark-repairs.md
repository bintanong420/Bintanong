# Owner benchmark repairs — 6 November 2026

Bounded repair work on `p12-dev` / `p12-post-gathering-fixes`, starting `730344e7`.
No new numbered phase, corpus activation or dependency/model change. Main gathering checkout stays separate.

## Evidence and acceptance

- Owner CSV: `E:/Hawksprey/Downloads/1_Bintanong 72 bench queries test log.csv`, SHA-256
  `293bc578ab3a41066825bdf3544596abe6e95f0f974d8eb70bf2322fba950273`.
- PDF edition 4: SHA-256 `be467633c1429dc72b49e473d4633f81045f340859dd86f0d167ff368577a9a3`;
  same 24 rows / 72 variants as the [existing run](2026-11-05-live-language-browser-results.md).
- Marks: 47 Y, 8 P, 14 N, 3 blank. Row 7 was not tested because program selection is mandatory.
  These are owner marks, not independent adjudication or a newly measured accuracy score.
- Owner confirmed these results came from 3217, whose temporary rate-limit override works.
  Do not modify main/public limits or reopen that resolved issue.
- Second CSV is the same run's fix-handoff export, SHA-256
  `247ad9efd335565c53a070e8d8727165d93b85e0481a918daa973bf3a3b9637c`.
  Its row 15 TG fix-log cell is `#REF!`; original checklist and exported prompt both say Y. Not a second evaluation.
- Consulted thesis physical 17–18, 39–44, runtime routing PNG, master section 3, current handoffs,
  undergraduate/source-gap policy and owner decisions. Preserve advisory scope, structured course reasoning,
  English/Taglish replies and existing deadline discrepancy readings. No architectural discrepancy identified.

## Repair order and reach

1. Course identity: row 9 cannot list a reviewed named course's prerequisites. Inspect literal extraction,
   scoped catalog binding and router validation; reuse existing routing tests with synthetic curricula.
2. Document selection: rows 10, 13–19 vary by language or choose the wrong topic/claim. Trace selector,
   interpretation and evidence separately; fix a demonstrated shared failure, not benchmark phrase routing.
3. Procedure completeness: rows 23–24 omit application requirements or substitute a library-specific service.
   Preserve original source limitations; establish applicable service coverage before changing claims.
4. Reply quality: row 8 should answer listing directly; Taglish wording and unrelated service prose need
   review at the shared generation seam. Source quotations retain their printed English.

For each slice: reproduce, failing public-boundary regression, smallest fix, related regressions, then a
bounded live rerun of affected variants. Keep evaluation questions out of prompt examples. Do not infer
source approval from a CSV expected-answer cell, or count a clarified source ambiguity as a fixed procedure.
Raw traces and original-source evidence remain ignored under workspace `audit-evidence/benchmark-fixes-20261106/`.

## Current state

Row 9 live router trace resolved `Forensic 3/L` but rejected the program phrase `BSCrim student`: the catalog
contains `BS Crim`, not its compact spelling. Shared program-alias matching now allows omitted whitespace
within a reviewed alias; whole-word boundaries, ambiguity and selected-scope checks remain. No course alias
or source data changed. Synthetic public validation regressions: corrected RED 6 failed / 5 passed;
GREEN 11 passed. Related validation/compiler/program-switch/catalog suite: 217 passed.
Commands use existing Python 3.13 venv, `-m pytest`, `-p no:cacheprovider`, external `--basetemp` beneath
the raw evidence directory. Bare `python` resolves to an unrelated environment; system Python lacks pytest.
No install was performed. Test files: `test_routing_program_spacing.py`, `test_routing_validation.py`,
`test_routing_compile.py`, `test_routing_program_switch.py`, `test_routing_catalog_separation.py`.

Forensic: real router resolves all three variants; full HTTP English turn lists Forensic 2/L.
Listing prose: removed the unrelated eligibility invitation (row 8). RED 6 failed / 18 passed;
GREEN 50 passed across listing/eligibility/course-fact tests. Rule trees, citations and unknown conditions stay.

General policy (row 10): compiler bypassed the existing topic-backed non-course correction, creating a
fake term target. Reuse that correction only without declared course/term mentions; named targets and
existing structural reconstruction remain. RED: compiled path asked for a term while normal path dispatched
RAG. GREEN 195 compiler/wire/understanding tests; larger routing group 282 passed. Hybrid tests retained.
Filipino: all-unknown fragments are retried once using the existing repair budget. Do not repeat the wrong
assistant interpretation in that retry. Complete review-bound body fields up to existing context bounds
now inform selected topics; no truncated body is added. Metadata fallback exposes reviewed claim names
when printed descriptions are unavailable; redundant selector labels removed. Context/selection group 143 passed.
Latest targeted router traces: EN/TG validated; Filipino validated after clean retry. Full answer rerun pending.
No benchmark wording was added to prompts. Source policy/guards remain; general policy alone is RAG,
while a checked course/term request plus documentary explanation remains Hybrid.

## Current offline repairs and live limits

Owner 6 Nov: fix round-two failures first; the supplied audit-driven remediation plan is deferred.
Preserved unchanged as [deferred proposal](2026-11-06-deferred-audit-remediation-proposal.md), SHA-256
`93a06cce464e5d69a1647d81a2bf46b61e5a9fa02a3554412309a9f148a20a95`.
Its branch graph is a historical planning baseline, not verified current remote state. Do not start its
PR/merge, new held-out corpus, multi-operation or release gates as part of this repair.

Saved grade-4 traces show deadline-only claim selection despite a procedure request; add/change traces
select Handbook policy. Existing procedure preference addresses the latter. Added review-bound per-claim
body context so the interpreter can distinguish a method from a deadline/meaning label: only one complete
body up to 1024 characters; held, oversized or multiple distinct bodies supply no hint. No new source claim.
RED 1 failed / 26 passed; GREEN 200 across topic/source-binding, document selection and coverage/cutoff tests.
This metadata correction is not yet live verified. New evidence remains separate from final success.
Routing/context fixes committed as `1ba98d82`. Final focused answer/facility/coverage gate: 66 passed.
Owner asked for a free inference window before loading/retesting; reply pending. Do not restart yet.

Working-tree repairs: clean semantic retry and bounded complete source context (296 routing checks);
legacy registration service labels (80 checks); unique approved-family procedure preference (290 checks);
cheating loanword recognition (98 checks); general facilities companion retrieval and source-bound reply
(55 checks). Owner chose quotations from both Handbook and Charter, with general and library scopes kept
distinct; decision recorded in the ledger. No original source was changed.

Live Taglish cheating now selects the relevant two claims; Taglish facilities quotes both scoped sources.
General-policy routing works in three languages, but full replies still omit material or abstain. A new
generation repair uses the existing second attempt when supported claims fail question coverage; 108
related tests pass. It is not loaded on the current API. Probation and INC remain unresolved end to end;
registration/procedure changes also need controlled live verification. Vehicle checklist expansion lacks
original-backed reviewed coverage; the active payment/office evidence does not establish a full procedure.

Integrated offline gate stopped at 697 passed / 1 failed: cutoff test expected one relevance review,
where the new bounded coverage retry performs two and still withholds unsupported answers. Updated that
expectation; cutoff/completeness group 32 passed. Remaining integrated tests are running separately.
Three other stale rejection-message assertions reproduced unchanged on main; the test now asserts rejection
without depending on which guard runs first (12 passed). No runtime guard was weakened.

Ignored candidate launcher temporarily captures model calls and retrieval IDs. Restore its
`start-candidate.py.before-repair-trace` backup after investigation, retaining the zero-window benchmark override.
Current dev API includes compiler/context and initial facility/cheating repairs, but predates the latest
generation coverage retry, registration labels and procedure preference. Main remains untouched.

Second round received: `E:/Hawksprey/Downloads/Bintanong_AI_Export_2026-11-06_1002.csv`, SHA-256
`ac426d1b43ec172b7beff9854ed225e44cf42ca051549b1e88c14b2a1d7d7268`.
72 roster rows, 33 retested: 20 Y / 13 N; 39 untested. Owner classifications: 12 fixed, 8 unchanged pass,
10 still failing, 3 regressed. Regressions: B-14-TG and B-15-TL/TG. Pass counts EN 7/11, TL 8/11,
TG 5/11; targeted subset only, not an overall language ranking or 72-case accuracy estimate.
Forensic A-09 all pass; cheating B-19 all pass; vehicle B-23 all owner-marked pass (does not expand reviewed
source coverage); facilities B-24 all pass with response pollution noted. Remaining failures:
A-10-TL/TG; B-13-EN; B-14 all; B-15 all; B-16-EN/TG; B-17-TG; B-18-TG.
Notes repeat at item level across languages; do not reinterpret an EN Y as N from a shared Taglish note.
Export contains marks/notes, not full answer transcripts, model IDs or source citations: use existing traces
for causes, and keep owner pass separate from independently source-verified correctness.
Recovered restarted remainder: 723 passed before an unrelated unknown-course wording expectation failed
(`test_routing_unknown_course.py`, expects 'as printed in your prospectus'). Do not claim a full integrated
pass or alter unrelated wording merely to clear the gate. Relevant focused gate above passes.

Hold automated model requests and server restarts pending a clear testing window; receiving the export
does not itself authorize interrupting the server. Next: prioritize grade-4 and add/change regressions,
finish the offline gate, then verify the untested generation/registration/procedure fixes live.
Reuse existing evidence; no full rerun until targeted checks pass. No full benchmark success claimed.
