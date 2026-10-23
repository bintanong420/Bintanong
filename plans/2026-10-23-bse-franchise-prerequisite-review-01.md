# BS Entrepreneurship, Specialized Track 1: Franchising and Trading (2018-2019) prerequisite review 01

23 October 2026, College of Business and Accountancy. Read from the rendered page (`bse-franchise/page.png`).
"Bachelor of Science in Entrepreneurship (Specialized Track 1: Franchising and Trading), Curriculum
Program of Study, Effective SY 2018-2019*" (*BOR Res. No. 62 s. 2019). Undergraduate: in scope.
Printed term totals 26/26/26/26/24/21/5/5 match the listed units (year 2 sem 2's "26" is printed in
the prerequisite column); total 159. All readings fall under the standing approval ("&"/"and" lists
all required; "ENTRE 2&3", "ENTRE 5 & 7", "ENTRE 7, 8 & BAC 4" written out). ENTRE 3 has a blank cell.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CBA/BS ENTREP - FRANCHISING TRADING/BSE-Franchising-and-Trading-for-student-new-version.pdf`,
SHA256 `531d0b3a86afa33a876bddaccf2c29f20a4f6232ccd88749c88438de3581a20e`. Scope `palsu-bse-franchise` / `bse-franchise-2018-2019`, review `p09-bse-franchise-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

BAC 2 "GE-MMW & ENTRE 3"; ENTRE 4 "ENTRE 2&3"; PATH Fit 3 "PATH Fit 1"; ENTRE 7 "ENTRE 3 & BAC 4"; ST 3 "BAC 4 & ST 2"; ENTRE 8 "ENTRE 5"; CBMEC 2 "CBMEC 1"; BAC 4 "BAC 3"; Elective 4 "ENTRE 5"; ENTRE 9 "GE-ET & ENTRE 6"; ENTRE 14 "ENTRE 10"; ENTRE 2 "ENTRE 1"; NSTP 2 "NSTP 1"; PATH Fit 2 "PATH Fit 1"; GE-LWR "GE-PH"; ENTRE 5 "ENTRE 4"; BAC 3 "BAC 2"; Elective 2 "ENTRE 4"; ST 2 "ST 1"; ENTRE 6 "BAC 2"; PATH Fit 4 "PATH Fit 1"; GE-IER "BE 1001 and BE 1002"; ENTRE 10 "ENTRE 5 & 7"; ST 4 "ST 3"; ENTRE 11 "Elective 3 & ENTRE 8"; ENTRE 12 "ENTRE 7, 8 & BAC 4"; Elective 5 "Elective 4"; ENTRE 15 "ENTRE 14".

53 courses; 28 printed cells; 25 blank cells stay **unknown**, not "no prerequisite": MKTG 2001, GE-UTS, GE-CW, GE-PC, ENTRE 1, GE-PS, GE-PH, NSTP 1, PATH Fit 1, GE-STS, BE 1001, Elective 1, ST 1, BAC 1, GE-Elect: GS, Elective 3, GE-Elect: ES, GE-ET, GE-MMW, GE-AA, ENTRE 3, BE 1002, GE-Elect: IT, CBMEC 1, ENTRE 13.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): ENTRE 4: "3" -> ENTRE 3; ENTRE 10: "7" -> ENTRE 7; ENTRE 12: "8" -> ENTRE 8.
- List -> all required: BAC 2: "GE-MMW & ENTRE 3"; ENTRE 4: "ENTRE 2&3"; ENTRE 7: "ENTRE 3 & BAC 4"; ST 3: "BAC 4 & ST 2"; ENTRE 9: "GE-ET & ENTRE 6"; GE-IER: "BE 1001 and BE 1002"; ENTRE 10: "ENTRE 5 & 7"; ENTRE 11: "Elective 3 & ENTRE 8"; ENTRE 12: "ENTRE 7, 8 & BAC 4".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bse-franchise/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 53 reviewed courses, kinds {'course': 19, 'all_of': 9, 'unresolved': 25},
activation_allowed false, file SHA256 `8993012a29e2f92885bc5e51d111f24c38849968092eed58f4c4e700f8c40000`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- BAC 4 {'passed': ['BAC 3']} -> eligible (expected eligible)
- BAC 3 {'failed': ['BAC 2']} -> ineligible (expected ineligible)
- ENTRE 12 {'passed': ['ENTRE 7', 'ENTRE 8', 'BAC 4']} -> eligible (expected eligible)
- ENTRE 10 {'passed': ['ENTRE 5', 'ENTRE 7']} -> eligible (expected eligible)
- ENTRE 11 {'passed': ['Elective 3', 'ENTRE 8']} -> eligible (expected eligible)
- ENTRE 3 {} -> unknown (expected unknown)
- ST 4 {'passed': ['ST 3']} -> eligible (expected eligible)

Affected by ENTRE 1: ENTRE 10, ENTRE 11, ENTRE 12, ENTRE 14, ENTRE 15, ENTRE 2, ENTRE 4, ENTRE 5, ENTRE 8, Elective 2, Elective 4, Elective 5.
Affected by BAC 2: BAC 3, BAC 4, ENTRE 10, ENTRE 12, ENTRE 14, ENTRE 15, ENTRE 6, ENTRE 7, ENTRE 9, ST 3, ST 4.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
