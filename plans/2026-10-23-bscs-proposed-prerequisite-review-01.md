# BS Computer Science, proposed curriculum (2025-2026) prerequisite review 01

23 October 2026, College of Sciences. Full review of the PROPOSED BSCS curriculum (Phase 06 delivered
five courses only). Read from the rendered page (`bscs-new/page.png`). "Proposed Bachelor of Science
in Computer Science Program of Study, Proposed Date of Implementation: First Semester, SY 2025-2026"
(section VIII of the BOR-approval document, rev02 v7, 6 August 2025, page 50). The "proposed" label
is preserved (owner guidance: incoming students use it). Undergraduate: in scope. Eight columns.

Consistency with Phase 06: same source version and course identities; CS 1 and CC 2/L (blank,
unknown), CC 3/L (CC 2/L), CS 2 (CS 1), CC 5/L (CC 3/L + CS 2) reproduced exactly.

Printed totals 23/23/24/23/24/23/14/5 match; total 159 matches. Title superscripts 1-26 and the
colour legend (added / transferred / modified courses) and the CS Elective 4/5 option lists change no
prerequisite. All readings fall under the standing approval: comma, semicolon-free and one-per-line
lists all required ("CS 6/L" / "CS 10/L"; "CS Elect 1" / "CS 5/L" / "AMR 1"); the trailing comma in
CS Elect 2/L's "CS 5/L, CC 4/L," ignored; "GE: MMW" -> GE-MMW and "CS Elect 1" -> CS Elect 1/L (single
obvious match); "70% of the total units of the past semesters(.)" and "90% of all major courses" kept as
printed. Note on the page: "All major courses are written in italics" (not used to expand conditions).

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CS/Computer Science/New Curriculum (2025-2026)/1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf`,
SHA256 `600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664`. Scope `palsu-bscs` / `bscs-proposed-2025-2026`, review `p09-bscs-proposed-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

CS 3 "CS 2, CC 2/L"; CS 4/L "CC 3/L, CC 1/L"; CS 5/L "CC 3/L"; CC 4/L "CC 3/L, CS 2"; CC 5/L "CC 3/L, CS 2"; AMR 2 "GE: MMW"; PATHFit 3 "PATH Fit 2"; CS 10/L "CC 5/L"; CS 11/L "CS 3"; CS Elect 1/L "CC 4/L, CS 3"; CS Elect 2/L "CS 5/L, CC 4/L,"; CC 6/L "CS 4/L, CS 5/L"; CS 16/L "CC 6/L"; CS 17 "CC 5/L, CC 6/L"; CS Elect 5/L "70% of the total units of the past semesters."; Thesis 2 "Thesis 1"; CS 2 "CS 1"; CC 3/L "CC 2/L"; PATHFit 2 "PATH Fit 1"; NSTP 2 "NSTP 1"; CS 6/L "CC 4/L, CC 1/L"; CS 7 "CC 4/L, CS 3"; CS 8/L "CC 1/L"; CS 9/L "CS 5/L, CC 5/L"; PATHFit 4 "PATH Fit 2"; CS 12/L "CS 9/L"; CS 13/L "CS 6/L CS 10/L"; CS 14/L "CS 6/L, CS 7"; CS 15/L "CC 4/L, CS 6/L"; CS Elect 3/L "CS Elect 1 CS 5/L AMR 1"; CS Elect 4/L "70% of the total units of the past semesters"; Thesis 1 "CS 9/L, CS Elect 1/L"; PRACTICUM "90% of all major courses"; Thesis 3 "Thesis 2".

55 courses; 34 printed cells; 21 blank cells stay **unknown**, not "no prerequisite": CS 1, CC 1/L, CC 2/L, GE-AA, GE-PH, GE-MMW, PATHFit 1, NSTP 1, GE-Elect: EM, GE-ET, GE-Elect: ES, GE-IER, GE-Elect: LIT, Electronics/L, AMR 1, GE-PC, GE-UTS, GE-CW, GE-LWR, GE-PS, GE-STS.

## Rules applied

- Kept as printed, unknown: CS Elect 5/L: "70% of the total units of the past semesters."; CS Elect 4/L: "70% of the total units of the past semesters"; PRACTICUM: "90% of all major courses".
- Shortened/variant code -> the one matching course: AMR 2: "GE: MMW" -> GE-MMW; CS Elect 3/L: "CS Elect 1" -> CS Elect 1/L.
- Spacing/case-only difference -> the one matching course: PATHFit 3: "PATH Fit 2" -> PATHFit 2; PATHFit 2: "PATH Fit 1" -> PATHFit 1; PATHFit 4: "PATH Fit 2" -> PATHFit 2.
- List -> all required: CS 3: "CS 2, CC 2/L"; CS 4/L: "CC 3/L, CC 1/L"; CC 4/L: "CC 3/L, CS 2"; CC 5/L: "CC 3/L, CS 2"; CS Elect 1/L: "CC 4/L, CS 3"; CS Elect 2/L: "CS 5/L, CC 4/L,"; CC 6/L: "CS 4/L, CS 5/L"; CS 17: "CC 5/L, CC 6/L"; CS 6/L: "CC 4/L, CC 1/L"; CS 7: "CC 4/L, CS 3"; CS 9/L: "CS 5/L, CC 5/L"; CS 13/L: "CS 6/L CS 10/L"; CS 14/L: "CS 6/L, CS 7"; CS 15/L: "CC 4/L, CS 6/L"; CS Elect 3/L: "CS Elect 1 CS 5/L AMR 1"; Thesis 1: "CS 9/L, CS Elect 1/L".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bscs-new/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 55 reviewed courses, kinds {'unresolved': 24, 'course': 15, 'all_of': 16},
activation_allowed false, file SHA256 `a3d6a438eb96d462de7a909bad00a5a5b139ee607584111a353a1a491e53c60a`.
Real SWI-Prolog/Janus checks (offline research path): 11/11 as the readings imply:

- CC 5/L {'passed': ['CC 3/L', 'CS 2']} -> eligible (expected eligible)
- CC 5/L {'passed': ['CC 3/L'], 'failed': ['CS 2']} -> ineligible (expected ineligible)
- CS 2 {'passed': ['CS 1']} -> eligible (expected eligible)
- CC 3/L {'passed': ['CC 2/L']} -> eligible (expected eligible)
- AMR 2 {'passed': ['GE-MMW']} -> eligible (expected eligible)
- CS Elect 2/L {'passed': ['CS 5/L', 'CC 4/L']} -> eligible (expected eligible)
- CS Elect 3/L {'passed': ['CS Elect 1/L', 'CS 5/L', 'AMR 1']} -> eligible (expected eligible)
- CS Elect 3/L {'passed': ['CS 5/L', 'AMR 1']} -> unknown (expected unknown)
- PATHFit 3 {'passed': ['PATHFit 2']} -> eligible (expected eligible)
- PRACTICUM {} -> unknown (expected unknown)
- CS 1 {} -> unknown (expected unknown)

Affected by CS 1: CC 4/L, CC 5/L, CS 10/L, CS 11/L, CS 12/L, CS 13/L, CS 14/L, CS 15/L, CS 17, CS 2, CS 3, CS 6/L, CS 7, CS 9/L, CS Elect 1/L, CS Elect 2/L, CS Elect 3/L, Thesis 1, Thesis 2, Thesis 3.
Affected by CC 4/L: CS 13/L, CS 14/L, CS 15/L, CS 6/L, CS 7, CS Elect 1/L, CS Elect 2/L, CS Elect 3/L, Thesis 1, Thesis 2, Thesis 3.

Not yet loaded into Supabase or wired into the runtime release.
