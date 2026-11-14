# BSEd major in Filipino (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`bsed-fil/page.png`). "BSEd major in Filipino, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BSEd-Fil-for-student-new-version.pdf`,
SHA256 `2557cf531dc64d4eecbfafb197aecc12331fb2c90f152e48b71cd504f7d53fb1`. Scope `palsu-bsed-fil` / `bsed-fil-2018-2019`, review `p09-bsed-fil-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

PATH-Fit 3 "PATH-Fit 1"; Fil 13 "Fil 12"; FS 2 "All Prof. Ed. & Specializ ation Courses"; Fil 3 "Fil 1"; GE-LWR "GE-PH"; PATH-Fit 2 "PATH-Fit 1"; PATH-Fit 4 "PATH-Fit 1"; Fil 20 "Ed 1 & 4"; Ed 10 "Ed 9"; NSTP 2 "NSTP 1"; FS 3 "FS 1 & 2"; Ed 12 "All Gen Ed, Prof. Ed. & Specializ ation Courses".

56 courses; 12 printed cells; 44 blank cells stay **unknown**, not "no prerequisite": Fil 1, Fil 2, GE-UTS, GE-PC:, GE-PH, Ed 1, Ed 2, PATH-Fit 1, GE-STS, Fil 5, Fil 6, Fil 7, Fil 8, Fil 9, GE-Elect: PPC, Ed 5, Fil 14, Fil 15, Fil 16, Fil 17, Ed 7, Ed 9, NSTP 1, GE-CW, GE-PS, Ed 11, Fil 4, GE-ET, GE-MMW, Ed 3, Ed 4, GE-Elect: ES, Fil 10, Fil 11, Fil 12, Fil Elektib 1, GE-AA:, GE-Elect: EM, Ed 6, Fil Elektib 2, Fil 18, Fil 19, Ed 8, FS 1.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): Fil 20: "4" -> Ed 4; FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 2: "All Prof. Ed. & Specializ ation Courses"; Ed 12: "All Gen Ed, Prof. Ed. & Specializ ation Courses".
- List -> all required: Fil 20: "Ed 1 & 4"; FS 3: "FS 1 & 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsed-fil/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 56 reviewed courses, kinds {'unresolved': 46, 'course': 8, 'all_of': 2},
activation_allowed false, file SHA256 `f62ebb39e7bc868e304786fa17d277761bdb65172dbace94f906d2fc1c9b1e48`.
Real SWI-Prolog/Janus checks (offline research path): 5/5 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)

Affected by Ed 1: Fil 20.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
