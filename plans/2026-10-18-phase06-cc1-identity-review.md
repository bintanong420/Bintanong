# Phase06: old CC1/L identity confirmed and regenerated

On18October2026 the owner answered the exact source-identity question:
"CC1/L - Intro to Computing is the pre-req for CS1/L - Discrete Structs 1".
The displayed evidence was old2018-2019 physical page1, first-year/first-semester
CC1/L row, alongside the CS1/L second-semester prerequisite cell. This confirms
the pending course-code identity and retains the already approved review03 edge.
No units, numerical passing grade, title fact or own-prerequisite rule was added.

## Applied through the existing pipeline

New ignored root:workspace/audit-evidence/p06-cc1-identity-20261018.
owner-decision.json records the question/actual answer, original/image hashes,
exact record digest and new review reference owner-old-cc1-identity-20261018.
verify_identity.py reuses build_curriculum_ledger, the partial review compiler,
prepare_runtime_bundle and the existing offline research/Janus runtime.

Only the oldCC1/L record changes:reviewed code identity, digest-bound review
reference and truthful unresolved-own-rule reason. Its only fact remains the
source-supported course_code. Its own condition stays unresolved. All other
course records and source lifecycle states remain identical; proposed artifacts
reproduce their prior hashes. All activation/eligibility flags remain false.

Original SHA-256:c781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d.
Code span:physical1, native chars699-705, text CC 1/L;
box25.399999618530273/239.60997009277344/50.27300262451172/248.52996826171875,
top-left origin, page612x936. This span locates the row; it does not quote an
unprinted no-prerequisite assertion. Eleven identities are now reviewed; seven
direct expressions and four unresolved direct conditions remain.

## Verified behavior and preservation

Baseline RED:original bundle returned unknown for failedCC1/L where the owner's
desired CS1/L result is ineligible. red.log contains that exact assertion failure.
GREEN:new generated bundle passes all73 existing BSCS cases with updated
expectations only where identity review permits the already approved CS1/L rule.

| Original IDs | Fictional CC1/L state | New CS1/L result |
| --- | --- | --- |
| H27-H28 | Failed | ineligible; CC1/L prerequisite unmet |
| H29-H30 | Passed | eligible; no missing prerequisite |
| H31 | Missing | unknown; completion missing |
| H32 | Passed and failed | unknown; completion conflict |

H34 still returns unknown/rule_unresolved for CC1/L's own eligibility. Four
concurrent request-isolation checks, repeat-result equality/timeout recovery for
both versions and39 native source spans pass. as_policy_result still rejects
research decisions. Prior source/bundle artifacts and the owner's CSV are unchanged.
CS1-REVIEW.md presents the six updated cases without internal course IDs.

Old generated PL SHA:d7f58f095f50ceee5a28b3ef6b1df41c0b4be9c328279639fe7eb367e72a1257.
Old runtime bundle SHA:4448702d80294c10d71270b5dca07847f71c1a101a41130be18bf8b699c4f351.
Proposed PL SHA:a81b4c40c690dfdc542c71ae926e8bbf822d52446a40c86960fbcc0dd618677a.
Proposed bundle SHA:3e136f28a9b10b783c6a3e01ac6adcabe5d2a530731d4d14415cbc3db723c0a3.
19 non-log files verified by manifest.json SHA:
275393faf80156eee4d3e8e826a0591ed56987be12c17d1586b2257f92b8bdb5.
CURRICULUM-REVIEW.md reduces the final generated-output inspection to seven
source-linked prerequisite meanings with exact generated line references.
Fresh docs/phase553 passed/11 subtests12.61s; raw log is under
workspace/audit-evidence/p06-closeout-checklist-20261018/docs-identity.log.

No product code, dependency, registry, source authority or release state changed.
The original reviewed CSV remains a historical review of its original bundle;
its outputs/hashes are not silently rewritten to describe this newer bundle.
No new blanket generated-output approval or institutional release is inferred.
Remaining closure items are in the [short checklist](2026-10-18-phase06-closeout-checklist.md).
