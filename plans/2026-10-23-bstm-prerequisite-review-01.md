# BS Tourism Management (2018-2019) prerequisite review 01

23 October 2026, College of Hospitality and Tourism Management. Read from the rendered page
(`bstm/page.png`). "Bachelor of Science in Tourism Management, Curriculum Program of Study, Effective SY
2018-2019*", Doc. Ref. PSU-CIM-CUR-017B (*BOR Res. No. 12 s. 2019 dated 14 March 2019). Undergraduate:
in scope. Printed term totals 26/26/25/23/18/18/summer 3/15/3 match the listed units; total 152.
All readings fall under the standing approval: "&"/comma lists all required; PATH-Fit 4's two lines
"PATH Fit 1" / "PATH Fit 3" both required; "GE Elect: PIC/ES" -> GE-Elect: PIC/ES, "PATH Fit 1" ->
PATH-Fit 1 (punctuation). Layout: summer row Pract 1-TM spans both halves (prerequisite "TPC 9/L" in the
right column). Characters inside three prerequisite cells that are not visible there (a "3" in TPS 4 and
TPS 5, a "w" in Pract 2-TM) are not used (visible-text rule).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CHTM/BSTM-for-student-new-version.pdf`,
SHA256 `7186c5428945363aaa063c68971a9f8b280ede361945574566ab7c86c8e452eb`. Scope `palsu-bstm` / `bstm-2018-2019`, review `p09-bstm-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

THC-PDE "GE-ET"; THC-QSM "THC-Macro"; TPS 1 "THC-Mktg & GE Elect: PIC"; TPS 2 "THC-Mktg & GE Elect: ES"; PATH-Fit 3 "PATH-Fit 1"; TMPE 3 "TPS 2"; TMPE 4 "THC-Micro"; TPC 3 "GE-PS & THC-PC"; TPC 4 "BME 1T & THC-Mktg"; TPC 5 "THC-Micro"; TPC 6 "THC-QSM"; Pract 1-TM "TPC 9/L"; TMPE 5 "GE-PC & TPC 8/L"; TPC 10 "THC-RM, TPC 6 & BME 2T"; TPS 4 "THC-RM, TPC 6 & BME 2T"; TPS 5 "TPC 7"; THC-Entrep "THC-Mktg"; THC-Micro "THC-Macro"; TPC 2 / FL 2 "TPC 1 / FL 1"; PATH-Fit 2 "PATH-Fit 1"; NSTP 2 "NSTP 1"; THC-LA "THC-PDE"; THC-MD "BME 1T & THC-Micro"; THC-PC "TPS 1"; TMPE 2 "TPS 1 & THC-Micro"; TPS 3 "BME 1T & THC-Micro"; PATH-Fit 4 "PATH Fit 1 PATH Fit 3"; BME 2T "BME 1T & TPC 6"; GE-LWR "GE-PH"; THC-RM "TPC 6 & THC-LA"; TPC 7 "THC-Micro & TPC 3"; TPC 8/L "THC-Mktg & THC-MD"; TPC 9/L "TPC 3"; Pract 2-TM "TPC 10 & TPS 4".

54 courses; 34 printed cells; 20 blank cells stay **unknown**, not "no prerequisite": GE-Elect: PPC, GE-PC, GE-STS, GE-UTS, THC-Macro, THC-Mktg, TPC 1 / FL 1, PATH-Fit 1, NSTP 1, BME 1T, GE-CW, GE-PH, TMPE 1 / LL 1, GE-IER, GE-Elect: ES, GE-Elect: PIC, GE-ET, GE-PS, GE AA, GE MMW.

Native text clipped out of the printed page (recorded, not used; owner 23 Oct 2026):

- TPS 4: native cell "3 THC-RM, TPC 6 & BME 2T"; hidden '3'
- TPS 5: native cell "3 TPC 7"; hidden '3'
- Pract 2-TM: native cell "w TPC 10 & TPS 4"; hidden 'w'

## Rules applied

- Spacing, case or hyphen variant -> the one matching course: TPS 1: "GE Elect: PIC" -> GE-Elect: PIC; TPS 2: "GE Elect: ES" -> GE-Elect: ES; PATH-Fit 4: "PATH Fit 1" -> PATH-Fit 1; PATH-Fit 4: "PATH Fit 3" -> PATH-Fit 3.
- List -> all required: TPS 1: "THC-Mktg & GE Elect: PIC"; TPS 2: "THC-Mktg & GE Elect: ES"; TPC 3: "GE-PS & THC-PC"; TPC 4: "BME 1T & THC-Mktg"; TMPE 5: "GE-PC & TPC 8/L"; TPC 10: "THC-RM, TPC 6 & BME 2T"; TPS 4: "THC-RM, TPC 6 & BME 2T"; THC-MD: "BME 1T & THC-Micro"; TMPE 2: "TPS 1 & THC-Micro"; TPS 3: "BME 1T & THC-Micro"; PATH-Fit 4: "PATH Fit 1 PATH Fit 3"; BME 2T: "BME 1T & TPC 6"; THC-RM: "TPC 6 & THC-LA"; TPC 7: "THC-Micro & TPC 3"; TPC 8/L: "THC-Mktg & THC-MD"; Pract 2-TM: "TPC 10 & TPS 4".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bstm/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 54 reviewed courses, kinds {'course': 18, 'all_of': 16, 'unresolved': 20},
activation_allowed false, file SHA256 `fe898dae5f33e7ca42b2202a792f5c888e66fde896d3291169519d14260bfd5f`.
Real SWI-Prolog/Janus checks (offline research path): 7/7 as the readings imply:

- TPS 1 {'passed': ['THC-Mktg', 'GE-Elect: PIC']} -> eligible (expected eligible)
- Pract 1-TM {'passed': ['TPC 9/L']} -> eligible (expected eligible)
- Pract 2-TM {'passed': ['TPC 10', 'TPS 4']} -> eligible (expected eligible)
- TPC 10 {'passed': ['THC-RM', 'TPC 6'], 'failed': ['BME 2T']} -> ineligible (expected ineligible)
- TPC 2 / FL 2 {'passed': ['TPC 1 / FL 1']} -> eligible (expected eligible)
- PATH-Fit 4 {'passed': ['PATH-Fit 1', 'PATH-Fit 3']} -> eligible (expected eligible)
- THC-Macro {} -> unknown (expected unknown)

Affected by THC-Macro: BME 2T, Pract 2-TM, THC-MD, THC-Micro, THC-QSM, THC-RM, TMPE 2, TMPE 4, TMPE 5, TPC 10, TPC 5, TPC 6, TPC 7, TPC 8/L, TPS 3, TPS 4, TPS 5.
Affected by TPC 6: BME 2T, Pract 2-TM, THC-RM, TPC 10, TPS 4.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
