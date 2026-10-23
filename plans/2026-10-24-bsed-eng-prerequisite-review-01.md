# BSEd major in English (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`bsed-eng/page.png`). "BSEd major in English, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).
EL 18 "EL 4 TTL 2 (co-requisite)": EL 4 required; "TTL 2" is not a printed course code (EL 21 is titled "Technology for Teaching and Learning 2"; a title is not a code), so that co-requisite is a recorded source gap (unknown). "EL 5, 8, 10, 11, 12, 13" written out with the EL prefix. A stray "N E" inside the FS 2 cell is not used.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BSEd-Eng-for-student-new-version.pdf`,
SHA256 `8f5a6d3e2a8fd8d42288bd5a1d1c1e46f713a899752c568553ae29244b797daf`. Scope `palsu-bsed-eng` / `bsed-eng-2018-2019`, review `p09-bsed-eng-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

EL 5 "EL 2"; EL 6 "EL 3"; EL 7 "EL 4"; EL 8 "EL 4"; EL 9 "EL 3"; PATH Fit 3 "PATH Fit 1"; EL 15 "EL 5, 8, 10, 11, 12, 13"; EL 16 "EL 4"; EL 17 "EL 3"; FS 2 "All Prof. Ed. & Specializ ation Courses"; EL 3 "EL 1"; EL 4 "EL 2"; GE-LWR "GE-PH"; PATH Fit 2 "PATH Fit 1"; EL 10 "EL 8"; EL 11 "EL 8"; EL 12 "EL 8"; EL 13 "EL 8"; EL 14 "EL 9"; PATH Fit 4 "PATH Fit 1"; EL 18 "EL 4 TTL 2 (co-requisite)"; EL 19 "EL 15"; EL 20 "EL 2"; EL 21 "Ed 1 & 4"; Ed 10 "Ed 9"; NSTP 2 "NSTP 1"; FS 3 "FS 1 and 2"; Ed 12 "All Gen Ed, Prof. Ed. & Specializ ation Courses".

57 courses; 28 printed cells; 29 blank cells stay **unknown**, not "no prerequisite": EL 1, EL 2, GE-UTS, GE-PC, GE-PH, Ed 1, Ed 2, PATH Fit 1, GE-STS, GE-Elect: PPC, Ed 5, EL-Elect 1, EL-Elect 2, Ed 7, Ed 9, NSTP 1, GE-CW, GE-PS, Ed 11, GE-ET, GE-MMW, Ed 3, Ed 4, GE-Elect: ES, GE-AA, GE-Elect: EM, Ed 6, Ed 8, FS 1.

Native text clipped out of the printed page (recorded, not used; owner 23 Oct 2026):

- FS 2: native cell "All Prof. Ed. & Specializ ation Courses N E"; hidden 'N E'

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): EL 15: "8" -> EL 8; EL 15: "10" -> EL 10; EL 15: "11" -> EL 11; EL 15: "12" -> EL 12; EL 15: "13" -> EL 13; EL 18: "EL 4 TTL 2 (co-requisite)" -> EL 4, TTL 2; EL 21: "4" -> Ed 4; FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 2: "All Prof. Ed. & Specializ ation Courses"; Ed 12: "All Gen Ed, Prof. Ed. & Specializ ation Courses".
- Source gap (no such course): EL 18: "TTL 2".
- List -> all required: EL 15: "EL 5, 8, 10, 11, 12, 13"; EL 18: "EL 4 TTL 2 (co-requisite)"; EL 21: "Ed 1 & 4"; FS 3: "FS 1 and 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsed-eng/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 57 reviewed courses, kinds {'unresolved': 31, 'all_of': 4, 'course': 22},
activation_allowed false, file SHA256 `fff5964740cd045c59d68de02d9893c6bc2ca265962e1f099ee4ca0f2df19905`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)
- EL 18 {'passed': ['EL 4']} -> unknown (expected unknown)
- EL 18 {'failed': ['EL 4']} -> ineligible (expected ineligible)

Affected by Ed 1: EL 21.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
