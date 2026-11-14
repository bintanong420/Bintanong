# BS Computer Science, old curriculum (2018-2019) prerequisite review 01

23 October 2026, College of Sciences. Full review of the old BSCS curriculum (Phase 06 delivered six
courses only). Read from the rendered page (`bscs-old/page.png`). "Bachelor of Science in Computer
Science, Curriculum Program of Study, Effective SY 2018-2019*", Doc. Ref. PSU-CIM-CUR-022B, Rev. 00,
effective 11 June 2018, *BOR Res. No. 62 s. 2019 dated 3 July 2019. Undergraduate: in scope.
Eight-column table (no Grade column).

Consistency with Phase 06: same source version and course identities; CC 1/L, CC 2/L (blank, unknown),
CC 3/L (CC 2/L), CS 1/L (CC 1/L), CC 4/L (CC 3/L + CS 1/L), CC 5/L (CC 3/L + CC 4/L) are reproduced
exactly (owner reviews 01-03, 17 Oct 2026).

Printed totals: year 2-4 terms 23/23/21/20/17/8 match; both year-1 TOTAL cells print "3" although the
listed units sum to 23 each (printing defect, recorded). Year 4 sem 2 shows a stray unit "3" in an
empty row under CS 20 (counted in the printed 8; no course code or title) - a possible missing row,
recorded as a source gap; no course is invented. All prerequisite readings fall under the standing
approval: comma lists all required; "3rd yr. Standing"/"4th yr. Standing" unknown unless the year is
given; CS 20's "70% of the total number of units in the curriculum must be completed" kept as printed;
"Electronics/" / "L" is a line wrap of the code "Electronics/L" and "Electronics /L" is spacing.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Computer Science/Old Curriculum (2018-2019)/ComSci-for-student-new-version.pdf`,
SHA256 `c781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d`. Scope `palsu-bscs` / `bscs-2018-2019`, review `p09-bscs-old-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

CC 4/L "CC 3/L, CS 1/L"; CS 2/L "CC 3/L"; CS 3 "CS 1/L"; PATH Fit 3 "PATH Fit 1"; Electronics/L "GE-MMW"; CC 6/L "CC 3/L, CS 2/L"; CS 7/L "CC 4/L, CS 4/L"; CS 8/L "CS 5"; CS 9/L "CS 5, CS 2/L"; CS 10/L "CS 6"; CS E1/L "3rd yr. Standing"; CS 16/L "CS 3, CS 4/L"; CS 17/L "CS 11/L"; CS 18/L "CS 6, CS 15/L"; CS 19 "CC 5/L, CC 6/L"; Thesis 2 "Thesis 1"; CS E3 "4th yr. Standing"; CC 3/L "CC 2/L"; CS 1/L "CC 1/L"; PATH Fit 2 "PATH Fit 1"; NSTP2 "NSTP1"; MATH ELEC "GE-MMW"; GE-LWR "GE-PH"; CC 5/L "CC 3/L, CC 4/L"; CS 4/L "CC 1/L, CC 4/L"; CS 6 "CC 4/L, CS 3"; CS 5 "CS 3"; PATH FIT 4 "PATH Fit 1"; CS 11/L "CC 6/L, CS 2/L, CC 5/L"; CS 12/L "CS 2/L, CC 6/L"; CS 13/L "CC 5/L"; CS 14/L "CC 4/L, CS 6"; CS 15/L "CC 6/L, CS 4/L"; Thesis 1 "Electronics /L, CS 8/L"; CS E2/L "3rd yr. Standing"; Thesis 3 "Thesis 2"; CS 20 "70% of the total number of units in the curriculum must be completed".

54 courses; 37 printed cells; 17 blank cells stay **unknown**, not "no prerequisite": GE-Elect: ES, GE-MMW, GE-AA, CC 1/L, CC 2/L, GE-PH, PATH Fit 1, NSTP1, GE-ET, IER, GE-EM, GE-MDS, GE-UTS, GE-CW, GE-PC, GE-STS, GE-PS.

## Rules applied

- Year standing -> unknown unless the student states their year: CS E1/L: "3rd yr. Standing"; CS E3: "4th yr. Standing"; CS E2/L: "3rd yr. Standing".
- Kept as printed, unknown: CS 20: "70% of the total number of units in the curriculum must be completed".
- Spacing/case-only difference -> the one matching course: Thesis 1: "Electronics /L" -> Electronics/L.
- List -> all required: CC 4/L: "CC 3/L, CS 1/L"; CC 6/L: "CC 3/L, CS 2/L"; CS 7/L: "CC 4/L, CS 4/L"; CS 9/L: "CS 5, CS 2/L"; CS 16/L: "CS 3, CS 4/L"; CS 18/L: "CS 6, CS 15/L"; CS 19: "CC 5/L, CC 6/L"; CC 5/L: "CC 3/L, CC 4/L"; CS 4/L: "CC 1/L, CC 4/L"; CS 6: "CC 4/L, CS 3"; CS 11/L: "CC 6/L, CS 2/L, CC 5/L"; CS 12/L: "CS 2/L, CC 6/L"; CS 14/L: "CC 4/L, CS 6"; CS 15/L: "CC 6/L, CS 4/L"; Thesis 1: "Electronics /L, CS 8/L".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bscs-old/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 54 reviewed courses, kinds {'all_of': 15, 'course': 18, 'unresolved': 21},
activation_allowed false, file SHA256 `4f56bf4bfa6aa84b5f781e0438f90a452bc1a2a4d25eb2b29ed012a94c523499`.
Real SWI-Prolog/Janus checks (offline research path): 11/11 as the readings imply:

- CC 5/L {'passed': ['CC 3/L', 'CC 4/L']} -> eligible (expected eligible)
- CC 5/L {'passed': ['CC 3/L'], 'failed': ['CC 4/L']} -> ineligible (expected ineligible)
- CC 4/L {'passed': ['CC 3/L', 'CS 1/L']} -> eligible (expected eligible)
- CS 1/L {'passed': ['CC 1/L']} -> eligible (expected eligible)
- CS 11/L {'passed': ['CC 6/L', 'CS 2/L', 'CC 5/L']} -> eligible (expected eligible)
- CS 11/L {'passed': ['CC 6/L', 'CS 2/L']} -> unknown (expected unknown)
- Thesis 1 {'passed': ['Electronics/L', 'CS 8/L']} -> eligible (expected eligible)
- NSTP2 {'passed': ['NSTP1']} -> eligible (expected eligible)
- CS E1/L {'passed': ['CC 6/L']} -> unknown (expected unknown)
- CS 20 {} -> unknown (expected unknown)
- CC 2/L {} -> unknown (expected unknown)

Affected by CC 4/L: CC 5/L, CS 10/L, CS 11/L, CS 13/L, CS 14/L, CS 15/L, CS 16/L, CS 17/L, CS 18/L, CS 19, CS 4/L, CS 6, CS 7/L.
Affected by CS 3: CS 10/L, CS 14/L, CS 16/L, CS 18/L, CS 5, CS 6, CS 8/L, CS 9/L, Thesis 1, Thesis 2, Thesis 3.

Not yet loaded into Supabase or wired into the runtime release.
