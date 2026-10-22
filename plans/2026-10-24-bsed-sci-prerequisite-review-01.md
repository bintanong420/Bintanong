# BSEd major in Science (2018-2019) prerequisite review 01

24 October 2026, College of Teacher Education. Read from the rendered page (`bsed-sci/page.png`). "BSEd major in Science, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019 dated 3 July 2019). Undergraduate: in scope.
All readings fall under the owner's standing approval: "&"/"and"/comma lists all required ("FS 1 & 2" = FS 1 + FS 2; "Ed 1 & 4" = Ed 1 + Ed 4); "All Prof. Ed. & Specialization Courses" and "All Gen Ed, Prof. Ed. & Specialization Courses" kept as printed (unknown, refer to the college). Page note: italics mark the specialization courses (not used to expand conditions).
The code "Sci Ed 3 - Science" is kept as printed.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CTE/BSEd-Science-for-student-new-version.pdf`,
SHA256 `fe8fbbebe6a5c6f1dd178ef62b188a034a0162c5aae9e9fbe844be7a9277eb67`. Scope `palsu-bsed-sci` / `bsed-sci-2018-2019`, review `p09-bsed-sci-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

Chem 2/L "Chem 1/L"; PATH-Fit 3 "PATH-Fit 1"; Bio 4/L "Bio 1/L & Chem 3"; Phy 4/L "Phy 3/L"; Phy 5/L "Phy 3/L"; FS 2 "All Prof. Ed. & Specializat ion Courses"; GE-LWR "GE-PH"; PATH-Fit 2 "PATH-Fit 1"; Chem 3 "Chem 2/L"; PATH-Fit 4 "PATH-Fit 1"; Chem 4/L "Chem 1/L"; Sci Ed 3 – Science "Ed 1 & 4"; Ed 10 "Ed 9"; NSTP 2 "NSTP 1"; FS 3 "FS 1 & 2"; Ed 12 "All Gen Ed, Prof. Ed. & Specializat ion Courses".

54 courses; 16 printed cells; 38 blank cells stay **unknown**, not "no prerequisite": Bio 1/L, Sci 1, GE-UTS, GE-PC, GE-PH, Ed 1, Ed 2, PATH-Fit 1, GE-STS, GE-Elect: IT, Bio 2/L, Phy 2/L, Sci 3, GE-Elect 2, Ed 5, Sci Ed 1, Ed 7, Ed 9, NSTP 1, GE-CW, GE-PS, Ed 11, Chem 1/L, Sci 2, GE-ET, GE-MMW, Ed 3, Ed 4, Phy 1, Bio 3/L, Phy 3/L, Sci 4, GE- Elect 3, GE-AA, Ed 6, Sci Ed 2, Ed 8, FS 1.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): Sci Ed 3 – Science: "4" -> Ed 4; FS 3: "2" -> FS 2.
- Kept as printed, unknown: FS 2: "All Prof. Ed. & Specializat ion Courses"; Ed 12: "All Gen Ed, Prof. Ed. & Specializat ion Courses".
- List -> all required: Bio 4/L: "Bio 1/L & Chem 3"; Sci Ed 3 – Science: "Ed 1 & 4"; FS 3: "FS 1 & 2".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsed-sci/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 54 reviewed courses, kinds {'unresolved': 40, 'course': 11, 'all_of': 3},
activation_allowed false, file SHA256 `d5f37778a0bd1fe6a0a191642eb7a6687a2cbdf4c0e7585a57dff763454f0831`.
Real SWI-Prolog/Janus checks (offline research path): 5/5 as the readings imply:

- FS 3 {'passed': ['FS 1', 'FS 2']} -> eligible (expected eligible)
- FS 3 {'passed': ['FS 1'], 'failed': ['FS 2']} -> ineligible (expected ineligible)
- Ed 12 {} -> unknown (expected unknown)
- Ed 10 {'passed': ['Ed 9']} -> eligible (expected eligible)
- FS 2 {} -> unknown (expected unknown)

Affected by Ed 1: Sci Ed 3 – Science.
Affected by Ed 9: Ed 10.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
