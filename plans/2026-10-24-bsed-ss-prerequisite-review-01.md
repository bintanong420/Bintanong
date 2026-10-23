# BSEd major in Social Studies (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`bsed-ss/page.png`). "BSEd major in Social Studies, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).
NSTP/LTS 2 "NSTP 1" -> NSTP/LTS 1 (shortened code, single match). SSE 18 has a blank units cell (no unit fact). The code "SSE 21 TTL 2 -" is kept as printed.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BSEd-social-studies-for-student-new-version.pdf`,
SHA256 `0be60b0bdd11c7aa73f6249b667dfe13a5e373520201bd656545505618fba5ae`. Scope `palsu-bsed-ss` / `bsed-ss-2018-2019`, review `p09-bsed-ss-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

PATH-Fit 3 "PATH-Fit 1"; FS 2 "All Prof. Ed. & Specializat ion Courses"; GE-LWR "GE-PH"; PATH-Fit 2 "PATH-Fit 1"; SSE 21 TTL 2 – "Ed 1 & 4"; Ed 10 "Ed 9"; NSTP/LTS 2 "NSTP 1"; FS 3 "FS 1 and 2"; Ed 12 "All Gen. Ed., Prof. Ed. & Specializat ion Courses".

57 courses; 9 printed cells; 48 blank cells stay **unknown**, not "no prerequisite": SSE 1, SSE 2, GE-UTS, GE-PC, GE-PH, Ed 1, Ed 2, PATH-Fit 1, GE-STS, SSE 5, SSE 6, SSE 7, SSE 8, SSE Elect 1, GE-Elect 2, Ed 5, SSE 13, SSE 14, SSE 15, SSE 16, SSE 17, Ed 7, Ed 9, NSTP/LTS 1, GE-CW, GE-PS, Ed 11, SSE 3, SSE 4, GE-ET, GE-MMW, Ed 3, Ed 4, GE-ES: Elect 1, SSE 9, SSE 10, SSE 11, SSE 12, SSE Elect 2, GE-Elect 3, GE-AA, Ed 6, PATH-Fit 4, SSE 18, SSE 19, SSE 20, Ed 8, FS 1.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): SSE 21 TTL 2 –: "4" -> Ed 4; FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 2: "All Prof. Ed. & Specializat ion Courses"; Ed 12: "All Gen. Ed., Prof. Ed. & Specializat ion Courses".
- Shortened/variant code -> the one matching course: NSTP/LTS 2: "NSTP 1" -> NSTP/LTS 1.
- List -> all required: SSE 21 TTL 2 –: "Ed 1 & 4"; FS 3: "FS 1 and 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsed-ss/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 57 reviewed courses, kinds {'unresolved': 50, 'course': 5, 'all_of': 2},
activation_allowed false, file SHA256 `98bcd0131e4233449981007b689cb967c086aa0e60a955b92b6da9936b1b94fc`.
Real SWI-Prolog/Janus checks (offline research path): 6/6 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)
- NSTP/LTS 2 {'passed': ['NSTP/LTS 1']} -> eligible (expected eligible)

Affected by Ed 1: SSE 21 TTL 2 –.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
