# BS Business Administration, major in Business Economics (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bsba-buseco/page.png`).
"Bachelor of Science in Business Administration (Major in Business Economics), Curriculum Program of
Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals
20/23/23/23/18/18/15/6 (total 146); the listed units match every term except year 2 sem 1, where
PATH Fit 3 prints 3 units (sum 24 vs printed 23; listed units total 147) - printing defect, recorded.

Owner decision (23 Oct 2026): GE-Elect: ES and BAC 5 print "None" - an explicit no-prerequisite
statement (eligible with no prerequisite). Standing approval otherwise: "BAC 1&2, E2401" = BAC 1, BAC 2,
E2401; "PATH FIT-1" -> PATH Fit 1 (case/hyphen variant); "GE PC" -> GE-PC; "Practicu" / "m" is a
line wrap of "Practicum"; its "All courses from 1st to 4th year" kept as printed (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BSBA - BUSINESS ECONOMICS/BSBA-Buss-Eco-for-student-new-version.pdf`,
SHA256 `4cb398d04a599e3c2203b49ef3861e3807ef1a9eafc78db56a065cc52ce231d8`. Scope `palsu-bsba-buseco` / `bsba-buseco-2018-2019`, review `p09-bsba-buseco-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

P2402 "BAC 1 & P2401"; GE-Elect: ES "None"; PATH Fit 3 "PATH FIT-1"; E2402 "BAC 1, P2404"; BAC 5 "None"; BAC 7 "BAC 1&2, E2401"; P2405 "P2403, P2404"; P2406 "BAC 1, P2401"; P2407 "BAC 1, P2401"; P2409 "P2403, P2404"; P2410 "BAC 1, P2401"; E2403 "BAC 1, P2401"; E2404 "P2403, P2404"; E2405 "BAC 1, P2401"; PATH Fit 2 "PATH Fit 1"; NSTP 2 "NSTP 1"; GE-LWR "GE-PH"; BE 2001 "GE PC"; BAC 3 "BA 2001"; P2403 "BAC 1, P2401"; P2404 "BAC 1, P2401"; PATH Fit 4 "PATH Fit 1"; P2408 "BAC 1, P2401"; BAC 6 "P2403, P2404"; BAC 8 "BAC 7"; Practicum "All courses from 1st to 4th year".

49 courses; 26 printed cells; 23 blank cells stay **unknown**, not "no prerequisite": GE-Elect: EM, GE-UTS, GE-CW, GE-PC, BAC 1, PATH Fit 1, NSTP 1, GE-PH, GE-STS, GE-PS, E2401, Bac 4, BE 2002, GE-ET, GE-MMW, GE-AA, BA 2001, P2401, BAC 2, GE-Elect: PES, BMEC 1, BMEC 2, GE-IER.

## Rules applied

- Printed "None" -> explicit no prerequisite (owner, 23 Oct 2026): GE-Elect: ES: "None"; BAC 5: "None".
- Shorthand or range written out, all required (owner, 23 Oct 2026): BAC 7: "2" -> BAC 2.
- Kept as printed, unknown: Practicum: "All courses from 1st to 4th year".
- Spacing, case or hyphen variant -> the one matching course: PATH Fit 3: "PATH FIT-1" -> PATH Fit 1; BE 2001: "GE PC" -> GE-PC.
- List -> all required: P2402: "BAC 1 & P2401"; E2402: "BAC 1, P2404"; BAC 7: "BAC 1&2, E2401"; P2405: "P2403, P2404"; P2406: "BAC 1, P2401"; P2407: "BAC 1, P2401"; P2409: "P2403, P2404"; P2410: "BAC 1, P2401"; E2403: "BAC 1, P2401"; E2404: "P2403, P2404"; E2405: "BAC 1, P2401"; P2403: "BAC 1, P2401"; P2404: "BAC 1, P2401"; P2408: "BAC 1, P2401"; BAC 6: "P2403, P2404".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsba-buseco/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 49 reviewed courses, kinds {'unresolved': 24, 'all_of': 15, 'course': 8, 'verified_none': 2},
activation_allowed false, file SHA256 `e2c103a5106ff89035aa887c17f3208515a636ce2f66a73053caa505cf2d8aa8`.
Real SWI-Prolog/Janus checks (offline research path): 8/8 as the readings imply:

- GE-Elect: ES {} -> eligible (expected eligible)
- BAC 5 {} -> eligible (expected eligible)
- BAC 7 {'passed': ['BAC 1', 'BAC 2', 'E2401']} -> eligible (expected eligible)
- BAC 7 {'passed': ['BAC 1', 'E2401'], 'failed': ['BAC 2']} -> ineligible (expected ineligible)
- PATH Fit 3 {'passed': ['PATH Fit 1']} -> eligible (expected eligible)
- P2405 {'passed': ['P2403', 'P2404']} -> eligible (expected eligible)
- Practicum {} -> unknown (expected unknown)
- BE 2001 {'passed': ['GE-PC']} -> eligible (expected eligible)

Affected by BAC 1: BAC 6, BAC 7, BAC 8, E2402, E2403, E2404, E2405, P2402, P2403, P2404, P2405, P2406, P2407, P2408, P2409, P2410.
Affected by P2401: BAC 6, E2402, E2403, E2404, E2405, P2402, P2403, P2404, P2405, P2406, P2407, P2408, P2409, P2410.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
