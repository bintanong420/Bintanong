# BS Social Work (2018-2019) prerequisite review 01

23 October 2026, College of Arts and Humanities. Read from the rendered page (`bssw/page.png`).
"Bachelor of Science in Social Work, Curriculum Program of Study, Effective SY 2018-2019*" (*BOR Res.
No. 62 s. 2019). Undergraduate: in scope. Printed term totals 23/23/23/23/15/15/18/18 match the listed
units; total 158 matches. All readings fall under the owner's standing approval: comma and "&" lists
are all required ("SW 20 & SW 24", "SW 23 & SW 24", "SW 25, SW 26, & SW 28" written out); SW 34's "All
major subjects" kept as printed (unknown). NSTP 2 has a blank cell on this page (unknown).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CAH/Social Work/BS-Social-Work-for-student-new-version.pdf`,
SHA256 `ceca3ff4b88ec275550289a3b9cfe7284eb9e89a61646f20060bfc2369623ab3`. Scope `palsu-bssw` / `bssw-2018-2019`, review `p09-bssw-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

SW 16 "SW 13, SW 15"; SW 17 "SW 13"; SW 19 "SW 13"; PATH Fit 3 "PATH Fit 1"; SW 25 "SW 20 & SW 24"; SW 26 "SW 23 & SW 24"; SW 27 "SW 21"; SW 28 "SW 24"; SW 34 "All major subjects"; SW 13 "SW 11"; SW 14 "SW 11"; SW 15 "SW 11, SW 12"; PATH Fit 2 "PATH Fit 1"; SW 20 "SW 16"; SW 21 "SW 18"; SW 22 "SW 16, SW 17"; SW 23 "SW 16 , SW 17"; SW 24 "SW 16"; GE-LWR "GE-PH"; PATH Fit 4 "PATH Fit 1"; SW 30 "SW 26, SW 28"; SW 31 "SW 24 , SW 28"; SW 33 "SW 25, SW 26, & SW 28"; SW 35 "SW 34"; SW 36 "SW 34".

46 courses; 25 printed cells; 21 blank cells stay **unknown**, not "no prerequisite": GE-UTS, GE-PC, GE-CW, SW 11, SW 12, GE-PS, PATH Fit 1, NSTP1, GE-STS, SW 18, GE-Elect: GS, GE-PH, SW 29, GE-IER, GE-MMW, GE-AA, GE-Elect: ES, NSTP 2, GE-Elect: PIC, SW 32, GE-ET.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): SW 25: "SW 20 & SW 24" -> SW 20, SW 24; SW 26: "SW 23 & SW 24" -> SW 23, SW 24; SW 33: "SW 25, SW 26, & SW 28" -> SW 25, SW 26, SW 28.
- Kept as printed, unknown: SW 34: "All major subjects".
- List -> all required: SW 16: "SW 13, SW 15"; SW 25: "SW 20 & SW 24"; SW 26: "SW 23 & SW 24"; SW 15: "SW 11, SW 12"; SW 22: "SW 16, SW 17"; SW 23: "SW 16 , SW 17"; SW 30: "SW 26, SW 28"; SW 31: "SW 24 , SW 28"; SW 33: "SW 25, SW 26, & SW 28".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bssw/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 46 reviewed courses, kinds {'course': 15, 'unresolved': 22, 'all_of': 9},
activation_allowed false, file SHA256 `b40386dba61046df6b370535948e517d8f9aa00fdd5ea340d4e9be35db4342ef`.
Real SWI-Prolog/Janus checks (offline research path): 9/9 as the readings imply:

- SW 13 {'passed': ['SW 11']} -> eligible (expected eligible)
- SW 15 {'passed': ['SW 11', 'SW 12']} -> eligible (expected eligible)
- SW 15 {'passed': ['SW 11'], 'failed': ['SW 12']} -> ineligible (expected ineligible)
- SW 25 {'passed': ['SW 20', 'SW 24']} -> eligible (expected eligible)
- SW 33 {'passed': ['SW 25', 'SW 26', 'SW 28']} -> eligible (expected eligible)
- SW 33 {'passed': ['SW 25', 'SW 26']} -> unknown (expected unknown)
- SW 35 {'passed': ['SW 34']} -> eligible (expected eligible)
- SW 34 {} -> unknown (expected unknown)
- GE-LWR {'passed': ['GE-PH']} -> eligible (expected eligible)

Affected by SW 11: SW 13, SW 14, SW 15, SW 16, SW 17, SW 19, SW 20, SW 22, SW 23, SW 24, SW 25, SW 26, SW 28, SW 30, SW 31, SW 33.
Affected by SW 16: SW 20, SW 22, SW 23, SW 24, SW 25, SW 26, SW 28, SW 30, SW 31, SW 33.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 23 Oct 2026 (runtime read-back equal).
