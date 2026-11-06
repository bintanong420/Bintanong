# Dependency-direction verification across the cached release

Code tested: `e3d4bce2`, on `p12-post-gathering-fixes`; no gathering server restart or model calls.
Student capability: ask which courses require a named course, without reversing the dependency,
requiring a rephrase or inventing a failed grade. No numbered phase exit is claimed.

## Results

**39/39 curricula passed**, with **1,696 compiler/validation replays**, **78 actual Prolog queries**
and **156 English/Taglish first-line checks**. No further program-specific code correction was needed.
The shared routing/presentation fixes are already in `56e7af6f` / `e3d4bce2`; no program constants added.
An additional actual BSIT query verified **IT 3/L -> IT 14/L**, with one unresolved condition retained
(the printed percentage requirement remains outside individual-course checking).

| Cached curriculum | Direction replays | Prolog checks | Result |
|---|---:|---:|---|
| abcomm-2018-2019 | 48 | 2 | PASS |
| abphilstud-2018-2019 | 48 | 2 | PASS |
| abpolsci-2018-2019 | 40 | 2 | PASS |
| beed-2018-2019 | 40 | 2 | PASS |
| bsa-2018-2019 | 40 | 2 | PASS |
| bsacct-2023-2024 | 32 | 2 | PASS |
| bsba-buseco-2018-2019 | 40 | 2 | PASS |
| bsba-fm-2018-2019 | 48 | 2 | PASS |
| bsba-hrm-2018-2019 | 32 | 2 | PASS |
| bsba-mm-2018-2019 | 40 | 2 | PASS |
| bsbio-medbio-2018-2019 | 48 | 2 | PASS |
| bsce-2018-2019 | 48 | 2 | PASS |
| bscrim-2018-2019 | 48 | 2 | PASS |
| bscs-2018-2019 | 40 | 2 | PASS |
| bscs-proposed-2025-2026 | 40 | 2 | PASS |
| bse-agri-2018-2019 | 48 | 2 | PASS |
| bse-franchise-2018-2019 | 40 | 2 | PASS |
| bse-innotech-2018-2019 | 48 | 2 | PASS |
| bsed-eng-2018-2019 | 48 | 2 | PASS |
| bsed-fil-2018-2019 | 48 | 2 | PASS |
| bsed-math-2018-2019 | 48 | 2 | PASS |
| bsed-sci-2018-2019 | 40 | 2 | PASS |
| bsed-ss-2018-2019 | 48 | 2 | PASS |
| bsed-valed-2018-2019 | 48 | 2 | PASS |
| bsee-2018-2019 | 40 | 2 | PASS |
| bses-2018-2019 | 48 | 2 | PASS |
| bshm-culinary-2018-2019 | 40 | 2 | PASS |
| bshm-hotel-2018-2019 | 40 | 2 | PASS |
| bsit-2018-2019 | 48 | 2 | PASS |
| bsma-2022-2023 | 48 | 2 | PASS |
| bsmb-2022-2023 | 40 | 2 | PASS |
| bsme-2018-2019 | 48 | 2 | PASS |
| bsmid-2019-2020 | 40 | 2 | PASS |
| bsn-2018-2019 | 48 | 2 | PASS |
| bspe-2018-2019 | 48 | 2 | PASS |
| bspsych-clin-2018-2019 | 32 | 2 | PASS |
| bspsych-io-2018-2019 | 40 | 2 | PASS |
| bssw-2018-2019 | 48 | 2 | PASS |
| bstm-2018-2019 | 40 | 2 | PASS |

## Reproduction and limits

`py -3.13 -B -m evaluation.memory_eligibility.dependency_offline --out <ignored>/all-curricula.json`
uses existing `BINTANONG_RESEARCH_CONFIG` and `BINTANONG_LEDGER_CACHE` from the memory gates.
Raw per-curriculum hashes, targets, expected course links and unknowns are ignored at
`C:/Coding-projects/bintanong_workspace/audit-evidence/p12dev-dependencies/all-curricula.json`.

For each curriculum, select one referenced course and one terminal course with unambiguous printed codes.
Replay four English/Taglish dependency phrasings using printed code, compact code and unique title where
available, under both mistaken eligibility and prerequisite-list operations. Validate the corrected target
and operation. Compare Prolog results with transitive references in the reviewed ledger; check first-line
rendering introduces no failure/block premise. Expectations share the authoring ledger with Prolog;
this is not an independent original-source accuracy audit. Other course rows are not exhaustively sampled.

This verifies the compiler's correction of supplied model packets, not the model's ability to produce them.
No live LLM, HTTP/browser, conversation-history or data-gathering end-to-end run was performed here.
The cached roster does not establish institutional approval, source currentness, unsupported-program coverage,
or that the serving app has loaded the branch. No corpus/source/rule edits or database writes occurred.
Next: isolate a development runtime and schedule live model language/history tests without competing with collection.
