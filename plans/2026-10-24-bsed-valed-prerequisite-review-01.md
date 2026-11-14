# BSEd major in Values Education (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`bsed-valed/page.png`). "BSEd major in Values Education, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).
The code "Ed 12" is printed on two rows, "Environmental Education" and "Integrating Course in Education": kept as two courses told apart by title (owner duplicate-code rule).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BSEd-ValEd-for-student-new-version.pdf`,
SHA256 `1ab6a0d0b878a85679c0e0dbd241bd9065b0009daf85928e8b4708ef4ade77b1`. Scope `palsu-bsed-valed` / `bsed-valed-2018-2019`, review `p09-bsed-valed-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

FS 2 "All Prof. Ed. & Specializat ion Courses"; GE-LWR "GE-PH"; PATH-Fit 2 "PATH Fit 1"; VED 21 "Ed 1 & 4"; Ed 10 "Ed 9"; NSTP 2 "NSTP 1"; FS 3 "FS 1 and 2"; Ed 12 "All Gen. Ed., Prof. Ed. & Specializat ion Courses".

55 courses; 8 printed cells; 47 blank cells stay **unknown**, not "no prerequisite": VED 1, VED 2, GE-UTS, GE-PC, GE-PH, Ed 1, Ed 2, PATH-Fit 1, GE-STS, VED 5, VED 6, VED 7, VED 8, VED 9, GE-Elect: PPC, Ed 5, PATH Fit 3, VED 14, VED 15, VED 16, VED 17, VED 18, Ed 7, Ed 9, NSTP 1, GE-CW, GE-PS, Ed 12, VED 3, VED 4, GE-ET, GE-MMW, Ed 3, Ed 4, GE-Elect: ES, VED 10, VED 11, VED 12, VED 13, GE-Elect: EM, GE-AA, Ed 6, PATH Fit 4, VED 19, VED 20, Ed 8, FS 1.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): VED 21: "4" -> Ed 4; FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 2: "All Prof. Ed. & Specializat ion Courses"; Ed 12 [Integrating Course in Education]: "All Gen. Ed., Prof. Ed. & Specializat ion Courses".
- Spacing, case or hyphen variant -> the one matching course: PATH-Fit 2: "PATH Fit 1" -> PATH-Fit 1.
- List -> all required: VED 21: "Ed 1 & 4"; FS 3: "FS 1 and 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsed-valed/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 55 reviewed courses, kinds {'unresolved': 49, 'course': 4, 'all_of': 2},
activation_allowed false, file SHA256 `3d5913d312d4d3c826bee7124bff52fb8cf20943d6d432f47d337bd1ae05a652`.
Real SWI-Prolog/Janus checks (offline research path): 5/5 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 [Integrating Course in Education] {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)

Affected by Ed 1: VED 21.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
