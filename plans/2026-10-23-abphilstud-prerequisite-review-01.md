# AB Philippine Studies (2018-2019) prerequisite review 01

23 October 2026, College of Arts and Humanities. Read from the rendered page (`abphilstud/page.png`).
"Bachelor of Arts in Philippine Studies, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR
Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals 20/20/17/20/18/21/18/9 match the
listed units; total 143 matches.

Owner decision (23 Oct 2026): a numbered range means every course of that prefix numbered in the
range, all required, electives excluded: SSc 13, SSc 14, SSc 16 "SSc 1- 9" = SSc 1..SSc 9; SSc 22
"SSc 1-19" = SSc 1..SSc 19; SSc 23 "SSc 1-20" = SSc 1..SSc 20 (every numbered SSc course 1-23 exists;
SSc Elect 1-3 excluded). Standing approval otherwise ("GE- PH" spacing). NSTP 2 has a blank cell
on this page. Page note: italics mark the specialization courses (not used to expand conditions).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAH/PhilStud/ABPhilStud-for-student-new-version.pdf`,
SHA256 `67bed602ab548a974a234424bfb578b377d10dca5aef83a1ea36651edc94f972`. Scope `palsu-abphilstud` / `abphilstud-2018-2019`, review `p09-abphilstud-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

SSc 1 "GE- PH"; SSc Elect 2 "GE- PH"; GE- Elect: PPC "GE-PH"; PATH Fit 3 "PATH Fit 1"; SSc 5 "GE- PH"; SSc 6 "GE- PH"; SSc 7 "GE- PH"; SSc 8 "SSc 3"; SSc 9 "SSc 3"; SSc 18 "SSc 14"; FL 2 "FL 1"; GE-LWR "GE-PH"; PATH Fit 2 "PATH Fit 1"; SSc 2 "SSc 1"; SSc 3 "SSc 1"; PATH Fit 4 "PATH Fit 1"; SSc 11 "SSc 8"; SSc 12 "SSc 3"; SSc 13 "SSc 1- 9"; SSc 14 "SSc 1- 9"; SSc 15 "GE- PH"; SSc 16 "SSc 1- 9"; SSc 17 "SSc 10"; SSc 22 "SSc 1-19"; SSc 23 "SSc 1-20".

48 courses; 25 printed cells; 23 blank cells stay **unknown**, not "no prerequisite": FL 1, GE- Elect: ES, GE-MMW, GE-AA, GE-PH, PATH Fit 1, NSTP 1, GE-ET, SSc Elect 1, SSc 10, SSc 19, SSc 20, SSc 21, GE-IER, GE- Elect: PES, GE-UTS, GE-CW, GE-PC, NSTP 2, GE-STS, SSc Elect 3, SSc 4, GE- PS.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): SSc 13: "SSc 1- 9" -> SSc 1, SSc 2, SSc 3, SSc 4, SSc 5, SSc 6, SSc 7, SSc 8, SSc 9; SSc 14: "SSc 1- 9" -> SSc 1, SSc 2, SSc 3, SSc 4, SSc 5, SSc 6, SSc 7, SSc 8, SSc 9; SSc 16: "SSc 1- 9" -> SSc 1, SSc 2, SSc 3, SSc 4, SSc 5, SSc 6, SSc 7, SSc 8, SSc 9; SSc 22: "SSc 1-19" -> SSc 1, SSc 2, SSc 3, SSc 4, SSc 5, SSc 6, SSc 7, SSc 8, SSc 9, SSc 10, SSc 11, SSc 12, SSc 13, SSc 14, SSc 15, SSc 16, SSc 17, SSc 18, SSc 19; SSc 23: "SSc 1-20" -> SSc 1, SSc 2, SSc 3, SSc 4, SSc 5, SSc 6, SSc 7, SSc 8, SSc 9, SSc 10, SSc 11, SSc 12, SSc 13, SSc 14, SSc 15, SSc 16, SSc 17, SSc 18, SSc 19, SSc 20.
- Spacing/case-only difference -> the one matching course: SSc 1: "GE- PH" -> GE-PH; SSc Elect 2: "GE- PH" -> GE-PH; SSc 5: "GE- PH" -> GE-PH; SSc 6: "GE- PH" -> GE-PH; SSc 7: "GE- PH" -> GE-PH; SSc 15: "GE- PH" -> GE-PH.
- List -> all required: SSc 13: "SSc 1- 9"; SSc 14: "SSc 1- 9"; SSc 16: "SSc 1- 9"; SSc 22: "SSc 1-19"; SSc 23: "SSc 1-20".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `abphilstud/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 48 reviewed courses, kinds {'course': 20, 'unresolved': 23, 'all_of': 5},
activation_allowed false, file SHA256 `85a94703f3d072fa8ce777d1d6150fdc090e3b8e52430efd81c53d4275c64657`.
Real SWI-Prolog/Janus checks (offline research path): 10/10 as the readings imply:

- SSc 2 {'passed': ['SSc 1']} -> eligible (expected eligible)
- SSc 2 {'failed': ['SSc 1']} -> ineligible (expected ineligible)
- SSc 13 {'passed': ['SSc 1', 'SSc 2', 'SSc 3', 'SSc 4', 'SSc 5', 'SSc 6', 'SSc 7', 'SSc 8', 'SSc 9']} -> eligible (expected eligible)
- SSc 13 {'passed': ['SSc 1', 'SSc 2', 'SSc 3', 'SSc 4', 'SSc 5', 'SSc 6', 'SSc 7', 'SSc 8']} -> unknown (expected unknown)
- SSc 13 {'passed': ['SSc 1', 'SSc 2', 'SSc 3', 'SSc 4', 'SSc 5', 'SSc 6', 'SSc 7', 'SSc 8'], 'failed': ['SSc 9']} -> ineligible (expected ineligible)
- SSc 23 {'passed': ['SSc 1', 'SSc 2', 'SSc 3', 'SSc 4', 'SSc 5', 'SSc 6', 'SSc 7', 'SSc 8', 'SSc 9', 'SSc 10', 'SSc 11', 'SSc 12', 'SSc 13', 'SSc 14', 'SSc 15', 'SSc 16', 'SSc 17', 'SSc 18', 'SSc 19', 'SSc 20']} -> eligible (expected eligible)
- SSc 18 {'passed': ['SSc 14']} -> eligible (expected eligible)
- SSc 1 {'passed': ['GE-PH']} -> eligible (expected eligible)
- FL 2 {'passed': ['FL 1']} -> eligible (expected eligible)
- SSc 10 {} -> unknown (expected unknown)

Affected by SSc 1: SSc 11, SSc 12, SSc 13, SSc 14, SSc 16, SSc 18, SSc 2, SSc 22, SSc 23, SSc 3, SSc 8, SSc 9.
Affected by GE-PH: GE- Elect: PPC, GE-LWR, SSc 1, SSc 11, SSc 12, SSc 13, SSc 14, SSc 15, SSc 16, SSc 18, SSc 2, SSc 22, SSc 23, SSc 3, SSc 5, SSc 6, SSc 7, SSc 8, SSc 9, SSc Elect 2.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal; ledger `316cecebd5b3`).
