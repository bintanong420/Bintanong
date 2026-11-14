# BS Business Administration, major in Marketing Management (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bsba-mm/page.png`).
"Bachelor of Science in Business Administration (major in Marketing Management), Curriculum Program of
Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019). Undergraduate: in scope. Printed term
totals 23/26/26/23/18/18/15/6 match the listed units; total 155. Label quirk: the semester headings
print "FIRST YEAR" / "SECOND YEAR" in place of first / second semester (layout unaffected).
All readings fall under the standing approval: "&" and comma lists all required ("P2201 & Mktg 2001,
BA 2002", "P2201& Mktg 2001"); "Mktg 2001" -> MKTG 2001 (case variant); "PATH- Fit 1" -> PATH-Fit 1;
"GE PC" -> GE-PC; "Practicu" / "m" is a line wrap of "Practicum", its "All courses from 1st to 4th
year" kept as printed (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BSBA - MARKETING MANAGEMENT/BSBA-MM-for-student-new-version.pdf`,
SHA256 `af3fd35dfbfccafac3ea07c5d4aae26596bb2d8099c08d4816943c803feddac0`. Scope `palsu-bsba-mm` / `bsba-mm-2018-2019`, review `p09-bsba-mm-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

BE 2001 "GE PC"; P2202 "P2201 & Mktg 2001"; PATH-Fit 3 "PATH-Fit 1"; BAC 8 "BAC 7 & P2201"; P2204 "P2201 & Mktg 2001"; TQM "BAC 5"; P2205 "P2201 & Mktg 2001"; E2205 "BAC 6"; P2210 "P2201& Mktg 2001"; P2201 "Mktg 2001"; BA 2002 "BA 2001"; PATH-Fit 2 "PATH-Fit 1"; NSTP 2 "NSTP 1"; GE-LWR "GE-PH"; P2203 "P2201 & Mktg 2001"; PATH-Fit 4 "PATH- Fit 1"; P2206 "P2201 & Mktg 2001, BA 2002"; BAC 2 "BA 2002"; P2207 "P2201 & Mktg 2001"; P2209 "P2201 & Mktg 2001"; P2208 "P2201, Mktg 2001, BAC 7, BAC 8"; Practicum "All courses from 1st to 4 th year".

52 courses; 22 printed cells; 30 blank cells stay **unknown**, not "no prerequisite": GE-Elect: ES, GE-MMW, MKTG 2001, BAC 1, BA 2001, GE-PH, PATH-Fit 1, NSTP 1, GE-Elect: EM, BMEC 1, E2202, GE-AA, GE-ET, BAC 5, E2203, BAC 3, BMEC 2, E2204, GE-IER, BE 2002, GE-UTS, GE-CW, E2201, GE-PS, GE-Elect: PES, BAC 4, GE-PC, GE-STS, BAC 7, BAC 6.

## Rules applied

- Kept as printed, unknown: Practicum: "All courses from 1st to 4 th year".
- Spacing, case or hyphen variant -> the one matching course: BE 2001: "GE PC" -> GE-PC; P2202: "Mktg 2001" -> MKTG 2001; P2204: "Mktg 2001" -> MKTG 2001; P2205: "Mktg 2001" -> MKTG 2001; P2210: "Mktg 2001" -> MKTG 2001; P2201: "Mktg 2001" -> MKTG 2001; P2203: "Mktg 2001" -> MKTG 2001; PATH-Fit 4: "PATH- Fit 1" -> PATH-Fit 1; P2206: "Mktg 2001" -> MKTG 2001; P2207: "Mktg 2001" -> MKTG 2001; P2209: "Mktg 2001" -> MKTG 2001; P2208: "Mktg 2001" -> MKTG 2001.
- List -> all required: P2202: "P2201 & Mktg 2001"; BAC 8: "BAC 7 & P2201"; P2204: "P2201 & Mktg 2001"; P2205: "P2201 & Mktg 2001"; P2210: "P2201& Mktg 2001"; P2203: "P2201 & Mktg 2001"; P2206: "P2201 & Mktg 2001, BA 2002"; P2207: "P2201 & Mktg 2001"; P2209: "P2201 & Mktg 2001"; P2208: "P2201, Mktg 2001, BAC 7, BAC 8".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsba-mm/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 52 reviewed courses, kinds {'unresolved': 31, 'course': 11, 'all_of': 10},
activation_allowed false, file SHA256 `695cb6f203cb56f07eada851686508f5d211ca7317e48918d040963af4323c95`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- P2201 {'passed': ['MKTG 2001']} -> eligible (expected eligible)
- P2206 {'passed': ['P2201', 'MKTG 2001', 'BA 2002']} -> eligible (expected eligible)
- P2206 {'passed': ['P2201', 'MKTG 2001'], 'failed': ['BA 2002']} -> ineligible (expected ineligible)
- P2208 {'passed': ['P2201', 'MKTG 2001', 'BAC 7', 'BAC 8']} -> eligible (expected eligible)
- PATH-Fit 4 {'passed': ['PATH-Fit 1']} -> eligible (expected eligible)
- Practicum {} -> unknown (expected unknown)
- E2203 {} -> unknown (expected unknown)

Affected by MKTG 2001: BAC 8, P2201, P2202, P2203, P2204, P2205, P2206, P2207, P2208, P2209, P2210.
Affected by P2201: BAC 8, P2202, P2203, P2204, P2205, P2206, P2207, P2208, P2209, P2210.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
