# Long procedures:segmented drafting results

[Plan](2026-10-28-segmented-procedure-drafting-plan.md). **Segmentation stopped and reverted (473fbe2)**
under the plan's stop rule;shared coverage (0fd0db6) and the disjunction guard (9990175) remain.

## Delivered and kept

- **Disjunction guard 9990175:** a model claim may not use more "or"/"o" than its cited records;
  repair gets a plain "list conditions as printed" instruction;host replies unchecked. RED6->GREEN6,
  host-scope RED1->GREEN. Replay on10saved real claims with or/o flags only the2known cross-enroll
  errors. Live:cross-enroll-en and hybrid-bscs-en now list a)–e) as printed (no OR),first draft.
- **Shared coverage 0fd0db6:** a nested same-subject part (e.g. totals inside whole service) may rely
  on the covering part's citations;every required record must still be cited once. Draft/review
  prompts name the covering part. RED2->GREEN6.

## Why segmentation failed (live,real good-moral/discipline integrations)

Root cause of long-procedure failure is the8-claim answer cap,not768output tokens:the model writes
one claim per record (good moral10records) and stops at8;facet parts also inherited the whole-group
coverage. Iterations (each RED->GREEN,focused1036–1038pass):
1. Segments of<=5records,one call each (26c720a):model still one-claim-per-record,drifted to step1.
2. Schema-bound record groups via llama.cpp `prefixItems` (5d8758a):coverage forced,but claim text
   narrated other steps;same-model review correctly marked4/7claims unsupported.
3. Segment sees only its own records (df44f89):text still shifted by one step inside the segment
   (caught by the disjunction guard);a discipline segment call exceeded120s.

Results:good moral117s abstain;discipline ~170s timeout (vs79–115s/99s single-call failures).
No wrong answer reached output — guards held — but no accuracy gain and worse latency. Generation
measured ~22tokens/s on the RTX4060,so long prose procedures are inherently slow on this model.

## Remaining option (owner judgement requested)

Host-rendered ordered steps from a normalized,reviewed step table (client step,agency action,office,
person,time,fee per step),with a short model-written lead. Exact and near-zero generation latency,
but needs a new derivation/verification pass over the34Charter services (field names vary across
~30shapes incl. continuations) and an answer-style decision. Until then long procedures refuse
safely with an office referral.

## Evidence

Ignored:workspace/audit-evidence/p11-procedure-split-20261028 (single-part probes,recheck run,
segment-probe/-2 traces,RED/GREEN/focused logs,full-suite for473fbe2).
