# BS Criminology prerequisite review 01

22 October 2026. Owner chose this program next (after [BS Architecture 01](2026-10-22-bsa-prerequisite-review-01.md)),
starting from the developer's sheet
`audit-evidence/BS-in-Criminology-for-student-new-version_review (version 1).xlsb.csv` (64 rows + a
"Missing: Path Fit DEFTAC 3" note).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CCJE/BS-in-Criminology-for-student-new-version.pdf`,
SHA256 `b3b43dece33b171af81fdc738da45864f204188b068d66a180b670270f36a2d3`, one page, "Bachelor of
Science in Criminology, Curriculum Program of Study, Effective SY 2018-2019", Doc. Ref.
PSU-CIM-CUR-010A, Rev. 00, effective 11 June 2018, *BOR Res. No. 62 s. 2019 dated 3 July 2019.
Readings below are taken from the rendered page (workspace `audit-evidence/p09-crim-review-20261022/crim-p1.png`),
not from the extraction. Undergraduate program: in scope. Phase 05 source register exists for this hash.

## A. Prerequisite cells read directly from the page (printed text, unchanged)

Year 1, sem 2: Crim 2 "Crim 1"; PATH Fit-DEF TAC 2 "PATH Fit-DEF TAC 1"; NSTP 2 "NSTP 1".
Year 2, sem 1: LEA 2 "LEA 1"; CDI 2 "CDI 1"; PATH Fit-DEFTAC 3 "PATH Fit-DEFTAC 2".
Year 2, sem 2: GE - LWR "GE-PH"; CDI 3 "CDI 2"; Forensic 2/L "Forensic 1/L"; Forensic 3/L "Forensic 2/L";
Crim 3 "Crim 2"; LEA 3 "LEA 2"; CLJ 2 "CLJ 1"; PATH Fit-DEFTAC 4 "PATH Fit-DEFTAC 3".
Year 3, sem 1: CLJ 3 "CLJ 2"; CDI 4 "CDI 3"; Forensic 4/L "Forensic 3/L"; LEA 4 "LEA 3"; Crim 4 "Crim 3";
CA 2 "CA 1"; CFLM 2 "CFLM 1"; CDI 5 "CDI 4 (co-requisite)"; Crim 5 "Crim 4 (co-requisite)".
Year 3, sem 2: CA 3 "CA 2"; CLJ 4 "CLJ 3"; Forensic 5/L "Forensic 4/L"; CDI 6 "CDI 5"; Crim 6 "Crim 5";
CDI 7 "CDI 6 (co-requisitie)" (misspelling printed); CDI 8 "CDI 7 (co-requisite)".
Year 4, sem 1: CP 1 "All major courses from 1st to 3rd year"; CLJ 5 "CLJ 4"; Crim 7 "Crim 6";
Forensic 6 "Forensic 5"; CDI 9 "CDI 8"; CE 1 "All major courses from 1st to 3rd year"; CDI 10 "CDI 9 (co-requisite)".
Year 4, sem 2: CP 2 "CP 1"; CLJ 6 "CLJ 5"; Crim 8 "Crim 7"; CDI 11 "CDI 10"; CE 2 "CE 1".
65 courses; 42 printed cells; 23 blank cells (e.g. Crim 1, LEA 1, CDI 1, CA 1, CLJ 1, CFLM 1,
Forensic 1/L, all GE courses, GE-IER, NSTP 1) stay **unknown**, not "no prerequisite".
Printed term totals 24/27/26/28/27/27/21/15 match the listed units; total 195 matches.
Page note: "Subjects printed in italics are the specialization courses for the BS in Criminology Program."

## B. Corrections to the developer's sheet (from the page)

- Missing row confirmed: PATH Fit-DEFTAC 3 "First Aid and Water Safety", 2 units, year 2 sem 1,
  prerequisite "PATH Fit-DEFTAC 2". Then PATH Fit-DEFTAC 4's "PATH Fit-DEFTAC 3" does name a course.
- Spill-over fixed from the page: CDI 10 is "CDI 9 (co-requisite)" (sheet: "to 3rd year");
  CDI 9 is "CDI 8" (sheet: "5 CDI 8"); CLJ 5 is "CLJ 4" (sheet: "3rd year CLJ 4"); Forensic 6 is
  "Forensic 5" (sheet: "Forensic"); CP 1 and CE 1 are the full "All major courses from 1st to 3rd year".
- GE - PC's title is "Purposive Communication" only (LEA 1's title text overflowed in the sheet).
- "GE sub" / "foundational course" notes are context, not a printed no-prerequisite.

## C. Questions for the owner (consequential readings)

1. "(co-requisite)" cells (CDI 5, Crim 5, CDI 7, CDI 8, CDI 10): record as co-requisite, meaning
   the student has passed that course before or is taking it the same term (engine `co_requisite`)?
2. "All major courses from 1st to 3rd year" (CP 1, CE 1): keep as a non-course condition that stays
   unknown (chatbot refers the student to the college), rather than expanding it to a course list?
3. Short printed references: "Forensic 5" -> Forensic 5/L; "PATH Fit-DEFTAC 2" (year 2) -> the
   year-1 course printed "PATH Fit-DEF TAC 2"; each code kept as printed (DEF TAC 1/2 vs DEFTAC 3/4)?

No rule is compiled or executed until these readings are approved.

## Owner decisions (22 October 2026)

Shown inline with program, course, title and printed text (the owner cannot open the files):
1. "(co-requisite)" cells are `co_requisite`: satisfied if the student passed that course or is
   taking it the same term; enrollment not supplied stays unknown. Approved.
2. "All major courses from 1st to 3rd year" (CP 1, CE 1): owner: "keep as whatever is in the
   paper/data because we dont wanna be changing stuff". Recorded verbatim as a non-course
   condition (unknown; chatbot shows the printed wording and refers to the college). Not expanded
   to the italic specialization courses.
3. "Forensic 5" -> Forensic 5/L and "PATH Fit-DEFTAC 2" -> PATH Fit-DEF TAC 2; every course code
   kept as printed. Approved.
Section A's 42 printed cells (23 blank; 65 courses) are the reviewed readings under these decisions.
