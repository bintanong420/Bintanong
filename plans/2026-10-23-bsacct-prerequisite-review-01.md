# BS Accountancy (2023-2024) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from page 3 of the PDF (`bsacct/page.png`);
pages 1-2 are a promotional brochure (career paths, mission/vision, CPALE passing rates) with no
curriculum content. "Bachelor of Science in Accountancy, Curriculum Program of Study (Based on CMO No.
27, s. 2017), Effective SY 2023-2024*", Doc. Ref. PSU-CIM-CUR-006A, Rev. 01_v1, effective 7 August 2023
(*BOR Res. No. 129 s. 2023 dated 6 September 2023). Undergraduate: in scope. Eight-column table (no
Grade column). Printed term totals 26/26/summer 6/26/26/summer 9/24/24/summer 9/12/6 match the listed
units ("2/1" counted as 3); total 194. All readings fall under the standing approval: comma lists all
required; "AE1" / "AE 8" -> the printed codes "AE 1" / "AE8" (spacing); PrE9 and PrE10 "4th year
Standing" unknown unless the year is given; AE29a/AE29b "All courses" kept as printed (unknown).
Source citations point to page 3.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/ACCOUNTANCY/BS-Accountancy-for-student-new-version.pdf`,
SHA256 `8960eb8ab967613a2ac6ce5c74fa503fa8cd8397f60ca244b21f5362b9d5ea27`. Scope `palsu-bsacct` / `bsacct-2023-2024`, review `p09-bsacct-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

AE8 "AE3"; PATH Fit 3 "PATH Fit 2"; AE20 "AE8, AE14"; AE21 "AE15"; AE22 "AE8, AE14"; AE23 "AE6, AE12, AE17"; AE24 "AE18"; PrE1 "AE8, AE14"; PrE2 "AE8, AE14"; PrE3 "AE8, AE14"; GE-LWR "GE-PH"; PrE9 "4th year Standing"; PrE10 "4th year Standing"; Pro-Elect3 "PrE4"; Pro-Elect4 "AE8, AE14, AE20"; AE2 "AE1"; AE3 "AE1"; NSTP 2 "NSTP 1"; PATH Fit 2 "PATH Fit 1"; AE14 "AE 8"; AE15 "AE2"; AE17 "AE12"; PATH Fit 4 "PATH Fit 3"; AE25 "AE21"; AE26 "AE24"; AE27 "AE22"; AE28 "AE4, AE20"; PrE4 "PrE1, PrE2"; PrE5 "PrE1, PrE3"; PrE6 "PrE3"; PrE7 "AE20"; PrE8 "AE4, AE28"; AE29a "All courses"; AE29b "All courses".

66 courses; 34 printed cells; 32 blank cells stay **unknown**, not "no prerequisite": AE 1, CBME 1, GE-AA, GE-CW, GE-Elect: ES, GE-Elect: IT, GE-UTS, NSTP 1, PATH Fit 1, GE-Elect: EM, AE7, AE9, AE10, AE11, AE12, AE13, Pro-Elect1, GE-ET, GE-IER, GE-STS, AE4, AE5, AE6, GE-MMW, GE-PC, GE-PH, AE16, AE18, AE19, CBME 2, Pro-Elect2, GE-PS.

## Rules applied

- Year standing -> unknown unless the student states their year: PrE9: "4th year Standing"; PrE10: "4th year Standing".
- Kept as printed, unknown: AE29a: "All courses"; AE29b: "All courses".
- Spacing, case or hyphen variant -> the one matching course: AE2: "AE1" -> AE 1; AE3: "AE1" -> AE 1; AE14: "AE 8" -> AE8.
- List -> all required: AE20: "AE8, AE14"; AE22: "AE8, AE14"; AE23: "AE6, AE12, AE17"; PrE1: "AE8, AE14"; PrE2: "AE8, AE14"; PrE3: "AE8, AE14"; Pro-Elect4: "AE8, AE14, AE20"; AE28: "AE4, AE20"; PrE4: "PrE1, PrE2"; PrE5: "PrE1, PrE3"; PrE8: "AE4, AE28".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsacct/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 66 reviewed courses, kinds {'course': 19, 'unresolved': 36, 'all_of': 11},
activation_allowed false, file SHA256 `2a28511012eb2eb45a9a8c2d5555a8be21373bb32383911e9d059d480210a3c3`.
Real SWI-Prolog/Janus checks (offline research path): 9/9 as the readings imply:

- AE3 {'passed': ['AE 1']} -> eligible (expected eligible)
- AE14 {'passed': ['AE8']} -> eligible (expected eligible)
- AE20 {'passed': ['AE8', 'AE14']} -> eligible (expected eligible)
- AE20 {'passed': ['AE8'], 'failed': ['AE14']} -> ineligible (expected ineligible)
- AE23 {'passed': ['AE6', 'AE12', 'AE17']} -> eligible (expected eligible)
- PrE9 {} -> unknown (expected unknown)
- AE29a {} -> unknown (expected unknown)
- Pro-Elect4 {'passed': ['AE8', 'AE14', 'AE20']} -> eligible (expected eligible)
- AE 1 {} -> unknown (expected unknown)

Affected by AE 1: AE14, AE15, AE2, AE20, AE21, AE22, AE25, AE27, AE28, AE3, AE8, PrE1, PrE2, PrE3, PrE4, PrE5, PrE6, PrE7, PrE8, Pro-Elect3, Pro-Elect4.
Affected by AE8: AE14, AE20, AE22, AE27, AE28, PrE1, PrE2, PrE3, PrE4, PrE5, PrE6, PrE7, PrE8, Pro-Elect3, Pro-Elect4.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
