# Memory and eligibility: delivery and verification (3 November 2026)

Branch `feat/memory-eligibility` (worktree `p12-memory-eligibility`), from `395079c`. Requirements: the
[owner plan](prolog/Bintanong_Backend_Memory_and_Eligibility_Plan.md); design: the
[implementation plan](2026-11-03-memory-eligibility-implementation-plan.md). Local commits, not pushed. This is
research/software work only: it grants no school approval, release activation or scope change.

## Delivered

| Task | Commit | What a student sees |
| --- | --- | --- |
| 1 Capture | `e8395e0` | The host keeps each course result as stated: passed, failed, not yet passed, never taken, or "took it" with the result not given, plus enrollment and its term. A model `passed` without pass words is not kept as a pass. A what-if applies only to its own check, and a friend's result adds nothing. "I passed CC 5/L" on its own is acknowledged. |
| 2 Memory | `bed1fe0`, `0688378` | The chat remembers stated results and the check waiting on a reply. "Oo, pasado" re-asks the waiting check with that result. Memory resets with a new chat or a curriculum switch, and a failed turn saves nothing. A correction replaces the earlier statement, while a disagreement with a confirmed upload is asked about. The UI copy is updated. |
| 3 Answer | `bad7a05` | The conclusion comes first (for example "Oo. Pasok ka sa prerequisite ng CS 13/L…" or "Not yet. You need to pass…"). A single missing result is asked by name, and the rule is worded with both, either or same-term. One bounded Bintu call after Prolog explains the checked evidence. A draft that names another course, reverses the verdict, promises enrollment or says "failed" is dropped, and the host text is shown. What-if answers are labeled conditional and unsaved. |
| 4 Term | `a13ca52`, `591e0a8` | `assess_term_prerequisites` checks each reviewed course of the requested term. Results are grouped as met, blocked or needs information, each with its reason. Already-passed courses and possible retakes are listed apart. A term missing from the source is reported as not covered, never as empty. "next sem" asks for the year and semester, and a bare "second year, second sem" re-asks the term check. |

## Verification

- New-program gate: a synthetic ledger with unfamiliar IDs answers a two-turn chat through the release builder with
  no prompt, evaluator or template edit (`acb683b`).

- Every new behavior was tested first. RED was observed before the code, except in two places where the test
  passed on its first run because the code had been written just before it: the enrollment `period` field, and the
  core `assess_term` test. Both are covered by later pipeline tests that did fail first.
- Real reviewed ledgers, offline through SWI-Prolog with no model call: **17/17 PASS**
  (`audit-evidence/mem-elig-tmp/real_cases.py`; ledgers read anonymously from release
  `p12-research-faqsplit-20261030`, cached untracked). Covered:
  - BSCS 2018 CS 13/L: asks about CC 5/L, then eligible after a pass. "Took it" still asks. CC 5/L without CC 3/L and CC 4/L shows both unmet.
  - Proposed BSCS CS 13/L with only CC 5/L passed is not cleared; the reply asks about CS 6/L and CS 10/L.
  - Phy 11/L with the same facts: BSCE prerequisite unmet, BSME prerequisites met.
  - Architecture ACAD-2/L eligible. Nursing NCM 15-103 asks only about NCM15-102B, then is eligible.
  - BusEco BE 2001 with GE-PC "not taken" is unmet (the recorded failure, fixed). BAC 5's reviewed "None" is eligible.
  - BSEd Math FS 2 gives no positive verdict.
  - Old BSCS second year, second semester: CC 5/L and CS 4/L blocked, GE-PS unresolved (blank cell).
  - Midwifery second year, first semester is not covered (the source has only years 3–4).
- Plan suite (the PowerShell command's file list) plus the new test files: 269 pass.
- Full `tests/` (Python 3.13.7, `p12-env-20261031`): the branch has 82 failed, 5,639 passed and 9 collection errors.
  The untouched baseline `395079c` has 82 failed, 5,536 passed and 9 errors. The failure lists are identical, with
  zero new failures; all of them come from `jsonschema`/`cv2`/docling, which this venv lacks. The full branch run
  started before the last few fixes; each of those has its own passing tests.

- Live with Gemma/Bintu (model container `bintanong-p09-cuda-latency`), through `ChatTurns` -> `ResearchPipeline` with
  the gate composition and Prolog on the cached ledgers (`audit-evidence/mem-elig-tmp/live_cases.py`):
  - The first run passed 10 of 12 turns. It exposed four defects, each now fixed with a regression test:
    - Civil and Mechanical failed because a repeated code was miscounted (`142afbf`).
    - "before you can take" was misread as a verdict (`96d990d`).
    - A what-if inside an "if" clause was saved as the student's record (`a9ac1df`).
    - An explanation said "both" for a single-prerequisite rule (`6f6a572`).
  - The rerun passed **7 of 7**: Civil prerequisite unmet, Mechanical met, Lawrence labelled as an unsaved what-if,
    and the BSCS four-turn demo. 6 of the 7 answers kept Bintu's explanation.
  - The other scenarios passed in the first run: fresh chat, proposed BSCS, the two-turn term check, and BusEco.
  - Warm backend turn time was 20–33 s per turn. This excludes the browser, network, queueing and Supabase, and is
    not student-visible latency.
  - Wording seen live and still open: one explanation used the internal word "all_of", and one said "your record
    shows" for a what-if.

## Handoff: long live gates (owner, 3 Nov: run on the other developer's 32 GB machine)

Run them with `evaluation/memory_eligibility/` (see its README): `offline` (passed 14/14 here), `scenarios`,
`curricula` (every release member) and `recorded` (113 questions). Here the `curricula` gate was stopped at the
owner's request after its first curriculum: `abcomm-2018-2019` passed 3/3. Neither `curricula` nor `recorded` has a
complete result yet. Every answer now records `explanation_check` (accepted/rejected/unavailable/skipped) and the
validator's error codes, so the explanation acceptance rate can be measured on those runs.

## Open gates (not done; do not report as passing)

- The live runs above go through the chat turn path in-process, not the HTTP `POST /chat` stream or the browser, and
  without document retrieval. Still to measure: claim extraction per language at scale, and the 113-question regression.
- The plan's every-release-member gate (39 curricula, multi-turn and negative cases) has not been run. Nine
  curricula are covered offline above.
- Frontend: `noted_*` and `term` replies arrive as text, and the clarification dialog adds no new controls. tsc
  was not run in this worktree (no `node_modules`); the only frontend change is one string.
- The host's word lists (English/Filipino/Taglish) are deliberately conservative. Unrecognized phrasing supplies
  no fact, so the student is asked rather than given a wrong verdict.
