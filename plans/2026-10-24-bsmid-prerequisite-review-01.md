# BS Midwifery (2019-2020) prerequisite review 01

24 October 2026, College of Nursing and Health Sciences. Read from the rendered page (`bsmid/page0.png`).
"Bachelor of Science in Midwifery, Curriculum Program of Study, Effective SY 2019-2020*", Doc. Ref.
PSU-CIM-CUR-0018B (*BOR Res. No. 66 s. 2019 dated 3 July 2019). Undergraduate: in scope. Units are split
into LEC / RLE / LAB columns.

Important limitation: this prospectus lists only the THIRD and FOURTH years (total 73 units). Cells refer
to earlier courses that are not on the page (Mid 102A, Mid 102 B, "Mid 102A&B", "M102A& B", HC 12,
GE MMW, Mid 100-103): under the standing rule each is a recorded source gap (unknown, refer to the
college). A row "Foreign Language (Arabic)" (3 units, third year first semester) has no printed course
code, so it is not cataloged as a course; nothing on the page refers to it.

Owner decisions (24 Oct 2026): A/B pairs - "Mid104 A&B" = Mid 104 A- and Mid104 - B, "Mid105 A and
Mid105 B" = Mid 105-A and Mid 105-B; ranges - "Mid 100- Mid 105" = Mid 100 to Mid 105 (A and B where they
exist; 100-103 are gaps). CHM -B "All Midwifery second year subjects" kept as printed (unknown); the
cell wraps "Midwifer" / "y". Printed totals on the page do not all reconcile with the LEC/RLE/LAB
columns (e.g. third year first semester prints 15/6/2 and 23); recorded, no unit facts are authored.

Source: `dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/CNHS/BS-Midwifery-for-student-new-version.pdf`,
SHA256 `b72a9c26d7478f7ed921408d74c72bab718c31c59a7f63c968fdc367623f7b2d`. Scope `palsu-bsmid` / `bsmid-2019-2020`, review `p09-bsmid-review-01`.

## Prerequisite cells read from the rendered page (visible printed text)

Mid 104 A- "Mid 102A"; Mid104 – B "Mid 102 B"; CHM-A "HC 12"; CHM -B "All Midwifery second year subjects"; MidPharm "Mid 102A&B"; Phy 1 F/L "GE MMW"; Biostat 1 "GE MMW"; Mid Res 1 "Biostat 1"; Mid106-A "Mid 100- Mid 105"; Mid 106-B "Mid105 A and Mid105 B"; Mid 105-A "M102A& B Mid104 A&B"; Mid 105-B "M102A& B Mid104 A&B"; MidRes2 "Mid Res 1"; HCFM-A "ME".

21 courses; 14 printed cells; 7 blank cells stay **unknown**, not "no prerequisite": Chem 2/L, GE-Lit, ME, ECC, ECC-B, GE PS, HCFM-B.

## Rules applied

- Shorthand or range written out, all required (owner, 23 Oct 2026): MidPharm: "Mid 102A&B" -> Mid 102A, Mid 102B; Mid106-A: "Mid 100- Mid 105" -> Mid 100, Mid 101, Mid 102, Mid 103, Mid 104 A-, Mid104 – B, Mid 105-A, Mid 105-B; Mid 106-B: "Mid105 A and Mid105 B" -> Mid 105-A, Mid 105-B; Mid 105-A: "M102A& B Mid104 A&B" -> M102A, M102B, Mid 104 A-, Mid104 – B; Mid 105-B: "M102A& B Mid104 A&B" -> M102A, M102B, Mid 104 A-, Mid104 – B.
- Kept as printed, unknown: CHM -B: "All Midwifery second year subjects".
- Source gap (no such course): Mid 104 A-: "Mid 102A"; Mid104 – B: "Mid 102 B"; CHM-A: "HC 12"; MidPharm: "Mid 102A"; MidPharm: "Mid 102B"; Phy 1 F/L: "GE MMW"; Biostat 1: "GE MMW"; Mid106-A: "Mid 100"; Mid106-A: "Mid 101"; Mid106-A: "Mid 102"; Mid106-A: "Mid 103"; Mid 105-A: "M102A"; Mid 105-A: "M102B"; Mid 105-B: "M102A"; Mid 105-B: "M102B".
- List -> all required: MidPharm: "Mid 102A&B"; Mid106-A: "Mid 100- Mid 105"; Mid 106-B: "Mid105 A and Mid105 B"; Mid 105-A: "M102A& B Mid104 A&B"; Mid 105-B: "M102A& B Mid104 A&B".

## Authoring and checks

`audit-evidence/p09-program-reviews/author_program.py` on `bsmid/spec.json`: all codes and printed cells matched the
native PDF text by page geometry. Ledger: 21 reviewed courses, kinds {'unresolved': 13, 'course': 3, 'all_of': 5},
activation_allowed false, file SHA256 `bf5306b91ddfe9f0acb49d38c7cd81f61b09f87e8ccc22ae666a11401845257b`.
Real SWI-Prolog/Janus checks (offline research path): 9/9 as the readings imply:

- Mid Res 1 {'passed': ['Biostat 1']} -> eligible (expected eligible)
- MidRes2 {'failed': ['Mid Res 1']} -> ineligible (expected ineligible)
- Mid 106-B {'passed': ['Mid 105-A', 'Mid 105-B']} -> eligible (expected eligible)
- Mid 105-A {'passed': ['Mid 104 A-', 'Mid104 – B']} -> unknown (expected unknown)
- Mid 105-A {'failed': ['Mid 104 A-']} -> ineligible (expected ineligible)
- Mid106-A {'passed': ['Mid 104 A-', 'Mid104 – B', 'Mid 105-A', 'Mid 105-B']} -> unknown (expected unknown)
- HCFM-A {'passed': ['ME']} -> eligible (expected eligible)
- CHM -B {} -> unknown (expected unknown)
- Phy 1 F/L {} -> unknown (expected unknown)

Affected by Mid Res 1: MidRes2.
Affected by Mid 104 A-: Mid 105-A, Mid 105-B, Mid 106-B, Mid106-A.

Not yet loaded into Supabase or wired into the runtime release.

Loaded to hosted research release p09-research-selected-20261022 on 24 Oct 2026 (runtime read-back equal).
