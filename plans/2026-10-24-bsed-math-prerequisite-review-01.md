# BSEd major in Mathematics (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`bsed-math/page.png`). "BSEd major in Mathematics, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).
Math 7 "Math 2 & 4, Math 5 (co-req)" = Math 2 + Math 4, Math 5 co-requisite (owner co-requisite-mark rule). Shorthand lists ("Math 2, 3, 4, & 10") written out with the Math prefix.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BSEd-Math-for-student-new-version.pdf`,
SHA256 `2ca91d0cb5f987bd6a57e608d626c15cee4f507f6222a0e3ea02142b89e0ec81`. Scope `palsu-bsed-math` / `bsed-math-2018-2019`, review `p09-bsed-math-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

Math 5 "Math 2"; Math 7 "Math 2 & 4, Math 5 (co-req)"; Math 8 "Math 2, 3"; Math 9 "Math 2"; PATH Fit 3 "PATH-Fit 1"; Math 13 "Math 7"; Math 14 "Math 3"; Math 15 "Math 12"; Math 16 "Math 2, 3, 4, & 10"; FS 2 "All Prof. Ed. & Specializ ation Courses"; Math 4 "Math 2"; GE-LWR "GE-PH"; PATH Fit 2 "PATH Fit 1"; Math 10 "Math 3 & 4"; Math 11 "Math 3"; Math 12 "Math 6"; PATH Fit 4 "PATH Fit 1"; Math 17 "Math 13"; Math 19 "Math 12"; Math 20 "Ed 1 & 4"; Ed 10 "Ed 9"; NSTP 2 "NSTP 1"; FS 3 "FS 1 and 2"; Ed 12 "All Gen. Ed., Prof. Ed. and Specializ ation Courses".

54 courses; 24 printed cells; 30 blank cells stay **unknown**, not "no prerequisite": Math 1, Math 2, GE-UTS, GE-PC, GE-PH, Ed 1, Ed 2, PATH Fit 1, GE-STS, Math 6, GE Elect: PPC, Ed 5, Ed 7, Ed 9, NSTP 1, GE-CW, GE-PS, Ed 11, Math 3, GE-MMW, GE-ET, Ed 3, Ed 4, GE-Elect: ES, GE-Elect: EM, GE-AA, Ed 6, Math 18, Ed 8, FS 1.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): Math 7: "4" -> Math 4; Math 7: "Math 2 & 4, Math 5 (co-req)" -> Math 2, Math 4, COREQ:Math 5; Math 8: "3" -> Math 3; Math 16: "3" -> Math 3; Math 16: "4" -> Math 4; Math 16: "10" -> Math 10; Math 10: "4" -> Math 4; Math 20: "4" -> Ed 4; FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 2: "All Prof. Ed. & Specializ ation Courses"; Ed 12: "All Gen. Ed., Prof. Ed. and Specializ ation Courses".
- Spacing, case or hyphen variant -> the one matching course: PATH Fit 3: "PATH-Fit 1" -> PATH Fit 1.
- Co-requisite: Math 7: "Math 5".
- List -> all required: Math 7: "Math 2 & 4, Math 5 (co-req)"; Math 8: "Math 2, 3"; Math 16: "Math 2, 3, 4, & 10"; Math 10: "Math 3 & 4"; Math 20: "Ed 1 & 4"; FS 3: "FS 1 and 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsed-math/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 54 reviewed courses, kinds {'unresolved': 32, 'course': 16, 'all_of': 6},
activation_allowed false, file SHA256 `eac112e91ce72e249a2126fa5dea215ba8fd5d7d1770346b82bbf3d0783645d3`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)
- Math 7 {'passed': ['Math 2', 'Math 4'], 'enrolled': ['Math 5']} -> eligible (expected eligible)
- Math 7 {'failed': ['Math 4']} -> ineligible (expected ineligible)

Affected by Ed 1: Math 20.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
