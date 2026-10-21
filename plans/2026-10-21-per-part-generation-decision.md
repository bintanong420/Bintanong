# Per-part generation: answer every question part by construction

21 October 2026. Phase 09 remains active. Owner decision this session: build
per-part generation (option recommended over the native-thinking checker trial).
This **supersedes the unrun proposal** in
[checker diagnosis](2026-10-21-checker-completeness-diagnosis-and-proposal.md);
that comparison will not be run. Earlier evidence and seals stay unchanged.

## Root cause the previous loop missed

The selected `scoped` generator (`DocumentExplanation` v1) received the declared
question parts only as background data. Its claim format had no link to a part
and its prompt never required every part to be answered, so omitting the fee in
the English case was unconstrained. All completeness detection then fell on a
post-hoc 4B reviewer asked to build the whole part-to-claim mapping itself, and
it mapped the fee part to an office claim. Successive prompt edits, reviewer
instructions and the proposed thinking toggle all targeted that second line of
defence; none made the generator commit to each part.

## Design (selected profile `parts`)

- Generation contract `bintanong-part-explanation-v1`: `answers` is an object
  with one **required** slot per declared document part (constrained decoding
  cannot skip one). Each slot is `answered` with claims, or `not_in_evidence` /
  `source_gap` with no claims. Structured parts get no slot; the host's
  canonical Prolog result still covers them.
- The host numbers claims `c1..cN` and derives the part mapping from the slots.
  A per-slot claim budget keeps the total within eight.
- A slot declared unavailable withholds the answer as `insufficient_evidence`
  with an `unavailable` ledger entry, without spending the review call.
- Review contract `bintanong-part-confirmation-v1`: the reviewer sees each part
  with ONLY its own claims and answers `answers` / `does_not_answer` /
  `uncertain`, plus the unchanged per-claim support verdicts. Any non-`answers`
  verdict withholds the answer, as before.
- Same two model calls per RAG/Hybrid answer as the scoped path; no new call,
  budget, model, training, dependency or threshold change. Older profiles stay
  as explicit historical options. Ledger contract and final validation unchanged.

## Verification so far

TDD: 12 new tests in `tests/test_generation_part_slots.py` failed first (10 for the
missing feature, then 2 for runtime default/evaluation hashes) and now pass.
Nine older tests that silently depended on the `scoped` default were pinned to
`scoped` or updated to the new default; their assertions were not weakened.
Full-suite result: see checkpoint.

## Actual-model observation protocol (fixed before running)

Runner: workspace `audit-evidence/p09-per-part-20261021/observe_parts.py`. It
reuses the sealed router-gate harness (hash-checked) and the task-first fixtures
(`request-inputs.json` SHA256 `7099cc39...e080`) read-only; only the generation
profile changes to `parts`. Existing CUDA container on 18088 (same model, build
b11723-31288c9c6, ctx 8192, out 768, temp 0, seed 0). One attempt per case in
fixed order d-en, d-fil, d-tl, h-en; no reruns, prompt edits or rescue.

Pass criteria are the previous gate's, unchanged: each case answered; every
requested part correctly answered by cited, source-supported claims (Office K
and the 7-token charge; h-en keeps the actual Janus `ineligible` result and
Office K with no invented link); appropriate requested language. d-en is the
case that previously failed. Withholding a complete answer counts as a failure,
not a pass. Four known developer cases are not an accuracy rate or independent
test; timings are warm component times, not student end-to-end latency.

## Limits and follow-ups

- Mock tests prove structure and host behaviour only. Whether Gemma actually
  fills the fee slot correctly is unmeasured until an actual-model run on the
  four saved developer cases (English, Filipino, Taglish, Hybrid relevance).
- The reviewer can still wrongly confirm a part; the narrower per-part question
  should reduce, not eliminate, that error. `semantic_completeness` stays
  `unverified`.
- A generator can wrongly declare `not_in_evidence`; that fails safe (withheld).
- Follow-up (not done): the answer contract withholds every claim when one part
  is unresolved. The thesis scope (physical 17-18) expects the system to state
  the unavailable detail; answering verified parts while naming the missing one
  is a separate design change needing its own review.
- All undergraduate, read-only, source-gap, privacy, institutional-release and
  one-week improvement boundaries are unchanged. No activation or Phase 10.
