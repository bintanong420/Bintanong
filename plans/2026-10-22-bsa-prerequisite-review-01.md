# BS Architecture prerequisite review 01

22 October 2026. Owner direction: review the programs that have no reviewed Prolog yet
(Phase 06 delivered the BSCS subset only), starting from the developer's sheet
`audit-evidence/cad_review_simple(AutoRecovered).csv` (77 extraction rows with verdicts).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAD/BSA-for-student-new-version.pdf`,
SHA256 `72dad4a0384f82228d63c8926e4ae8a1eb14a33497c9952e0f60782083e82666`, one page, "Bachelor of
Science in Architecture, Curriculum Program of Study, Effective SY 2018-2019*", Doc. Ref.
PSU-CIM-CUR-011B, Rev. 00, effective 11 June 2018, BOR Res. No. 62 s. 2019. Readings below
are taken from the rendered page (workspace `audit-evidence/p09-bsa-review-20261022/bsa-p1.png`),
not from the extraction. Undergraduate program: in scope.

## A. Prerequisite cells read directly from the page (printed text, unchanged)

Year 1, sem 2: AD-2/L "AD-1/L, TOA-1"; AR-INT/L "TOA-1"; GR-2/L "GR-1/L"; VT-2/L "VT-1/L";
TOA-2 "TOA-1"; NSTP-2 "NSTP-1"; PATH-Fit 2 "PATH-Fit 1".
Year 2, sem 1: AD-3/L "AD-2/L, TOA-2, AR-INT"; VT-3/L "VT-2/L"; Math 20 "MATH 19"; PATH-Fit 3 "PATH-Fit 1".
Year 2, sem 2: AD-4/L "AD-3/L"; BT-2/L "BT-1, BU-1/L"; HOA-2 "HOA-1"; BES 1 "MATH 20";
CE 31/FB "MATH 19-20"; PATH-Fit 4 "PATH-Fit 1".
Year 3, sem 1: AD-5/L "AD-4/L"; BT-3/L "BT-2, BU-1/L"; BU-2/L "BU-1/L"; HOA-3 "HOA-2";
GE-LWR "GE-PH"; Mech 32B "BES 1".
Year 3, sem 2: AD-6/L "AD-5/L"; ACAD-1/L "VT-3/L"; BT-4/L "BT-3/L"; BU-3/L "BU-2/L"; HOA-4 "HOA-3";
PLN-1 "CE 31/FB, TD-1"; CE47/B "Mech 32B".
Year 4, sem 1: AD-7/L "AD-6/L"; Ar-RM 1 "4th Year Standing"; BT-5/L "BT-4/L"; PLN-2 "PLN-1";
PP-2 "PP-1"; SP-1 "PLN-2"; ACAD-2/L "ACAD-1/L"; AS-1 "CE47/B".
Year 4, sem 2: AD-8/L "AD-7/L"; Ar-CC 1 "4th Year Standing"; Ar-RM 2 "4th Year Standing, Ar RM 1";
PLN-3 "PLN-2"; PP-3 "PP-2"; AS-2 "AS-1".
Year 5, sem 1: AD-9/L "AD-8/L"; Ar-CC 2 "4th Year Standing, Arc 1"; BM/AA-1 "PLN-2, PP-3";
HSNG "PLN-2, PP-1"; SP 2 "BT-5, PP-3".
Year 5, sem 2: D-10/L "AD-9/L"; SP-3 "D-7, PLN-2"; BM/AA-2 "PLN-2, PP-4".
Blank prerequisite cells (all other courses, e.g. AD-1/L, GE-CW, BT-1, PP-1, PEC) stay
**unknown**, not "no prerequisite" (source-gap policy; same as BSCS review03).

## B. Corrections to the developer's sheet (from the page)

- Confirmed extraction errors the developer marked: PATH-Fit 3 and PATH-Fit 4 need "PATH-Fit 1";
  GE-CW has a blank cell (the extraction's "PATH-Fit 1" belongs to PATH-Fit 4); ACAD-2/L needs
  "ACAD-1/L"; Ar-RM 2 needs "4th Year Standing, Ar RM 1"; PLN-3 needs only "PLN-2";
  BM/AA-1 is "PLN-2, PP-3"; HSNG is "PLN-2, PP-1"; SP 2 is "BT-5, PP-3".
- Marked "Passed / correct" but referencing courses that do not exist in this curriculum:
  BM/AA-2 "PP-4" (only PP-1 to PP-3 exist); SP-3 "D-7" (no D-7; closest is AD-7/L).
- "GE course" / "Foundational course" notes are context, not a printed no-prerequisite.
- Printed term totals: year 2 sem 2 prints 23; listed units sum to 22 (developer's note stands).

## C. Questions for the owner (consequential readings)

1. Comma lists ("AD-1/L, TOA-1"): all required (all_of), as approved for BSCS?
2. Printed shorter codes: TOA-1 -> TOA-1/L, AR-INT -> AR-INT/L, BT-2 -> BT-2/L, BT-5 -> BT-5/L,
   Ar RM 1 -> Ar-RM 1 (the 21 Oct alias rule covers spacing and "/L" only when unambiguous)?
3. "Arc 1" (Ar-CC 2) -> Ar-CC 1? "MATH 19-20" (CE 31/FB) -> both Math 19 and Math 20?
4. Code "D-10/L" titled "Architectural Design 9 - Thesis Research Application": keep printed code
   D-10/L as the course identity (its title's "9" kept as printed)?
5. Unresolvable printed references ("PP-4", "D-7"): keep as recorded source gaps (that
   condition unknown) rather than guessing PP-3 / AD-7/L?
6. "4th Year Standing": record as a non-course condition that stays unknown unless the student's
   year level is supplied (no year-level rule is invented)?

No rule is compiled or executed until these readings are approved.
