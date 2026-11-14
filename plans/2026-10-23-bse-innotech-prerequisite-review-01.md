# BS Entrepreneurship, Specialized Track 3: Technology and Innovation (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bse-innotech/page.png`).
"Bachelor of Science in Entrepreneurship (Specialized Track 3: Technology and Innovation), Curriculum
Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019). Undergraduate: in scope.
Printed term totals 26/26/26/26/24/21/5/5 match the listed units; total 159.

Owner decision (23 Oct 2026): BAC 4 "BAC 4" and BAC 3 "BAC 3" (self-references) are recorded source
gaps, unknown, refer to the college. The code "CBME" / "C 2" is a line wrap of "CBMEC 2" (joined as
technical transcription). Standing approval otherwise ("&"/"and" lists; "ENTRE 2&3", "ENTRE 5 & 7",
"ENTRE 7, 8 & BAC 3" written out).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BS ENTREP - INNOVATION TECH/BSE-Innovation-and-Tech-for-student-new-version.pdf`,
SHA256 `bb565585a24422c40e32b6da98b8389cc45b8be7f6538d5d4040821fb5d150c3`. Scope `palsu-bse-innotech` / `bse-innotech-2018-2019`, review `p09-bse-innotech-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

BAC 2 "GE-MMW & ENTRE 3"; ENTRE 4 "ENTRE 2&3"; PATH Fit 3 "PATH Fit 1"; ENTRE 7 "ENTRE 3 & BAC 4"; ST 3 "BAC 4 & ST 2"; ENTRE 8 "ENTRE 5"; CBMEC 2 "CBMEC 1"; BAC 4 "BAC 4"; Elective 4 "ENTRE 5"; ENTRE 9 "GE-ET & ENTRE 6"; ENTRE 14 "ENTRE 10"; ENTRE 2 "ENTRE 1"; ENTRE 3 "BAC 1"; NSTP 2 "NSTP 1"; PATH-Fit 2 "PATH Fit 1"; GE-LWR "GE-PH"; ENTRE 5 "ENTRE 4"; BAC 3 "BAC 3"; Elective 2 "ENTRE 4"; ST 2 "ST 1"; ENTRE 6 "BAC 2"; PATH Fit 4 "PATH Fit 1"; GE-IER "BE 1001 and BE 1002"; ENTRE 10 "ENTRE 5 & 7"; ST 4 "ST 3"; ENTRE 11 "Elective 3 & ENTRE 8"; ENTRE 12 "ENTRE 7, 8 & BAC 3"; Elective 5 "Elective 4"; ENTRE 15 "ENTRE 14".

53 courses; 29 printed cells; 24 blank cells stay **unknown**, not "no prerequisite": MKTG 2001, GE-UTS, GE-CW, GE-PC, ENTRE 1, GE-PS, GE-PH, NSTP 1, PATH-Fit 1, GE-STS, BE 1001, Elective 1, ST 1, BAC 1, GE-Elect: GS, Elective 3, GE-Elect: ES, GE-ET, GE-MMW, GE-AA, BE 1002, GE-Elect: IT, CBMEC 1, ENTRE 13.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): ENTRE 4: "3" -> ENTRE 3; ENTRE 10: "7" -> ENTRE 7; ENTRE 12: "8" -> ENTRE 8.
- Source gap (no such course): BAC 4: self-reference "BAC 4"; BAC 3: self-reference "BAC 3".
- Spacing, case or hyphen variant -> the one matching course: PATH Fit 3: "PATH Fit 1" -> PATH-Fit 1; PATH-Fit 2: "PATH Fit 1" -> PATH-Fit 1; PATH Fit 4: "PATH Fit 1" -> PATH-Fit 1.
- List -> all required: BAC 2: "GE-MMW & ENTRE 3"; ENTRE 4: "ENTRE 2&3"; ENTRE 7: "ENTRE 3 & BAC 4"; ST 3: "BAC 4 & ST 2"; ENTRE 9: "GE-ET & ENTRE 6"; GE-IER: "BE 1001 and BE 1002"; ENTRE 10: "ENTRE 5 & 7"; ENTRE 11: "Elective 3 & ENTRE 8"; ENTRE 12: "ENTRE 7, 8 & BAC 3".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bse-innotech/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 53 reviewed courses, kinds {'all_of': 9, 'course': 18, 'unresolved': 26},
activation_allowed false, file SHA256 `c560c934b1e41043835728baccf7259230f30eb66a26cf15a535e10a7b04dc3d`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- BAC 4 {'passed': ['BAC 3']} -> unknown (expected unknown)
- BAC 3 {} -> unknown (expected unknown)
- CBMEC 2 {'passed': ['CBMEC 1']} -> eligible (expected eligible)
- ENTRE 12 {'passed': ['ENTRE 7', 'ENTRE 8', 'BAC 3']} -> eligible (expected eligible)
- ENTRE 3 {'failed': ['BAC 1']} -> ineligible (expected ineligible)
- PATH-Fit 2 {'passed': ['PATH-Fit 1']} -> eligible (expected eligible)
- ENTRE 15 {'passed': ['ENTRE 14']} -> eligible (expected eligible)

Affected by ENTRE 1: ENTRE 10, ENTRE 11, ENTRE 12, ENTRE 14, ENTRE 15, ENTRE 2, ENTRE 4, ENTRE 5, ENTRE 8, Elective 2, Elective 4, Elective 5.
Affected by BAC 1: BAC 2, ENTRE 10, ENTRE 11, ENTRE 12, ENTRE 14, ENTRE 15, ENTRE 3, ENTRE 4, ENTRE 5, ENTRE 6, ENTRE 7, ENTRE 8, ENTRE 9, Elective 2, Elective 4, Elective 5.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
