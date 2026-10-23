# AB Political Science (2018-2019) prerequisite review 01

23 October 2026, College of Arts and Humanities. Read from the rendered page (`abpolsci/page.png`).
"Bachelor of Arts in Political Science, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR
Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals 20/20/20/20/18/15/9/9 match the
listed units; total 131 matches.

Owner decisions (23 Oct 2026): (1) shorthand written out with the shared prefix: "PSM 1,2" = PSM 1 +
PSM 2 (PSM 3-7); "PSM 1,2,5" = PSM 1 + PSM 2 + PSM 5 (PSM 8); "PSM 1,2,5,8 PSIE 6" = PSM 1, PSM 2,
PSM 5, PSM 8 + PSIE 6 (PSM 9, PSM 10). (2) The printed code "PSIE 5" appears on two rows with
different titles - "Geopolitics" (year 3 sem 2) and "Public Fiscal Administration" (year 4 sem 2) -
kept as two courses with their printed title and units recorded; a code-only question matches both
and Bintanong asks which is meant. Both have blank prerequisite cells (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAH/PolSci/PolSci-for-student-new-version.pdf`,
SHA256 `52b5fcd19173e68f8cec96bd157021be39a0ac3f71f8e076e231b2a204acf6cc`. Scope `palsu-abpolsci` / `abpolsci-2018-2019`, review `p09-abpolsci-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

PSM 3 "PSM 1,2"; PSM 4 "PSM 1,2"; PATH Fit 3 "PATH Fit 1"; PSM 7 "PSM 1,2"; PSM 6 "PSM 1,2"; PSIE 3 "PSM 5"; PSM 9 "PSM 1,2,5,8 PSIE 6"; GE-LWR "GE-PH"; PSM 2 "PSM 1"; FL 2 "FL 1"; NSTP 2 "NSTP 1"; PATH Fit 2 "PATH Fit 1"; PSE 2 "PSM 4"; PSM 5 "PSM 1,2"; PATH Fit 4 "PATH Fit 1"; PSM 8 "PSM 1,2,5"; PSM 10 "PSM 1,2,5,8 PSIE 6"; PSIE 7 "PSE 6".

45 courses; 18 printed cells; 27 blank cells stay **unknown**, not "no prerequisite": GE-MMW, GE-AA, GE-PH, PSM 1, FL 1, NSTP 1, PATH Fit 1, GE-ET, GE-Elect: ES, PSIE 1, PSE 1, PSIE 6, PSIE 4, GE-Elect: PPC, PSE 6, GE-IER, GE-PC, GE-UTS, GE-CW, GE-STS, GE-PS, PSIE 2, PSE 4, PSIE 5, PSE 3, GE-Elect: GS, PSIE 5.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): PSM 3: "PSM 1,2" -> PSM 1, PSM 2; PSM 4: "PSM 1,2" -> PSM 1, PSM 2; PSM 7: "PSM 1,2" -> PSM 1, PSM 2; PSM 6: "PSM 1,2" -> PSM 1, PSM 2; PSM 9: "PSM 1,2,5,8 PSIE 6" -> PSM 1, PSM 2, PSM 5, PSM 8, PSIE 6; PSM 5: "PSM 1,2" -> PSM 1, PSM 2; PSM 8: "PSM 1,2,5" -> PSM 1, PSM 2, PSM 5; PSM 10: "PSM 1,2,5,8 PSIE 6" -> PSM 1, PSM 2, PSM 5, PSM 8, PSIE 6.
- List -> all required: PSM 3: "PSM 1,2"; PSM 4: "PSM 1,2"; PSM 7: "PSM 1,2"; PSM 6: "PSM 1,2"; PSM 9: "PSM 1,2,5,8 PSIE 6"; PSM 5: "PSM 1,2"; PSM 8: "PSM 1,2,5"; PSM 10: "PSM 1,2,5,8 PSIE 6".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `abpolsci/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 45 reviewed courses, kinds {'unresolved': 27, 'course': 10, 'all_of': 8},
activation_allowed false, file SHA256 `95c80aa8049ff1920257607a586c0152a602a790adbfcc450859a8ed9beca537`.
Real SWI-Prolog/Janus checks (offline research path): 10/10 as the readings imply:

- PSM 2 {'passed': ['PSM 1']} -> eligible (expected eligible)
- PSM 3 {'passed': ['PSM 1', 'PSM 2']} -> eligible (expected eligible)
- PSM 3 {'passed': ['PSM 1'], 'failed': ['PSM 2']} -> ineligible (expected ineligible)
- PSM 10 {'passed': ['PSM 1', 'PSM 2', 'PSM 5', 'PSM 8', 'PSIE 6']} -> eligible (expected eligible)
- PSM 10 {'passed': ['PSM 1', 'PSM 2', 'PSM 5']} -> unknown (expected unknown)
- PSIE 7 {'passed': ['PSE 6']} -> eligible (expected eligible)
- PSE 2 {'failed': ['PSM 4']} -> ineligible (expected ineligible)
- GE-LWR {'passed': ['GE-PH']} -> eligible (expected eligible)
- PSIE 5 [Geopolitics] {} -> unknown (expected unknown)
- PSIE 5 [Public Fiscal Administration] {} -> unknown (expected unknown)

Affected by PSM 1: PSE 2, PSIE 3, PSM 10, PSM 2, PSM 3, PSM 4, PSM 5, PSM 6, PSM 7, PSM 8, PSM 9.
Affected by PSM 5: PSIE 3, PSM 10, PSM 8, PSM 9.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal; ledger `df935d0bf40e`). The chatbot catalog keeps both PSIE 5 rows (`8f024d7`).
