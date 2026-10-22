# Phase 06 translation review 01: two version-specific prerequisite lists

Status: both logic translations approved by the owner on 17 October 2026.
Source authority and institutional execution remain separate.
Student capability: correctly distinguish CC 5/L's prerequisite requirements across
the two supplied BSCS curricula before implementing a prerequisite check.

The course-row readings were confirmed on 14 October; do not reconfirm their
transcription. This new review concerns the proposed logical relationship between
the named courses. It does not ask the owner to reconstruct missing information.
Original pages were inspected read-only; crops below reproduce source pixels.

| Review | Scope | Already confirmed prerequisite cell | Proposed translation |
| --- | --- | --- | --- |
| P06-T01-old | BSCS 2018–2019; CC 5/L Information Management; physical 1, second year/second semester | `CC 3/L, CC 4/L` | Both CC 3/L **and** CC 4/L are required; `all_of(course(CC 3/L), course(CC 4/L))` |
| P06-T01-proposed | BSCS **proposed** 2025–2026; CC 5/L Information Management 1; physical 1 (printed 50), second year/first semester | `CC 3/L, CS 2` | Both CC 3/L **and** CS 2 are required; `all_of(course(CC 3/L), course(CS 2))` |

Each course reference stays within its own curriculum and source version. Preserve
`/L` and printed codes; do not merge editions or infer an equivalency. This review
only decides conjunction versus alternatives. It does not decide what passing
grade, repeated attempt, exemption, concurrency or substitution would satisfy a
requirement; those need explicit evidence before an executable decision.

## Exact original evidence

- Old original: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Computer Science/Old Curriculum (2018-2019)/ComSci-for-student-new-version.pdf`.
  SHA-256 `c781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d`.
  [Original page](../../../../audit-evidence/p06-foundation-20261017/old-bscs-physical1.png) ·
  [Second-year region](../../../../audit-evidence/p06-foundation-20261017/old-bscs-second-year.png).
- Proposed original: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Computer Science/New Curriculum (2025-2026)/1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf`.
  SHA-256 `600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664`.
  [Original page](../../../../audit-evidence/p06-foundation-20261017/proposed-bscs-physical1.png) ·
  [Second-year region](../../../../audit-evidence/p06-foundation-20261017/proposed-bscs-second-year.png).

Source version IDs are `ver-` followed by their full original SHA-256. Full pages
retain headings and proposed-edition labels; crop coordinates are pixel regions,
not invented native source-span geometry. Original bytes remain untouched.

## Reviewed question and owner decision

The question concerned whether each list means **both** named courses are required
in its respective curriculum. The owner answered: "yes approve to both, both are
currently still being used." Both proposed `all_of` translations above are accepted
for offline research. This does not select a curriculum for an unspecified student.
Keep the newer document's **proposed** label and the existing edition/cohort rules.

The owner also emphasized that `/L` belongs in the course codes and offered the
tentative explanation "I think that stands for Lab", referring to computer
laboratory classes alongside lectures. Preserve `/L` exactly as printed. Record
the expansion as tentative; do not derive separate courses, lecture/lab units,
pass conditions, equivalencies or co-requisite relationships from the suffix.

The exact original proposal records retain their historical pending status under
workspace `audit-evidence/p06-foundation-20261017/translation-proposals.json`:

- Old proposal SHA-256 `a5a7d71c95f3c0a855b3de846169e7d45c8dcd12de849e355890c7aa855e65e4`.
- Proposed proposal SHA-256 `c0b902d64d960b1eebbe0753c001424b408da95365cecf3e5b5ba2b6360127c4`.

The actual reply and both accepted proposal hashes are bound in the separate
ignored `translation-review-receipt.json`, SHA-256
`713e0b2c9b8cf551697dc569f338a53ae775c0131ac884d7a1da56b1c3df095f`.
`reviewed-translation-proposals.json` applies both accepted expressions separately;
the original proposal file is unchanged. Both files share the evidence directory.

These preliminary translation records are not Task 1 course-review receipts: full
scoped referenced-course records and complete source spans must be prepared before
minting their exact content digests. No new benchmark wording is approved here.
Source applicability/currentness/authority and all release guards remain unchanged.
