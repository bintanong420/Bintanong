# Teammate regression checklist — 4 November 2026

Owner supplied duplicate reports; this checklist consolidates their distinct failures.
Apply fixes through shared curriculum/routing contracts, with synthetic cases across programs.
Do not interpret a passed course as proof that every other prerequisite is satisfied.

| Capability | Acceptance condition | Current evidence / remaining work |
|---|---|---|
| Prerequisite listing | Describe reviewed requirements without demanding grades or making an eligibility decision | Integrated; six source-backed OFF/ON listing/eligibility checks pass |
| Follow-up clarification | A reply giving a prerequisite result preserves the intended target and updates only asserted facts | Atomic bounded ledger delivered, 84 focused session/API tests pass; context compiler still pending |
| Conversational repair | Recognize corrections and references using bounded dialogue state; clarify only actual ambiguity | Independent conversation tests required after ledger integration |
| Topic switching | Eligibility followed by program-shifting procedure uses the document path and applicable office referral | Fresh and after-prerequisite live tests pending |
| Natural dependency question | “What can I take after passing X?” selects dependency reasoning without requiring a term unless the user asks for a term plan | Cross-program routing tests pending |
| Curriculum planning | Preserve true all-of/any-of/co-requisite semantics, unknown facts and advisory limits | Unsafe optional dependency prose withheld; checked host grouping remains; 25 term tests pass |
| What-if presentation | Show printed course codes, keep premise conditional and unsaved | Missing assumption labels corrected; RED 2, GREEN 29 session/pipeline tests |
| Recovery planning | Preferred just-in-time shape and faster alternative both remain available | Integrated; expanded gate 51 pass/4 stale fixtures, corrected selections 4 pass, plan-view 10 pass; real-curriculum acceptance pending |
| Partial/unreviewed data | Distinguish source defects, retrieval coverage and dialogue failures; held fields stay inactive | Typed reasons integrated; graduation procedure present but original endpoint clipped; no corpus-wide accuracy claim |
| Frontend presentation | Concise conclusion, readable grouped details, no repeated question or internal identifiers | Labels/control styling/About link corrected; TypeScript passes; browser rendering and broader conversation review pending |

Verification for assumption labels:
`py -3.13 -B -m pytest tests/test_orchestration_sessions.py tests/test_orchestration_pipeline.py -q -p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/assumption-label-green`
returned **29 passed**. Two focused tests first reproduced the raw-ID defect.
Synthetic fixtures only; no institutional records or source content changed.
