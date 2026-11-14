# BS Entrepreneurship, Specialized Track 2: Agribusiness (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bse-agri/page.png`).
"Bachelor of Science in Entrepreneurship (Specialized Track 2: Agribusiness), Curriculum Program of
Study, Effective SY 2018-2019*", Doc. Ref. PSU-CIM-CUR-008.2B (*BOR Res. No. 62 s. 2019).
Undergraduate: in scope. Printed term totals 26/26/26/26/24/21/5/5 match the listed units; total 159.

Owner decision (23 Oct 2026): BAC 4 "Cost and Management Accounting" prints "BAC 4" and BAC 3
"Accounting for Non-Accountants" prints "BAC 3" (self-references): recorded source gaps, unknown,
refer the student to the college; nothing is borrowed from the BSE Franchising & Trading page.
Standing approval otherwise: "&" and "and" lists all required; "ENTRE 2&3", "ENTRE 5 & 7",
"ENTRE 7, 8 & BAC 3" written out with the repeated prefix.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BS ENTREP - AGRI BUSINESS/BSE-Agribusiness-for-student-new-version.pdf`,
SHA256 `a1b2f972789a82a59cc194461a2bc6b4d742b47177d0ea68e2fbcd62d524e67e`. Scope `palsu-bse-agri` / `bse-agri-2018-2019`, review `p09-bse-agri-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

BAC 2 "GE-MMW & ENTRE 3"; ENTRE 4 "ENTRE 2&3"; PATH Fit 3 "PATH Fit 1"; ENTRE 7 "ENTRE 3 & BAC 4"; ST 3 "BAC 4 & ST 2"; ENTRE 8 "ENTRE 5"; CBMEC 2 "CBMEC 1"; BAC 4 "BAC 4"; ENTRE 9 "GE-ET & ENTRE 6"; ENTRE 14 "ENTRE 10"; ENTRE 2 "ENTRE 1"; ENTRE 3 "BAC 1"; NSTP 2 "NSTP 1"; PATH Fit 2 "PATH Fit 1"; GE-LWR "GE-PH"; ENTRE 5 "ENTRE 4"; BAC 3 "BAC 3"; Elective 2 "ENTRE 4"; ST 2 "ST 1"; ENTRE 6 "BAC 2"; PATH Fit 4 "PATH Fit 1"; GE-IER "BE 1001 and BE 1002"; ENTRE 10 "ENTRE 5 & 7"; ST 4 "ST 1"; ENTRE 11 "Elective 3 & ENTRE 8"; ENTRE 12 "ENTRE 7, 8 & BAC 3"; Elective 5 "Elective 4"; ENTRE 15 "ENTRE 14".

53 courses; 28 printed cells; 25 blank cells stay **unknown**, not "no prerequisite": MKTG 2001, GE-UTS, GE-CW, GE-PC, ENTRE 1, GE-PS, GE-PH, NSTP 1, PATH Fit 1, GE-STS, BE 1001, Elective 1, ST 1, BAC 1, GE-Elect: GS, Elective 3, Elective 4, GE-Elect: ES, GE-ET, GE-MMW, GE-AA, BE 1002, GE-Elect: IT, CBMEC 1, ENTRE 13.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): ENTRE 4: "3" -> ENTRE 3; ENTRE 10: "7" -> ENTRE 7; ENTRE 12: "8" -> ENTRE 8.
- Source gap (no such course): BAC 4: self-reference "BAC 4"; BAC 3: self-reference "BAC 3".
- List -> all required: BAC 2: "GE-MMW & ENTRE 3"; ENTRE 4: "ENTRE 2&3"; ENTRE 7: "ENTRE 3 & BAC 4"; ST 3: "BAC 4 & ST 2"; ENTRE 9: "GE-ET & ENTRE 6"; GE-IER: "BE 1001 and BE 1002"; ENTRE 10: "ENTRE 5 & 7"; ENTRE 11: "Elective 3 & ENTRE 8"; ENTRE 12: "ENTRE 7, 8 & BAC 3".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bse-agri/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 53 reviewed courses, kinds {'unresolved': 27, 'all_of': 9, 'course': 17},
activation_allowed false, file SHA256 `233fab0f0e9f28664e90fe73a214340b0d270d98d9f2b41d2e2466a24f404818`.
Real SWI-Prolog/Janus checks (offline research path): 8/8 as the readings imply:

- ENTRE 4 {'passed': ['ENTRE 2', 'ENTRE 3']} -> eligible (expected eligible)
- ENTRE 4 {'passed': ['ENTRE 2'], 'failed': ['ENTRE 3']} -> ineligible (expected ineligible)
- ENTRE 12 {'passed': ['ENTRE 7', 'ENTRE 8', 'BAC 3']} -> eligible (expected eligible)
- GE-IER {'passed': ['BE 1001', 'BE 1002']} -> eligible (expected eligible)
- BAC 4 {'passed': ['BAC 3']} -> unknown (expected unknown)
- BAC 3 {} -> unknown (expected unknown)
- ENTRE 7 {'failed': ['BAC 4']} -> ineligible (expected ineligible)
- ENTRE 15 {'passed': ['ENTRE 14']} -> eligible (expected eligible)

Affected by ENTRE 1: ENTRE 10, ENTRE 11, ENTRE 12, ENTRE 14, ENTRE 15, ENTRE 2, ENTRE 4, ENTRE 5, ENTRE 8, Elective 2.
Affected by BAC 4: ENTRE 10, ENTRE 12, ENTRE 14, ENTRE 15, ENTRE 7, ST 3.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
