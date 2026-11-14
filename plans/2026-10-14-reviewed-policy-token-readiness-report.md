# Exact token and source-governance readiness

The 77-reading candidate has **two exact encoder overflows** despite passing the
480-token estimate. No candidate is activated. This diagnostic continues Phase 05
from `94097c5`; plan `354b7b0` and the current checkpoint govern continuation.

| Inactive preview | Estimated tokens | Exact SEA-LION tokens | Encoder limit |
| --- | ---: | ---: | ---: |
| Charter pre-enrollment step 3 | 451 | 563 | 512 |
| Handbook cover | 423 | 539 | 512 |

All 77 exact measurements include special tokens, use the empty document prompt
and disable truncation. Counts range from 111 to 563. Source text alone fits for
both rows (70 and 27 tokens); the serialized fields and limitation metadata cause
the overflows. No vectors, rankings, quality scores or LLM answers were produced.
This does not establish whole-corpus token coverage or approved retrieval quality.

## Evidence and method

Ignored packet:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-reviewed-policy-token-readiness-20261014/`.
`measure.py` observes existing serializer return values during the real pending
adapter replay using a temporary Python profile hook. No input, scope or adapter
output is changed. The result equals the previously saved result: all 77 readings
withheld only for unknown undergraduate applicability, zero chunks. Each captured
text is explicitly an inactive preview, not a Chunk or assembled retrieval context.

Strict `QueryEncoder` verifies the existing external SEA-LION assets, pinned model
revision, Retrieval configuration and 512 context length before counting. Existing
approved Python 3.13.7/offline environment and CPU are reused; no dependency/model
installation or download. Configuration matches the saved real-encoder report.
Model/configuration/digests and exact package versions are in `model-binding.json`.
Pinned weights/revision SHA256:
`df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1`.
Existing versions: torch2.14.0, transformers5.19.0, sentence-transformers6.1.0,
tokenizers0.23.3. No version resolution or upgrade was performed.
The original token counts, previews, pending source registers and governance
inventory are retained separately from the trial below.

## Complete-field partition trial

`partition_and_measure.py` uses the existing checked helper without product changes.
Pre-enrollment step 3 divides into client/agency wording and fee/time/person/office;
the cover has one whole reviewed field per part. Full original-row bindings and
mandatory groups preserve 267 fields, 29 source blanks, 235 spans and seven logical
gap groups. Both policy defects and unknown applicability remain unchanged.

The trial has 81 unknown readings, zero chunks, and 13 projected gap-bearing parts.
The other 75 preview texts/source texts are unchanged. Existing full-group manifest
validation passes for the new groups. Estimated sizes fit, but exact sizes still
reach 542 tokens: pre-enrollment part 0 is 535; cover parts 1–3 are
542, 522 and 517, respectively. All exceed 512. The script
exits 1 on its intended sizing assertion. **The trial is not an accepted replacement
for the 77-reading candidate.** Saved failed outputs remain diagnostic evidence.

Repeating the complete manifest in each part's serialized text offsets the benefit
of smaller fields. Another arbitrary split cannot establish a safe encoder bound.
The next implementation must preserve complete stored manifests, original gap
reconstruction, all policy wording and limitations, while versioning any display
change and retaining legacy validation. It requires synthetic TDD and exact replay;
no limit increase, truncation or field omission is authorized by this measurement.

## Source governance and development evidence

Both exact source registers still have acquisition, verification and content-review
states pending; approval is not requested, approval IDs are null, and evidence lists
are empty. Issuer, campus, college, program, cohort, printed revision, effectivity
and supersession fields remain pending in those registers. All 77 applicability
declarations remain unknown with no applicability evidence reference.

These register states do not erase later selected transcription confirmations.
The owner has already confirmed the selected wording and reported the handbook's
Student Government Facebook origin and the Charter's PalSU website origin. The
staff comment was a qualified informal exchange about minimal changes. Preserve
those actual statements; do not repeat answered comparisons, characterize the
exchange as an interview, infer current effectivity, or treat it as issuing-office
authorization. The preparation bundle remains separate from source governance.

The existing governance contract requires verified acquisition/scope and evidence
for issuer/scope/effectivity (or a verified absence where allowed), followed by
issuing-office authorization bound to an approval ID. Diagnostics cannot supply
those decisions. Approved policy development labels and runtime retrieval/calibration
also remain outstanding. No prospectus review or incoming batch processing occurs.

## Historical drift and verification

The current 34-file evidence seal and six code digests match. Of its 809 historical
inputs, 808 still match. The superseded guide
`p05-owner-handbook-cover-confirmation-20261013/NEXT-REVIEW-SOURCE-RECORDS.md`
has changed from SHA256
`96fcd5f507c5ac068716331f4572e4fc72a5797584b1f814a611487685c0f51d` to
`f4320145d6d9d8dacc3767c23274097f365bbc62230e9b837541c8536945579f`.
The cause is unknown. Its old digest and filename are absent from active bundle
references/review events. Current bytes are copied into this new packet and both
hashes recorded; no previous file or seal was repaired or overwritten. Its obsolete
interview wording does not supersede the later recorded owner correction.

The first diagnostic stopped on this historical mismatch before producing previews;
the next run explicitly records the drift. The first regression command named one
nonexistent test module and ran no tests. Corrected relevant verification passes:
**64 tests and 94 subtests, 2.39s, exit 0**. Raw logs for both attempts are retained.
No product code changes require a new full repository run; the previous full-suite
result remains the evidence for unchanged product code.

One independent review found no Critical, Important or Minor findings. Fresh
verification reproduced all baseline/trial counts and real adapter replays,
reconstructed four original bindings and seven gaps, checked 15 active events and
both source bytes, and checked 45 native spans against original text/geometry.
Both original sections were visually inspected. Its final script exits 0; retained
reviewer harness assertion/output-name failures were corrected, not product bugs.
Trust remains limited to selected inactive previews, not assembled-context or
whole-corpus/retrieval/source approval evidence. No second review required.

Documentary checks:397 passed,3.57s,exit0; phase validate0/can-advance1(expected
blocked), diff check passes. New evidence manifest seals37files/sixcode digests;
SHA256 `7550fc07cb5d5e8448ea70629a822b7e995af6053129986db760dca71d1a187f`.
All861 observed input/model/code hashes match this run's recorded baseline; the
separate historical-drift report preserves the older mismatch, not a repaired seal.

The owner requested original sections for judgment. [Charter103step3](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-reviewed-policy-token-readiness-20261014/reviewer-original-charter-pre-enrollment-step-3.png>)
and [handbook cover](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-reviewed-policy-token-readiness-20261014/reviewer-original-handbook-cover.png>)
were shown with the70/27source-token distinction. No new judgment is inferred.

## Next action

Implement compatible compaction of record manifest display under a bounded TDD
plan, then rerun exact sizing on the unchanged 77-reading baseline and proposed
complete groups. Keep full manifests and limits in stored metadata and enforce
their reconstruction before context assembly. Source approval and development
labels remain separate gates; formal Phase 05 advancement stays blocked.

Final closure recheck:397 documentation tests pass1.06s; all37sealed artifacts/sixcode digests and manifest hash match. Seven curated text paths only, no private artifacts staged.
