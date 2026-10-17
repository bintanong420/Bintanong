# Phase 06 translation review 02: four referenced-course rows

Status: pending owner source/translation review. This batch adds four direct
prerequisite relationships; the two CC 5/L conjunctions from P06-T01 stay approved.
Student capability: preserve the correct version-scoped prerequisite/dependency
chain before compiling supported decisions. No grades or eligibility are evaluated.

## Exact original regions

Both are physical page 1 of the same originals used for review01; the proposed
page is printed 50. Regions retain the course-code/title/prerequisite columns and
semester headings. Images are unaltered pixel crops from the saved original renders.

- BSCS 2018–2019: [first/second-year rows](../../../../audit-evidence/p06-bscs-authoring-selections-20261017/old-reference-rows.png).
  Source SHA-256 `c781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d`.
- BSCS **proposed** 2025–2026: [first/second-year rows](../../../../audit-evidence/p06-bscs-authoring-selections-20261017/proposed-reference-rows.png).
  Source SHA-256 `600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664`.

The original paths and full-page images remain linked in [review01](2026-10-17-phase06-translation-review-01.md).
Source versions are `ver-` followed by the original SHA-256. Exact character ranges,
text and native bounding boxes are retained in the ignored proposal records.

## Proposed readings and logic

| Review | Curriculum | Printed course (title for locating the row) | Printed prerequisite cell | Proposed meaning |
| --- | --- | --- | --- | --- |
| P06-T02-old-1 | 2018–2019 | CC 3/L — Computer Programming 2 | CC 2/L | Requires CC 2/L |
| P06-T02-old-2 | 2018–2019 | CC 4/L — Data Structures and Algorithms | CC 3/L, CS 1/L (wrapped onto two lines) | Requires **both** CC 3/L and CS 1/L |
| P06-T02-proposed-1 | **Proposed** 2025–2026 | CC 3/L — Computer Programming 2 | CC 2/L | Requires CC 2/L |
| P06-T02-proposed-2 | **Proposed** 2025–2026 | CS 2 — Discrete Structures 2 | CS 1 | Requires CS 1 |

The proposed CS 2 row's superscript title footnote is separate from the course
identity/number. Preserve the codes exactly: old **CS 1/L** and proposed **CS 1**
are different scoped records; do not append/remove `/L` or assume equivalence.
Titles here locate the rows and are not added as reviewed authoring facts.

## Focused question

Do these four code/prerequisite readings and proposed direct relationships match
the original rows? Confirm all four, or identify the item/reading that needs correction.
This does not ask again about either CC 5/L rule. It does not approve passing
thresholds, exceptions, unit interpretation, source authority or activation.

The six-course draft selections remain held: referenced-course logic is unresolved,
so no whole-selection Prolog is emitted. If approved, extend only these direct
relationships using their actual referenced-course records. Unknown or blank
prerequisite cells on other courses stay unresolved; no blanket no-prerequisite rule.

## Exact proposal identities

Ignored records: workspace `audit-evidence/p06-bscs-authoring-selections-20261017/`
`reference-translation-proposals.json`. Each includes its exact native source spans.

- P06-T02-old-1: `bd9da3439f1428c902a0f093afe99c24dcbbc500028d8753c9a89a744d6a3bd6`.
- P06-T02-old-2: `a42e25862a15f351a31504cd86645ad75489f35c319ba98d185365b979ca421c`.
- P06-T02-proposed-1: `a5a1380063023ef71055df2322dcea2e0d44b90c9e739e2619e5287e027bed83`.
- P06-T02-proposed-2: `5622815781aa769585ecc35fa899443448cb1255cb03ec1619cedf87ebf13099`.

Record the actual answer separately against these hashes; preserve the original
proposals. This is a bounded research review, not whole-curriculum approval.
