# BS Information Technology prerequisite review 01

23 October 2026. Next program after [BS Criminology 01](2026-10-22-crim-prerequisite-review-01.md)
(owner: "ok lets proceed"). No developer CSV exists for this program; readings come only from the page.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Information Technology/IT-for-student-new-version.pdf`,
SHA256 `70f7893959244addd897e77a57ac69736c55c1f6262292faf6e278fb0df26ac5`, one page, "Bachelor of
Science in Information Technology, Curriculum Program of Study, Effective SY 2018-2019*", Doc. Ref.
PSU-CIM-CUR-024, Rev. 00, effective 11 June 2018, *BOR Res. No. 62 s. 2019 dated 3 July 2019.
Read from the rendered page (workspace `audit-evidence/p09-bsit-review-20261023/bsit-p1.png`).
Undergraduate program: in scope. Phase 05 source register exists for this hash.

## A. Prerequisite cells read directly from the page (printed text, unchanged)

Year 1, sem 2: IT 2/L "CC 2/L"; CC 3/L "CC 2/L"; PATH Fit 2 "PATH Fit 1"; NSTP 2 "NSTP1".
Year 2, sem 1: IT 3/L "GE-MMW"; CC 4/L "CC 3/L"; IT E1/L "CC 3/L"; IT E2/L "2nd year standing";
PATH Fit 3 "PATH Fit 1".
Year 2, sem 2: GE-Elect: MDS "GE-MMW"; Electronics/L "GE-MMW"; CC 5/L "CC 3/L, CC 4/L";
IT 4 "IT 1/L, GE-MMW"; IT 5/L "IT E2/L"; IT 6/L "IT E1/L, IT E2/L"; IT 7/L "CC 4/L, IT E2/L";
PATH Fit 4 "PATH Fit 1".
Year 3, sem 1: IT 8/L "CC 5/L"; IT 9/L "IT 5/L, Electronics/L"; IT 10/L "IT 7/L"; IT 11/L "IT 6/L";
IT 12/L "CC 1/L"; IT E3/L "3rd year standing".
Year 3, sem 2: IT 13 "3rd yr. Standing"; CC 6/L "IT 8/L"; IT 14/L "IT 3/L"; IT 15/L "IT 7/L";
IT 16/L "IT 10/L"; IT 17 "IT 8/L, IT 10/L"; GE-LWR "GE-PH"; GE-IER "3rd yr. Standing".
Year 4, sem 1: IT 18/L "IT 16/L"; IT 19 "IT 17"; IT E4/L "4th year standing"; IT 20 "4th year standing".
Year 4, sem 2: IT 21 "IT 19"; IT 22 "70% total units of major courses passed and completed".
53 courses; 37 printed cells; 16 blank cells (all year-1 sem-1 courses, GE-AA, GE-ES, GE-MMW,
IT 1, GE-PH, GE-Elect: EM, GE-PS, GE-ET) stay **unknown**, not "no prerequisite".
Printed term totals 23/23/23/23/21/23/11/8 match the listed units; total 155 matches.
Layout: the code "Electronics/L" wraps without a hyphen ("Electroni" / "cs/L") in both its own
code cell and IT 9/L's cell; it is read as one word.

## B. Questions for the owner (consequential readings)

1. IT 4 (Quantitative Methods w/ Modelling and Simulation) prints "IT 1/L, GE-MMW", but the only
   IT 1 course is "IT 1" Discrete Mathematics (no "/L"). Map "IT 1/L" -> IT 1, or keep it as a
   source gap (that part unknown)?
2. Apply the patterns already approved for BS Architecture / BS Criminology: comma lists = all
   required (all_of); "2nd/3rd/4th year standing" and "3rd yr. Standing" = non-course condition,
   unknown unless the student states their year; IT 22's "70% total units of major courses passed
   and completed" kept as printed (unknown, refer to the college); "NSTP1" -> NSTP 1 (spacing rule)?

No rule is compiled or executed until these readings are approved.

## Owner decisions (23 October 2026)

Shown inline with program, course, title and printed text:
1. "IT 1/L" (IT 4) -> IT 1 Discrete Mathematics, the only IT 1 course. Approved.
2. Same rules as BS Architecture / BS Criminology, approved: comma lists are all_of; year-standing
   conditions ("2nd year standing", "3rd year standing", "3rd yr. Standing", "4th year standing")
   are non-course conditions, unknown unless the student states their year (chatbot may ask);
   IT 22's "70% total units of major courses passed and completed" kept as printed (unknown, refer
   to the college); "NSTP1" -> NSTP 1.
Section A's 37 printed cells (16 blank; 53 courses) are the reviewed readings under these decisions.
