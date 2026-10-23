# BS Psychology, major in Industrial Organization (2018-2019) prerequisite review 01

23 October 2026, College of Arts and Humanities. Read from the rendered page (`bspsych-io/page.png`).
"Bachelor of Science in Psychology (major in Industrial Organization), Curriculum Program of Study, Effective SY
2018-2019*" (*BOR Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals 25/22/summer 5/20/22/summer 5/20/20/14/6; total 159
(all match the listed units). Only three printed prerequisite cells: GE-LWR "GE-PH"; Psych 20 and
Psych 21 "All major subjects from first year to fourth year" (kept as printed, unknown; standing
approval). Every other cell is blank (unknown). Page note: italics mark the specialization courses.

Owner decision (23 Oct 2026, duplicate codes): "Psych 13 Psychological Assessment" is printed twice in year 3 sem 2 (5 and 3 units; the printed total 20 counts both). Kept as two courses, told apart by printed units; labels read "Psych 13 (Psychological Assessment, 5 units)" / "(..., 3 units)".

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAH/Psychology/BS-Psychology-Industrial-Track-for-student-new-version.pdf`,
SHA256 `c578a61d89420e4c4d7e00e7e157b124954c5c855bd90ce0f814f119c7477c36`. Scope `palsu-bspsych-io` / `bspsych-io-2018-2019`, review `p09-bspsych-io-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

GE-LWR "GE-PH"; Psych 20 "All major subjects from first year to fourth year"; Psych 21 "All major subjects from first year to fourth year".

49 courses; 3 printed cells; 46 blank cells stay **unknown**, not "no prerequisite": GE - Elect: ES, GE-MMW, GE-AA, GE-ET, Psych 1, Sci 1, PATH-Fit1, NSTP 1, Sci 2, FL 1, GE-PH, GE-Elect: GS, Psych 3, Psych 4, Psych 5, PATH-Fit 3, Sci 3, Psych 9, Psych 10, Psych Elect, GE-IER, Psych 11, Psych 12, Psych 19-IO, Psych 15, Psych Elect 2, Sci 4, GE-UTS, GE-CW, GE-PC, GE-Elect: RRES, Psych 2, PATH-Fit2, NSTP 2, GE-PS, GE-STS, Psych 6, Psych 7, Psych 8, PATH-Fit4, Psych 13, Psych 14, Psych 16-IO, Psych 17-IO, Psych 18, Psych 13.

## Rules applied

- Kept as printed, unknown: Psych 20: "All major subjects from first year to fourth year"; Psych 21: "All major subjects from first year to fourth year".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bspsych-io/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 49 reviewed courses, kinds {'unresolved': 48, 'course': 1},
activation_allowed false, file SHA256 `10df0b56010c7fc9db5d89d79f45c7c0f262dfef0e32d62cb4fb18cb25bb305d`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- GE-LWR {'passed': ['GE-PH']} -> eligible (expected eligible)
- GE-LWR {'failed': ['GE-PH']} -> ineligible (expected ineligible)
- Psych 20 {'passed': ['Psych 1']} -> unknown (expected unknown)
- Psych 21 {} -> unknown (expected unknown)
- Psych 2 {} -> unknown (expected unknown)
- Psych 13 [Psychological Assessment, 5 units] {} -> unknown (expected unknown)
- Psych 13 [Psychological Assessment, 3 units] {} -> unknown (expected unknown)

Affected by GE-PH: GE-LWR.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
