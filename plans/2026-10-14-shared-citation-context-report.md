# Optional shared citation context — 14 October 2026

An optional source/page table removes repeated citation metadata while retaining
every original chunk payload and structured citation. The completion-conflict
group now fits 2,048 tokens at 1,917; the complete overload group remains too large
at 2,265 and is withheld intact. Candidate preparation remains provisional
undergraduate research with the owner's existing source limitations.

## Interface and preserved evidence

`build_context(..., shared_citations=True)` selects the new display. Both the
existing full citation format and `compact_citations=True` keep their original
behavior when this new option is absent or false. Neither runtime callers nor
defaults opt in. The flag requires an explicit boolean.

The first display line contains `citation_format: shared-source-locators-v1`
and `citation_sources`. Each source entry binds its exact version/hash/page and
`locator_defaults`, consisting only of keys with identical JSON values across
all locators for that source/page. Chunk headers retain original chunk IDs and
ordered groups of `source_index` plus residual `locators`. Merge each source's
defaults with its residual to reconstruct the exact original locator, including
missing keys, blank/null values and type distinctions such as false versus zero.

Only adjacent references are combined, preserving citation order. Each block's
text remains the exact original payload. All returned evidence fields, citations,
selection reasons, scores, source limits and complete logical groups remain
structured as before. Failed budget trials do not change accepted source defaults.
Trial and final admission use exact counts of their complete serialized display.
Existing source, manifest and required-neighbor checks still run before admission.

## Saved-case comparison

No embeddings, questions, rankings, source conversions or dependencies changed.
The comparison reused 21 candidate chunks, 36 accepted questions and existing scoped
rankings, with the same 900 context observations and the same local tokenizer hash:
`883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085`.

| Complete group | Previous compact citation tokens | Shared tokens | Citations retained |
| --- | --- | --- | --- |
| Overload, five parts |3186 |2265 |15 |
| Completion timing conflict, four parts |2270 |1917 |4 |

At the exploratory k=3 / threshold=0.5 point:

| Observation | Previous2048 | Shared2048 | Previous4096 | Shared4096 |
| --- | --- | --- | --- | --- |
| Complete expected evidence, scoped variants |24/30 |27/30 |30/30 |30/30 |
| Complete expected policy evidence |12/18 |15/18 |18/18 |18/18 |
| Cases with budget-gap entries, including rejected extras |18 |15 |12 |6 |
| Invalid context cases |0 |0 |0 |0 |

All 900 default-format observations replay exactly. The new displays yield 17 distinct
emitted strings, 212 archived citation bindings and 6,855 citation instances across
900 observations; each instance was decoded back to its exact original citation.
The 68 exact token counts include both old/new contexts and rejected trial strings.
These are repeated observations and citation instances, not independent source facts.

The remaining three overload language variants cannot recover the complete group
at 2,048. No field or condition was truncated to force it to fit. Larger budgets can
still reject extras while recovering all expected evidence. Reduced metadata also
allows additional irrelevant evidence to fit; it is not relevance calibration.
Primary ranking metrics remain unchanged and separate from full-group coverage.
Six BSCS variants still need curriculum scope. All scored cases are positive;
unsupported detection is unmeasured and no global threshold was selected.

## Verification and provenance

Plan `1e260ec`; verified pre-change baseline `ee38320` / product `f9b1502`.
Fresh context/phase baseline: 29 tests and 14 subtests passed in 10.05s. Eight regressions
observed expected missing-keyword RED: 10 failures including 3 subtest failures,
32 passed / 48 subtests in 1.09s. GREEN related suite: 82 tests / 97 subtests in 1.54s.
Full pytest: **5,252 passed / 497 subtests**, 6 skipped / 6 existing warnings in 315.28s,
exit 0. Run: existing Python 3.13 `-B -m pytest -q -p no:cacheprovider --basetemp`
with the ignored task pytest-full directory and `--tb=short`. Independent review
passes with no findings. The independent QA script/results and actual counts
are sealed alongside the raw measurements. Final documentation/phase results
are recorded at closure.

1,467 prior hashes verify, with exact old bytes snapshotted for authorized modified
code/test paths instead of falsely claiming their current bytes unchanged. Original
PDFs, historical raw packets, registers, questions, ranks and vectors remain unchanged.
Raw scripts, snapshots, context archives, token measurements and logs stay ignored at
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-shared-citation-context-20261014/`.

Consulted actual thesis physical 17–18, routing PNG, master section 10, Phase 04/05
records and scope/source-gap/service-association/dataset policies; no discrepancy.
School verification remains deferred separately, source activation is not approved,
and Phase 05 stays active with its blocked formal exit. Owner artifact changes remain
untouched; no runtime/API/Docker/database/Prolog work or Phase 06 advancement.

## Next action

Preserve the verified optional display and saved evidence. A further bounded
display-only change can share repeated whole-group metadata while retaining all
fields, source-limit messages, original identities and full structured evidence;
the overload group still requires 2,265 tokens in this format. Use synthetic TDD and
measure exact complete-group counts before changing budgets or admitting partial content.

Relevance calibration needs separately presented owner-reviewed unavailable-query
proposals before testing. Shared audience and reviewed wording decisions remain
settled; do not reopen them or repeat model encoding on a session change.

## Final review

Closure: **464 documentation/ledger tests and 11 subtests passed in 10.73s**.
Phase validation exits 0; advancement exits 1 as expected for blocked Phase 05.
The 33 ignored evidence files and 13 current code/test digests are sealed. Manifest
SHA256: `aa2b6c038e6501d0d1bab4bf0c91ff99efffd6904054f9378e41ed0c97bf2ca2`.
Product commit: `dea9442`; the following documentation commit is discoverable in Git.

Independent QA verified 1,800 full/compact baseline comparisons, 900 separate
admission simulations, 900 shared-format flag comparisons and 300 randomized
JSON-sensitive round trips. It independently checked 1,008 complete-group member
bindings, 5,025 field associations and 456 source-limit payloads; 104 distinct
strings were locally tokenized, including all 68 saved counts. Seven real-group
negative controls and two exact budget-boundary checks passed. All 1,467 prior
hashes, two authorized original test snapshots, six BSCS scope holds and the
reported group minima match. No implementation behavior was declined for review.

Final review: independent verification PASS, no Critical/Important/Minor findings.
Separate source-reference decoding, exact token counts and complete-group budget
replay agree with saved results; prior1467 hashes remain preserved through explicit
old-byte snapshots for authorized tracked edits. No calibration/source-authority/
activation claim is made by these technical checks; existing gates stand.
