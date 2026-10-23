# BS Management Accounting (2022-2023) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bsma/page.png`).
"Bachelor of Science in Management Accounting, Curriculum Program of Study (Based on CMO no. 28, s.
2017), Effective SY 2022-2023", Doc. Ref. PSU-CIM-CUR-043B (*BOR Res. No. 78 s. 2022 dated 14 June
2022). Undergraduate: in scope. Printed term totals 26/26/26/26/24/24/summer 3/21/6 match the listed
units (AE 5 "2/1" counted as 3); total 182. All readings fall under the standing approval: comma
lists all required; PrE 10 "4th year standing" unknown unless the year is given; AE 25b "All courses"
kept as printed (unknown). GE-LWR and NSTP 2 have blank cells on this page (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/MANAGEMENT ACCOUNTING/BS-Management-Accounting-prospectus_students-copy_07.07.2022.pdf`,
SHA256 `4c54b249162db431225fc2f179f1da2dc6555d8783f0e838c2b0786aff55993e`. Scope `palsu-bsma` / `bsma-2022-2023`, review `p09-bsma-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

AE 8 "AE 2"; PATH-Fit 3 "PATH-Fit 1"; AE 14 "AE 3"; AE 15 "AE 11"; AE 16 "AE 12"; AE 17 "AE 2, AE 5"; AE 18 "AE 9"; PrE 4 "AE 3"; PrE 5 "AE 3"; AE 25a "AE 20, PrE 5"; AE 27 "AE 23, AE 24"; PrE 9 "AE 20"; PE1 "AE 12"; PE2 "AE 12"; AE 2 "AE 1"; AE 3 "AE 1"; PATH-Fit 2 "PATH-Fit 1"; AE 10 "AE 7"; AE 11 "AE 8"; AE 12 "AE 3"; PATH-Fit 4 "PATH-Fit 1"; AE 20 "AE 14"; PrE 6 "AE 12"; PrE 7 "AE 15"; PrE 8 "AE 17"; AE 25b "All courses"; PrE 10 "4 th year standing".

62 courses; 27 printed cells; 35 blank cells stay **unknown**, not "no prerequisite": GE-AA, GE-CW, GE-Elect: ES, GE-Elect: IT, GE-PH, GE-UTS, AE 1, PATH-Fit 1, NSTP 1, GE-ET, GE-PS, GE-STS, AE 6, AE 7, PrE 1, PrE 2, AE 19, GE-IER, AE 26, CBME 2, GE-Elect: EM, GE-MMW, GE-PC, AE 4, AE 5, NSTP 2, GE-LWR, AE 9, AE 13, PrE 3, CBME 1, AE 21, AE 22, AE 23, AE 24.

## Rules applied

- Year standing -> unknown unless the student states their year: PrE 10: "4 th year standing".
- Kept as printed, unknown: AE 25b: "All courses".
- List -> all required: AE 17: "AE 2, AE 5"; AE 25a: "AE 20, PrE 5"; AE 27: "AE 23, AE 24".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsma/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 62 reviewed courses, kinds {'course': 22, 'all_of': 3, 'unresolved': 37},
activation_allowed false, file SHA256 `af8d01ab86454bb663835bacac60d849d9d801a39b17f005faaf92e9a8e804d7`.
Real SWI-Prolog/Janus checks (offline research path): 8/8 as the readings imply:

- AE 2 {'passed': ['AE 1']} -> eligible (expected eligible)
- AE 17 {'passed': ['AE 2', 'AE 5']} -> eligible (expected eligible)
- AE 17 {'passed': ['AE 2'], 'failed': ['AE 5']} -> ineligible (expected ineligible)
- AE 25a {'passed': ['AE 20', 'PrE 5']} -> eligible (expected eligible)
- PrE 10 {} -> unknown (expected unknown)
- AE 25b {} -> unknown (expected unknown)
- PE1 {'passed': ['AE 12']} -> eligible (expected eligible)
- AE 1 {} -> unknown (expected unknown)

Affected by AE 1: AE 11, AE 12, AE 14, AE 15, AE 16, AE 17, AE 2, AE 20, AE 25a, AE 3, AE 8, PE1, PE2, PrE 4, PrE 5, PrE 6, PrE 7, PrE 8, PrE 9.
Affected by AE 3: AE 12, AE 14, AE 16, AE 20, AE 25a, PE1, PE2, PrE 4, PrE 5, PrE 6, PrE 9.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
