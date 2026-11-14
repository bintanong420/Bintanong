# BS Business Administration, major in Human Resource Management (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page 1 (`bsba-hrm/page.png`;
page 2 of the PDF holds only a repeated footer). "Bachelor of Science in Business Administration (major
in Human Resource Management), Curriculum Program of Study, Effective SY 2018-2019*", Doc. Ref.
PSU-CIM-CUR-007.3B (*BOR Res. No. 62 s. 2019). Undergraduate: in scope. Printed term totals
23/23/23/20/18/18/15/6 match the listed units; total 146. Printing oddities kept as printed: BAC 8 is
titled "Business Research 1/Thesis 2"; P2106 "Labor Law ang Legislations". All readings fall under the
standing approval: "&" and comma lists all required ("BAC 5 & P2101, P2105"); GE-IER "4th Year
Standing" unknown unless the year is given; "GE PC" -> GE-PC; Practicum "All courses from 1st to 4th
year" kept as printed (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BSBA - HUMAN RESOURCE/BSBA-HRM-for-student-new-version.pdf`,
SHA256 `10d415d041e9b35e6b264789c78b9868ab1059fea1fbfecb290eaf0a9c92ae16`. Scope `palsu-bsba-hrm` / `bsba-hrm-2018-2019`, review `p09-bsba-hrm-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

BAC 5 "E2101 & HBO"; BE 2001 "GE PC"; BAC 3 "BA 2001"; BMEC 1 "E2101"; PATH-Fit 3 "PATH-Fit 1"; P2102 "P2101"; P2103 "P2101"; BAC 7 "E2101"; BMEC 2 "E2101"; GE-IER "4 th Year Standing"; P2106 "BAC 2"; P2107 "BAC 5 & P2101, P2105"; P2108 "BAC 5"; BAC 6 "E2101"; HBO "E2101"; PATH-Fit 2 "PATH-Fit 1"; NSTP 2 "NSTP 1"; P2101 "BAC 5"; BAC 4 "E2101"; PATH-Fit 4 "PATH-Fit 1"; BAC 8 "BAC 7"; TQM "E2101"; P2104 "E2101 & BAC 5"; GE-LWR "GE-PH"; P2105 "P2101"; Practicum "All courses from 1st to 4 th year".

49 courses; 26 printed cells; 23 blank cells stay **unknown**, not "no prerequisite": GE-ET, GE-MMW, E2103, GE-AA, BA 2001, E2101, PATH-Fit 1, NSTP 1, GE-Elect: ES, GE-PH, GE-Elect: EM, BAC 2, IT-HRM, BE 2002, BAC 1, E2104, GE-PC, GE-UTS, GE-STS, GE-CW, E2102, GE-Elect: PES, GE-PS.

## Rules applied

- Year standing -> unknown unless the student states their year: GE-IER: "4 th Year Standing".
- Kept as printed, unknown: Practicum: "All courses from 1st to 4 th year".
- Spacing, case or hyphen variant -> the one matching course: BE 2001: "GE PC" -> GE-PC.
- List -> all required: BAC 5: "E2101 & HBO"; P2107: "BAC 5 & P2101, P2105"; P2104: "E2101 & BAC 5".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsba-hrm/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 49 reviewed courses, kinds {'course': 21, 'unresolved': 25, 'all_of': 3},
activation_allowed false, file SHA256 `9febaedc1d3821fbd6edeafcb821d88d78974e4f9193894f998ba523eb9bd009`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- BAC 5 {'passed': ['E2101', 'HBO']} -> eligible (expected eligible)
- BAC 5 {'passed': ['E2101'], 'failed': ['HBO']} -> ineligible (expected ineligible)
- P2107 {'passed': ['BAC 5', 'P2101', 'P2105']} -> eligible (expected eligible)
- GE-IER {} -> unknown (expected unknown)
- Practicum {} -> unknown (expected unknown)
- BE 2001 {'passed': ['GE-PC']} -> eligible (expected eligible)
- E2101 {} -> unknown (expected unknown)

Affected by E2101: BAC 4, BAC 5, BAC 6, BAC 7, BAC 8, BMEC 1, BMEC 2, HBO, P2101, P2102, P2103, P2104, P2105, P2107, P2108, TQM.
Affected by BAC 5: P2101, P2102, P2103, P2104, P2105, P2107, P2108.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
