# Per-part generation: actual-model observation results

21 October 2026. Protocol fixed in the [decision record](2026-10-21-per-part-generation-decision.md)
before running; code `6745393`, docs `32418e7`. Raw evidence (ignored):
workspace `audit-evidence/p09-per-part-20261021/` (`binding.json`, `*-result.json`,
`*-call-*.json`, `summary.json`). Author assessment of known fictional developer
cases, not independent human or institutional gold.

## Result: 4/4 complete content, 3/4 full quality (strict gate still FAIL)

| Case | Answer | Assessment |
| --- | --- | --- |
| d-en | "Students submit slip S to Office K." / "The listed charge is 7 tokens." | **PASS**. Previously failed (fee omitted, falsely marked complete). |
| d-fil | "Ihahain ang slip S sa Office K." / "Ang nakasaad na bayad ay 7 tokens." | PASS (unchanged). |
| d-tl | Same two claims as d-en, **in plain English** | **FAIL on language**: content complete and cited, but claims are not Taglish (previous scoped run: "Ang slip S ay isusumite sa Office K."). The reviewer still marked `language_appropriate=true`. |
| h-en | Janus `ineligible` / `not_completed:course-1` kept; "Students submit slip S to Office K." | PASS (unchanged). No invented link or approval. |

The per-part change fixed the targeted completeness failure. It did not
preserve Taglish claim style in one of one Taglish case, and the reviewer did not
detect that. One observation per case: no rate, causal or general claim. The
style miss is consistent with the two Taglish style errors already disclosed in
Phase 07.

## Timing (warm component, fixed documents; not student end-to-end)

Outer pipeline 45.3-48.7 s per case (scoped run: 43.7-49.8 s); generation stage
21.6-28.9 s. Four model calls per case (routing two, generation two), no repairs.
Excluded: embedding/vector/Supabase, API, browser, network, queueing. The
container cold start (~72 s after restarting the stopped container) is excluded.

## Runner defect before the counted run (disclosed)

The first attempt pointed the sealed harness's output folder at the sealed
task-first evidence for fixture reads; its write-once per-call logging hit
existing files and surfaced as routing `tool_error` after one routing call per
case. Zero generation calls; no quality data. The sealed folder was verified
unchanged (57/57 manifest hashes). Fixed by copying the four fixtures locally
(byte-checked); outputs kept in `attempt0-runner-defect/`. The counted run
above is the first run that reached generation.

## Next decision (owner)

Options for the Taglish style miss, none started: (a) a deterministic host
guard that triggers the existing one repair when a fil/taglish claim contains no
Filipino function words; (b) one prompt line asking each claim to mirror the
question's language mix; (c) accept and disclose it as the known Taglish
limitation. Option (a) adds no model call unless the guard fires. No prompt,
guard or rerun was attempted after this result.

## Second observation protocol: style guard (fixed before running)

Owner chose option (a) and directed natural Taglish: Filipino grammar words with
everyday English terms; no deep Tagalog such as "isusumite". Code `cd8e49b` adds
the deterministic style floor (existing single repair) and that prompt guidance.
Same runner, fixtures, model, settings and order, copied to a fresh evidence
folder `audit-evidence/p09-style-guard-20261021/`; one attempt per case.
Criteria: the unchanged strict gate, plus the owner's Taglish naturalness
reading (d-tl claims should read like typed Taglish; deep-Tagalog verbs are
reported as a style finding). Prompt examples share no wording with fixtures.
