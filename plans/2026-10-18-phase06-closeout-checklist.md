# Phase06: what is finished and what remains

Current18October2026; product49bc993. The scoped curriculum engine is implemented
and tested offline. Formal Phase06 completion is still blocked. This is the short
working checklist; the original phase plan retains its earlier increment history.

## Only three groups are needed to understand the tests

| Group | Simple question | Review responsibility |
| --- | --- | --- |
| Prerequisites | Given this curriculum's actual rule and fictional passed/failed courses, is the prerequisite satisfied, unmet or undetermined? | Researcher checks source meaning; developer tests the combinations. |
| Affected courses | Which later courses depend on this course through the reviewed prerequisite paths? | Developer derives/checks paths; researcher decides only genuinely new or ambiguous source meanings. |
| Developer checks | Does the software handle missing/conflicting input, wrong curriculum, unknown courses, unsupported operations, repeated execution and timeouts correctly? | Developer tests/logs; no owner grading of internal mechanics required. |

The existing CSV labels are test names, not required thesis terminology. Keep
their original IDs/results for audit, but do not present the engineering group as
additional university rules or mandatory researcher verdicts. Master11.3 requires
bounded execution/isolation;11.4-11.5 require truthful unknown/error outcomes and
rule verification. Those checks belong in Phase06's developer evidence.

## Finished for the selected BSCS subset

| Work | Status and evidence |
| --- | --- |
| Structured authoring records with source/curriculum binding | Implemented. Reviewed records are authoring truth. |
| JSON-to-Prolog compiler and reproducible bundles | Implemented. Both actual BSCS versions regenerate; seven direct expressions retained. |
| Typed Python/Janus/Prolog runtime | Implemented. Check prerequisites, list missing prerequisites, list potentially affected courses. |
| Controlled execution of actual BSCS data | Verified offline with fictional completion facts; institutional use remains closed. |
| Software checks, including technical categories | Latest developer run:73 cases, four isolation checks,39 native spans; repeat equality and timeout recovery also asserted. |
| Received human runtime feedback |48 affirmative verdicts recorded; three no verdicts and22 blank verdicts preserved with comments. Technical blanks do not require owner grading. |
| Old CS1/L disagreement, H27-H32 | Resolved after the actual18October CC1/L identity confirmation:failed -> ineligible, passed -> eligible, missing/conflicting -> unknown. New bundle passes all73 cases. |

Latest raw evidence:ignored workspace/audit-evidence/p06-cc1-identity-20261018.
The [identity review](2026-10-18-phase06-cc1-identity-review.md) binds the actual
answer and new artifacts; the original reviewed CSV is preserved unchanged.
The [review guide](2026-10-17-phase06-human-verification-guide.md) maps original
case labels and fields to their implementation roles. No source/activation flags
were changed by executing tests or editing reviewer CSVs.

## Remaining work

| Item | What finishes it |
| --- | --- |
| Complete the generated-output review | Reconcile the returned verdicts with the exact generated mappings; show only actual pending source/output questions. Do not regrade48 accepted rows or require technical CSV verdicts. Record the scoped final review result. |
| Governed institutional runtime/release | Current standard runtime path rejects real institutional bundles; the explicit research path is implemented. Institutional source authority/approval and governed release/runtime integration remain separate outstanding gates in the blocked handoff. |
| Formal final exit | After applicable gates are satisfied, rerun affected acceptance/regressions and phase checks; replace the blocked handoff with a verified complete handoff and update checkpoint/index. Passing tests alone cannot do this. |

The current handoff does not authorize an automatic offline-only closure in place
of its recorded recovery condition. Do not silently waive that condition. Pending
school validation does not prevent independent offline development/testing.

## Boundaries that must remain visible

- Unknown printed prerequisite conditions stay unknown; they do not all need to
  become resolved/no-prerequisite for a bounded capability to be tested honestly.
- The full-prospectus53/55-row exports still have extraction/source gaps and no
  full PL. That delivery is incomplete; it does not invalidate the tested selected
  subset or automatically require whole-curriculum completion to close that scope.
- Chat UI, LLM routing, full conversational evaluation and later phases are outside
  this Phase06 increment. No complete chatbot or whole-BSCS coverage is claimed.
- Two historical full-suite failures are the recorded system Docling dependency
  conflict. No all-project-green or fixed-environment claim is made here.

Next action: inspect the seven source-linked generated meanings in ignored
workspace/audit-evidence/p06-cc1-identity-20261018/CURRICULUM-REVIEW.md and record
the scoped final output verdict. Retain the institutional release/formal-exit gates.
