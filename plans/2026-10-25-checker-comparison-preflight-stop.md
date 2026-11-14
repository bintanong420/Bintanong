# Checker comparison — preflight stopped, zero completions

25 October 2026, Codex resume at `357aa80`. This records the mandatory stop under the
[approved frozen proposal](2026-10-21-checker-completeness-diagnosis-and-proposal.md).
No semantic comparison ran; the result is neither improvement nor failure of native thinking.
Phase11 remains active and the expanded research release stays inactive.

## Verified evidence

- All57 files in the old delivery manifest match their sealed hashes. Manifest SHA256:
  `e10ca82c572f48557b04aa258b17cdb1bd11d5c0f5ec46369fc866ba36b0fd3d`.
- Prior diagnosis seal matches:
  `134ed42fad1788627ad6bc5a4612159f9fa073374c32d79b561528942a6eff39`.
- The current public pack/draft/review functions cannot reconstruct any of the four exact
  saved messages/schemas. Current question-part serialization adds `subject_id:null` and
  `requested_claims:[]`; these enter both the reviewer payload and requirements identity.
  Draft validation passes and draft hashes are unchanged in all four cases.
- First case expected requirements hash:
  `a683a8412b613d8c81bd5d7ad93f8a62ba8c8e2d7a621eee48fe371b0ab3714a`;
  current hash: `49f95bbbf96ddbc07c0c1ebf751c73f40e93319741ed61dbb6d14f304f35b825`.
- `GET http://127.0.0.1:18088/props` refuses connections (WinError10061).
  `docker ps -a --filter name=bintanong-p09-cuda-latency` exits1 because the
  `dockerDesktopLinuxEngine` pipe is absent. No startup/restart was attempted.
- Saved completion requests contain NO logit bias. Current production `infer()` bans
  the thought-channel opener and newline tokens; blindly replaying through it would
  change frozen controls. The prepared diagnostic does not use `infer()`.

The protocol says: "A mismatch stops with zero completions" and "Failure or inconclusive
evidence ends this diagnostic without a replacement run." Both apply. No template rendering,
tokenization/headroom check or off/on completion occurred. No input/hash/schema repair or
rescue attempt followed. A prepared runner failed its first offline assertion and was never
frozen for inference; do not treat its existence as readiness or permission to run it.

## Commands and evidence

Shared Python executable:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Workspace evidence directory `audit-evidence/p11-checker-comparison-20261025/` contains:

- `compare.py offline`: expected exact-message assertion failure for d-en, exit1.
- `verify_stop.py`: offline audit of all four inputs/seals, exit0. No HTTP code or inference.
- `preflight-stop.json`: full identities and limitations. SHA256:
  `461e1a8df1c0787ca828e7ba0ec4c414a8ea7e747142e49fe351afcd3f113f22`.

Python commands used `-X utf8 -B`; no installs or dependency changes. Current Context thesis
physical17–18,39–44 and routing PNG were consulted. The thesis's illustrative missing-fact
example does not override the settled unknown-versus-unmet requirement. No new scope discrepancy.
Master3/11/13/16/23/24 and prompt/latency decisions reviewed; current Context7 server docs confirm
thinking controls but cannot substitute for absent resident-build/template verification.

## Recovery proposal — requires owner decision

Recommended only if the owner still wants this comparison: explicitly authorize a revised
preflight using the original checker code snapshot and starting the existing server. Before
any completion, resolve the exact historical source snapshot from sealed software hashes,
isolate it under ignored workspace evidence, and prove all four original messages/schemas/
identities match. Do not strip fields or patch identities in current production code.
Then verify the same resident build/model/template and all off/on prompts/token counts;
keep original four cases/order,768 output tokens,120s deadline and eight-call ceiling.
No new prompt, model, source, default or release change. A failed preflight stops again.

This proposal has NOT been executed or approved. A startup-only question was issued before
the input mismatch was diagnosed; startup approval alone does not approve a replacement run.
Alternatively end this diagnostic and choose the next quality correction separately.
The failed expanded-release gate, pending5856e82 full suite/review and other frontend prerequisites
remain outstanding. Documentation/diagnostic-only work uses seal/identity checks and phase-state
validation; no new PRD or artificial product tests. No full-suite result is claimed for this resume.
Phase-state validation passes; all22 local links in the four edited documents resolve;
`git diff --cached --check` passes. No source/model/runtime/default changes were staged.
