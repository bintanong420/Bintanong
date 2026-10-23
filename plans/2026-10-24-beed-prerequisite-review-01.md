# Bachelor of Elementary Education (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`beed/page.png`). "Bachelor of Elementary Education, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).
Two stray "3" marks inside the FS 1 / FS 2 cells are not visible text (not used). The elective row "Elective *" (Structure of English / Astronomy / Teaching Multi-grade Classes; choose one) is kept as printed.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BEEd-for-student-new-version.pdf`,
SHA256 `f98e9b4436f225a2d5a09ecefdeb5c2d913a3f6f054fd0a7bc0fb72fe6b491a0`. Scope `palsu-beed` / `beed-2018-2019`, review `p09-beed-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

PATH Fit 3 "PATH Fit 1"; SC-TTL 1 "Ed 1 & Ed 4"; FS 1 "All Prof. Ed. & Specializatio n Courses"; FS 2 "All Prof. Ed. & Specializatio n Courses"; GE-LWR "GE-PH"; PATH Fit 2 "PATH Fit 1"; PATH Fit 4 "PATH Fit 1"; Ed 10 "Ed 9"; FS 3 "FS 1 & 2"; Ed 12 "All Gen Ed, Prof. Ed. & Specialization Courses".

54 courses; 10 printed cells; 44 blank cells stay **unknown**, not "no prerequisite": GE-Elect: ES, GE-MMW, GE-PH, GE-AA, Ed 1, Ed 2, Ed 3, PATH Fit 1, Ed 6, SC-VE, SC-ARTS, SC-SCI 1, SC-MATH 1, SC-SSC1, GE-Elect: PPC, Ed 8, Ed 9, SC-MUSIC 1, SC-ENG 1, SC- FIL 1, SC-TLE 1, NSTP 2, GE-ET, GE-PS, GE-UTS, GE-CW, GE-PC, GE-STS, Ed 4, Ed 5, Ed 7, Elective *, SC-SCI 2, SC-MATH 2, SC-SSC 2, GE-Elect: EM, NSTP 1, Ed 11, SC-ENG 2, SC- FIL 2, SC-TLE 2, SC-PEH 2, SC-MTB-MLE 2, SC-RES 2.

Native text clipped out of the printed page (recorded, not used; owner 23 Oct 2026):

- FS 1: native cell "3 All Prof. Ed. & Specializatio n Courses"; hidden '3'
- FS 2: native cell "3 All Prof. Ed. & Specializatio n Courses"; hidden '3'

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 1: "All Prof. Ed. & Specializatio n Courses"; FS 2: "All Prof. Ed. & Specializatio n Courses"; Ed 12: "All Gen Ed, Prof. Ed. & Specialization Courses".
- List -> all required: SC-TTL 1: "Ed 1 & Ed 4"; FS 3: "FS 1 & 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `beed/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 54 reviewed courses, kinds {'unresolved': 47, 'all_of': 2, 'course': 5},
activation_allowed false, file SHA256 `f63a907ef9a2dfffd879475c8d2e0a5891a52287151b9f463276a362e93a752f`.
Real SWI-Prolog/Janus checks (offline research path): 5/5 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)

Affected by Ed 1: SC-TTL 1.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
