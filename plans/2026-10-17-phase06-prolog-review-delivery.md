# Phase 06 generated Prolog review delivery

Product `6fedc45`: separate partial review exporter. Owner approved its design
and review03 on 17 October 2026; candidate data is generated from reviewed records.
Status: **inactive partial research candidates**, not an eligibility evaluator or
institutional release. Strict preview behavior/version and exact baseline preserved.

## Files for human inspection

- [Readable generated review table](../../../../audit-evidence/p06-review-bundle-20261017/REVIEW.md).
- [2018–2019 candidate Prolog](../../../../audit-evidence/p06-review-bundle-20261017/old/bscs-old-candidate.pl) ·
  [coverage JSON](../../../../audit-evidence/p06-review-bundle-20261017/old/coverage.json).
- [Proposed2025–2026 candidate Prolog](../../../../audit-evidence/p06-review-bundle-20261017/proposed/bscs-proposed-candidate.pl) ·
  [coverage JSON](../../../../audit-evidence/p06-review-bundle-20261017/proposed/coverage.json).
- Original printed rows: [2018–2019](../../../../audit-evidence/p06-bscs-authoring-selections-20261017/old-reference-rows.png),
  [proposed2025–2026](../../../../audit-evidence/p06-bscs-authoring-selections-20261017/proposed-reference-rows.png).
  Exact source hashes/full originals remain in [review01](2026-10-17-phase06-translation-review-01.md).

Human check: compare the generated expressions/coverage labels against the already
accepted source meanings and original regions. Identify any generated line that
misrepresents them. This does not reopen the source/logic decisions in reviews01–03.
The readable table maps exact printed codes to hashed scoped IDs and file lines.

## Generated reviewed expressions

| Curriculum | Course | Generated direct prerequisite meaning | `.pl` line |
| --- | --- | --- | --- |
| 2018–2019 | CC 5/L | (CC 3/L) AND (CC 4/L) | 13 |
| 2018–2019 | CC 4/L | (CC 3/L) AND (CS 1/L) | 19 |
| 2018–2019 | CC 3/L | CC 2/L | 28 |
| 2018–2019 | CS 1/L | CC 1/L | 39 |
| **Proposed**2025–2026 | CC 5/L | (CC 3/L) AND (CS 2) | 13 |
| **Proposed**2025–2026 | CC 3/L | CC 2/L | 19 |
| **Proposed**2025–2026 | CS 2 | CS 1 | 30 |

There are eleven identities, ten reviewed identities and seven reviewed direct
expressions. Old CC1/L is a draft identity; oldCS1/L's reference to it is explicitly
flagged. Four direct-rule states are unknown: oldCC2/L, oldCC1/L, proposedCC2/L and
proposedCS1. Three of these are owner-confirmed blank-cell readings; oldCC1/L is
still an unreviewed source-row identity. No verified_none assertion is generated.

The owner's foundation-course explanation is retained as context, not a blanket
no-prerequisite rule. First-year placement alone does not resolve a blank cell.
No grade threshold, units, equivalency, exemption or enrollment approval is inferred.

## Predicate meanings

`candidate_fact` holds only values from reviewed records. `candidate_requirement`
holds only reviewed, fully specified direct expression trees. `candidate_reference_identity`
includes every printed identity and explicit reviewed/draft state. `candidate_coverage`
records all direct-rule states, unknown reasons and pending identity references.
The source/review/record JSON predicates are audit data, not additional approved
institutional rules. Unknown courses have no requirement fact, but stay in coverage.
Neither generated file contains an eligibility rule or consult directive.

## Verification and delivery scope

Focused RED15: expected absent new API; GREEN35 included strict-preview regressions.
Final related suites: **330 passed,29.91s**, exit0. One independent code review found
no actionable issue; reviewer independently observed330 passes. Synthetic output
was parsed as ground candidate data using installed SWI-Prolog with timeout.
No real-source file was consulted and no student decision or new benchmark was run.

Source delivery verification exit0: exact authoring/compiler replay for both
versions,53 native span occurrences (28 old,25 proposed), source hash/text/range/
box/page-size checks, applied review03 receipt hashes, prior record/manifest
preservation and generated file/coverage/human-line-map checks. Original source
states are unchanged. Windows newline translation initially changed saved file
hashes; exact UTF8 byte writing resolved this, and both bytes now match compiler
digests. This affected only the offline delivery script, not policy content.

## Reproduction and artifact identities

Raw evidence root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p06-review-bundle-20261017/`.
Use Python3.13 readiness executable at
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Preparation commands use `-B`, one script in the raw root, and repository absolute
path: `deliver_bundles.py` then `verify_delivery.py`. Both exit0. Generated `.pl`
bytes, ledgers, full review-bundle/coverage JSON, human maps and raw receipts stay
outside Git; only product code, synthetic tests and curated docs are tracked.

Related test invocation: `-B -m pytest -q -p no:cacheprovider
 tests/test_symbolic_review_bundle.py tests/test_symbolic_compiler.py
 tests/test_symbolic_authoring.py tests/test_contracts_symbolic.py
 tests/test_rule_candidates.py tests/test_prospectus_rule_handoff.py
 --basetemp=<raw-root>/regressions-temp`; external TEMP/TMP under the raw root.

Owner receipt SHA-256:
`5f06f640b750656300dc9bfc2b11abdbe722e4b86ce640ea07635d4ade092282`.
Original approved design bytes238ad3b are retained as ignored `approved-design.md`;
its hash is bound in the receipt. Review03 original proposals stay unchanged.

old Prolog SHA-256: `3be2d80c2c3f668d87b236cb664d3d958bb2cb6d70771e9fc2b6a4f91ce96967`;
semantic ledger SHA-256: `061bb19eb22e4bbc966a1fc8bdfcea3bcdea1a8b05ccb40a364e9c9a456163b6`.

proposed Prolog SHA-256: `a91487a48413bb37c024b6b88aa457186874176ef20d72a5d830dc429286635a`;
semantic ledger SHA-256: `cae2fa5d10bf33a78939b791fab838517e43c3d3c612927ad7256e27b2217fe4`.

Full Phase06 exit, source authority/release approval and typed Janus integration
remain separate. This delivery implements review export only. No dependency/model,
Supabase, Docker, API or registry change. Known model-path mismatch/Janus absence
remain in the checkpoint; they do not prevent human artifact inspection.

Docs/phase: **541 passed / 11 subtests,11.95s**, exit0 (`docs.log`).
Evidence manifest: 921 files, SHA-256 `8f578ad04dc039011621b08b7952a11498502a51ba1b1e7aa54fcabd6ea1cb1a`.
Generated-output human inspection was presented; actual answer remains pending.
