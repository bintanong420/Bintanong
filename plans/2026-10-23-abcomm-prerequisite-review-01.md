# AB Communication (2018-2019) prerequisite review 01

23 October 2026, College of Arts and Humanities. Read from the rendered page (`abcomm/page.png`).
"Bachelor of Arts in Communication, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res.
No. 62 s. 2019). Undergraduate: in scope. Printed term totals 20/20/20/23/21/18/23/3 (total 148);
the listed units match every term except year 4 sem 1, whose seven 3-unit courses sum to 21 while 23
is printed (printing defect, recorded; listed courses total 146).

Owner decision (23 Oct 2026), shown inline: shorthand cells are written out by repeating the shared
prefix, "&" meaning all required ("COMM BC 12 & 14" = COMM BC 12 + COMM BC 14; "COMM BC 12, SSH 15 &
RE 14" = COMM BC 12 + COMM SSH 15 + COMM RE 14; "GE-ES" = GE-Elect: ES). Standing approval otherwise:
"CCOMM BC 15" -> COMM BC 15 (typo); "FL1", "GE- PH" spacing; COMM 100's "All courses" kept as printed.
Page note: italics mark the specialization courses (not used to expand any condition).

Finding: the affected-course listing for COMM BC 11 returns runtime error `runtime_result_limit`
(nearly every major depends on it and the answer, with full source spans per course, exceeds the
runtime's 64 KB result cap). Safe (an error, never a wrong list) but unhelpful; a separate engine
fix is proposed to the owner.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAH/Communication/ABComm-for-student-new-version.pdf`,
SHA256 `998a83c0c0a64dbe90552e6212a73e017ea5d4d08def617589ca51ffc07fc14f`. Scope `palsu-abcomm` / `abcomm-2018-2019`, review `p09-abcomm-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

COMM BC 12 "COMM BC 11"; COMM BC 13 "COMM BC 11"; PATH Fit 3 "PATH Fit 1"; COMM BC 15 "COMM BC 12"; COMM CRC 13 "COMM BC 12"; COMM CRC 14 "COMM BC 14"; COMM SSH 12 "COMM BC 14"; COMM SSH 13 "GE-ES, COMM CRC 11, & BC 14"; COMM RE 11 "COMM BC 14"; COMM RE 12 "COMM BC 12 & 14"; COMM CRC 16 "COMM BC 14"; COMM BC 16 "COMM BC 12"; COMM BC 17 "COMM BC 12"; COMM RE 15 "COMM BC 12, SSH 15 & RE 14"; COMM SSH 16 "COMM BC 12, SSH 15 & RE 14"; COMM 50/B "COMM 50/A"; GE-IER "ENG 10"; FL 2 "FL1"; PATH Fit 2 "PATH Fit 1"; NSTP 2 "NSTP 1"; GE-LWR "GE- PH"; COMM BC 14 "COMM BC 13"; COMM CRC 11 "COMM BC 12"; COMM CRC 12 "COMM BC 12"; COMM SSH 11 "COMM BC 11"; PATH Fit 4 "PATH Fit 1"; COMM SSH 14 "COMM BC 14 & CRC 12"; COMM SSH 15 "COMM BC 14 & CRC 12"; COMM RE 13 "COMM RE 11 & SSH 12"; COMM RE 14 "COMM BC 14"; COMM CRC15 "COMM RE 11 & BC 13"; COMM 50/A "CCOMM BC 15"; COMM 100 "All courses".

50 courses; 33 printed cells; 17 blank cells stay **unknown**, not "no prerequisite": FL 1, GE-UTS, GE-CW, GE-PC, PATH Fit 1, NSTP 1, ENG 10, GE-STS, GE-PH, GE-Elect: PPC, GE - PS, GE-Elect: ES, GE-MMW, COMM BC 11, GE-AA, GE-ET, GE-Elect: EM.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): COMM SSH 13: "GE-ES, COMM CRC 11, & BC 14" -> GE-Elect: ES, COMM CRC 11, COMM BC 14; COMM RE 12: "COMM BC 12 & 14" -> COMM BC 12, COMM BC 14; COMM RE 15: "COMM BC 12, SSH 15 & RE 14" -> COMM BC 12, COMM SSH 15, COMM RE 14; COMM SSH 16: "COMM BC 12, SSH 15 & RE 14" -> COMM BC 12, COMM SSH 15, COMM RE 14; COMM SSH 14: "COMM BC 14 & CRC 12" -> COMM BC 14, COMM CRC 12; COMM SSH 15: "COMM BC 14 & CRC 12" -> COMM BC 14, COMM CRC 12; COMM RE 13: "COMM RE 11 & SSH 12" -> COMM RE 11, COMM SSH 12; COMM CRC15: "COMM RE 11 & BC 13" -> COMM RE 11, COMM BC 13.
- Kept as printed, unknown: COMM 100: "All courses".
- Shortened/variant code -> the one matching course: COMM 50/A: "CCOMM BC 15" -> COMM BC 15.
- Spacing/case-only difference -> the one matching course: FL 2: "FL1" -> FL 1; GE-LWR: "GE- PH" -> GE-PH.
- List -> all required: COMM SSH 13: "GE-ES, COMM CRC 11, & BC 14"; COMM RE 12: "COMM BC 12 & 14"; COMM RE 15: "COMM BC 12, SSH 15 & RE 14"; COMM SSH 16: "COMM BC 12, SSH 15 & RE 14"; COMM SSH 14: "COMM BC 14 & CRC 12"; COMM SSH 15: "COMM BC 14 & CRC 12"; COMM RE 13: "COMM RE 11 & SSH 12"; COMM CRC15: "COMM RE 11 & BC 13".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `abcomm/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 50 reviewed courses, kinds {'course': 24, 'all_of': 8, 'unresolved': 18},
activation_allowed false, file SHA256 `041c0e514d5520f40e28c61e7d18513ac68ba0a1df6c591490e095d1c2f0000e`.
Real SWI-Prolog/Janus checks (offline research path): 10/10 as the readings imply:

- COMM BC 12 {'passed': ['COMM BC 11']} -> eligible (expected eligible)
- COMM RE 12 {'passed': ['COMM BC 12', 'COMM BC 14']} -> eligible (expected eligible)
- COMM RE 12 {'passed': ['COMM BC 12'], 'failed': ['COMM BC 14']} -> ineligible (expected ineligible)
- COMM RE 15 {'passed': ['COMM BC 12', 'COMM SSH 15', 'COMM RE 14']} -> eligible (expected eligible)
- COMM SSH 13 {'passed': ['GE-Elect: ES', 'COMM CRC 11', 'COMM BC 14']} -> eligible (expected eligible)
- COMM 50/A {'passed': ['COMM BC 15']} -> eligible (expected eligible)
- GE-IER {'passed': ['ENG 10']} -> eligible (expected eligible)
- FL 2 {'passed': ['FL 1']} -> eligible (expected eligible)
- COMM 100 {} -> unknown (expected unknown)
- COMM BC 11 {} -> unknown (expected unknown)

Affected by COMM BC 11: ERROR runtime_result_limit.
Affected by COMM BC 14: COMM CRC 14, COMM CRC 16, COMM CRC15, COMM RE 11, COMM RE 12, COMM RE 13, COMM RE 14, COMM RE 15, COMM SSH 12, COMM SSH 13, COMM SSH 14, COMM SSH 15, COMM SSH 16.

Not yet loaded into Supabase or wired into the runtime release.
