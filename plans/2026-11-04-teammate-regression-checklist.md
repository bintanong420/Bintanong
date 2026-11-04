# Teammate regression checklist — 4 November 2026

Owner supplied duplicate reports; this checklist consolidates their distinct failures.
Apply fixes through shared curriculum/routing contracts, with synthetic cases across programs.
Do not interpret a passed course as proof that every other prerequisite is satisfied.

| Capability | Acceptance condition | Current evidence / remaining work |
|---|---|---|
| Prerequisite listing | Describe reviewed requirements without demanding grades or making an eligibility decision | Recovered listing branch under review |
| Follow-up clarification | A reply giving a prerequisite result preserves the intended target and updates only asserted facts | Generic dialogue ledger/compiler slice still pending; listing alone does not solve this |
| Conversational repair | Recognize corrections and references using bounded dialogue state; clarify only actual ambiguity | Independent conversation tests required after ledger integration |
| Topic switching | Eligibility followed by program-shifting procedure uses the document path and applicable office referral | Fresh and after-prerequisite live tests pending |
| Natural dependency question | “What can I take after passing X?” selects dependency reasoning without requiring a term unless the user asks for a term plan | Cross-program routing tests pending |
| Curriculum planning | Preserve true all-of/any-of/co-requisite semantics, unknown facts and advisory limits | False OR in generated term paragraph confirmed; narrow correction underway |
| What-if presentation | Show printed course codes, keep premise conditional and unsaved | Missing assumption labels corrected; RED 2, GREEN 29 session/pipeline tests |
| Recovery planning | Preferred just-in-time shape and faster alternative both remain available | Recovered JIT branch under review |
| Partial/unreviewed data | Distinguish source defects, retrieval coverage and dialogue failures; held fields stay inactive | Reason taxonomy branch under review; graduation source diagnosis separate |
| Frontend presentation | Concise conclusion, readable grouped details, no repeated question or internal identifiers | Host label fix verified; broader presentation/browser review pending |

Verification for assumption labels:
`py -3.13 -B -m pytest tests/test_orchestration_sessions.py tests/test_orchestration_pipeline.py -q -p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/assumption-label-green`
returned **29 passed**. Two focused tests first reproduced the raw-ID defect.
Synthetic fixtures only; no institutional records or source content changed.
