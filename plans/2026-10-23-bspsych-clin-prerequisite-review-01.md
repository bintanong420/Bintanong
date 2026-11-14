# BS Psychology, major in Clinical Psychology (2018-2019) prerequisite review 01

23 October 2026, College of Arts and Humanities. Read from the rendered page (`bspsych-clin/page.png`).
"Bachelor of Science in Psychology (major in Clinical Psychology), Curriculum Program of Study, Effective SY
2018-2019*" (*BOR Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals 25/22/summer 5/20/22/summer 5/20/17/14/6; total 156
(all match the listed units). Only three printed prerequisite cells: GE-LWR "GE-PH"; Psych 20 and
Psych 21 "All major subjects from first year to fourth year" (kept as printed, unknown; standing
approval). Every other cell is blank (unknown). Page note: italics mark the specialization courses.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAH/Psychology/BS-Psychology-Clinical-Psych-for-student-new-version.pdf`,
SHA256 `96cffef73d79160aa02442e9ec88d121836a4575cefa21dd6c2d11a40e52cd28`. Scope `palsu-bspsych-clin` / `bspsych-clin-2018-2019`, review `p09-bspsych-clin-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

GE-LWR "GE-PH"; Psych 20 "All major subjects from first year to fourth year"; Psych 21 "All major subjects from first year to fourth year".

48 courses; 3 printed cells; 45 blank cells stay **unknown**, not "no prerequisite": GE-Elect: ES, GE-MMW, GE-AA, GE-ET, Psych 1, Sci 1, PATH-Fit1, NSTP 1, Sci 2, FL 1, GE-PH, GE-Elect: GS, Psych 3, Psych 4, Psych 5, PATH-Fit 3, Sci 3, Psych 9, Psych 10, Psych Elect, GE-IER, Psych 11, Psych 12, Psych 19-CP, Psych 15, Psych Elect 2, Sci 4, GE-UTS, GE-CW, GE-PC, GE-Elect: RRES, Psych 2, PATH-Fit2, NSTP 2, GE-PS, GE-STS, Psych 6, Psych 7, Psych 8, PATH-Fit4, Psych 13, Psych 14, Psych 16- CP, Psych 17- CP, Psych 18.

## Rules applied

- Kept as printed, unknown: Psych 20: "All major subjects from first year to fourth year"; Psych 21: "All major subjects from first year to fourth year".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bspsych-clin/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 48 reviewed courses, kinds {'unresolved': 47, 'course': 1},
activation_allowed false, file SHA256 `1d054287c49ce725795ab8de51a270abdb1f6c4c29f2e4bc679c39220a67668c`.
Real SWI-Prolog/Janus checks (offline research path): 5/5 as the readings imply:

- GE-LWR {'passed': ['GE-PH']} -> eligible (expected eligible)
- GE-LWR {'failed': ['GE-PH']} -> ineligible (expected ineligible)
- Psych 20 {'passed': ['Psych 1']} -> unknown (expected unknown)
- Psych 21 {} -> unknown (expected unknown)
- Psych 2 {} -> unknown (expected unknown)

Affected by GE-PH: GE-LWR.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
